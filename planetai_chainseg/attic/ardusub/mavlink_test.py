import json  # to write dict into a txt file
import time

from pymavlink import mavutil

# Create the connection, listening on a UDP port
connection = mavutil.mavlink_connection("udpin:192.168.2.1:9998")

# Wait for first heartbeat to set the system and component ID of remote system for the link
connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))
# why is there no target_system bzw. ID = 0?

# TODO clean up code

# # Möglichkeit 1
# while True:
#     msg = connection.recv_match()
#     if not msg:
#         continue
#     # 1 SYS_STATUS - general system status - 2.0Hz
#     # SYS_STATUS.voltage_battery - battery voltage in mV
#     if msg.get_type() == "SYS_STATUS":
#         print("\n\n*****Got message: %s*****" % msg.get_type())
#         print("\nAs dictionary: %s" % msg.to_dict())
#         print("Battery voltage: %s mV" % msg.voltage_battery)
#     # 2 SYSTEM_TIME - time of the master clock, typically the computer clock - 3.0Hz
#     # SYSTEM_TIME.time_unix_usec - Timestamp (UNIX epoch time)
#     if msg.get_type() == "SYSTEM_TIME":
#         print("\n\n*****Got message: %s*****" % msg.get_type())
#         print("\nAs dictionary: %s" % msg.to_dict())
#         timestemp = datetime.datetime.fromtimestamp(msg.time_unix_usec)
#         print("System time: %s " % timestemp)
#     # 30 ATTITUDE - attitude in the frame (right-handed, Z-down, Y-right, Y-front, ZYX, intrinsic) - 10.0Hz
#     # ATTITUDE.roll - Roll angle (-pi..+pi) in rad
#     # ATTITUDE.pitch - Pitch angle (-pi..+pi) in rad
#     # ATTITUDE.yaw - Yaw angle (-pi..+pi) in rad
#     if msg.get_type() == "ATTITUDE":
#         print("\n\n*****Got message: %s*****" % msg.get_type())
#         print("\nAs dictionary: %s" % msg.to_dict())
#         print("Roll: %s, Pitch: %s, Yaw: %s " % (msg.roll, msg.pitch, msg.yaw))
#     # 74 VFR_HUD - metrics displayed on a HUD(head up display) for fixed wing aircraft - 10.0 Hz
#     # VFR_HUD.groundspeed - current ground speed in m/s
#     # VFR_HUD.heading - current heading in compass units )0-360, 0=north) in deg
#     # VFR_HUD.alt - current altitude (MSL) in m
#     # VFR_HUD.climb - current climb rate in m/s
#     if msg.get_type() == "VFR_HUD":
#         print("\n\n*****Got message: %s*****" % msg.get_type())
#         print("\nAs dictionary: %s" % msg.to_dict())
#         print(
#             "Groundspeed: %s, Heading: %s, Altitude: %s, Climbrate: %s"
#             % (msg.groundspeed, msg.heading, msg.alt, msg.climb)
#         )

## Möglichkeit 2
# while True:  # eine ewig laufende Schleife
#     msg = connection.recv_match(type='SYS_STATUS', blocking=True)
#     if not msg:
#         continue
#     if msg.get_type():
#         print(msg.voltage_battery)  # hier erscheint jetzt nur noch der Wert

# ## Möglichkeit 3 - läuft so schön - zeigt alle reinkommenden msg
# while True:
#     try:
#         print(connection.recv_match().to_dict())
#     except:
#         pass
#     time.sleep(0.1)

## Möglichkeit 4 - soweit so gut 06.12.
while True:
    # msg no 1 - Sys_status - battery voltage
    msg_001 = connection.recv_match(type="SYS_STATUS", blocking=True)
    msg_001_dict = msg_001.to_dict()
    voltage_battery = msg_001.voltage_battery

    # msg no 2 - timestemp
    msg_002 = connection.recv_match(type="SYSTEM_TIME", blocking=True)
    msg_002_dict = msg_002.to_dict()
    time_unix_usec = msg_002.time_unix_usec
    #    timestemp = datetime.datetime.fromtimestamp(msg_002.time_unix_usec)

    # msg no 30 - attitude (roll, pitch, yaw)
    msg_030 = connection.recv_match(type="ATTITUDE", blocking=True)
    msg_030_dict = msg_030.to_dict()
    roll = msg_030.roll
    pitch = msg_030.pitch
    yaw = msg_030.yaw

    # msg no 74 VRH_HUD
    msg_074 = connection.recv_match(type="VFR_HUD", blocking=True)
    msg_074_dict = msg_074.to_dict()
    groundspeed = msg_074.groundspeed
    heading = msg_074.heading
    altitude = msg_074.alt
    climbrate = msg_074.climb

    # create own dictorny vor overlay of video
    overlay_dict = {}
    # add single key-value pairs
    overlay_dict["Bat"] = (msg_001.voltage_battery, "V")
    overlay_dict["timestemp"] = (time_unix_usec, "")
    overlay_dict["roll"] = (roll, "d")
    overlay_dict["pitch"] = (pitch, "d")
    overlay_dict["yaw"] = (yaw, "d")
    overlay_dict["groundspeed"] = (groundspeed, "ms")
    overlay_dict["heading"] = (heading, "d")
    overlay_dict["altitude"] = (altitude, "m")
    overlay_dict["climbrate"] = (climbrate, "ms")

    try:
        print(overlay_dict)
        with open("overlay_dict.txt", "w") as fp:
            json.dump(overlay_dict, fp)  # encode dict into json
    except:
        pass
    time.sleep(0.1)

# TODO add messagelist to readme?

## Messages
# 0 HEARTBEAT - shows that system and component is present and responding
# 1 SYS_STATUS - general system status
# SYS_STATUS.voltage_battery - battery voltage in mV

# 2 SYSTEM_TIME - time of the master clock, typically the computer clock
# SYSTEM_TIME.time_unix_usec - Timestamp (UNIX epoch time)
# SYSTEM_TIME.time_boot_ms - Timestamp (time since system boot) in ms

# 29 SCALED_PRESSURE - typical setup of one absolute and differential pressure sensor
# SCALED_PRESSURE.press_abs - absolute pressure in hPa
# SCALED_PRESSURE.press_diff - differential pressure 1 in hPa

# 30 ATTITUDE - attitude in the frame (right-handed, Z-down, Y-right, Y-front, ZYX, intrinsic)
# ATTITUDE.roll - Roll angle (-pi..+pi) in rad
# ATTITUDE.pitch - Pitch angle (-pi..+pi) in rad
# ATTITUDE.yaw - Yaw angle (-pi..+pi) in rad

# 74 VFR_HUD - metrics displayed on a HUD(head up display) for fixed wing aircraft
# VFR_HUD.groundspeed - current ground speed in m/s
# VFR_HUD.heading - current heading in compass units )0-360, 0=north) in deg
# VFR_HUD.alt - current altitude (MSL) in m
# VFR_HUD.climb - current climb rate in m/s

# 116 SCALED_IMU2
# 137 SCALED_PRESSURE2
# 147 BATTERY_STATUS.voltages - voltage of cell 1 to 10
