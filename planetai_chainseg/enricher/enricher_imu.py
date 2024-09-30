import time
from datetime import datetime
from multiprocessing import Manager, Process
from typing import Dict, List, Tuple

import cv2
import numpy as np

from planetai_chainseg.enricher.enricher_base import EnricherBase
from planetai_chainseg.mavlink_engine.mav_engine import MavLinkEngine
from planetai_chainseg.utils.keys import Key


def mavlink_worker(state_dict, control_dict, offline_dummy):
    """worker for async log receiving"""

    UPDATE_RATE = 0.1
    mav_engine = MavLinkEngine(addr="udpin:192.168.2.1:9998", state_dict=state_dict, offline_dummy=offline_dummy)

    while control_dict["run"]:
        mav_engine.update()
        time.sleep(UPDATE_RATE)
    print("finish mavlink")


class EnricherIMU(EnricherBase):
    """Enriches frames with IMU log data"""

    def __init__(
        self,
        bg=(50, 50, 50),
        font_color=(200, 200, 200),
        element_color=(170, 170, 170),
        alert_color=(200, 0, 0),
        drift_color=(0, 200, 0),
        scale=2,
        thickness=2,
        offline_dummy=False,
    ):
        """Init"""
        super().__init__()
        self._bg = bg
        self._font_color = font_color
        self._element_color = element_color
        self._alert_color = alert_color
        self._drift_color = drift_color
        self._scale = scale
        self._thickness = thickness
        self._line_height = 15
        self._dims = None
        self._center = None

        manager = Manager()
        self.state_dict = manager.dict()
        self.control_dict = manager.dict()
        self.control_dict["run"] = True
        time.sleep(1)
        self.mav_process = Process(
            target=mavlink_worker,
            args=(self.state_dict, self.control_dict, offline_dummy),
        )
        self.mav_process.start()
        time.sleep(5)
        self.info_list = sorted(list(self.state_dict.keys()))

    def stop(self):
        self.control_dict["run"] = False
        self.mav_process.join()

    def _enrich_frame(self, frame: np.ndarray):
        if self._dims is None:
            self._dims = frame.shape
            self._center = [int(np.round(e / 2)) for e in self._dims]

        width = int(self._scale * 100) + 5
        left_right_bar = self._dims[1] - width
        upper_text = int(15 * self._scale)
        left_text = int(40 * self._scale) + 5

        # voltage
        voltage_value = float(self.state_dict[Key.VOLTAGE_BATTERY][0])  # warum noch die [0]
        alert = voltage_value < 12500

        self.add_text_box_at_pos(
            frame,
            {Key.VOLTAGE_BATTERY: self.state_dict[Key.VOLTAGE_BATTERY]},
            [Key.VOLTAGE_BATTERY],
            [left_right_bar, 0, width],
            [5, upper_text],
            [left_text, upper_text],
            color_list=[self._font_color if not alert else self._alert_color],
        )

        # alt
        self.add_text_box_at_pos(
            frame,
            {Key.ALTITUDE: self.state_dict[Key.ALTITUDE]},
            [Key.ALTITUDE],
            [left_right_bar, int(30 * self._scale), width],
            [5, upper_text],
            [left_text, upper_text],
        )

        # climb, speed
        self.add_text_box_at_pos(
            frame,
            {Key.CLIMBRATE: self.state_dict[Key.CLIMBRATE], Key.GROUNDSPEED: self.state_dict[Key.GROUNDSPEED]},
            [Key.CLIMBRATE, Key.GROUNDSPEED],
            [left_right_bar, int(60 * self._scale), width],
            [5, upper_text],
            [left_text, upper_text],
        )

        # heading, pitch, roll, yaw
        self.add_text_box_at_pos(
            frame,
            {
                Key.HEADING: self.state_dict[Key.HEADING],
                Key.PITCH: self.state_dict[Key.PITCH],
                Key.ROLL: self.state_dict[Key.ROLL],
                Key.YAW: self.state_dict[Key.YAW],
            },
            [Key.HEADING, Key.PITCH, Key.ROLL, Key.YAW],
            [left_right_bar, int(120 * self._scale), width],
            [5, upper_text],
            [left_text, upper_text],
        )

        # time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%d.%m.%Y")

        self.add_text_box_at_pos(
            frame,
            {"a": (current_time, ""), "b": (current_date, "")},
            ["a", "b"],
            [left_right_bar, self._dims[0] - int(40 * self._scale), width],
            [5, upper_text],
            [5, upper_text],
            skip_name=True,
        )

        # compass
        compass_scale = 0.6 * self._scale
        compass_half_width = int(80 * compass_scale)
        compass_vshift = 0
        self.add_arrow_at_pos(
            frame,
            float(self.state_dict[Key.HEADING][0]),
            [compass_half_width, compass_half_width + compass_vshift],
            1,
            scale=compass_scale,
            vsqueeze=1,
            show_inter_circ=False,
        )

        # roll,pitch compilation
        xvalue = float(self.state_dict[Key.ROLL][0])
        yvalue = float(self.state_dict[Key.PITCH][0])
        alen = np.sqrt(xvalue**2 + yvalue**2)
        angle = np.rad2deg(np.arctan2(xvalue, -yvalue))
        alen_norm = min(alen / 30.0, 1.0)
        alert = alen > 30.0

        self.add_arrow_at_pos(
            frame,
            angle,
            [compass_half_width, 3 * compass_half_width + compass_vshift],
            alen_norm,
            scale=compass_scale,
            vsqueeze=1,
            arrow_color=self._drift_color if not alert else self._alert_color,
        )
        return frame

    def add_text_box_at_pos(
        self,
        frame,
        text_dict: Dict,
        key_list: List[str],
        leftupperwidth_box: List[int],
        leftupper_name: List[int],  # [5, 15]
        leftupper_val: List[int],  # [50, 15]
        bottom_border: int = 5,
        skip_name: bool = False,
        color_list: List[Tuple] = None,
    ):
        color_list = color_list or [None] * len(key_list)
        assert len(color_list) == len(key_list), "len of color_list and key_list doesnt match."

        leftupper_name[0] += leftupperwidth_box[0]
        leftupper_name[1] += leftupperwidth_box[1]
        leftupper_val[0] += leftupperwidth_box[0]
        leftupper_val[1] += leftupperwidth_box[1]

        cv2.rectangle(
            frame,
            leftupperwidth_box[0:2],
            (
                leftupperwidth_box[0] + leftupperwidth_box[2],
                leftupperwidth_box[1] + (len(text_dict)) * int(self._line_height * self._scale) + bottom_border,
            ),
            self._bg,
            -1,
        )

        for idx, (k, c) in enumerate(zip(key_list, color_list)):
            val, unit = text_dict[k]
            if isinstance(val, float):
                val = f"{val:3.2f}"
            if isinstance(val, int):
                val = f"{val:3}"
            if not skip_name:
                self.add_text_at_pos(frame, f"{k}", list(leftupper_name), voffset=idx, color=c)
            if val is not None:
                self.add_text_at_pos(frame, f"{str(val):7s}", list(leftupper_val), voffset=idx, color=c)
            else:
                self.add_text_at_pos(frame, f"---", list(leftupper_val), voffset=idx, color=c)

    def add_text_at_pos(self, frame, text, leftupper: List[int], voffset: int, color=None):
        """add a text element to frame"""
        color = color or self._font_color
        pos = leftupper
        pos[1] = pos[1] + voffset * int(self._line_height * self._scale)
        cv2.putText(
            frame,
            text,
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5 * self._scale,
            color=color,
            thickness=self._thickness,
        )

    def add_arrow_at_pos(
        self,
        frame,
        angle_deg: float,
        center: List[int],
        alen: float,
        scale: float = 1,
        vsqueeze=0.5,
        show_inter_circ: bool = True,
        arrow_color=(200, 0, 0),
    ):
        """add a radar style element to frame"""
        angle_rad = np.deg2rad(angle_deg)
        ellipse_size = 80 * scale
        ellipse_dims = [int(ellipse_size), int(ellipse_size * vsqueeze)]
        # downward correct center for vsqueeze
        center[1] = center[1] + int(ellipse_size) - ellipse_dims[1]
        target = [
            center[0] + int(ellipse_dims[0] * alen * np.sin(angle_rad)),
            center[1] - int(ellipse_dims[1] * alen * np.cos(angle_rad)),
        ]

        cv2.ellipse(
            frame, center=center, axes=ellipse_dims, angle=0, startAngle=0, endAngle=360, color=self._bg, thickness=-1
        )
        cv2.ellipse(
            frame,
            center=center,
            axes=ellipse_dims,
            angle=0,
            startAngle=0,
            endAngle=360,
            color=self._element_color,
            thickness=1,
        )
        cv2.line(
            frame,
            [center[0], int(center[1] - ellipse_dims[1])],
            [center[0], int(center[1] + ellipse_dims[1])],
            color=self._element_color,
            thickness=1,
        )
        cv2.line(
            frame,
            [int(center[0] - ellipse_dims[0]), center[1]],
            [int(center[0] + ellipse_dims[0]), center[1]],
            color=self._element_color,
            thickness=1,
        )
        if show_inter_circ:
            cv2.ellipse(
                frame,
                center=center,
                axes=[e // 2 for e in ellipse_dims],
                angle=0,
                startAngle=0,
                endAngle=360,
                color=self._element_color,
                thickness=1,
            )
        cv2.arrowedLine(frame, center, target, color=arrow_color, thickness=2)

    def scale_up(self):
        self._scale += 0.1
        print("scale up")

    def scale_down(self):
        self._scale -= 0.1
        print("scale down")
