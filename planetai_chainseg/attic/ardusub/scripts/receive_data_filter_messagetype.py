# Example of how to filter for specific mavlink messages coming from the
# autopilot using pymavlink.
#
# Can also filter within recv_match command - see "Read all parameters" example
# Source: https://www.ardusub.com/developers/pymavlink.html#receive-data-and-filter-by-message-type

# Import mavutil
from pymavlink import mavutil

# Create the connection
# From topside computer
master = mavutil.mavlink_connection("udpin:192.168.2.1:9998")

# while True:
#     msg = master.recv_match()
#     if not msg:
#         continue
#     if msg.get_type() == 'HEARTBEAT':
#         print("\n\n*****Got message: %s*****" % msg.get_type())
#         print("Message: %s" % msg)
#         print("\nAs dictionary: %s" % msg.to_dict())
#         # Armed = MAV_STATE_STANDBY (4), Disarmed = MAV_STATE_ACTIVE (3)
#         print("\nSystem status: %s" % msg.system_status)

while True:
    msg = master.recv_match()
    if not msg:
        continue
    if msg.get_type() == "SCALED_IMU2":
        print("\n\n*****Got message: %s*****" % msg.get_type())
        print("Message: %s" % msg)
        print("\nAs dictionary: %s" % msg.to_dict())
#       print("\nSystem status: %s" % msg.system_status)
