# autonomous
Autonomous driving algorithm development and simulation with ROS

# Getting Started
There are two options for development:
* Develop on local machine with Ubuntu 20; must install all dependencies
  *  WSL is an option
* Develop using Docker container (see README file in **docker/** folder)

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
# Build without debug flags
source shellscripts/cpp_build.sh

# Build with GDB debug flags
source shellscripts/cpp_build -d
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

# Working with ROS
To install ROS, you can either look at the lines in the Dockerfile in this repo which pertain to ROS installation, or visit http://wiki.ros.org/noetic/Installation/Ubuntu and follow the instructions there. We use ROS noetic for this project.

ROS tutorials are located at http://wiki.ros.org/ROS/Tutorials
