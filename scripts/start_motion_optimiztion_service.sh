#!/bin/sh
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

# copied from get.docker.com
command_exists() {
	command -v "$@" > /dev/null 2>&1
}

command_success() {
	"$@" > /dev/null 2>&1
}

if ! command_exists docker; then
    echo -e "###############################################################"
    echo -e "# please run the init.sh script in nw_init to setup your computer for motion_optimization"
    echo -e "###############################################################"
    exit 1
fi

if ! command_success docker info;then
    echo -e "###############################################################"
    echo -e "# please run the init.sh script in nw_init to setup your computer for motion_optimization"
    echo -e "###############################################################"
    exit 1
fi

bash ${SCRIPT_DIR}/.docker_tools.py --container motion-optimization-service --run "source /root/workspace/devel/setup.bash && rosrun riemo_programs grasp_problem_service"
