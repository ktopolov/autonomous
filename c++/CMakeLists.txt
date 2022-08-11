# Specify CMAKE version 
cmake_minimum_required(VERSION 3.16.3)
set(CMAKE_CXX_STANDARD 17)

# Give the project a name. CMake will automativally store this name as the variable PROJECT_NAME
project(autonomous)

# Ensure dependencies exist
find_package(OpenCV REQUIRED)

# Include external directories
include_directories( ${OpenCV_INCLUDE_DIRS} )
include_directories(external/eigen-3.4.0)

# Add all internal subdirectories for cmake to go through
add_subdirectory(common)
add_subdirectory(algo)
