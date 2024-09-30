import numpy as np
from pymavlink import mavutil

from planetai_chainseg.utils.keys import Key


class MavLinkEngine:
    """mav link wrapper"""

    def __init__(self, addr: str = None, state_dict=None, offline_dummy=False):
        """init"""
        self.offline_dummy = offline_dummy
        self._addr = addr or "udpin:192.168.2.1:9998"
        print(f"Connecting to {self._addr}")
        if not self.offline_dummy:
            self._connection = mavutil.mavlink_connection(device=self._addr, force_connected=True)
            self._connection.wait_heartbeat()
            print(
                f"Connection established. Heartbeat received.\n"
                f"{self._connection.target_system}, {self._connection.target_component}"
            )
        else:
            print(f"Skip - offline dummy")
        assert state_dict is not None
        self.state_dict = state_dict

    def update(self):
        """update mav information and save to state_dict"""
        if self.offline_dummy:
            self.state_dict.update(
                {
                    Key.VOLTAGE_BATTERY: (11.82, "v"),
                    Key.TIME_UNIX_USEC: ("12:30", ""),
                    Key.ROLL: (7.01241234214, "d"),
                    Key.PITCH: (5.0453, "d"),
                    Key.YAW: (26.7, "d"),
                    Key.GROUNDSPEED: (0.91, ""),
                    Key.HEADING: (12.2, "d"),
                    Key.ALTITUDE: (-6.122, ""),
                    Key.CLIMBRATE: (0.091, ""),
                }
            )
            return

        msg_001 = self._connection.recv_match(type="SYS_STATUS", blocking=True)
        self.state_dict.update({Key.VOLTAGE_BATTERY: (msg_001.voltage_battery, "v")})

        msg_002 = self._connection.recv_match(type="SYSTEM_TIME", blocking=True)
        self.state_dict.update({Key.TIME_UNIX_USEC: (msg_002.time_unix_usec, "")})

        msg_030 = self._connection.recv_match(type="ATTITUDE", blocking=True)
        self.state_dict.update(
            {
                Key.ROLL: (np.rad2deg(msg_030.roll), "d"),
                Key.PITCH: (np.rad2deg(msg_030.pitch), "d"),
                Key.YAW: (np.rad2deg(msg_030.yaw), "d"),
            }
        )

        msg_074 = self._connection.recv_match(type="VFR_HUD", blocking=True)
        self.state_dict.update(
            {
                Key.GROUNDSPEED: (msg_074.groundspeed, "m/s"),
                Key.HEADING: (msg_074.heading, "d"),
                Key.ALTITUDE: (msg_074.alt, "m"),
                Key.CLIMBRATE: (msg_074.climb, "m/s"),
            }
        )
