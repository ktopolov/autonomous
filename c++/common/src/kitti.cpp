// Standard Imports
#include <filesystem>
#include <fstream>

// Third-Party Imports
#include <Eigen/Dense>

// Local Imports
#include "common/kitti.h"

kitti::KittiCalibInfo kitti::readCalibInfo(std::filesystem::path path)
{
    size_t col;
    std::string str;
    std::ifstream calibFile(path);
    kitti::KittiCalibInfo calibInfo;
    while (std::getline(calibFile, str))
    {
        col = 0;

        // Calibration files are 13-column files; first is key, last 12 are entries of the
        // 3x4 projection/transformation matrices
        size_t globalStartLoc = 0;
        size_t delimeterPos;
        size_t iRow = 0;
        size_t iCol = 0;
        std::string key, substring;
        const size_t nMatrixRow = 3;
        const size_t nMatrixCol = 4;
        Eigen::MatrixXf matrix(nMatrixRow, nMatrixCol);
        for (size_t col = 0; col < 13; col++)
        {
            // Parse left to right; once part of string is extracted from left, remove it and search
            // remaining string
            substring = str.substr(globalStartLoc, str.length());
            delimeterPos = substring.find(' ', col);

            if (col == 0){
                key = str.substr(0, delimeterPos);
            }
            else{
                iRow = (col - 1) / nMatrixCol; // should be integer division
                iCol = (col - 1) % nMatrixCol;
                matrix(iRow, iCol) = std::stof(substring.substr(0, delimeterPos));
            }
            if (key == "P0:"){ calibInfo.projMat0 = matrix; }
            else if (key == "P1:"){ calibInfo.projMat1 = matrix; }
            else if (key == "P2:"){ calibInfo.projMat2 = matrix; }
            else if (key == "P3:"){ calibInfo.projMat3 = matrix; }
            else if (key == "R0_rect:"){ calibInfo.r0Rect = matrix; }
            else if (key == "Tr_velo_to_cam:"){ calibInfo.velodyneToCamTransform = matrix; }
            else if (key == "Tr_imu_to_velo:"){ calibInfo.imuToVelodyneTransform = matrix; }
            else if (key == "Tr_cam_to_road:"){ calibInfo.cameraToRoadTransform = matrix; }
            else { throw; }

            globalStartLoc += delimeterPos;
        }
    }
    return calibInfo;
}
