# Example of how to read all the parameters from the Autopilot with pymavlink
# Source: https://www.ardusub.com/developers/pymavlink.html#read-all-parameters


# Disable "Broad exception" warning
# pylint: disable=W0703

import sys
import time

# Import mavutil
from pymavlink import mavutil

# Create the connection
master = mavutil.mavlink_connection("udpin:192.168.2.1:9998")
# Wait a heartbeat before sending commands
master.wait_heartbeat()

# Request all parameters
master.mav.param_request_list_send(master.target_system, master.target_component)
while True:
    time.sleep(0.01)
    try:
        message = master.recv_match(type="PARAM_VALUE", blocking=True).to_dict()
        print("name: %s\tvalue: %d" % (message["param_id"], message["param_value"]))
    except Exception as error:
        print(error)
        sys.exit(0)
