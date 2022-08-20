# Specify CMAKE version 
cmake_minimum_required(VERSION 3.16.3)
set(CMAKE_CXX_STANDARD 17)

# Needed for spdlog for some reason...
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

# Give the project a name. CMake will automativally store this name as the variable PROJECT_NAME
project(autonomous)

# Ensure dependencies exist
find_package(OpenCV REQUIRED)

# Include external directories
include_directories( ${OpenCV_INCLUDE_DIRS} )
include_directories(${PROJECT_SOURCE_DIR}/external/eigen-3.4.0)
include_directories(${PROJECT_SOURCE_DIR}/external/spdlog)

# Add all internal subdirectories for cmake to go through
add_subdirectory(common)
add_subdirectory(algo)
