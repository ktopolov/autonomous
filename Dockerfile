# syntax=docker/dockerfile:1
FROM ubuntu:20.04

# Install other dependencies
RUN apt update

RUN echo "Installing CMAKE"
RUN apt install -y wget g++ git

# Avoid cmake install asking about geographic area
ARG DEBIAN_FRONTEND=noninteractive
RUN apt install -y cmake

RUN apt install -y python3 python3-pip python3-venv
RUN apt install -y libopencv-dev
RUN apt install -y clang-tidy

# Copy whole repo to autonomous folder
COPY . /autonomous

# Install and use bash terminal
RUN apt install -y bash
RUN bash

# Get python packages
RUN pip install -r /autonomous/python/requirements.txt

# Can also pip install repo but then can't develop inside container
ENV PYTHONPATH=/autonomous/python

# Build C++ code
RUN cmake -S /autonomous/c++ -B /autonomous/c++/build
RUN cmake --build /autonomous/c++/build 

# CMD defines what will be executed when you launch the container.
# this is the main application
CMD echo "My Container has been started"

