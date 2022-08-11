// Standard Imports
#include <iostream>
#include <fstream>
#include <filesystem>

// Third-Party Imports
#include "opencv2/opencv.hpp"
#include <Eigen/Dense>

// Local Imports
// #include <common/include/helper.h>
#include "common/kitti.h"
#include<iostream>

int main()
{
    if (__cplusplus == 201703L) std::cout << "C++17\n";
    else if (__cplusplus == 201402L) std::cout << "C++14\n";
    else if (__cplusplus == 201103L) std::cout << "C++11\n";
    else if (__cplusplus == 199711L) std::cout << "C++98\n";
    else std::cout << "pre-standard C++\n";

    std::filesystem::path repoPath = std::filesystem::path(std::getenv("AUTONOMOUS_PATH"));
    std::filesystem::path inputImagePath = repoPath / "data/kitti_data_road/testing/image_2/um_000000.png";
    std::filesystem::path inputCalibPath = repoPath / "data/kitti_data_road/testing/calib/um_000000.txt";

    // Sample code to ensure Eigen works
    cv::Mat img = cv::imread(inputImagePath);
    std::cout << "Image size: " << img.size() << std::endl;

    // Parse calibration file:
    std::cout << "Reading file..." << std::endl;
    const kitti::KittiCalibInfo calibInfo = kitti::readCalibInfo(inputCalibPath);
    std::cout << "Here is P0: \n" << calibInfo.P0 << std::endl;
}
