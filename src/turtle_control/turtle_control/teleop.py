import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtle_interfaces.srv import SetMotionMode


HELP = '''
小海龟遥控（在此终端按键）
w/s : 前进/后退     a/d : 左转/右转
0   : 恢复直线      1   : 正弦式前进
2   : 方波式前进    3/空格 : 暂停
q   : 暂停并退出遥控
按住方向键持续运动；松开后约 0.6 秒停止，按 0/1/2 恢复自动运动。
'''


class TurtleTeleop(Node):
    def __init__(self):
        super().__init__('turtle_teleop')
        self.declare_parameter('keyboard_enabled', True)
        self.declare_parameter('linear_speed', 1.5)
        self.declare_parameter('angular_speed', 1.2)
        self.publisher = self.create_publisher(Twist, '/turtle_controller/manual_cmd', 10)
        self.client = self.create_client(SetMotionMode, '/turtle_controller/set_mode')

    def set_mode(self, mode):
        if not self.client.service_is_ready():
            self.get_logger().warning('模式服务尚未就绪，请稍后再按一次')
            return None
        request = SetMotionMode.Request()
        request.mode = mode
        future = self.client.call_async(request)

        def show_result(done):
            try:
                result = done.result()
                self.get_logger().info(f'mode={result.current_mode}, success={result.success}: {result.message}')
            except Exception as error:
                self.get_logger().error(str(error))
        future.add_done_callback(show_result)
        return future

    def publish_key(self, key):
        directions = {'w': (1.0, 0.0), 's': (-1.0, 0.0), 'a': (0.0, 1.0), 'd': (0.0, -1.0)}
        linear, angular = directions[key]
        msg = Twist()
        msg.linear.x = linear * self.get_parameter('linear_speed').value
        msg.angular.z = angular * self.get_parameter('angular_speed').value
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleTeleop()
    old_settings = None
    try:
        if not node.get_parameter('keyboard_enabled').value:
            node.get_logger().info('遥控节点已启动，keyboard:=false 时不读取键盘')
            rclpy.spin(node)
            return
        if not sys.stdin.isatty():
            node.get_logger().error('需要交互终端：请单独运行 ros2 run turtle_control teleop')
            return
        print(HELP, flush=True)
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.02)
            if not select.select([sys.stdin], [], [], 0.03)[0]:
                continue
            key = sys.stdin.read(1).lower()
            if key in 'wasd':
                node.publish_key(key)
            elif key in '0123' or key == ' ':
                node.set_mode(3 if key == ' ' else int(key))
            elif key in ('q', '\x03'):
                future = node.set_mode(3)
                if future is not None:
                    rclpy.spin_until_future_complete(node, future, timeout_sec=1.0)
                break
    except KeyboardInterrupt:
        if rclpy.ok():
            future = node.set_mode(3)
            if future is not None:
                rclpy.spin_until_future_complete(node, future, timeout_sec=1.0)
    finally:
        if old_settings is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
