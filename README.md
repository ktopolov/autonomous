# autonomous
Autonomous driving algorithm development and simulation with ROS

# Getting Started
Install dependencies on WSL using:
```bash
sudo apt update
sudo apt install -y cmake g++ wget unzip python3 python3-pip git libopencv-dev clang-tidy
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

# Interactive Plotting
Assuming you work on WSL2 and want to show plots on your Windows machine:
*  Download and Install Vcxsrv on Windows from https://sourceforge.net/projects/vcxsrv/
*  Open WSL2 and add the following lines into your `~/.bashrc` or whatever file runs on setup:
```bash
export DISPLAY=$(ip route list default | awk '{print $3}'):0
export LIBGL_ALWAYS_INDIRECT=1
```

In windows start menu, search for **XLaunch** and open it. Select "Multiple Windows". Hit next and select "Start no client". Hit next and check **all boxes**, including the **Disable access control**. If you don't do this, it won't work. Hit "Next" >> "Finish".

Now if you open a WSL window (or source your `~/.bashrc` file) and run something like **gedit** you should see a window appear.

Alternatively, you can simply load a VCXSRV configuration file in this repo (**vcxsrv_wsl2**) by:
*  Double click the **vcxsrv_wsl2** file in Windows machine
*  Open with **Xlaunch**
Now, an X-server should be open for you.

## Working with ROS
To install ROS, you can either look at the lines in the Dockerfile in this repo which pertain to ROS installation, or visit http://wiki.ros.org/noetic/Installation/Ubuntu and follow the instructions there. We use ROS noetic for this project.

ROS tutorials are located at http://wiki.ros.org/ROS/Tutorials

## Pushing/Pulling Docker Images from Dockerhub
We like docker images to be stored on Dockerhub such that we can share them across developers and so our CI/CD pipeline can pull from there rather than building the image from scratch. There is a shell script in this repo which can be run to do the following:
*  Build Docker image locally
*  Push Docker image to DockerHub

To run this script, simply run:
```bash
source <path-to-autonomous-repo>/docker/build_deploy_dev_docker.sh
```
If you are NOT logged into Docker already, it will prompt you for username and password for DockerHub. After entering, it will proceed to build and deploy the Docker image.
