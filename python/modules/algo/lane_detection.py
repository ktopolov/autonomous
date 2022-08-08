"""Support code for lane line detection"""
# Standard Imports
import typing

# Third Party Imports
import numpy as np
import cv2
import matplotlib.pyplot as plt

# Local Imports
from modules.common import computer_vision as cvision

# %% ENCAPSULATIONS
class LaneLineDetector:
    """ "Class to run lane detection algorithm"""

    def __init__(
        self,
        config: dict,
        tr_cam_to_road: np.ndarray,
        camera_matrix: np.ndarray,
    ):
        """Initialize instance

        Args:
            config: Configuration parameters:
                'blur_kernel_shape': (2,) tuple stored as (width, length) in pixels
                'canny_low_threshold': int, 0-255 lower threshold for Canny edge detection
                'canny_high_threshold': int, 0-255 upper threshold for Canny edge detection
                'roi_polygon': (n_vertex,) list of (x, y) pixel coordinates defining polygon ROI
                               boundaries
                'hough_rho_res': Hough transform rho (distance from origin) resolution (pixels)
                'hough_theta_res_deg': Hough transform theta (line angle) resolution (degrees)
                'hough_accumulator_threshold': Hough transform min number of points lying on line to
                                               consider a line
                'hough_min_line_length': Hough transform minimum line length (pixels)
                'hough_max_line_gap': Hough transform maximum gap between two line points (pixels)
            tr_cam_to_road: (3, 4) transformation matrix from road to camera; composed of rotation
                            and translation: [R | t]
            camera_matrix: (3, 3) intrinsic camera matrix
        """
        self.config = config
        self.tr_cam_to_road = tr_cam_to_road
        self.camera_matrix = camera_matrix

    def run(
        self,
        image: np.ndarray,
        fig_num: typing.Union[int, str] = None,
    ) -> dict:
        """Run algorithm for lane line detection

        Args:
            image : (n_row, n_col, 3) BGR image
            fig_num: Figure number / label for plotting, if desired

        Returns:
            out: Contains output parameters
                'left_lane_angle': Angle of left lane w.r.t. road coordinates (rad)
                'right_lane_angle': Angle of right lane w.r.t. road coordinates (rad)
        """
        # Convert to HSV and select only the value channel
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        image_value = image_hsv[:, :, 2]

        # Apply Gaussian blur to image
        image_blur = cv2.GaussianBlur(image_value, self.config["blur_kernel_shape"], 0)

        # Canny Edge Detection
        image_edges = cv2.Canny(
            image_blur,
            self.config["canny_low_threshold"],
            self.config["canny_high_threshold"],
            apertureSize=3,
        )

        # Create Region of Interest Mask
        n_row, n_col, _ = image.shape
        roi_mask = np.zeros_like(image, shape=(n_row, n_col))
        cv2.fillPoly(roi_mask, np.array([self.config["roi_polygon"]]), 255)

        # Threshold for white lines only
        threshold = 200
        threshold_mask = image_value > threshold

        # Intersect edges with white threshold mask
        image_edges_with_mask = image_edges * roi_mask  # * threshold_mask

        # Detect lines in mask
        lines = cv2.HoughLinesP(
            image_edges_with_mask,
            self.config["hough_rho_res"],
            np.deg2rad(self.config["hough_theta_res_deg"]),
            threshold=self.config["hough_accumulator_threshold"],
            minLineLength=self.config["hough_min_line_length"],
            maxLineGap=self.config["hough_max_line_gap"],
        )

        # Store points belonging to each line as (n_point, xy) = (2, 2) matrix:
        # left_points[0, :] = (x1, y1)
        # left_points[1, :] = (x2, y2)
        left_points = None
        right_points = None
        n_line = lines.shape[0]
        n_row, n_col, _ = image.shape
        for i_line in range(n_line):
            # Lines ordered by confidence level
            x1, y1, x2, y2 = lines[i_line, 0, :]
            slope = (y2 - y1) / (x2 - x1)
            intercept = y2 - slope * x2
            line_side = check_lane_side(
                slope=slope, intercept=intercept, n_row=n_row, n_col=n_col
            )

            # If this line is on left and left lane not yet found...
            if (line_side == "left") and (left_points is None):
                left_points = np.stack((np.array([x1, y1]), np.array([x2, y2])), axis=0)

            # If this line is on right and right lane not yet found...
            elif (line_side == "right") and (right_points is None):
                right_points = np.stack(
                    (np.array([x1, y1]), np.array([x2, y2])), axis=0
                )

            # If both left/right lanes are found, stop looking
            if (left_points is not None) and (right_points is not None):
                break

        # === Project to real world ===
        # Left line: sample two points on line, rotate into road coordiante frame (centered at camera)
        # where x/y in road and +z out of road. Drop z coordinate and fit road-frame line
        cam_to_road = self.tr_cam_to_road[:3, :3]  # (3, 3) rotation matrix
        tvec_cam_to_road = self.tr_cam_to_road[
            :3, 3
        ]  # (3,) translation vector = -cam_to_road * p_road_in_cam_frame

        # Compute camera height off ground.
        # See http://www.cvlibs.net/datasets/kitti/setup.php for coordinate frames:
        # Camera frame: +z: forward, +x: right, +y: down (toward ground)
        p_roadorigin_cam = -np.linalg.solve(
            cam_to_road, tvec_cam_to_road
        )  # road coord frame origin in camera frame
        camera_height = p_roadorigin_cam[1]  # y-value

        # Define bird's eye frame. Note: This is similar to the "Road" coordinate frame, but chosen such
        # that the +z axis points directly downward instead of +y
        ux_road_cam = cam_to_road[
            0, :
        ]  # get the road frame basis vectors in the camera frame
        uy_road_cam = cam_to_road[1, :]
        uz_road_cam = cam_to_road[2, :]
        cam_to_bev = np.stack((uz_road_cam, ux_road_cam, uy_road_cam), axis=0)

        # Rotate to equivalent bird's eye frame (still centered at camera)
        p_bevs = []  # list for each left/right lane, each have 2 points with xyz coords
        for ii, cam_pix in enumerate([left_points, right_points]):
            bev_pix = cvision.apply_perspective_transform(
                v=cam_pix, transform=cam_to_bev
            )

            # Augment pixel to 4D so we can recover point with inverse depth
            depth = camera_height
            bev_pix_aug = cvision.augment(bev_pix)
            bev_pix_aug_4d = cvision.augment(bev_pix_aug)
            bev_pix_aug_4d[..., -1] /= depth

            # Invert perspective transform
            camera_matrix_4d = np.eye(4)
            camera_matrix_4d[:3, :3] = self.camera_matrix[
                :3, :3
            ]  # see kitti documentation; this is cam matrix
            camera_matrix_inv = np.linalg.inv(camera_matrix_4d)
            p_bev_homo = np.einsum(
                "ij, ...j -> ...i", camera_matrix_inv, bev_pix_aug_4d
            )
            p_bev = cvision.homo_to_cart(p_bev_homo)
            p_bevs.append(p_bev)

        # Forget about +z coord which is height off ground; care only about angle of x/y coords
        p_bev_left, p_bev_right = p_bevs
        v_left_lane = (
            p_bev_left[1, :] - p_bev_left[0, :]
        )  # left lane vector from point (x1, y1, z1) to (x2, y2, z2)
        v_right_lane = p_bev_right[1, :] - p_bev_right[0, :]

        left_lane_angle = np.arctan2(v_left_lane[1], v_left_lane[0])
        right_lane_angle = np.arctan2(v_right_lane[1], v_right_lane[0])

        out = {"left_lane_angle": left_lane_angle, "right_lane_angle": right_lane_angle}

        if fig_num is not None:
            # Plot lines onto original image
            is_left_found = left_points is not None
            is_right_found = right_points is not None

            image_infos = [
                {"image": image, "title": "Original", "kwargs": {}},
                {
                    "image": image_value,
                    "title": "HSV - Value",
                    "kwargs": {"cmap": "gray"},
                },
                {
                    "image": image_blur,
                    "title": "Value - Gaussian Blur",
                    "kwargs": {"cmap": "gray"},
                },
                {
                    "image": image_edges,
                    "title": "Canny Edges",
                    "kwargs": {"cmap": "gray"},
                },
                {"image": roi_mask, "title": "ROI Mask", "kwargs": {"cmap": "gray"}},
                {
                    "image": threshold_mask,
                    "title": "Original",
                    "kwargs": {"cmap": "gray"},
                },
                {
                    "image": image_edges_with_mask,
                    "title": "Edges w/ ROI & Threshold Mask",
                    "kwargs": {"cmap": "gray"},
                },
                {
                    "image": image,
                    "title": f"Image w/ Lane Lines\nLeft/Right found? {is_left_found}/{is_right_found}",
                    "kwargs": {},
                },
            ]
            plt.figure(fig_num, clear=True, figsize=(12, 8))
            for ii, image_info in enumerate(image_infos):
                plt.subplot(3, 3, ii + 1)
                plt.imshow(image_info["image"], aspect="auto", **image_info["kwargs"])
                plt.title(image_info["title"])

            # Assuming last plot was final image, plot lines on top
            if left_points is not None:
                plt.plot(left_points[:, 0], left_points[:, 1], "r")

            if right_points is not None:
                plt.plot(right_points[:, 0], right_points[:, 1], "r")

            plt.xlim([0, n_col - 1])
            plt.ylim([n_row - 1, 0])

            # Plot real-world left/right lane line points
            plt.subplot(3, 3, 9)
            labels = [
                f"left - {left_lane_angle:.2f} deg",
                f"right - {right_lane_angle:.2f} deg",
            ]
            styles = ["r-x", "b-x"]
            for ii, p_bev in enumerate(p_bevs):  # go through right and left side
                plt.plot(p_bev[:, 0], p_bev[:, 1], styles[ii], label=labels[ii])

            plt.title("Bird's Eye Frame (Cartesian; not image)")
            plt.grid()
            plt.legend()

            plt.tight_layout()

        return out


# %% FUNCTIONS
def check_lane_side(slope: float, intercept: float, n_row: int, n_col: int):
    """Check whether lane line is a left lane line or right lane line

    Args:
        slope: Line slope
        intercept: Line intercept
        n_row: Number of image rows
        n_col: Number of image columns

    Returns:
        line_type: 'left' or 'right'
    """
    # Find x for where y = (bottom image) = slope * x + intercept
    x_bottom = (n_row - intercept) / slope
    line_side = "left" if x_bottom < (n_col / 2) else "right"
    return line_side
