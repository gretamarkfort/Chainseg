from enum import StrEnum


class Key(StrEnum):
    """Define visible names of MAV info"""

    VOLTAGE_BATTERY = "bat"
    TIME_UNIX_USEC = "clk"
    ROLL = "rol"
    PITCH = "pit"
    YAW = "yaw"
    GROUNDSPEED = "spe"
    HEADING = "hea"
    ALTITUDE = "alt"
    CLIMBRATE = "cli"
