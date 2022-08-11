#ifndef KITTICALIBINFO_H
#define KITTICALIBINFO_H

// Standard Imports
#include <filesystem>

// Third-Party Imports
#include <Eigen/Dense>

namespace kitti
{
    struct KittiCalibInfo
    {
        Eigen::MatrixXf P0;
        Eigen::MatrixXf P1;
        Eigen::MatrixXf P2;
        Eigen::MatrixXf P3;
        Eigen::MatrixXf R0_rect;
        Eigen::MatrixXf Tr_velo_to_cam;
        Eigen::MatrixXf Tr_imu_to_velo;
        Eigen::MatrixXf Tr_cam_to_road;
    };

    KittiCalibInfo readCalibInfo(std::filesystem::path path);
}

#endif // KITTICALIBINFO_H
