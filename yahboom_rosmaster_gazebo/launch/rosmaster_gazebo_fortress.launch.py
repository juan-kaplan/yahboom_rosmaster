#!/usr/bin/env python3
"""
Launch Gazebo Fortress simulation for ROSMASTER X3 with physics-based mecanum drive.

Uses gz_ros2_control + fdir1 gz:expressed_in="base_link" for correct holonomic strafing.
"""
import os

from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def _launch_rviz(context):
    launch_rviz = context.launch_configurations.get("rviz", "true")
    if launch_rviz.lower() in ("true", "1", "yes"):
        pkg_gz = get_package_share_directory("yahboom_rosmaster_gazebo")
        default_rviz = os.path.join(pkg_gz, "rviz", "gazebo.rviz")
        use_sim_time = context.launch_configurations.get("use_sim_time", "true")
        rviz_node = Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", default_rviz],
            parameters=[{"use_sim_time": use_sim_time == "true"}],
            output="screen",
        )
        return [TimerAction(period=5.0, actions=[rviz_node])]
    return []


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    world = LaunchConfiguration("world")

    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    pkg_desc = get_package_share_directory("yahboom_rosmaster_description")
    pkg_gz = get_package_share_directory("yahboom_rosmaster_gazebo")

    default_world = os.path.join(pkg_gz, "worlds", "empty.world")
    default_xacro = os.path.join(pkg_desc, "urdf", "robots", "rosmaster_x3.urdf.xacro")
    bridge_config = os.path.join(pkg_gz, "config", "ros_gz_bridge.yaml")
    ros2_control_config = os.path.join(pkg_gz, "config", "ros2_control.yaml")
    twist_script = os.path.join(pkg_gz, "scripts", "twist_to_stamped.py")

    declare_use_sim_time = DeclareLaunchArgument("use_sim_time", default_value="true")
    declare_world = DeclareLaunchArgument("world", default_value=default_world)
    declare_rviz = DeclareLaunchArgument(
        "rviz", default_value="true", description="Launch RViz (true/false)")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "robot_description": ParameterValue(Command([
                "xacro", " ", default_xacro,
                " use_gazebo:=true",
                " use_ignition:=true",
                " robot_name:=rosmaster_x3",
                " prefix:=",
            ]), value_type=str),
        }],
    )

    # Gazebo Fortress server (headless)
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")),
        launch_arguments=[("gz_args", ["-r -s -v 4 ", world])],
    )

    # Gazebo Fortress GUI
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")),
        launch_arguments=[("gz_args", "-g")],
    )

    # Spawn robot from robot_description topic
    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-name", "rosmaster_x3",
            "-allow_renaming", "true",
        ],
        output="screen",
    )

    # Bridge sensor topics: camera info, point cloud, LiDAR, IMU, clock
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{"config_file": bridge_config}],
        output="screen",
    )

    # Optimized image bridge for camera
    ros_gz_image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/cam_1/image"],
        remappings=[("/cam_1/image", "/cam_1/color/image_raw")],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
            "--param-file", ros2_control_config,
        ],
        output="screen",
    )

    mecanum_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "mecanum_drive_controller",
            "--controller-manager", "/controller_manager",
            "--param-file", ros2_control_config,
        ],
        output="screen",
    )

    # Convert /cmd_vel (Twist) → /mecanum_drive_controller/cmd_vel (TwistStamped)
    twist_converter = ExecuteProcess(
        cmd=["python3", twist_script],
        output="screen",
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_world,
        declare_rviz,
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.join(pkg_gz, "models")),
        robot_state_publisher,
        gazebo_server,
        gazebo_client,
        TimerAction(period=3.0, actions=[spawn]),
        TimerAction(period=5.0, actions=[ros_gz_bridge, ros_gz_image_bridge]),
        TimerAction(period=8.0, actions=[joint_state_broadcaster_spawner]),
        TimerAction(period=9.0, actions=[mecanum_controller_spawner]),
        TimerAction(period=10.0, actions=[twist_converter]),
        OpaqueFunction(function=_launch_rviz),
    ])
