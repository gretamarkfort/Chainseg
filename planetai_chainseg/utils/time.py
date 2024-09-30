import time


class LogTime:
    """Class to measure the execution time in a with block

    Usage:
        with MeasureTime() as t:
            ...
        print(t.duration)
    """

    def __init__(self, caption="Passed time:"):
        """starts time measure"""
        self.start = 0
        self.end = 0
        self.duration = -1
        self.caption = caption

    def __enter__(self):
        """(re)-starts time measure"""
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """stops time measure and save value"""
        self.end = time.time()
        self.duration = self.end - self.start
        time_value, time_unit = get_proper_time(self.duration)
        print(f"{self.caption} {time_value:2.4f} {time_unit}")

    def duration_till_now(self):
        """returns the time until now but does not save in duration.

        if measure was already stopped, return the real duration (from start to end, NOT from start to now)
        """
        if self.duration != -1:
            return self.duration  # already measured
        return time.time() - self.start


def get_proper_time(sec: float) -> (float, str):
    """converts a float of seconds into a meaningful time unit for display purposes

    Supported time frames: mikros, millis, s, min, h

    :param sec: float of seconds
    :return: tuple of new value and unit
    """
    value = sec
    unit = "s"
    if value <= 1:
        value *= 1000
        unit = "millis"
        if value <= 1:
            value *= 1000
            unit = "mikros"
        return value, unit
    if value >= 60:
        value /= 60
        unit = "min"

        if value >= 60:
            value /= 60
            unit = "h"
    return value, unit
