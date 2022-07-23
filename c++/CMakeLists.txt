# Specify CMAKE version 
cmake_minimum_required(VERSION 3.16.3)

# Give the project a name. CMake will automativally store this name as the variable PROJECT_NAME
project(autonomous)

# Ensure dependencies exist
find_package( OpenCV REQUIRED )

# Add subfolder(s) to build folder
# add_subdirectory(src/apps)

# Note that $PROJECT_SOURCE_DIR refers to the ./c++ folder
# Includes folders
include_directories( ${OpenCV_INCLUDE_DIRS} )
include_directories(${PROJECT_SOURCE_DIR}/external/eigen-3.4.0)
include_directories(${PROJECT_SOURCE_DIR}/include)

# Link Headers to their Implementations
add_library(helper ${PROJECT_SOURCE_DIR}/include/helper.h ${PROJECT_SOURCE_DIR}/src/modules/helper.cpp)

# Applications
add_executable(helloworld ${PROJECT_SOURCE_DIR}/src/apps/helloworld.cpp)

# Link Applications to their Required Libraries
target_link_libraries(helloworld helper ${OpenCV_LIBS})

