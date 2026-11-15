import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from rclpy.parameter import Parameter


class ParameterNode(Node):
    def __init__(self):
        super().__init__('parameter_py')
        self.declare_parameters('', [
            ('frames/odom', 'odom'),
            ('frames/baselink', 'base_link'),
            ('frames/lidar', 'lidar'),
            ('frames/imu', 'imu'),
        ])
        self.add_on_set_parameters_callback(self.validate_parameters)
        self.print_parameters()
        # 与 C++ 的 wall timer 对应，不依赖仿真时间是否推进。
        self.timer = self.create_timer(
            2.0, self.print_parameters, clock=Clock(clock_type=ClockType.STEADY_TIME))

    @staticmethod
    def validate_parameters(parameters):
        for param in parameters:
            if param.name.startswith('frames/'):
                if param.type_ != Parameter.Type.STRING or not param.value:
                    return SetParametersResult(
                        successful=False, reason='frame must be a non-empty string')
        return SetParametersResult(successful=True)

    def print_parameters(self):
        names = ['use_sim_time', 'frames/odom', 'frames/baselink', 'frames/lidar', 'frames/imu']
        values = self.get_parameters(names)
        text = ' | '.join(f'{p.name}={str(p.value).lower() if isinstance(p.value, bool) else p.value}'
                          for p in values)
        self.get_logger().info(text)


def main(args=None):
    rclpy.init(args=args)
    node = ParameterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
