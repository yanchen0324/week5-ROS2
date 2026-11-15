from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = LaunchConfiguration('params_file')
    override = {'frames/odom': ParameterValue(LaunchConfiguration('odom'), value_type=str)}
    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=PathJoinSubstitution([FindPackageShare('week5_bringup'), 'config', 'params.yaml'])),
        DeclareLaunchArgument('odom', default_value='odom_from_launch'),
        # 故意交换顺序，用实验比较谁覆盖谁。
        Node(package='parameter_cpp', executable='parameter_node', name='yaml_then_launch',
             parameters=[params, override], output='screen'),
        Node(package='parameter_cpp', executable='parameter_node', name='launch_then_yaml',
             parameters=[override, params], output='screen'),
    ])
