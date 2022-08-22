// Standard Includes
#include <iostream>
#include <vector>
#include <math.h>

// Third-Party Includes
#include "spdlog/spdlog.h"
#include "spdlog/fmt/ostr.h"

// Local Includes
#include "algo/LaneDetector.h"

algo::LaneDetector::LaneDetector(
    const Eigen::MatrixXf cameraMatrix,
    const Eigen::MatrixXf cameraToRoadTransform)
{
    this->cameraMatrix = cameraMatrix;
    this->cameraToRoadTransform = cameraToRoadTransform;
}

const algo::LaneDetectorOutput algo::LaneDetector::run(
    cv::Mat image,
    std::shared_ptr<spdlog::logger> logger,
    const bool isDebugPlot = false
) const
{
    logger->info("Beggining lane line detection");
    if (isDebugPlot) cv::imshow("Original", image);

    algo::LaneDetectorOutput output;

    // Convert to HSV and get value channel
    cv::Mat singleChannel;
    cv::cvtColor(image, singleChannel, cv::COLOR_BGR2HSV);
    cv::extractChannel(singleChannel, singleChannel, 2);
    if (isDebugPlot) cv::imshow("HSV - Value", singleChannel);

    cv::GaussianBlur(
        singleChannel,
        singleChannel,
        cv::Size(5, 5),  // size of kernel (x, y)
        0.0  // Sigma X for Gaussian kernel
    );
    if (isDebugPlot) cv::imshow("Gaussian Blur", singleChannel);

    cv::Canny(
        singleChannel,
        singleChannel,
        130, // lowThreshold
        200, // highThreshold
        3);  // apertureSize
    if (isDebugPlot) cv::imshow("Canny Edges", singleChannel);

    // Create polygon for region of interest
    cv::Mat roiMask(singleChannel.size(), CV_8U, cv::Scalar(0)); 
    std::vector<cv::Point> polygonVertices;
    polygonVertices.push_back(cv::Point(398, 375));
    polygonVertices.push_back(cv::Point(493, 181));
    polygonVertices.push_back(cv::Point(1231, 357));
    std::vector<std::vector<cv::Point>> fillContAll;
    fillContAll.push_back(polygonVertices);
    cv::fillPoly(roiMask, fillContAll, cv::Scalar(255));
    if (isDebugPlot) cv::imshow("ROI Mask", roiMask);

    // Apply ROI mask
    cv::Mat edgesInRoi;
    singleChannel.copyTo(edgesInRoi, roiMask);
    if (isDebugPlot) cv::imshow("Edges w/ ROI", edgesInRoi);

    // # Detect lines in mask
    std::vector<cv::Vec4i> outputLines;
    cv::HoughLinesP(
        edgesInRoi,
        outputLines,
        2.0,  // rho: distance resolution for hough search
        2.0 * (M_PI / 180.0),  // theta: angle resolution for hough search
        10,  // accumulator threshold; min # of points along line
        20.0,  // minimum length of line in pixels
        10.0);  // largest allowable pixel gap between consecutive points on line

    logger->debug("HoughLinesP found {} lines", outputLines.size());
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
            edgesInRoi.rows,  // number rows in image
            edgesInRoi.cols  // # columns in image
        );
        if ((side == algo::LaneSide::LEFT) && !output.isLeftFound) {
            output.isLeftFound = true;
            leftStartPoint << x1, y1;
            leftEndPoint << x2, y2;
        }
        else if ((side == algo::LaneSide::RIGHT) && !output.isRightFound) {
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

    logger->debug("Left lane line found? {}", output.isLeftFound);
    logger->debug("Right lane line found? {}", output.isRightFound);

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
    logger->debug("Left Start: {}", leftStartPoint);
    logger->debug("Left End: {}", leftEndPoint);
    logger->debug("Right Start: {}", rightStartPoint);
    logger->debug("Right End: {}", rightEndPoint);

    // Rotate to equivalent bird's eye frame (still centered at camera)
    Eigen::VectorXf augmented4d(4);  // augment 2d vecs to 4d; last element is inverse depth

    // Construct 4D identity, insert camera matrix block, then invert
    Eigen::MatrixXf cameraMatrix4dInv(4, 4);
    cameraMatrix4dInv.block(0, 0, 4, 4) = Eigen::MatrixXf::Identity(4, 4);  // default identity
    cameraMatrix4dInv.block(0, 0, 3, 3) = this->cameraMatrix;
    logger->debug("4D Camera Matrix:\n{}", cameraMatrix4dInv);
    cameraMatrix4dInv = cameraMatrix4dInv.inverse();
    logger->debug("4D Camera Matrix - Inverted:\n{}", cameraMatrix4dInv);

    // Should be four points to loop through
    std::vector<Eigen::VectorXf> pBevs;
    logger->info("Recovering points in 3D...");
    for (auto & imagePoint : imagePoints) {
        // Rotate to bird's eye frame; annoyingly forced to provide a vector of points
        std::vector<cv::Point2f> imagePointVec{cv::Point2f(imagePoint(0), imagePoint(1))};
        std::vector<cv::Point2f> bevPixels;
        cv::perspectiveTransform(imagePointVec, bevPixels, camToBev);

        // Augment point and recover by assuming depth
        augmented4d << bevPixels.at(0).x, bevPixels.at(0).y, 1.0, (1.0 / cameraHeight);
        Eigen::VectorXf pBevHomo(4);
        pBevHomo << cameraMatrix4dInv * augmented4d;
        Eigen::VectorXf pBev(3);
        pBev << pBevHomo.block(0, 0, 3, 1) / pBevHomo(3);  // normalize by last elm
        pBevs.push_back(pBev);

        logger->debug("augmented4d: {}", augmented4d);
        logger->debug("pBevHomo: {}", pBevHomo);
        logger->debug("pBev: {}", pBev);
    }

    // Form vector(s) starting from left/right startPoint to left/right Endpoint; then find
    // angle of vector
    Eigen::VectorXf vLeft(3);
    vLeft << pBevs.at(1) - pBevs.at(0);

    Eigen::VectorXf vRight(3);
    vRight << pBevs.at(3) - pBevs.at(2);

    logger->debug("vLeft: {}", vLeft);
    logger->debug("vRight: {}", vRight);

    // Only consider x/y in angle computation. Z should be constant value since it's recovered
    // directly from the depth value
    output.leftLaneAngle = atan2(vLeft(1), vLeft(0));
    output.rightLaneAngle = atan2(vRight(1), vRight(0));

    if (output.leftLaneAngle < 0.0) output.leftLaneAngle += M_PI;
    if (output.rightLaneAngle < 0.0) output.rightLaneAngle += M_PI;

    logger->debug("Left angle: {} radians", output.leftLaneAngle);
    logger->debug("Right angle: {} radians", output.rightLaneAngle);

    if (isDebugPlot){
        cv::Mat tempImage = image.clone(); 
        if (output.isLeftFound){
            cv::line(
                tempImage,
                cv::Point(leftStartPoint(0), leftStartPoint(1)),
                cv::Point(leftEndPoint(0), leftEndPoint(1)),
                cv::Scalar(255, 0, 0),
                10  // line thickness
            );
        }
        if (output.isRightFound){
            cv::line(
                tempImage,
                cv::Point(rightStartPoint(0), rightStartPoint(1)),
                cv::Point(rightEndPoint(0), rightEndPoint(1)),
                cv::Scalar(255, 0, 0),
                10
            );
        }
        std::ostringstream out;
        out << "Image w/ Lane Lines\nLeft/Right found? " << output.isLeftFound 
            << "/" << output.isRightFound;
        cv::imshow(out.str(), tempImage);
    }

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
