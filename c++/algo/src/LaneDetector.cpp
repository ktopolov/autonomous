// Standard Includes
#include <iostream>
#include <vector>
#include <math.h>

// Local Includes
#include "algo/LaneDetector.h"

algo::LaneDetector::LaneDetector(
    const Eigen::MatrixXf cameraMatrix,
    const Eigen::MatrixXf cameraToRoadTransform)
{
    this->cameraMatrix = cameraMatrix;
    this->cameraToRoadTransform = cameraToRoadTransform;
}

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
    cv::Mat roiMask;
    std::vector<cv::Point> polygonVertices;
    polygonVertices.push_back(cv::Point(398, 375));
    polygonVertices.push_back(cv::Point(493, 181));
    polygonVertices.push_back(cv::Point(1231, 357));
    std::vector<std::vector<cv::Point>> fillContAll;
    fillContAll.push_back(polygonVertices);
    cv::fillPoly(roiMask, fillContAll, cv::Scalar(255));

    // Apply ROI mask
    singleChannel.copyTo(singleChannel, roiMask);

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

    std::cout << "Lines found: " << std::endl;
    Eigen::Vector2f leftStartPoint, leftEndPoint, rightStartPoint, rightEndPoint;
    size_t x1, y1, x2, y2;
    double slope, intercept;
    
    output.isLeftFound = false;
    output.isRightFound = false;

    for(auto line : outputLines)
    {
        x1 = line.val[0];
        y1 = line.val[1];
        x2 = line.val[2];
        y2 = line.val[3];

        slope = (y2 - y1) / (x2 - x1);
        intercept = y2 - (x2 * slope);
        const algo::LaneSide side = algo::checkLaneSide(
            slope,
            intercept,
            singleChannel.rows,  // number rows in image
            singleChannel.cols  // # columns in image
        );
        if (side == algo::LaneSide::LEFT){
            output.isLeftFound = true;
            leftStartPoint << x1, y1;
            leftEndPoint << x2, y2;
        }
        else if(side == algo::LaneSide::RIGHT){
            output.isRightFound = true;
            rightStartPoint << x1, y1;
            rightEndPoint << x2, y2;
        }

        // No need to keep looping once both lanes found
        if (output.isRightFound && output.isLeftFound)
        {
            break;
        }
    }

    Eigen::Matrix3f camToRoad = this->cameraToRoadTransform.block(0, 0, 3, 3);
    Eigen::Vector3f tvecCamToRoad = this->cameraToRoadTransform.block(0, 3, 3, 1);

    // Origin of the road camera frame represented in camera coordinates
    Eigen::Vector3f pRoadOriginCam = camToRoad.colPivHouseholderQr().solve(tvecCamToRoad);
    const double cameraHeight = pRoadOriginCam(1);

    // # Define bird's eye frame. Note: This is similar to the "Road" coordinate frame, but chosen such
    // # that the +z axis points directly downward instead of +y
    cv::Mat camToBev = (cv::Mat_<double>(3, 3) << 
        camToRoad(2, 0), camToRoad(2, 1), camToRoad(2, 2),
        camToRoad(0, 0), camToRoad(0, 1), camToRoad(0, 2),
        camToRoad(1, 0), camToRoad(1, 1), camToRoad(1, 2));

    // Recover all points; store in vector to avoid redundant code:
    std::vector<Eigen::Vector2f> imagePoints {
        leftStartPoint,
        leftEndPoint,
        rightStartPoint,
        rightEndPoint
    };

    // # Rotate to equivalent bird's eye frame (still centered at camera)
    std::cout << "camToBev: " << camToBev << std::endl;
    Eigen::VectorXf augmented4d(4);  // augment 2d vecs to 4d; last element is inverse depth

    // Construct 4D identity, insert camera matrix block, then invert
    Eigen::MatrixXf cameraMatrix4dInv(4, 4);
    cameraMatrix4dInv.block(0, 0, 4, 4) = Eigen::MatrixXf::Identity(4, 4);  // default identity
    cameraMatrix4dInv.block(0, 0, 3, 3) = this->cameraMatrix;
    std::cout << "cameraMatrix4dInv - pre-inversion:\n" << cameraMatrix4dInv << std::endl;
    cameraMatrix4dInv = cameraMatrix4dInv.inverse();
    std::cout << "cameraMatrix4dInv - post-inversion:\n" << cameraMatrix4dInv << std::endl;

    // Should be four points to loop through
    std::vector<Eigen::VectorXf> pBevs;
    for (auto & imagePoint : imagePoints) {
        augmented4d << imagePoint(0), imagePoint(1), 1.0, (1.0 / cameraHeight);
        std::cout << "augmented4d:\n" << augmented4d << std::endl;

        Eigen::VectorXf pBevHomo(4);
        pBevHomo << cameraMatrix4dInv * augmented4d;
        std::cout << "pBevHomo:\n" << pBevHomo << std::endl;
        Eigen::VectorXf pBev(3);
        pBev << pBevHomo.block(0, 0, 3, 1) / pBevHomo(3);  // normalize by last elm
        std::cout << "pBev: " << pBev << std::endl;
        pBevs.push_back(pBev);
    }

    // Form vector(s) starting from left/right startPoint to left/right Endpoint; then find
    // angle of vector
    Eigen::VectorXf vLeft(3);
    vLeft << pBevs.at(1) - pBevs.at(0);

    Eigen::VectorXf vRight(3);
    vRight << pBevs.at(3) - pBevs.at(2);

    // Only consider x/y in angle computation. Z should be constant value since it's recovered
    // directly from the depth value
    output.leftLaneAngle = atan2(vLeft(1), vLeft(0));
    output.rightLaneAngle = atan2(vRight(1), vRight(0));

    std::cout << "Left angle: " << output.leftLaneAngle << std::endl;
    std::cout << "Right angle: " << output.rightLaneAngle << std::endl;

    return output;
}

const algo::LaneSide algo::checkLaneSide(
    const double slope,
    const double intercept,
    const size_t nRow,
    const size_t nCol
)
{
    // Check x-coordinate (column) where line intersects at bottom of image
    LaneSide side;
    if (((nRow - intercept) / slope) < ((nCol - 1) / 2))
    {
        side = LaneSide::LEFT;
    }
    else
    {
        side = LaneSide::RIGHT;
    }
    return side;
}
