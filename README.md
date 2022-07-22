# autonomous
Autonomous driving algorithm development and simulation with ROS

# Getting Started
Install dependencies on WSL using:
```bash
sudo apt update && sudo apt install -y cmake g++ wget unzip python3 git libeigen3-dev
```

# Cloning the Repo
To clone the repo, use Git with SSH:
```bash
git -C <path-to-repo> clone git@github.com:ktopolov/autonomous.git
```
or simply just
```bash
git clone git@github.com:ktopolov/autonomous.git
```
to clone into the current folder.

# Building and Compiling C++ Code
If this is your first time in the repom or any files have been moved/added, navigate to the top level of the repo and run:
```bash
cmake -S <path-to-repo>/c++ -B <path-to-repo>/c++/build
```
CMake will see the CMakeLists.cpp in the **c++** folder and then generate make files for your project and properly structure your **c++/build** folder. Then, to compile, run:
```bash
make -C <path-to-repo>/c++/build
```
Make will change folders into the **c++/build** folder and then compile.
