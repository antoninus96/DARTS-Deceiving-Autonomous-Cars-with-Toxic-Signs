import numpy as np
import tensorflow as tf
import keras.backend as K
import cv2

from parameters import *
import utils

def gradient_fn(model):

    y_true = K.placeholder(shape=(OUTPUT_DIM, ))
    loss = tf.nn.softmax_cross_entropy_with_logits_v2(labels=y_true, logits=model.output)
    grad = K.gradients(loss, model.input)

    return K.function([model.input, y_true, K.learning_phase()], grad)


def fg(model, x, y, mask, target):

    x_adv = np.zeros(x.shape, dtype=np.float32)
    grad_fn = gradient_fn(model)

    for i, x_in in enumerate(x):
        utils.printProgressBar(i+50, 100, prefix = 'Progress ITERATIVE TARGET ATTACK:', suffix = 'Complete', length = 50)

        if target == True:
            grad = -1 * grad_fn([x_in.reshape(INPUT_SHAPE), y[i], 0])[0][0]
        else:
            grad = grad_fn([x_in.reshape(INPUT_SHAPE), y[i], 0])[0][0]


        mask_rep = np.repeat(mask[i, :, :, np.newaxis], N_CHANNEL, axis=2)
        grad *= mask_rep

        try:
            grad /= np.linalg.norm(grad)
        except ZeroDivisionError:
            raise

        x_adv[i] = x_in + grad * 3.5

    x_adv = np.clip(x_adv, 0, 1)

    return x_adv
