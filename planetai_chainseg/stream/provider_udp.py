import numpy as np

from planetai_chainseg.bluerov.video import Video
from planetai_chainseg.stream.provider_base import StreamProviderBase


class StreamProviderUDP(StreamProviderBase):
    """Class to provide frames with video source"""

    def __init__(self, port=5600, **kwargs):
        """Init UDP StreamProvider on a given port"""
        super().__init__(**kwargs)
        self._video = Video(port=port)

        # print("Initialising stream...")
        # waited = 0
        # while not self._video.frame_available():
        #     waited += 1
        #     print("\r  Frame not available (x{})".format(waited), end="")
        #     cv2.waitKey(30)
        # print('\nSuccess!\nStarting streaming - press "q" to quit.')
        #
        # while True:
        #     # Wait for the next frame to become available
        #     if self._video.frame_available():
        #         # Only retrieve and display a frame if it's new
        #         frame = self._video.frame()
        #         cv2.imshow("frame", frame)
        #     # Allow frame to display, and check if user wants to quit
        #     if cv2.waitKey(1) & 0xFF == ord("q"):
        #         break

    def get_last_frame(self) -> (bool, np.ndarray):
        """Returns most recent frame of video source

        :return numpy array of shape [height, width, 3]
        """
        ret = self._video.frame_available()
        frame = self._video.frame() if ret else None
        frame = self.process_frame_rgb(frame)
        return ret, frame

    def is_frame_available(self) -> bool:
        """Determines if frame is available"""

        return self._video.frame_available()
