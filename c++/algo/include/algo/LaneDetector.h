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
            LaneDetector(const Eigen::MatrixXf cameraMatrix,
                         const Eigen::MatrixXf cameraToRoadTransform)
            {
                this->cameraMatrix = cameraMatrix;
                this->cameraToRoadTransform = cameraToRoadTransform;
            }

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
};
#endif // ALGO_INCLUDE_ALGO_LANEDETECTOR_H
