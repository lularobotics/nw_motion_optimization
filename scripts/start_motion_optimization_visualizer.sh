#!/bin/bash

# this will return the current directory
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

cd ${SCRIPT_DIR};

# this is some shell magic such that we can the shell output and
# the output in a variable
exec 5>&1
# pipefail will return the non zero return value of any command in the pipe
res=$(set -o pipefail; ./.docker_tools.py --container motion-optimization-visualizer --run "source /root/workspace/devel/setup.bash;/root/workspace/src/nw_riemo_robots/scripts/run_riemo_robot_visualizer.sh" | tee >(cat - >&5))

# if docker tools succeeded we run the output as a shell script
if [[ "$?" == "1" ]];then
    echo "running command"
    echo -e "${res}"
    eval "${res}"
fi
