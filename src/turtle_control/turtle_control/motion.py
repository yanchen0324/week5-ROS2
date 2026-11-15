"""不依赖 ROS 的运动计算，便于单独检查边界处理。"""
import math
from dataclasses import dataclass


MODE_NAMES = {0: 'straight', 1: 'sine', 2: 'square', 3: 'paused'}


def wrap_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


@dataclass
class MotionConfig:
    linear_speed: float = 1.5
    angular_speed: float = 1.2
    wave_period: float = 4.0
    boundary_margin: float = 1.0
    turn_gain: float = 3.0
    manual_timeout: float = 0.6
    world_size: float = 11.088889


class Motion:
    def __init__(self, config=None):
        self.config = config or MotionConfig()
        self.mode = 0
        self.phase_time = 0.0
        self.turn_target = None
        self.manual = None
        self.manual_at = 0.0
        self.state = 'waiting_pose'

    def set_mode(self, mode):
        if mode not in MODE_NAMES:
            return False
        self.mode = mode
        self.phase_time = 0.0
        self.turn_target = None
        self.manual = None
        return True

    def set_manual(self, linear, angular, now):
        cfg = self.config
        self.manual = (
            max(-cfg.linear_speed, min(cfg.linear_speed, linear)),
            max(-cfg.angular_speed, min(cfg.angular_speed, angular)),
        )
        self.manual_at = now

    def update(self, pose, dt, now):
        if pose is None:
            self.state = 'waiting_pose'
            return 0.0, 0.0
        cfg = self.config
        x, y, theta = pose
        self.phase_time += max(0.0, min(dt, 0.2))
        if self.manual is not None:
            if now - self.manual_at > cfg.manual_timeout:
                self.turn_target = None
                self.state = 'manual_timeout'
                return 0.0, 0.0
            linear, angular = self.manual
            self.state = 'manual'
        elif self.mode == 3:
            self.state = 'paused'
            return 0.0, 0.0
        else:
            linear = cfg.linear_speed
            phase = 2.0 * math.pi * self.phase_time / cfg.wave_period
            if self.mode == 1:
                angular = cfg.angular_speed * math.sin(phase)
            elif self.mode == 2:
                angular = cfg.angular_speed * (1.0 if math.sin(phase) >= 0.0 else -1.0)
            else:
                angular = 0.0
            self.state = MODE_NAMES[self.mode]

        # 只在靠近边界且运动方向朝外时触发，否则容易原地反复触发。
        vx = linear * math.cos(theta)
        vy = linear * math.sin(theta)
        margin = cfg.boundary_margin
        limit = cfg.world_size - margin
        outward = ((x < margin and vx < 0.0) or (x > limit and vx > 0.0)
                   or (y < margin and vy < 0.0) or (y > limit and vy > 0.0))
        if self.turn_target is None and outward:
            center = cfg.world_size / 2.0
            self.turn_target = math.atan2(center - y, center - x)
            if linear < 0.0:
                self.turn_target = wrap_angle(self.turn_target + math.pi)
        if self.turn_target is not None:
            error = wrap_angle(self.turn_target - theta)
            if abs(error) > 0.10:
                self.state = 'turning'
                return 0.0, max(-cfg.angular_speed, min(cfg.angular_speed, cfg.turn_gain * error))
            self.turn_target = None
            self.phase_time = 0.0
        return linear, angular
