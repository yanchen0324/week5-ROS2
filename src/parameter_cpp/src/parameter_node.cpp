#include <chrono>
#include <memory>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "rcl_interfaces/msg/set_parameters_result.hpp"

class ParameterNode : public rclcpp::Node
{
public:
  ParameterNode() : Node("parameter_cpp")
  {
    // use_sim_time 由 rclcpp 声明，这里不重复声明。
    declare_parameter<std::string>("frames/odom", "odom");
    declare_parameter<std::string>("frames/baselink", "base_link");
    declare_parameter<std::string>("frames/lidar", "lidar");
    declare_parameter<std::string>("frames/imu", "imu");

    callback_ = add_on_set_parameters_callback(
      [](const std::vector<rclcpp::Parameter> & parameters) {
        rcl_interfaces::msg::SetParametersResult result;
        result.successful = true;
        for (const auto & p : parameters) {
          if (p.get_name().rfind("frames/", 0) == 0 &&
            (p.get_type() != rclcpp::ParameterType::PARAMETER_STRING || p.as_string().empty()))
          {
            result.successful = false;
            result.reason = "frame must be a non-empty string";
            break;
          }
        }
        return result;
      });
    print_parameters();
    // 示例 YAML 开启了仿真时间，但并没有 /clock；用墙上时钟照样打印。
    timer_ = create_wall_timer(std::chrono::seconds(2), [this]() {print_parameters();});
  }

private:
  void print_parameters()
  {
    // 每次从参数服务器取值，不能只在构造函数中存一份旧值。
    RCLCPP_INFO(
      get_logger(),
      "use_sim_time=%s | frames/odom=%s | frames/baselink=%s | frames/lidar=%s | frames/imu=%s",
      get_parameter("use_sim_time").as_bool() ? "true" : "false",
      get_parameter("frames/odom").as_string().c_str(),
      get_parameter("frames/baselink").as_string().c_str(),
      get_parameter("frames/lidar").as_string().c_str(),
      get_parameter("frames/imu").as_string().c_str());
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr callback_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ParameterNode>());
  rclcpp::shutdown();
  return 0;
}
