import os
import cv2
import numpy as np
import tensorflow as tf
import scipy.io as sio
from tvnet import TVNet
flags = tf.app.flags
# flags.DEFINE_integer("scale", 5, " TVNet scale [3]")
# flags.DEFINE_integer("warp", 5, " TVNet warp [1]")
# flags.DEFINE_integer("iteration", 5, " TVNet iteration [10]")
flags.DEFINE_string("gpu", '0', " gpu to use [0]")
FLAGS = flags.FLAGS

# scale = FLAGS.scale
# warp = FLAGS.warp
# iteration = FLAGS.iteration
if int(FLAGS.gpu > -1):
    os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu

# print 'TVNet Params:\n scale: %d\n warp: %d\n iteration: %d\nUsing gpu: %s' \
#       % (scale, warp, iteration, FLAGS.gpu)

# load image
img1 = cv2.imread("Middlebury/eval-data/Backyard/frame11.png")
img2 = cv2.imread("Middlebury/eval-data/Backyard/frame12.png")
# print(img1[np.newaxis, ...].shape)
h, w, c = img1.shape

# model construct
x1 = tf.placeholder(shape=[1, h, w, 3], dtype=tf.float32)
x2 = tf.placeholder(shape=[1, h, w, 3], dtype=tf.float32)
tvnet = TVNet()
# u1, u2, rho = tvnet.tvnet_flow(x1, x2, max_scales=scale,
#                      warps=warp,
#                      max_iterations=iteration)
u1, u2, rho = tvnet.tvnet_flow(x1, x2)
# init
sess = tf.Session(config=tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True), allow_soft_placement=True))

#saver = tf.train.import_meta_graph("ckpt/nn_model.ckpt.meta")
#saver.restore(sess, tf.train.latest_checkpoint('ckpt/'))
#print(sess.run('u1'))


saver = tf.train.Saver()
saver.restore(sess, "ckpt/nn_model.ckpt")
# sess.run(tf.global_variables_initializer())
all_var = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
# run model
u1_np, u2_np = sess.run([u1, u2], feed_dict={x1: img1[np.newaxis, ...], x2: img2[np.newaxis, ...]})

u1_np = np.squeeze(u1_np)
u2_np = np.squeeze(u2_np)
flow_mat = np.zeros([h, w, 2])
flow_mat[:, :, 0] = u1_np
flow_mat[:, :, 1] = u2_np

if not os.path.exists('result'):
    os.mkdir('result')
res_path = os.path.join('result', 'frame11.flo')
sio.savemat(res_path, {'flow': flow_mat})