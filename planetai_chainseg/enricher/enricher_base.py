import numpy as np


class EnricherBase:
    """Enriches frames - adds elements to a frame independent of frame content"""

    def __init__(self):
        """Init"""
        ...

    def enrich_frame(self, frame: np.ndarray):
        """class wide modifications for frame"""
        return self._enrich_frame(frame)

    def _enrich_frame(self, frame: np.ndarray):
        """specific modifications for frame. To be implemented in child classes"""
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def scale_up(self):
        raise NotImplementedError

    def scale_down(self):
        raise NotImplementedError
