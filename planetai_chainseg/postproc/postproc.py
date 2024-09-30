import numpy as np
import scipy


def pred_postproc(y_pred):
    """single frame postproc by dilatiopn"""
    for idx in range(np.shape(y_pred)[-1]):
        y_pred[..., idx] = scipy.ndimage.grey_dilation(y_pred[..., idx], size=10)
    return y_pred


def pred_multipostproc(y_last, y_pred):
    """multi frame postproc to filter small artifacts"""
    for idx in range(np.shape(y_pred)[-1]):
        y_pred[..., idx] = y_last[..., idx] * y_pred[..., idx] / 255
    return y_pred
