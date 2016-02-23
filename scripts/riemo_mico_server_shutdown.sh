#!/bin/bash -e
# Shutdown the riemo mico server

# Will kill these ROS nodes
nodes=" \
  riemo_mico_rviz \
  riemo_robot_emulator \
  riemo_move \
  riemo_robot_visualizer \
"

# Will remove these Docker containers (they automatically stop when the nodes
# are killed.)
containers=" \
  motion-optimization-service \
  motion-optimization-visualizer \
  motion-optimization-emulator \
"

docker_container_exists() {
  container_name=$1
  res=`docker ps -a | grep $container_name | awk '{print $(NF)}'`
  if [ "$res" == "$container_name" ]; then
    echo "true"
  else
    echo "false"
  fi
}

echo "Shutting down RieMO mico service:"
for N in $nodes; do
  echo -n "--Killing ROS node: $N..."
  res=$(rosnode kill $N)
  if [ `echo $res | awk '{print $(NF)}'` == 'killed' ]; then
    echo "<success>"
  else
    echo "<failed>"
  fi
done
echo "Service shutdown complete."

echo
wait_time=1
echo "Waiting for containers to stop [$wait_time s]..."
sleep $wait_time

echo
echo "Removing Docker containers:"
for C in $containers; do
  if [ `docker_container_exists $C` == "true" ]; then
    echo -n "--Removing container: $C..."
    res=$(docker rm $C)
    if [ "$res" == $C ]; then
      echo "<success>"
    else
      echo "WARNING -- unexpected output from 'docker rm $C': $res; continuing..."
    fi
  else
    echo "Docker container not found: $C" 
  fi
done

echo
echo "Done. Exiting successfully."
