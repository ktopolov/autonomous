# === BUILD ALGO LIBRARY ===
# 1) Gather all cpp files
# 2) Gather all .h files
# 3) Add everything to the library
# 4) Add include directory to library
file(GLOB_RECURSE SRC_FILES src/*.cpp)  # find all .cpp files
file(GLOB_RECURSE HDR_FILES include/*.h)  # find all .h files
add_library(algo STATIC ${SRC_FILES} ${HDR_FILES})
target_include_directories(algo PUBLIC include)

# === EXECUTABLES ===
add_executable(test_lane_detection test/test_lane_detection.cpp)
target_include_directories(test_lane_detection PUBLIC include)
target_link_libraries(test_lane_detection PUBLIC algo common ${OpenCV_LIBS})
