# emlid_interface
Converts raw data from Emlid into published GPS data

## Parameters
| Parameter Name | Type | Description | Default |
| -------- | ------- | ------- | ------- |
| `baud_rate` | int | Data stream rate from Emlid GPS | 57600 |
| `navsat_link_id` | str | Sets `frame_id` for NavSatFix message header | navsat_link |
| `emlid_device_path` | str | Device path for the Emlid GPS unit | /dev/emlid |
| `timer_callback_frequency` | int | How often the GPS data stream should be queried [Hz] | 50 |

## Subscribers
None

## Publishers
| Topic Name | Type | Description |
| -------- | ------- | ------- |
| `rtk/fix` | [NavSatFix](https://docs.ros2.org/foxy/api/sensor_msgs/msg/NavSatFix.html) | GPS coordinates in decimal degrees |
 
## Notes


## TO-DO:
