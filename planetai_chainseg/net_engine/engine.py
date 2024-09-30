import tensorflow as tf

from planetai_chainseg import default_seg_net_path


class NetEngine:
    """tf model wrapper"""

    def __init__(self, net_path: str = None, is_tf_compile: bool = False):
        """init

        :param net_path: str to tf model serve
        :param is_tf_compile: flag to compile tf model
        """
        self._net_path = net_path if net_path is not None else default_seg_net_path
        self._model: tf.keras.Model = tf.keras.models.load_model(
            self._net_path,
            compile=is_tf_compile,
            custom_objects={},
        )

    def predict(self, inputs):
        """predict a frame

        :param inputs: input tensor thats passed to model
        :return: model outputs
        """

        res = self._model.predict(inputs, batch_size=1, verbose=0)["seg_cls_confidence"]
        return res
