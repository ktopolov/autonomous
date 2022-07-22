# autonomous
Autonomous driving algorithm development and simulation with ROS

# Getting Started
Install dependencies on WSL using:
```bash
sudo apt update && sudo apt install -y cmake g++ wget unzip python3
```

# Building and Compiling C++ Code
If this is your first time in the repom or any files have been moved/added, navigate to the top level of the repo and run:
```bash
cmake -S CMakeLists.txt -B build
```
CMake will then generate make files for your project and properly structure your **build** folder. Then, to compile, run:
```bash
make -C build
```
Make will change folders into the **build** folder and then compile.
