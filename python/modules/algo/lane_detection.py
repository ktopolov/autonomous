"""Support code for lane line detection"""
# Standard Imports

# Third Party Imports
import numpy as np
import cv2
import matplotlib.pyplot as plt

# Local Imports

# %% ENCAPSULATIONS
class LaneLineDetector:
    """ "Class to run lane detection algorithm"""

    def __init__(
        self,
        config: dict,
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
            road_to_cam_proj_mat: (3, 4) projection matrix from road to camera; composed of
                                  K * [R | t]
        """
        self.config = config

    def run(
        self,
        image: np.ndarray,
        road_to_cam_proj_mat: np.ndarray,
        fig_num=None,
    ) -> dict:
        """Run algorithm for lane line detection

        Args:
            image : (n_row, n_col, 3) BGR image

        Returns:
            out: Contains output parameters
                'left_lane_slope': Slope of left lane line w.r.t. road coordinates
                'left_lane_intercept': Intercept of left lane line w.r.t. road coordinates
                'right_lane_slope': Slope of right lane line w.r.t. road coordinates
                'right_lane_intercept': Intercept of right lane line w.r.t. road coordinates
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

        # Store indices of msot confident left and right linea
        i_left_line = None
        i_right_line = None

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

            if (line_side == "left") and (i_left_line is None):
                i_left_line = i_line
            elif (line_side == "right") and (i_right_line is None):
                i_right_line = i_line

            if (i_left_line is not None) and (i_right_line is not None):
                break

        if fig_num is not None:
            # Plot lines onto original image
            final_image = image.copy()
            for index in [i_left_line, i_right_line]:
                if index is not None:
                    x1, y1, x2, y2 = lines[i_left_line].flatten()
                    cv2.line(
                        img=final_image,
                        pt1=(x1, y1),
                        pt2=(x2, y2),
                        color=(240, 30, 20),
                        thickness=5,
                    )

            is_left_found = i_left_line is not None
            is_right_found = i_right_line is not None
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
                    "image": final_image,
                    "title": f"Image w/ Lane Lines\nLeft/Right found? {is_left_found}/{is_right_found}",
                    "kwargs": {},
                },
            ]
            plt.figure(fig_num, clear=True, figsize=(8, 8))
            for ii, image_info in enumerate(image_infos):
                plt.subplot(3, 3, ii + 1)
                plt.imshow(image_info["image"], aspect="auto", **image_info["kwargs"])
                plt.title(image_info["title"])

            plt.tight_layout()


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
