#!/bin/bash
# Terminate if any command fails
set -e

GREEN='\033[0;32m' # Green text
NC='\033[0m'       # No Color

show_help() {
    echo "-----------------------------------------------------------------------"
    echo " This script builds a  Dash lambda image and pushes to ECR             "
    echo ""
    echo " To deploy the image, perform the following steps:                     "
    echo "    1) update your credentials file                                    "
    echo "    2) ./image.sh ecr_login                                            "
    echo "    3) ./image.sh build                                                "
    echo "-----------------------------------------------------------------------"
    echo ""
    exit 1
}

ecr_login() {
  aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin  889772541283.dkr.ecr.us-west-2.amazonaws.com
}

build_image() {
    # dash-gridcerf:branch
    # branch=$(git rev-parse --abbrev-ref HEAD)  
    branch=$1
    image_uri=889772541283.dkr.ecr.us-west-2.amazonaws.com/dash-gridcerf:${branch}

    docker build -t ${image_uri} -f Dockerfile .
    docker push ${image_uri}
}

build() {
    # For now we don't have buildable main branch, so we are building both from dev
    build_image dev
    build_image main
}

# Set msdlive profile to use for any aws operations
export AWS_PROFILE='msdlive'

command="$1"

if [[ -z $command ]] ; then
  show_help

else
  case $command in
    build)
      build
      ;;
    ecr_login)
      ecr_login
      ;;
    *)
      show_help
      ;;
  esac
fi

