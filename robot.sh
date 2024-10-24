#!/bin/bash

source /opt/ros/humble/setup.bash
source /home/pi/ros2_ws/install/setup.bash
ros2 launch ~/ros2_ws/src/control_board_hardware_interface/test/test_state_publisher.launch.py &
python3 /home/pi/StanfordQuadruped/examples/pupper_v3_ds4_control.py &
ros2 run pupper_feelings face_control 

