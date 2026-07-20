from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription


def generate_launch_description():
    params_file = LaunchConfiguration("params_file")
    emlid_interface_param_file = PathJoinSubstitution(
        [FindPackageShare("emlid_interface"), "param", "emlid_interface_param.yaml"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file", default_value=emlid_interface_param_file
            ),
            Node(
                package="emlid_interface",
                executable="emlid_interface_node",
                name="emlid_interface",
                parameters=[params_file],
                remappings=[
                    ("rtk/fix", "sensors/gps/fix"),
                ],
            ),
        ]
    )
