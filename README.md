# yahboom_rosmaster

![OS](https://img.shields.io/badge/Ubuntu-22.04-orange)
![ROS_2](https://img.shields.io/badge/ROS2-Humble-blue)
![Gazebo](https://img.shields.io/badge/Gazebo-Classic%2011-green)

ROS 2 Humble support for the **ROSMASTER X3** mecanum wheel robot by Yahboom.

> This repository is forked from [automaticaddison/yahboom_rosmaster](https://github.com/automaticaddison/yahboom_rosmaster) (Jazzy) and adapted for ROS 2 Humble with Gazebo Classic.

![ROSMASTER X3 in Gazebo](https://automaticaddison.com/wp-content/uploads/2024/11/gazebo-800-square-mecanum-controller.gif)

## Features

- **Mecanum wheel robot** with holonomic (omnidirectional) movement
- **Gazebo Classic** simulation with realistic physics
- **Sensors**: RGB-D Camera, 2D LiDAR, IMU
- **ROS 2 Control** integration for wheel velocity control
- **Nav2 & SLAM** ready configuration
- Multiple world files for testing

## Prerequisites

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic 11

## Installation

```bash
# Create workspace
mkdir -p ~/rosmaster_ws/src
cd ~/rosmaster_ws/src

# Clone the repository
git clone https://github.com/juan-kaplan/yahboom_rosmaster.git

# Install dependencies
cd ~/rosmaster_ws
rosdep install --from-paths src --ignore-src -r -y

# Build
colcon build --symlink-install

# Source
source install/setup.bash
```

## Quick Start

### 1. Launch Simulation

```bash
# Empty world (with RViz)
ros2 launch yahboom_rosmaster_gazebo rosmaster_gazebo_classic.launch.py

# Simple room (recommended for SLAM/Nav)
ros2 launch yahboom_rosmaster_gazebo rosmaster_gazebo_classic.launch.py \
  world:=$(ros2 pkg prefix yahboom_rosmaster_gazebo)/share/yahboom_rosmaster_gazebo/worlds/simple_room.world

# Without RViz
ros2 launch yahboom_rosmaster_gazebo rosmaster_gazebo_classic.launch.py rviz:=false
```

### 2. Teleoperation

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Use keys: `u i o`, `j k l`, `m , .` to control the robot.

### Launch Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `world` | `empty.world` | Path to the Gazebo world file |
| `rviz` | `true` | Launch RViz automatically |
| `use_sim_time` | `true` | Use simulation time |

## Available Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/cmd_vel` | `geometry_msgs/Twist` | Velocity commands |
| `/scan` | `sensor_msgs/LaserScan` | LiDAR data |
| `/imu/data` | `sensor_msgs/Imu` | IMU readings |
| `/cam_1/image_raw` | `sensor_msgs/Image` | RGB camera |
| `/cam_1/depth/image_raw` | `sensor_msgs/Image` | Depth image |
| `/mecanum_drive_controller/odom` | `nav_msgs/Odometry` | Odometry |

## Packages

| Package | Description |
|---------|-------------|
| `yahboom_rosmaster` | Metapackage |
| `yahboom_rosmaster_description` | URDF, meshes, RViz configs |
| `yahboom_rosmaster_gazebo` | Simulation launch files, worlds |
| `yahboom_rosmaster_navigation` | Nav2 configuration |
| `yahboom_rosmaster_localization` | Localization (robot_localization) |
| `yahboom_rosmaster_bringup` | Robot bringup launch files |
| `yahboom_rosmaster_docking` | Docking functionality |
| `yahboom_rosmaster_msgs` | Custom messages |

## License

BSD-3-Clause
