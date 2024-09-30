import time
from typing import List

import cv2
import numpy as np

from planetai_chainseg.enricher.enricher_base import EnricherBase
from planetai_chainseg.stream.provider_base import StreamProviderBase

TIME_MEASURE_STEPS = 15


class VisualizerBase:
    """Shows frames of StreamProvider class"""

    def __init__(self, provider: StreamProviderBase = None, enrichers: List[EnricherBase] = None):
        """Init Visualizer"""
        assert provider is not None
        self._provider = provider
        self._enrichers: List[EnricherBase] = enrichers or []

    @staticmethod
    def _shrink_frame(frame):
        frame = np.ascontiguousarray(frame[::2, ::2, :])
        return frame

    def stop_enrichers(self):
        for e in self._enrichers:
            e.stop()

    def show(self, max_frames=None):
        """Show window displaying Stream"""
        current_frame_cnt = 0
        start = time.time()
        start_total = time.time()
        while True:
            if not self._provider.is_frame_available():
                continue
            ret, frame = self._provider.get_last_frame()
            current_frame_cnt += 1
            if not ret:
                break
            if max_frames is not None:
                if current_frame_cnt >= max_frames:
                    break
            if current_frame_cnt % TIME_MEASURE_STEPS == 0:
                current = time.time()
                time_diff = current - start
                time_diff_total = current - start_total
                start = current
                print(f"Last {TIME_MEASURE_STEPS} frames fps: {TIME_MEASURE_STEPS/time_diff:2.2f}")
                print(f"Total fps: {current_frame_cnt / time_diff_total:2.2f}")

            frame = self._enrich_frame(frame=frame)
            for e in self._enrichers:
                frame = e.enrich_frame(frame)
            if self._provider.output_rgb:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            cv2.imshow("Frame", frame)

            # Press Q on keyboard to exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("+"):
                for e in self._enrichers:
                    e.scale_up()
            if key == ord("-"):
                for e in self._enrichers:
                    e.scale_down()

    def _enrich_frame(self, frame):
        return frame
