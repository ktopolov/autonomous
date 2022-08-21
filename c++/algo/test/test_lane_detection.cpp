// Standard Imports
#include <iostream>
#include <fstream>
#include <filesystem>
#include <assert.h>

// Third-Party Imports
#include "opencv2/opencv.hpp"
#include "spdlog/spdlog.h"
#include "spdlog/fmt/ostr.h"
#include "Eigen/Dense"
#include "Eigen/Core"

// Local Imports
// #include <common/include/helper.h>
#include "algo/LaneDetector.h"
#include "common/kitti.h"

int main()
{
    // Console logger with color
    std::shared_ptr<spdlog::logger> logger = spdlog::stdout_color_st("MyLogger");
    logger->set_level(spdlog::level::debug);
    logger->set_pattern("%n: [%H:%M:%S] (%l) [thread %t] %v");  // info, error, warn, critical are functions

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

    // Instantiate algo
    algo::LaneDetector LaneDetectorAlgo = algo::LaneDetector(
        cameraMatrix,
        calibInfo.cameraToRoadTransform
    );
    const algo::LaneDetectorOutput output = LaneDetectorAlgo.run(
        img,
        logger,
        true  // show debug plots
    );
}
