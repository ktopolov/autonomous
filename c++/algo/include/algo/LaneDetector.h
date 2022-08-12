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
                std::cout << "Hello World!";
            }

            /*! Run algorithm on an incoming image
                \param image (nRow, nCol, 3) RGB image.
                \return output Output lane angles.  
            */
            const LaneDetectorOutput run(const cv::Mat image) const
            {
                LaneDetectorOutput output;
                output.leftLaneAngle = 30.0;
                output.rightLaneAngle = 20.0;
                return output;
            }
            

        // Members
        int a;
        void printHello(){
            this->printHelloPrivate();
        }

        // Member functions
        private:
        int b;
        void printHelloPrivate();

    };
};
#endif // ALGO_INCLUDE_ALGO_LANEDETECTOR_H
