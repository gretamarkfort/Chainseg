from multiprocessing import Manager, Process, Queue

import matplotlib.cm as cm
import numpy as np
import tensorflow as tf

from planetai_chainseg.net_engine.engine import NetEngine
from planetai_chainseg.visualizer.visualizer_base import VisualizerBase

RESULT_PERSIST_FRAME_NR = 10


def tensorflow_worker(input_queue, output_queue, control_dict):
    """worker for async processing of tf model in separate process

    :param control_dict:
    :param input_queue: if frame is put into this queue this method processes it
    :param output_queue: processed frames are put here
    """
    # Load or define your TensorFlow model here
    # For example, a dummy model:
    net_engine = NetEngine()

    while control_dict["run"]:
        frame = input_queue.get()  # Receive data from the main process
        if frame is None:
            # Use 'None' as a signal to stop the process
            break

        frame = frame.astype(float) / 255.0
        frame_shape = np.shape(frame)
        batched_tf_frame = tf.convert_to_tensor(frame)[tf.newaxis, ...]
        batched_tf_frame_shape = tf.convert_to_tensor(frame_shape)[tf.newaxis, ...]
        inputs = {"img": batched_tf_frame, "img_shape": batched_tf_frame_shape}

        # Process the data
        output = net_engine.predict(inputs)
        output_queue.put(output)  # Send results back to the main process
    print("finish tf")


class VisualizerNeural(VisualizerBase):
    """Shows frames of StreamProvider class"""

    def __enter__(self):
        """context enter dummy"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """context exit to ensure that worker is closed correctly"""
        self.stop_enrichers()
        self.control_dict["run"] = False
        self.tf_process.join()

    def __init__(self, pred_postproc=None, pred_multi_postproc=None, mask_idxs=None, **kwargs):
        """Init Visualizer"""
        super().__init__(**kwargs)

        self.y_lastpred = None
        self.pred_postproc = pred_postproc
        self.pred_multi_postproc = pred_multi_postproc
        assert self._provider.output_rgb
        self.colors_arr = cm.get_cmap("Set1").colors
        self.color_list = [np.array([[[255.0 * e for e in color_tuple]]]) for color_tuple in list(self.colors_arr)]

        self.mask_idxs = mask_idxs or [0]

        self.input_queue = Queue()
        self.output_queue = Queue()
        manager = Manager()
        self.control_dict = manager.dict()
        self.control_dict["run"] = True

        # Start the TensorFlow worker process
        self.tf_process = Process(
            target=tensorflow_worker, args=(self.input_queue, self.output_queue, self.control_dict)
        )
        self.tf_process.start()

        self.persist_counter = 0
        self.persistent_result = None

    def _enrich_frame(self, frame):
        # frame = self._shrink_frame(frame)
        frame_raw = np.array(frame)

        if self.output_queue.empty() and self.input_queue.empty():
            self.input_queue.put(frame)

        got_new_result = False
        y_pred = None
        if not self.output_queue.empty():
            outputs_with_batch = self.output_queue.get()
            y_pred = 255.0 * outputs_with_batch[0]
            if self.pred_postproc is not None:
                y_pred = self.pred_postproc(y_pred)
            if self.pred_multi_postproc is not None:
                y_pred_pre = np.array(y_pred)
                if self.y_lastpred is not None:
                    y_pred = self.pred_multi_postproc(self.y_lastpred, y_pred)
                self.y_lastpred = np.array(y_pred_pre)
            got_new_result = True

        if got_new_result:
            self.persist_counter = 0

            alpha_list = [np.repeat(y_pred[..., [mask_idx]], 3, axis=-1) / 255.0 for mask_idx in self.mask_idxs]
            alpha_minus_one_list = [(1.0 - alpha_list[mask_idx]) for mask_idx in self.mask_idxs]
            alpha_color_list = [alpha_list[mask_idx] * self.color_list[mask_idx] for mask_idx in self.mask_idxs]
            self.persistent_result = {
                "alpha_color_list": alpha_color_list,
                "alpha_minus_one_list": alpha_minus_one_list,
            }
        else:
            self.persist_counter += 1

        if self.persist_counter <= RESULT_PERSIST_FRAME_NR:
            result = self.persistent_result
        else:
            result = None

        frame = frame_raw

        if result is not None:
            for mask_idx in self.mask_idxs:
                frame = result["alpha_minus_one_list"][mask_idx] * frame + result["alpha_color_list"][mask_idx]

        return frame.astype(np.uint8)
