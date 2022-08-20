/********************************************//**
Encapsulation and functions relating to lane line detection algorithm
************************************************/
#ifndef ALGO_INCLUDE_ALGO_LANEDETECTOR_H
#define ALGO_INCLUDE_ALGO_LANEDETECTOR_H

// Standard Imports

// Third-Party Imports
#include <Eigen/Dense>
#include "opencv2/opencv.hpp"

namespace algo
{
    struct LaneDetectorOutput
    {
        bool isLeftFound;  // whether left lane line found; Only use leftLaneAngle if this is true
        bool isRightFound;  //whether right lane line found; Only use rightLaneAngle if this is true
        float leftLaneAngle;  // Angle (degrees) of left lane line in road coordinate frame
        float rightLaneAngle;  // Angle (degrees) of right lane line in road coordinate frame
    };

    class LaneDetector {
        public:
            /*! Constructor function.  
                \param cameraMatrix (3, 3) camera matrix containing focal length(s), principal point
                    and skewness parameters
                \param cameraToRoadTransform (3, 4) Transformation matrix in form [R | t] from
                    camera to road coordinate frame
            */  
            LaneDetector(
                const Eigen::MatrixXf cameraMatrix,
                const Eigen::MatrixXf cameraToRoadTransform);

            /*! Run algorithm on an incoming image
                \param image (nRow, nCol, 3) RGB image.
                \return output Output lane angles.  
            */
            const LaneDetectorOutput run(cv::Mat image) const;

        // Member functions
        private:
            Eigen::MatrixXf cameraMatrix;  // (3, 3) camera projection matrix w/ focal lengths, principal point, etc.
            Eigen::MatrixXf cameraToRoadTransform;  // [R | t] (3, 4) extrinsic transformation from camera to road coords
    };

    // Enum describing possible lane line sides
    enum LaneSide{
        LEFT,
        RIGHT,
        UNKNOWN,
    };

    /*! Check which side of road lane line is on
        \param slope Line slope (y2 - y1) / (x2 - x1) in image
        \param intercept Line y-intercept in image
        \param nRow Number of rows in image (height) in pixels
        \param nCol Number of cols in image (width) in pixels
        \return side Side of road  
    */
    const LaneSide checkLaneSide(
        const double slope,
        const double intercept,
        const size_t nRow,
        const size_t nCol
    );

};
#endif // ALGO_INCLUDE_ALGO_LANEDETECTOR_H
