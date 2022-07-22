# Specify CMAKE version 
cmake_minimum_required(VERSION 3.16.3)

# Give the project a name. CMake will automativally store this name as the variable PROJECT_NAME
project(autonomous)

add_executable(helloworld ${PROJECT_SOURCE_DIR}/src/app/helloworld.cpp)

