from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = LaunchConfiguration('params_file')
    keyboard = LaunchConfiguration('keyboard')
    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=PathJoinSubstitution([FindPackageShare('week5_bringup'), 'config', 'turtle.yaml'])),
        DeclareLaunchArgument('keyboard', default_value='true',
                              description='Open a GNOME terminal for keyboard teleop'),
        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim',
             parameters=[params], output='screen'),
        Node(package='turtle_control', executable='controller', name='turtle_controller',
             parameters=[params], output='screen'),
        # launch 本身不把终端输入转发给子节点，遥控需要单独的交互终端。
        Node(package='turtle_control', executable='teleop', name='turtle_teleop',
             prefix='gnome-terminal --wait --', parameters=[params],
             condition=IfCondition(keyboard), output='screen'),
        Node(package='turtle_control', executable='teleop', name='turtle_teleop',
             parameters=[params, {'keyboard_enabled': False}],
             condition=UnlessCondition(keyboard), output='screen'),
    ])
