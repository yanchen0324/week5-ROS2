from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = LaunchConfiguration('params_file')
    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=PathJoinSubstitution([FindPackageShare('week5_bringup'), 'config', 'params.yaml'])),
        Node(package='parameter_cpp', executable='parameter_node', name='parameter_cpp',
             parameters=[params], output='screen'),
        Node(package='parameter_py', executable='parameter_node', name='parameter_py',
             parameters=[params], output='screen'),
    ])
