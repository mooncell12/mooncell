import cv2
import numpy as np
import os

RECOGNIZER =cv2.face.LBPHFaceRecognizer_create()#LBPH识别器
PASS_CONF =45#最高评分
FACE_CASCADE =cv2.CascadeClassifier(os.getcwd()+"\\cascades\\haarcascade_frontalface_default.xml")#加载人脸识别级联分类器

def train(photos, lables):
    '''
    训练识别器
    :param photos: 样本图像列表
    :param lables: 标签列表
    :return:
    '''
    RECOGNIZER.train(photos, np.array(lables))#识别器开始训练

def found_face(gary_img):
    '''
    发现人脸
    :param gary_img: 测试图片
    :return: 含有人脸的图片数量
    '''
    faces = FACE_CASCADE.detectMultiScale(gary_img,1.15,4)#找出图像中的人脸
    return len(faces) >0#返回大于0的结果

def recognise_face(photo):
    '''
    识别人脸
    :param photo: 员工人脸
    :return: 对应员工特征码 或者 -1（不存在）
    '''
    label, confidence =RECOGNIZER.predict(photo)#识别器分析人脸图像
    if confidence >PASS_CONF:#忽略大于最高评分结果
        return -1;
    return label

