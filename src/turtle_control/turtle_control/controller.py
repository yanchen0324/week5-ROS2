import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from std_msgs.msg import String
from turtle_interfaces.srv import SetMotionMode
from turtlesim.msg import Pose

from turtle_control.motion import MODE_NAMES, Motion, MotionConfig


class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        defaults = MotionConfig()
        self.parameter_names = [
            'linear_speed', 'angular_speed', 'wave_period', 'boundary_margin',
            'turn_gain', 'manual_timeout',
        ]
        for name in self.parameter_names:
            self.declare_parameter(name, getattr(defaults, name))
        validation = self.validate_parameters(self.get_parameters(self.parameter_names))
        if not validation.successful:
            raise ValueError(validation.reason)
        self.motion = Motion(self.read_config())
        self.pose = None
        self.pose_at = 0.0
        self.last_tick = time.monotonic()
        self.last_state = ''
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.state_publisher = self.create_publisher(String, '/turtle_controller/state', 10)
        self.pose_subscription = self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)
        self.manual_subscription = self.create_subscription(
            Twist, '/turtle_controller/manual_cmd', self.on_manual, 10)
        self.service = self.create_service(
            SetMotionMode, '/turtle_controller/set_mode', self.on_set_mode)
        self.add_on_set_parameters_callback(self.validate_parameters)
        self.timer = self.create_timer(0.05, self.on_tick)
        self.get_logger().info('默认直线前进；set_mode: 0=直线 1=正弦 2=方波 3=暂停')

    def read_config(self):
        return MotionConfig(**{name: self.get_parameter(name).value for name in self.parameter_names})

    def validate_parameters(self, parameters):
        for param in parameters:
            if param.name not in self.parameter_names:
                continue
            value = param.value
            if not isinstance(value, float) or not math.isfinite(value) or value <= 0.0:
                return SetParametersResult(successful=False, reason=f'{param.name} must be a positive double')
            if param.name == 'boundary_margin' and not 0.5 <= value <= 4.0:
                return SetParametersResult(successful=False, reason='boundary_margin must be in [0.5, 4.0]')
            if param.name == 'linear_speed' and value > 3.0:
                return SetParametersResult(successful=False, reason='linear_speed must be <= 3.0')
        return SetParametersResult(successful=True)

    def on_pose(self, msg):
        self.pose = (msg.x, msg.y, msg.theta)
        self.pose_at = time.monotonic()

    def on_manual(self, msg):
        if not math.isfinite(msg.linear.x) or not math.isfinite(msg.angular.z):
            return
        self.motion.set_manual(msg.linear.x, msg.angular.z, time.monotonic())

    def on_set_mode(self, request, response):
        response.success = self.motion.set_mode(request.mode)
        response.current_mode = self.motion.mode
        response.message = MODE_NAMES[self.motion.mode] if response.success else 'mode must be 0, 1, 2 or 3'
        self.get_logger().info(f'set_mode({request.mode}): {response.message}')
        return response

    def on_tick(self):
        now = time.monotonic()
        self.motion.config = self.read_config()
        # 位姿断流时停止输出运动命令。
        pose = self.pose if now - self.pose_at < 1.0 else None
        linear, angular = self.motion.update(pose, now - self.last_tick, now)
        self.last_tick = now
        command = Twist()
        command.linear.x = linear
        command.angular.z = angular
        self.publisher.publish(command)
        self.state_publisher.publish(String(data=self.motion.state))
        if self.motion.state != self.last_state:
            self.get_logger().info(f'state: {self.motion.state}')
            self.last_state = self.motion.state

    def stop(self):
        self.publisher.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
