#!/usr/bin/python3

import sys
import ctypes

libgcc_s = ctypes.CDLL('libgcc_s.so.1')

print(sys.version)

import cv2

import rospy
import numpy as np
from std_msgs.msg import String, Float32, Bool, Int16MultiArray, Int16
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import PoseStamped, Pose, PoseArray, PointStamped, TransformStamped, Quaternion
from sensor_msgs.msg import JointState
from message_filters import ApproximateTimeSynchronizer
from message_filters import Subscriber as ATS_Subscriber
import time
import threading

import roslib
# roslib.load_manifest('learning_tf')
import math
# import tf
import geometry_msgs.msg
import transforms3d
import copy

import pdb

import tf


class DisplayBaxterTrajectory():

    def __init__(self):

        rospy.on_shutdown(self.shutdown)
        rospy.init_node('display_baxter_trajectory_node', anonymous=True)
        rospy.loginfo("This node is going to display the baxter's trajectory")

        self.left_arm_pub = rospy.Publisher('/baxter_display_traj/joint_state_command', JointState, queue_size=1)

        self.left_arm_msg = JointState()
        self.left_arm_msg.header.frame_id = "base"
        self.left_arm_msg.name = [
            "head_pan", "right_s0", "right_s1", "right_e0", "right_e1", "right_w0", "right_w1", "right_w2", "left_s0", "left_s1", \
                                    "left_e0", "left_e1", "left_w0", "left_w1", "left_w2", "l_gripper_l_finger_joint", "l_gripper_r_finger_joint", \
                                    "r_gripper_l_finger_joint", "r_gripper_r_finger_joint"
        ]  # Joint name (array assignment)
        self.left_arm_msg.position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.left_arm_msg.velocity = []
        self.left_arm_msg.effort = []

        self.left_arm_traj_npy = np.load('/home/fei/baxter_ros_ws/src/display_baxter_trajectory/data/baxter_wobbler/gt_joint.npy')
        self.cam2baxter_traj_npy = np.load('/home/fei/baxter_ros_ws/src/display_baxter_trajectory/data/baxter_wobbler/camera_pose.npy')

        self.tf_br_camera2baxter = tf.TransformBroadcaster()

        # init_cam_mat_x90z90 = np.matmul(self.doRotation3DInputAngle(np.pi / 2, 0), self.doRotation3DInputAngle(np.pi / 2, 2))
        # self.init_cam_mat = init_cam_mat_x90z90.copy()
        # self.init_cam_mat[:, -1] = -1 * init_cam_mat_x90z90[:, -1]

        # pdb.set_trace()

    def publishJointStates(self, frame_id):
        # Construct message & publish joint states

        self.left_arm_msg.position[8:15] = self.left_arm_traj_npy[frame_id, :]

        print(self.left_arm_msg.position, '\n')

        self.left_arm_msg.header.stamp = rospy.Time.now()
        self.left_arm_pub.publish(self.left_arm_msg)

    def broadTFCameraToBaxterBase(self, frame_id):

        self.tf_br_camera2baxter.sendTransform(
            (self.cam2baxter_traj_npy[frame_id, 0], self.cam2baxter_traj_npy[frame_id, 1], self.cam2baxter_traj_npy[frame_id, 2]),
            (self.cam2baxter_traj_npy[frame_id, 3], self.cam2baxter_traj_npy[frame_id, 4], self.cam2baxter_traj_npy[frame_id, 5], self.cam2baxter_traj_npy[frame_id, 6]), rospy.Time.now(),
            'opencv_camera_base', 'left_arm_mount')

        # self.cam2baxter_tvec = self.cam2baxter_traj_npy[frame_id, 0:3]

        # cam2baxter_quat = self.cam2baxter_traj_npy[frame_id, 3:7]
        # cam2baxter_mat = self.getInputRotationMat(cam2baxter_quat)

        # self.init_cam_mat = np.array([[0.0000000, -0.0000000, 1.0000000], [1.0000000, 0.0000000, -0.0000000], [0.0000000, 1.0000000, 0.0000000]])
        # rotated_cam2baxter_mat = np.matmul(cam2baxter_mat, self.init_cam_mat)

        # rotated_cam2baxter_mat_H = np.vstack((np.hstack((rotated_cam2baxter_mat, np.array([[0], [0], [0]]))), np.array([0, 0, 0, 1])))
        # rotated_cam2baxter_quat = tf.transformations.quaternion_from_matrix(rotated_cam2baxter_mat_H)

        # self.tf_br_camera2baxter.sendTransform((self.cam2baxter_traj_npy[frame_id, 0], self.cam2baxter_traj_npy[frame_id, 1], self.cam2baxter_traj_npy[frame_id, 2]), list(rotated_cam2baxter_quat),
        #                                        rospy.Time.now(), 'camera_base', 'left_arm_mount')

        # (alpha, beta, gammaa) = tf.transformations.euler_from_quaternion(cam2baxter_quat)
        # rotated_cam2baxter_quat = tf.transformations.quaternion_from_euler(alpha, beta, gammaa)
        # self.tf_br_camera2baxter.sendTransform((self.cam2baxter_traj_npy[frame_id, 0], self.cam2baxter_traj_npy[frame_id, 1], self.cam2baxter_traj_npy[frame_id, 2]),
        #                                        (rotated_cam2baxter_quat[0], rotated_cam2baxter_quat[1], rotated_cam2baxter_quat[2], rotated_cam2baxter_quat[3]), rospy.Time.now(), 'opencv_cam_base',
        #                                        'left_arm_mount')

        self.tf_br_camera2baxter.sendTransform((0, 0, 0), (-0.5, 0.5, 0.5, 0.5), rospy.Time.now(), 'urdf_camera_base', 'opencv_camera_base')

        # self.tf_br_camera2baxter.sendTransform((self.cam2baxter_traj_npy[frame_id, 0], self.cam2baxter_traj_npy[frame_id, 1], self.cam2baxter_traj_npy[frame_id, 2]), (0, 0, 0, 1), rospy.Time.now(),
        #                                        'camera_base', 'left_arm_mount')
        # self.tf_br_camera2baxter.sendTransform((0, 0, 0), (0, 0, 0, 1), rospy.Time.now(), 'camera_base', 'left_arm_mount')

    def getInputRotationMat(self, input_pose):
        return transforms3d.quaternions.quat2mat([input_pose[3], input_pose[0], input_pose[1], input_pose[2]])

    def doRotation3DInputAngle(self, angle, axis=0):
        # points: [N, point_size, 3]
        # return rotation matrix per axis : counter-clockwise?
        rot_sin = np.sin(angle)
        rot_cos = np.cos(angle)
        if axis == 0:
            rot_mat = np.stack([
                [1, 0, 0],
                [0, rot_cos, -rot_sin],
                [0, rot_sin, rot_cos],
            ])
        elif axis == 1:
            rot_mat = np.stack([[rot_cos, 0, rot_sin], [0, 1, 0], [-rot_sin, 0, rot_cos]])
        elif axis == 2:
            rot_mat = np.stack([[rot_cos, -rot_sin, 0], [rot_sin, rot_cos, 0], [0, 0, 1]])
        else:
            raise ValueError("axis should in range")
        return rot_mat

    def shutdown(self):
        # sys.exit()
        rospy.loginfo("Stopping ...")

    def quit(self, signum, frame):
        print('')
        print('stop program')
        sys.exit()


if __name__ == '__main__':

    demoLeftArm = DisplayBaxterTrajectory()

    print("\n\n  starting ! \n\n")
    rospy.sleep(1)

    frame_id = 0

    ## -----------------------------------------------------------------------------------
    try:
        while not rospy.is_shutdown():

            demoLeftArm.publishJointStates(frame_id)

            demoLeftArm.broadTFCameraToBaxterBase(frame_id)

            frame_id = frame_id + 1

            print("---------------- DISPLAY ", frame_id, " ^_^ FRAMES ---------------- \n")

            if frame_id >= demoLeftArm.left_arm_traj_npy.shape[0]:
                break

            rospy.sleep(1.1)

    except KeyboardInterrupt:
        print('error!')
        sys.exit()
        pass