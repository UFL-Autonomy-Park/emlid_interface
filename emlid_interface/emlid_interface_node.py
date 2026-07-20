#!/usr/bin/env python3

# ROS2 library imports
import math

# System imports - not always used but necessary sometimes
import os
import sys
import traceback
from email import message

import rclpy
import rclpy.logging
from nmea import input_stream
from rclpy.node import Node

# Note, for eloquent, tf_transformations is not available
from sensor_msgs.msg import NavSatFix, NavSatStatus


class EmlidInterface(Node):
    def __init__(self):
        super().__init__("emlid_interface_node")

        # Declare parameters
        self.declare_parameter("baud_rate", 57600)
        self.declare_parameter("navsat_link_id", "navsat_link")
        self.declare_parameter("emlid_device_path", "/dev/emlid")
        self.declare_parameter("timer_callback_frequency", 50)

        # Assign parameters
        baud_rate = self.get_parameter("baud_rate").get_parameter_value().integer_value
        emlid_device_path = (
            self.get_parameter("emlid_device_path").get_parameter_value().string_value
        )
        self.navsat_link_id = (
            self.get_parameter("navsat_link_id").get_parameter_value().string_value
        )
        timer_callback_frequency = (
            self.get_parameter("timer_callback_frequency")
            .get_parameter_value()
            .integer_value
        )

        # Publishers
        self.rtk_pub_ = self.create_publisher(NavSatFix, "rtk/fix", 1)

        # Set the timer period and define the timer function that loops at the desired rate
        if timer_callback_frequency <= 0.0:
            raise ValueError("Callback frequency must be >0.")
        timer_period = 1.0 / timer_callback_frequency

        # GPS stream
        self.stream = input_stream.GenericInputStream.open_stream(
            emlid_device_path, baud_rate, timeout=timer_period
        )
        self.get_logger().info("Connected to Emlid and streaming data.")

        self.timer = self.create_timer(timer_period, self.timer_callback)

    @staticmethod
    def nmea_coords_to_decimal(
        coordinate: str,
        hemisphere: str,
    ) -> float:
        value = float(coordinate)
        degrees = int(value // 100)
        minutes = value - 100 * degrees

        decimal_degrees = degrees + minutes / 60.0

        if hemisphere in ("S", "W"):
            decimal_degrees = -decimal_degrees

        return decimal_degrees

    def timer_callback(self):
        received = self.stream.get_line()

        if not received:
            return
        if isinstance(received, bytes):
            message = received.decode("ascii", errors="ignore").strip()
        else:
            message = str(received).strip()

        self.parse(message)

    def parse(self, msg: str) -> None:
        data = msg.split(",")

        if not data or not data[0].endswith("GGA"):
            return

        if len(data) < 15:
            self.get_logger().warning("Received incomplete GGA sentence")
            return

        latitude_raw = data[2]
        latitude_hemisphere = data[3]
        longitude_raw = data[4]
        longitude_hemisphere = data[5]

        if not latitude_raw or not longitude_raw:
            return

        try:
            latitude = self.nmea_coords_to_decimal(latitude_raw, latitude_hemisphere)
            longitude = self.nmea_coords_to_decimal(longitude_raw, longitude_hemisphere)

            self.pack_navsatfix(
                latitude=latitude,
                longitude=longitude,
                data=data,
            )

        except (ValueError, IndexError) as exception:
            self.get_logger().warning(f"Could not parse GGA sentence: {exception}")

    def pack_navsatfix(self, latitude: float, longitude: float, data: list[str]):
        navsat_msg = NavSatFix()
        navsat_msg.header.stamp = self.get_clock().now().to_msg()
        navsat_msg.header.frame_id = self.navsat_link_id

        gps_quality = int(data[6])
        if gps_quality == 0:
            navsat_msg.status.status = NavSatStatus.STATUS_NO_FIX
        elif gps_quality in (2, 4, 5):
            navsat_msg.status.status = NavSatStatus.STATUS_GBAS_FIX
        else:
            navsat_msg.status.status = NavSatStatus.STATUS_FIX

        navsat_msg.status.service = NavSatStatus.SERVICE_GPS

        navsat_msg.latitude = latitude
        navsat_msg.longitude = longitude

        if data[9] and data[11]:
            navsat_msg.altitude = float(data[9]) + float(data[11])
        else:
            navsat_msg.altitude = float("nan")

        # Publish NavSatFix message
        self.rtk_pub_.publish(navsat_msg)


def main(args=None):
    rclpy.init(args=args)
    emlid_interface = None

    try:
        emlid_interface = EmlidInterface()
        rclpy.spin(emlid_interface)

    except KeyboardInterrupt:
        pass

    except Exception:
        if emlid_interface is not None:
            logger = emlid_interface.get_logger()
        else:
            logger = rclpy.logging.get_logger("emlid_interface")
        logger.error(traceback.format_exc())
        raise

    finally:
        if emlid_interface is not None:
            emlid_interface.stream.ensure_closed()
            emlid_interface.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
