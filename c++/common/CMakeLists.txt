# === BUILD COMMON LIBRARY ===
# 1) Gather all cpp files
# 2) Gather all .h files
# 3) Add everything to the library
# 4) Add include directory to library
file(GLOB_RECURSE SRC_FILES src/*.cpp)  # find all .cpp files
file(GLOB_RECURSE HDR_FILES include/*.h)  # find all .h files
add_library(common STATIC ${SRC_FILES} ${HDR_FILES})
target_include_directories(common PUBLIC include)

# Executable Tests
add_executable(test_helper test/test_helper.cpp)
target_link_libraries(test_helper common)
