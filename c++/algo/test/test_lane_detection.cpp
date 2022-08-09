// Standard Imports
#include <iostream>
#include <fstream>

// Third-Party Imports
#include "opencv2/opencv.hpp"
#include <Eigen/Dense>

// Local Imports
// #include <common/include/helper.h>
#include "common/helper.h"

int main()
{
    std::string inputImagePath = "../../data/kitti_data_road/testing/image_2/um_000000.png";
    std::string inputCalibPath = "../../data/kitti_data_road/testing/calib/um_000000.txt";

    // Sample code to ensure Eigen works
    cv::Mat img = cv::imread(inputImagePath);
    std::cout << "Image size: " << img.size() << std::endl;

    // Parse calibration file:
    std::map<std::string, Eigen::MatrixXi> mapOfWords;
    std::ifstream calibFile(inputCalibPath);
    std::string str;
    std::cout << "Reading file..." << std::endl;
    int ii = 0;
    while (std::getline(calibFile, str))
    {
        std::cout << str << std::endl;

        Eigen::MatrixXi matrix(3, 4);
        matrix.setZero(3, 4);

        std::string key = "someKey" + std::to_string(ii);
        mapOfWords.insert(std::make_pair(key, matrix));
        ii++;
    }

    for (auto const& x : mapOfWords)
    {
        std::cout << x.first << ':' << x.second << std::endl;
    }

    // std::cout << "Result from Eigen: " << m << std::endl;

    // Sample code to ensure internal library works
    helper::printhello();
}
