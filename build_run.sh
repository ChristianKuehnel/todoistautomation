#!/bin/bash
set -eu

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
IMAGE_NAME=todoistautomation

docker rm "${IMAGE_NAME}" || true

docker build --tag "${IMAGE_NAME}" "${SCRIPT_DIR}"

docker run --name "${IMAGE_NAME}" -v "${SCRIPT_DIR}":/config "${IMAGE_NAME}"
