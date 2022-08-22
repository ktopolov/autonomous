#ifndef COMMON_INCLUDE_COMMON_KITTI_H
#define COMMON_INCLUDE_COMMON_KITTI_H

// Standard Imports
#include <filesystem>

// Third-Party Imports
#include <Eigen/Dense>

namespace kitti
{
    struct KittiCalibInfo
    {
        Eigen::MatrixXf projMat0; // Cam 0 projection matrix; (3, 4); first (3, 3) is camera matrix
        Eigen::MatrixXf projMat1; // Cam 1 projection matrix; (3, 4); first (3, 3) is camera matrix
        Eigen::MatrixXf projMat2; // Cam 2 projection matrix; (3, 4); first (3, 3) is camera matrix
        Eigen::MatrixXf projMat3; // Cam 3 projection matrix; (3, 4); first (3, 3) is camera matrix
        Eigen::MatrixXf r0Rect; // ?
        Eigen::MatrixXf velodyneToCamTransform; // [R | t] transformation from velodyne LiDAR to camera coords
        Eigen::MatrixXf imuToVelodyneTransform; // [R | t] transformation from IMU to velodyne LiDAR coords
        Eigen::MatrixXf cameraToRoadTransform; // [R | t] transformation from camera to road coords
    };

    /*! Read KITTI calibration information from calibration file
        \param path Path to calibration file um_<######>.txt
        \return calibInfo Calibration matrices  
    */
    KittiCalibInfo readCalibInfo(std::filesystem::path path);
}

#endif // COMMON_INCLUDE_COMMON_KITTI_H
