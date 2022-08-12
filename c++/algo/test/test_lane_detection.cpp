// Standard Imports
#include <iostream>
#include <fstream>
#include <filesystem>
#include <assert.h>

// Third-Party Imports
#include "opencv2/opencv.hpp"
#include <Eigen/Dense>
#include "Eigen/Core"

// Local Imports
// #include <common/include/helper.h>
#include "algo/LaneDetector.h"
#include "common/kitti.h"

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

    assert(std::filesystem::exists(inputImagePath));
    assert(std::filesystem::exists(inputCalibPath));

    // Sample code to ensure Eigen works
    cv::Mat img = cv::imread(inputImagePath);

    // Parse calibration file:
    const kitti::KittiCalibInfo calibInfo = kitti::readCalibInfo(inputCalibPath);
    Eigen::MatrixXf cameraMatrix = calibInfo.projMat2.block<3, 3>(0, 0);
    std::cout << "camera matrix: " << cameraMatrix << std::endl;

    // Instantiate algo
    algo::LaneDetector LaneDetectorAlgo = algo::LaneDetector(
        cameraMatrix,
        calibInfo.cameraToRoadTransform
    );
    // LaneDetectorAlgo.printHello();
}
