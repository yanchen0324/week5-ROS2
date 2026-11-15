#include <cinttypes>
#include <memory>

#include "example_interfaces/srv/add_two_ints.hpp"
#include "rclcpp/rclcpp.hpp"

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("add_server");
  auto service = node->create_service<example_interfaces::srv::AddTwoInts>(
    "add_two_ints",
    [node](const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
      std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response) {
      response->sum = request->a + request->b;
      RCLCPP_INFO(node->get_logger(), "request: %" PRId64 " + %" PRId64 " = %" PRId64,
        request->a, request->b, response->sum);
    });
  RCLCPP_INFO(node->get_logger(), "add_two_ints ready");
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
