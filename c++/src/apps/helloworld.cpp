// Standard Imports
#include <iostream>

// Third-Party Imports
#include "opencv2/opencv.hpp"
#include <Eigen/Dense>

// Local Imports
#include <helper.h>

int main()
{
    // Sample code to ensure Eigen works
    Eigen::MatrixXd m(2, 2);
    m(0, 0) = 3;
    m(1, 0) = 2.5;
    m(0, 1) = -1;
    m(1, 1) = m(1, 0) + m(0, 1);
    std::cout << "Result from Eigen: " << m << std::endl;

    // Sample code to ensure OpenCV works
    cv::Mat output = cv::Mat::zeros(120, 350, CV_8UC3);
    std::cout << "Result from OpenCV: " << output.size << std::endl;

    // Sample code to ensure internal library works
    helper::printhello();
}
