# Specify CMAKE version 
cmake_minimum_required(VERSION 3.16.3)

# Give the project a name. CMake will automativally store this name as the variable PROJECT_NAME
project(autonomous)

# Note that $PROJECT_SOURCE_DIR refers to the ./c++ folder

# Includes
include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR}/external/eigen-3.4.0)

# Link Headers to their Implementations
add_library(helper ${PROJECT_SOURCE_DIR}/include/helper.h ${PROJECT_SOURCE_DIR}/src/helper.cpp)

# Applications
add_executable(helloworld ${PROJECT_SOURCE_DIR}/src/app/helloworld.cpp)

# Link Applications to their Required Libraries
target_link_libraries(helloworld helper)
