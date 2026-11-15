#include <chrono>
#include <cinttypes>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>

#include "example_interfaces/srv/add_two_ints.hpp"
#include "rclcpp/rclcpp.hpp"

int64_t parse_integer(const std::string & text)
{
  std::size_t used = 0;
  const auto value = std::stoll(text, &used);
  if (used != text.size()) {
    throw std::invalid_argument("not an integer");
  }
  return value;
}

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  const auto args = rclcpp::remove_ros_arguments(argc, argv);
  int64_t a = 0, b = 0;
  try {
    std::string first, second;
    if (args.size() == 3) {
      first = args[1];
      second = args[2];
    } else if (args.size() == 1) {
      std::cout << "Input two integers: " << std::flush;
      if (!(std::cin >> first >> second)) {
        throw std::invalid_argument("expected two integers");
      }
    } else {
      throw std::invalid_argument("usage: ros2 run add_service_cpp add_client 2 3");
    }
    a = parse_integer(first);
    b = parse_integer(second);
    if ((b > 0 && a > std::numeric_limits<int64_t>::max() - b) ||
      (b < 0 && a < std::numeric_limits<int64_t>::min() - b))
    {
      throw std::out_of_range("sum exceeds int64 range");
    }
  } catch (const std::exception & e) {
    std::cerr << e.what() << std::endl;
    rclcpp::shutdown();
    return 1;
  }

  auto node = std::make_shared<rclcpp::Node>("add_client");
  auto client = node->create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");
  if (!client->wait_for_service(std::chrono::seconds(10))) {
    RCLCPP_ERROR(node->get_logger(), "add_two_ints unavailable after 10 seconds");
    rclcpp::shutdown();
    return 2;
  }
  auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
  request->a = a;
  request->b = b;
  auto future = client->async_send_request(request);
  const auto result = rclcpp::spin_until_future_complete(node, future, std::chrono::seconds(5));
  int exit_code = 0;
  if (result == rclcpp::FutureReturnCode::SUCCESS) {
    RCLCPP_INFO(node->get_logger(), "%" PRId64 " + %" PRId64 " = %" PRId64,
      a, b, future.get()->sum);
  } else {
    RCLCPP_ERROR(node->get_logger(), "request failed or timed out");
    exit_code = 3;
  }
  rclcpp::shutdown();
  return exit_code;
}
