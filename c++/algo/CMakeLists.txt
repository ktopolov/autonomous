# Executable Tests
file(GLOB_RECURSE SRC_FILES src/*.cpp)  # find all .cpp files
file(GLOB_RECURSE HDR_FILES include/*.h)  # find all .h files

add_executable(test_lane_detection test/test_lane_detection.cpp)
target_include_directories(test_lane_detection PUBLIC include)
target_link_libraries(test_lane_detection PUBLIC common ${OpenCV_LIBS})
