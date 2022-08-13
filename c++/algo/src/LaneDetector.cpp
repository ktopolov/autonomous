// Standard Includes
#include <iostream>
#include <vector>
#include <math.h>

// Local Includes
#include "algo/LaneDetector.h"

const algo::LaneDetectorOutput algo::LaneDetector::run(cv::Mat image) const
{
    algo::LaneDetectorOutput output;

    // Get value channel
    cv::Mat singleChannel;
    cv::extractChannel(image, singleChannel, 2);
    cv::GaussianBlur(
        singleChannel,
        singleChannel,
        cv::Size(5, 5),  // size of kernel (x, y)
        1.0,  // Sigma X for Gaussian kernel
        1.0,  // Sigma Y for Gaussian kernel
        cv::BORDER_CONSTANT);
    cv::Canny(
        singleChannel,
        singleChannel,
        130, // lowThreshold
        200, // highThreshold
        3);  // apertureSize

    // Create polygon for region of interest
    cv::Mat roi;
    std::vector<cv::Point> polygonVertices;
    polygonVertices.push_back(cv::Point(398, 375));
    polygonVertices.push_back(cv::Point(493, 181));
    polygonVertices.push_back(cv::Point(1231, 357));
    std::vector<std::vector<cv::Point>> fillContAll;
    fillContAll.push_back(polygonVertices);
    cv::fillPoly(roi, fillContAll, cv::Scalar(255));

    // Intersect edges with white threshold mask
    singleChannel = singleChannel * roi;

    // # Detect lines in mask
    std::vector<cv::Vec4i> outputLines;
    cv::HoughLinesP(
        singleChannel,
        outputLines,
        2.0,  // rho: distance resolution for hough search
        2.0 * (M_PI / 180.0),  // theta: angle resolution for hough search
        10,  // accumulator threshold; min # of points along line
        20.0,  // minimum length of line in pixels
        10.0);  // largest allowable pixel gap between consecutive points on line

    // # Store points belonging to each line as (n_point, xy) = (2, 2) matrix:
    // # left_points[0, :] = (x1, y1)
    // # left_points[1, :] = (x2, y2)
    // left_points = None
    // right_points = None
    // n_line = lines.shape[0]
    // n_row, n_col, _ = image.shape
    // for i_line in range(n_line):
    //     # Lines ordered by confidence level
    //     x1, y1, x2, y2 = lines[i_line, 0, :]
    //     slope = (y2 - y1) / (x2 - x1)
    //     intercept = y2 - slope * x2
    //     line_side = check_lane_side(
    //         slope=slope, intercept=intercept, n_row=n_row, n_col=n_col
    //     )

    //     # If this line is on left and left lane not yet found...
    //     if (line_side == "left") and (left_points is None):
    //         left_points = np.stack((np.array([x1, y1]), np.array([x2, y2])), axis=0)

    //     # If this line is on right and right lane not yet found...
    //     elif (line_side == "right") and (right_points is None):
    //         right_points = np.stack(
    //             (np.array([x1, y1]), np.array([x2, y2])), axis=0
    //         )

    //     # If both left/right lanes are found, stop looking
    //     if (left_points is not None) and (right_points is not None):
    //         break

    // # === Project to real world ===
    // # Left line: sample two points on line, rotate into road coordiante frame (centered at camera)
    // # where x/y in road and +z out of road. Drop z coordinate and fit road-frame line
    // cam_to_road = self.tr_cam_to_road[:3, :3]  # (3, 3) rotation matrix
    // tvec_cam_to_road = self.tr_cam_to_road[
    //     :3, 3
    // ]  # (3,) translation vector = -cam_to_road * p_road_in_cam_frame

    // # Compute camera height off ground.
    // # See http://www.cvlibs.net/datasets/kitti/setup.php for coordinate frames:
    // # Camera frame: +z: forward, +x: right, +y: down (toward ground)
    // p_roadorigin_cam = -np.linalg.solve(
    //     cam_to_road, tvec_cam_to_road
    // )  # road coord frame origin in camera frame
    // camera_height = p_roadorigin_cam[1]  # y-value

    // # Define bird's eye frame. Note: This is similar to the "Road" coordinate frame, but chosen such
    // # that the +z axis points directly downward instead of +y
    // ux_road_cam = cam_to_road[
    //     0, :
    // ]  # get the road frame basis vectors in the camera frame
    // uy_road_cam = cam_to_road[1, :]
    // uz_road_cam = cam_to_road[2, :]
    // cam_to_bev = np.stack((uz_road_cam, ux_road_cam, uy_road_cam), axis=0)

    // # Rotate to equivalent bird's eye frame (still centered at camera)
    // p_bevs = []  # list for each left/right lane, each have 2 points with xyz coords
    // for ii, cam_pix in enumerate([left_points, right_points]):
    //     bev_pix = cvision.apply_perspective_transform(
    //         v=cam_pix, transform=cam_to_bev
    //     )

    //     # Augment pixel to 4D so we can recover point with inverse depth
    //     depth = camera_height
    //     bev_pix_aug = cvision.augment(bev_pix)
    //     bev_pix_aug_4d = cvision.augment(bev_pix_aug)
    //     bev_pix_aug_4d[..., -1] /= depth

    //     # Invert perspective transform
    //     camera_matrix_4d = np.eye(4)
    //     camera_matrix_4d[:3, :3] = self.camera_matrix[
    //         :3, :3
    //     ]  # see kitti documentation; this is cam matrix
    //     camera_matrix_inv = np.linalg.inv(camera_matrix_4d)
    //     p_bev_homo = np.einsum(
    //         "ij, ...j -> ...i", camera_matrix_inv, bev_pix_aug_4d
    //     )
    //     p_bev = cvision.homo_to_cart(p_bev_homo)
    //     p_bevs.append(p_bev)

    // # Forget about +z coord which is height off ground; care only about angle of x/y coords
    // p_bev_left, p_bev_right = p_bevs
    // v_left_lane = (
    //     p_bev_left[1, :] - p_bev_left[0, :]
    // )  # left lane vector from point (x1, y1, z1) to (x2, y2, z2)
    // v_right_lane = p_bev_right[1, :] - p_bev_right[0, :]

    // left_lane_angle = np.arctan2(v_left_lane[1], v_left_lane[0])
    // right_lane_angle = np.arctan2(v_right_lane[1], v_right_lane[0])

    // out = {"left_lane_angle": left_lane_angle, "right_lane_angle": right_lane_angle}

    output.leftLaneAngle = 30.0;
    output.rightLaneAngle = 20.0;
    return output;
}