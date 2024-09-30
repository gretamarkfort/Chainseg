from planetai_chainseg.visualizer.visualizer_base import VisualizerBase


class VisualizerBasic(VisualizerBase):
    """Shows frames of StreamProvider class"""

    def __init__(self, **kwargs):
        """Init Visualizer"""
        super().__init__(**kwargs)

    def _enrich_frame(self, frame):
        frame = self._shrink_frame(frame)
        return frame
