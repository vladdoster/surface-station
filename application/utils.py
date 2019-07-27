import sys

import docker


def start_ml_docker_container():
    client = docker.from_env()
    # kill all running containers
    running_containers = client.containers.list()
    for container in running_containers:
        container.kill()
    try:
        return client.containers.run(image="gcr.io/automl-vision-ondevice/gcloud-container-1.12.0:latest",
                                     detach=True).id
    except docker.errors.APIError as e:
        print("Error starting ml container\n\n{}".format(e))
        sys.exit(1)
