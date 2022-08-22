#!/bin/bash

# Script to build all C++ targets (tests, apps, libraries, etc.) across repo.
# Enter "source cpp_build.sh -h" to see help
if [ "$1" == "-h" ]; then
  echo "* Build all targets without debug flags: source cpp_build.sh"
  echo "* Build all targets WITH debug flags: source cpp_build.sh -d"
  echo ""
  exit 0
fi

# Automatically determine absolute path to repo
SHELLSCRIPTS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
REPO_DIR="${SHELLSCRIPTS_DIR}/.."

if [[ $1 == "-d" ]]
then
    echo "Building with debug flags"
    cmake -S ${REPO_DIR}/c++ -B ${REPO_DIR}/c++/build -DCMAKE_BUILD_TYPE=Debug
else
    echo "Building without debug flags"
    cmake -S ${REPO_DIR}/c++ -B ${REPO_DIR}/c++/build
fi

cmake --build ${REPO_DIR}/c++/build
