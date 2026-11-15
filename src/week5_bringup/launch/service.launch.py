from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='add_service_cpp', executable='add_server', output='screen'),
    ])
