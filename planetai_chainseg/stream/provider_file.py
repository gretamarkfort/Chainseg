import time
from pathlib import Path

import cv2
import numpy as np

from planetai_chainseg.stream.provider_base import StreamProviderBase


class StreamProviderFile(StreamProviderBase):
    """Class to provide frames with video source"""

    def __init__(self, vid_path: Path, target_fps=30.0, **kwargs):
        """Init File StreamProvider for given file"""
        super().__init__(**kwargs)
        self.vid_path = vid_path
        assert self.vid_path.exists(), f"No file found for path: {self.vid_path}"
        self.target_fps = target_fps
        self.time_of_last_frame = time.time()

        cap = cv2.VideoCapture(str(self.vid_path))
        if not cap.isOpened():
            raise IOError
        self._cap = cap

    def get_last_frame(self) -> (bool, np.ndarray):
        """Returns most recent frame of video source

        :return numpy array of shape [height, width, 3]
        """
        ret, frame = self._cap.read()
        frame = self.process_frame_rgb(frame)
        return ret, frame

    def is_frame_available(self) -> bool:
        """Determines if frame is available"""
        current = time.time()
        if current - self.time_of_last_frame >= 1 / self.target_fps:
            self.time_of_last_frame = current
            return True
        else:
            return False
