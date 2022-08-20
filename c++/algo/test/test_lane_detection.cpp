// Standard Imports
#include <iostream>
#include <fstream>
#include <filesystem>
#include <assert.h>

// Third-Party Imports
#include "opencv2/opencv.hpp"
#include "spdlog/spdlog.h"
#include "Eigen/Dense"
#include "Eigen/Core"

// Local Imports
// #include <common/include/helper.h>
#include "algo/LaneDetector.h"
#include "common/kitti.h"

int main()
{
    // Console logger with color
    auto console = spdlog::stdout_color_st("console");
    console->set_pattern("%n: [%H:%M:%S %z] [thread %t] %v");
    console->info("Welcome to spdlog!");
    console->error("Some error message with arg{}..", 1);
    
    // Formatting examples
    console->warn("Easy padding in numbers like {:08d}", 12);
    console->critical("Support for int: {0:d};  hex: {0:x};  oct: {0:o}; bin: {0:b}", 42);
    console->info("Support for floats {:03.2f}", 1.23456);
    console->info("Positional args are {1} {0}..", "too", "supported");
    console->info("{:<30}", "left aligned");

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
    const algo::LaneDetectorOutput output = LaneDetectorAlgo.run(img);
    std::cout << "Left angle found? " << output.isLeftFound << std::endl;
    std::cout << "Left angle: " << output.leftLaneAngle << std::endl;
    std::cout << "Right angle found? " << output.isRightFound << std::endl;
    std::cout << "Right angle: " << output.rightLaneAngle << std::endl;
}
