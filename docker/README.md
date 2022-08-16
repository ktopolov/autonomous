
# Developing with Docker
Within this repository, there is a `Dockerfile-dev`. To build a Docker image from this, run:
```bash
# Build with cache
source shellscripts/docker_build.sh

# Build without cache; fresh rebuild
source shellscripts/docker_build.sh --no-cache
```

To then begin an interactive session with this container, run:
```bash
source shellscripts/docker_start_interactive.sh
```
Note that your `${HOME}` directory will be mounted as a volumne into the Docker container's `${HOME}` directory, allowing you to modify code outside of the container and instantly build/run code within the container.

To avoid having to build the Docker container, you can simply pull the container from the DockerHub remote registry. To do this, run:
```bash
source shellscripts/docker_pull.sh
```
Note that you will be prompted for your DockerHub login credentials if you are not already signed in. Lastly, if you modify the `Dockerfile` and want to push those changes to the remote registry, first build the docker image as discussed above. then, run:
```bash
source docker_push.sh
```

Again, you may be prompted for DockerHub login credentials.
