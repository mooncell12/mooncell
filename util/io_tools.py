from service import hr_service as hr
from entity import organizations as o
from service import recognize_service as rs
import os
import cv2
import numpy as np

PATH = os.getcwd() + "\\data\\"#数据文件夹根目录
PIC_PATH=PATH+"faces\\"#照片文件夹
DATA_FILE=PATH +"employee_data.txt"#员工信息文件
WORK_TIME = PATH +"work_time.txt"#上下班时间文件
USER_PASSWORD =PATH +"user_password.txt"#管理员账号密码文件
RECORD_FILE = PATH + "lock_record.txt"#打卡记录文件
IMG_WIDTH = 640#文件宽度
IMG_HEIGHT = 480#文件高度

def checking_data_files():
    '''
     #自检 检查默认文件夹
    :return:
    '''
    if not os.path.exists(PATH): #检查存在
        os.mkdir(PATH)
        print("数据文件夹丢失,已重新创建:"+PATH)
    if not os.path.exists(PIC_PATH):
        os.mkdir(PIC_PATH)
        print("照片文件夹丢失，已重新创建:"+PIC_PATH)
    sample1 = PIC_PATH + "1000000000.png"
    #样本1文件路径
    if not os.path.exists(sample1):
        sample_img_1 = np.zeros((IMG_HEIGHT,IMG_WIDTH,3),np.uint8) #创建一个空内容图像
        sample_img_1[:,:,0] = 255 #纯蓝
        cv2.imwrite(sample1, sample_img_1)
        print("默认样本1已补充")
    sample2 = PIC_PATH + "2000000.png"
    #样本2文件路径
    if not os.path.exists(sample2):
        sample_img_2=np.zeros((IMG_HEIGHT,IMG_WIDTH,3),np.uint8) #创建一个空内容图像
        sample_img_2[:,:, 1]=255#纯绿
        cv2.imwrite(sample2, sample_img_2)
        print("默认样本2已补充")
    if not os.path.exists(DATA_FILE):
        open(DATA_FILE, "a+")#读写打开文件 达到创建空文件目的
        print("员工信息文件丢失，已重新创建："+DATA_FILE)
    if not os.path.exists(RECORD_FILE):
        open(RECORD_FILE, "a+")#读写打开文件 达到创建空文件目的
        print("打卡记录文件丢失，已重新创建:"+RECORD_FILE)
    if not os.path.exists(USER_PASSWORD):
        file = open(USER_PASSWORD, "a+", encoding="utf-8")
        user = dict()
        user["mr"]="mrsoft"
        file.write(str(user))#将默认管理员账号密码写入文件中
        file.close()#关闭文件
        print("管理员账号密码文件丢失，已重新创建："+USER_PASSWORD)
    if not os.path.exists(WORK_TIME):
        file = open(WORK_TIME, "a+",encoding="utf-8")
        file.write("09:00:00/17:00:00")#写入默认时间
        file.close()
        print( "上下班时间配置文件丢失，已重新创建：" + WORK_TIME)

def load_employee_info():
    '''
    #加载员工信息
    :return:
    '''
    max_id=1 #最大员工id
    file = open(DATA_FILE,"r", encoding="utf-8")#只读
    for line in file.readlines():#遍历文件行内容
        id, name,code = line.rstrip().split(",",2)#去除换行符，以，分割为三份
        o.add(o.Employee(id, name, code))#组织结构内添加员工信息
        if int(id) > max_id:#发现大于最大id
            max_id = int(id)#修改
    o.MAX_ID = max_id#记录
    file.close()#关闭

def load_lock_record():
    '''
    #加载打卡记录
    :return:
    '''
    with open(RECORD_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()  # 去除首尾空格和换行符
            if not line:  # 跳过空行
                continue
            parts = line.split(",")  # 按逗号分割
            if len(parts) < 2:  # 至少需要用户名 + 1个打卡时间
                print(f"⚠️ 警告：跳过无效行 -> {line}")
                continue
            name = parts[0].strip()  # 用户名
            punch_times = [t.strip() for t in parts[1:] if t.strip()]  # 过滤空时间
            o.LOCK_RECORD[name] = punch_times

def load_employee_pic():
    '''
    加载员工图像
    :return:
    '''
    photos=list()#图像列表
    lables = list()#标签列表
    pics = os.listdir(PIC_PATH)#读取所有照片
    if len(pics)!= 0:#不为空
        for file_name in pics:#遍历
            code = file_name[0:o.CODE_LEN]#截取特征码
            photos.append(cv2.imread(PIC_PATH + file_name,0))#以灰度图像的方式读取样本
            lables.append(int(code))#样本特征码作为识别标签
        rs.train(photos,lables)#训练样本
    else:#为空
        print("Error>>员工照片文件丢失，请重新启动程序并录入员工信息！")

def load_work_time_config():
    '''
    加载上下班时间数据
    :return:
    '''
    file=open(WORK_TIME,"r",encoding="utf-8")
    text= file.read().rstrip()
    times =text.split("/")
    o.WORK_TIME= times[0]
    o.CLOSING_TIME = times[1]
    file.close()

def load_users():
    '''
    加载管理员账号密码
    :return:
    '''
    try:
        with open(USER_PASSWORD, "r", encoding="utf-8") as file:#只读
            for line in file:#遍历
                line = line.strip()#去空
                if line and ":" in line:#存在：在一行
                    username, password = line.split(":", 1)#以：为标志进行分割
                    o.USERS[username.strip()] = password.strip()#存入字典
        return o.USERS
    except FileNotFoundError:
        print(f"警告: {USER_PASSWORD} 不存在，将创建空用户数据。")
        return o.USERS

def save_employee_all():
    '''
    将员工信息持久化
    :return:
    '''
    file =open(DATA_FILE,"w", encoding="utf-8")#只写
    info="";#待写入的字符串
    for emp in o.EMPLOYEES:#遍历
        info += str(emp.id)+","+str(emp.name)+","+str(emp.code) + "\n"#拼接
    file.write(info)#写入
    file.close()

def save_lock_record():
    '''
    将打卡记录持久化
    :return:
    '''
    with open(RECORD_FILE, "w", encoding="utf-8") as file:
        for name, punch_times in o.LOCK_RECORD.items():
            # 将打卡时间列表转为逗号分隔的字符串
            punch_str = ",".join(punch_times)
            # 写入文件，格式：姓名,打卡时间1,打卡时间2,...
            file.write(f"{name},{punch_str}\n")

def save_work_time_config():
    '''
    将上下班时间写到文件里
    :return:
    '''
    file =open(WORK_TIME,"w",encoding="utf-8")#只写
    times =str(o.WORK_TIME)+"/"+str(o.CLOSING_TIME)#时间
    file.write(times)#写入
    file.close()

def remove_pics(id):
    '''
    删除员工照片
    :param id: 员工id
    :return:
    '''
    pics = os.listdir(PIC_PATH)#读取照片
    code = str(hr.get_code_with_id(id))#获取特征码
    for file_name in pics:#遍历
        if file_name.startswith(code):#特征码开头
            os.remove(PIC_PATH + file_name)#删除
            print("删除照片："+ file_name)

def create_CSV(file_name, text):
    '''
    生成csv文件
    :param file_name: 文件名称
    :param text: 写入的文本内容
    :return:
    '''
    file = open(PATH + file_name + ".csv","w", encoding="gbk")#只写 覆盖
    file.write(text)#文本写入文件
    file.close()
    print("已生成文件，请注意查看：" +PATH + file_name + "csv")

