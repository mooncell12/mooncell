import cv2
from util import public_tools as tool
from util import io_tools as io
from service import recognize_service as rs
from service import hr_service as hr

ESC_KEY=27
ENTER_KEY=13

def register(code):
    '''
    打开摄像头进行登记
    :param code: 员工特征码
    :return:
    '''
    cameraCapture = cv2.VideoCapture(0,cv2.CAP_DSHOW) #获得默认摄像头
    success, frame = cameraCapture.read()#读取一帧
    shooting_time =0#拍摄次数
    while success:#有效
        cv2.imshow("register",frame)#展示当前画面
        success, frame = cameraCapture.read()#再读一帧
        key = cv2.waitKey(1)#记录按键
        if key == ESC_KEY:#是ESC
            break#结束
        if key == ENTER_KEY:#是ENTER
            photo = cv2.resize(frame, (io.IMG_WIDTH, io.IMG_HEIGHT))#当前帧缩放为统一大小
            img_name = io.PIC_PATH + str(code) + str(tool.randomNumber(8)) + ".png"#拼接照片名 文件夹 特征码 随机数字
            cv2.imwrite(img_name, photo)#保存
            shooting_time += 1#拍摄次数+1
            if shooting_time == 3:#三张
                break#结束
    cv2.destroyAllWindows()#释放窗体
    cameraCapture.release()#释放摄像头
    io.load_employee_pic()#载入员工照片

def clock_in():
    '''
    打开摄像头进行打卡
    :return:
    '''
    cameraCapture = cv2.VideoCapture(0, cv2.CAP_DSHOW)#获得默认摄像头
    success, frame = cameraCapture.read()#读取一帧
    while success and cv2.waitKey(1) ==-1:#有效
        cv2.imshow("check in", frame)#展示当前画面
        gary = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#彩色图片转换为灰度图片
        if rs.found_face(gary):#出现正面人脸
            gary = cv2.resize(gary,(io.IMG_WIDTH, io.IMG_HEIGHT))#当前帧缩放为统一大小
            code = rs.recognise_face(gary)#识别
            if code!=-1:#如果识别成功
                name = hr.get_name_with_code(code)#返回特征码对应员工名称
                if name != None:#非空
                    cv2.destroyAllWindows()#释放窗体
                    cameraCapture.release()#释放摄像头
                    return name
        success, frame = cameraCapture.read()
    cv2.destroyAllWindows()#释放窗体
    cameraCapture.release()#释放摄像头