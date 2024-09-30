import cv2
import numpy as np


class StreamProviderBase:
    """Base class that provides frames"""

    def __init__(self, output_rgb=True, **kwargs):
        """base init"""
        self.output_rgb = output_rgb

    def get_last_frame(self) -> (bool, np.ndarray):
        """Returns most recent frame of source as numpy array of shape [height, width, 3]"""
        raise NotImplementedError

    def is_frame_available(self) -> bool:
        """Determines if frame is available"""
        raise NotImplementedError

    def process_frame_rgb(self, frame):
        """Convert given frame from BGR to RGB format"""
        if self.output_rgb:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
