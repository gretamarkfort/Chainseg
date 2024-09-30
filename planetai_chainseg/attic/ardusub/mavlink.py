from pymavlink import mavutil


class Mavlink:
    """Class to provide BlueROV MAVLink messages on a given port"""

    def __init__(self, port=9998, **kwargs):
        """Summary

        Args:
            port: UDP Client Port
            as added in BlueOS frontend (Mavlink Endpoints)
        """

        super().__init__(**kwargs)
        self.port = port  # ist das notwendig?

        print("udpin:192.168.2.1:" + str(self.port))
        # Mavlink UDP Client (:9998), create connection
        self.master = mavutil.mavlink_connection("udpin:192.168.2.1:" + str(self.port))

    # function to get heartbeat messages
    def get_mavlink_heartbeat(self):
        """Returns Mavlink heartbeat messages"""

        # use connection from topside computer, as in __init__, erneutes angeben des ports ist nervig!!
        print("udpin:192.168.2.1:" + str(self.port))

        # receive heartbeat
        self.master.wait_heartbeat()
        print("received heartbeat")
