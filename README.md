# autonomous
Autonomous driving algorithm development and simulation with ROS

# Getting Started
Install dependencies on WSL using:
```bash
sudo apt update
sudo apt install -y cmake g++ wget unzip python3 python3-pip git libopencv-dev
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

# Setting up Python Virtual Environment
Now, we setup a Python virtual environment:
```bash
# get virtualenv package
sudo apt install python3-venv

# Create virtual env
python3 -m venv ~/venvs/auto_venv

# Activate virtual env
source ~/venvs/auto_venv/bin/activate

# Install packages for this repo
pip install -r <path-to-repo>/python/requirements.txt
```

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

# My Aliases
Some helpful aliases I set:
```bash
export AUTONOMOUS_PATH='~/repos/autonomous'
alias go-auto="cd ${AUTONOMOUS_PATH}"

# activate Python virtual environment, set python path
alias auto-setup="source ~/venvs/auto_venv/bin/activate; export PYTHONPATH=${AUTONOMOUS_PATH}/python"

# Use cmake to configure build directory
alias auto-cfg="cmake -S ${AUTONOMOUS_PATH}/c++ -B ${AUTONOMOUS_PATH}/c++/build"

# build c++ project
alias auto-bld="cmake --build ${AUTONOMOUS_PATH}/c++/build"
```

