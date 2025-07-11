from util import camera
from util import public_tools as tool
from service import hr_service as hr
import pyodbc

ADMIN_LOGIN =True

def login():
    '''
    #管理员登录
    :return:
    '''
    while True:
        print("=== 管理员登录 ===")
        username = input("请输入管理员账号(输入0取消操作):")
        if username == "0":
            return
        password = input("请输入管理员密码：")
        if hr.valid_user(username.strip(),password.strip()):
            global ADMIN_LOGIN
            ADMIN_LOGIN = True
            print(username+"登录成功!请选择重新选择功能菜单")
            break
        else:
            print("“账号或密码错误，请重新输入！")
            print("-----------------------")

def start():
    '''
    启动界面
    :return:
    '''
    finish = False  #程序结束标志
    menu ="""
+--------------------------------------------------+
|                     主功能菜单                     |
+--------------------------------------------------+
  1.打卡 2.查看记录 3.员工管理 4.考勤报表 5.添加管理员 6.退出
----------------------------------------------------"""

    while not finish:
        print(menu) #打印菜单
        option = input("请输入菜单序号：")
        if option == "1": #选择打卡
            face_clock() #人脸识别
        elif option == "2": #选择查看记录
            if ADMIN_LOGIN: #检查管理员是否登录
                check_record() #查看记录
            else:
                login() #让管理员登录
        elif option == "3": #选择员工管理
            if ADMIN_LOGIN:
                employee_management() #进入员工管理界面
            else:
                login()
        elif option == "4": #选择考勤报表
            if ADMIN_LOGIN:
                check_report() #查看考勤报表
            else:
                login()
        elif option == "5": #选择添加管理员
            if ADMIN_LOGIN:  # 检查管理员是否登录
                username = input("请输入管理员账号:")
                hr.add_user(username)  # 添加管理员
            else:
                login()  # 让管理员登录
        elif option == "6":  # 选择退出
            finish = True  # 循环结束
        else:
            print("输入的指令有误，请重新输入！")
    print("Bye Bye")

def face_clock():
    '''
    启动打卡
    :return:
    '''
    print("请正面对准摄像头进行打卡")
    name = camera.clock_in() #打开摄像头 返回员工名称
    if name is not None: #员工名称存在
        hr.add_lock_record(name) #保存打卡记录

def check_record():
    '''
    启动查看记录菜单
    :return:
    '''
    menu = """
+------------------------------+
|         员工管理功能菜单        |
+------------------------------+
1.查看员工2.查看打卡记录3.返回上级菜单
+------------------------------+"""
    while True:
        print(menu) #打印菜单
        option = input("请输入菜单序号:")
        if option == "1": #选择员工列表
            print(hr.get_employee_report())
        elif option == "2": #选择查看打卡记录
            report = hr.get_record_all()
            print(report)
        elif option == "3": #返回上级菜单
            return #退出查看查看记录界面
        else:
            print("输入的指令有误，请重新输入！")


def employee_management():
    '''
    启动员工管理界面
    :return: 退出
    '''
    menu = """
+------------------------------+
|         员工管理功能菜单        |
+------------------------------+
 1.录入新员工2.删除员工3.返回上级菜单
+------------------------------+"""
    while True:
        print(menu) #打印菜单
        option = input("请输入菜单序号:")
        if option == "1": #选择录入新员工
            name = str(input("请输入新员工姓名(输入0取消操作):")).strip()
            if name != "0": #输入不为0
                code = hr.add_new_employee(name) #服务模块添加员工 并获取员工特征码
                print("请面对摄像头，按3次Enter键完成拍照!")
                camera.register(code) #打开摄像头为新员工照相
                print("录入成功!")
                # return #退出员工管理界面
        elif option == "2": #选择删除员工
            # show_employee_all() #展示所有员工
            print(hr.get_employee_report()) #打印员工列表
            id = int(input("请输入要删除的员工编号(输入0取消操作): "))
            if id > 0: #输入不为0
                if hr.check_id(id): #编号有对应员工
                    verification = tool.randomNumber(4) #生成四位随机数
                    inputVer = input("[" + str(verification) + "]请输入验证码:") #让用户输入验证码
                    if str(verification) == str(inputVer).strip(): #验证码正确
                        hr.remove_employee(id) #服务模块删除员工
                        print(str(id) + "号员工已删除！")
                    else: #验证码不正确
                        print("验证码有误，操作取消")
                else: #编号无对应员工
                    print("无此员工，操作取消")
        elif option == "3": #选择返回上级菜单
            return #退出员工管理界面
        else:
            print("输入的指令有误，请重新输入！")


def report_config():
    menu = """
+------------------------------+
|         员工管理功能菜单        |
+------------------------------+
    1.作息时间设置2.返回上级菜单
+------------------------------+"""
    while True:
            print(menu)# 打印菜单
            option = input("请输入菜单序号:")
            if option == "1":
                # 如果选择“作息时间设置”
                while True:
                    work_time = input("请设置上班时间，格式为(08:00:00):")
                    if tool.valid_time(work_time):# 如果时间格式正确
                        break# 结束循环
                    else:# 如果时间格式不对
                        print("上班时间格式错误，请重新输入")
                while True:
                    close_time = input("请设置下班时间, 格式为(23: 59:59):")
                    if tool.valid_time(close_time):# 如果时间格式正确
                        break
                    else:                    # 如果时间格式不对
                        print("下班时间格式错误，请重新输入")
                hr.save_work_time(work_time, close_time)                # 保存用户设置的上班时间和下班时间
                print("设置完成，上班时间："+ work_time+ "下班时间："+ close_time)
            elif option == "2":# 如果选择“返回上级菜单
                return # 退出查看记录功能菜单
            else:
                print("输入的指令有误，请重新输入！")


def check_report():
    '''
    打开考勤报表
    :return: 退出
    '''
    menu = """
+------------------------------+
|         员工管理功能菜单        |
+------------------------------+
 1日报 2月报 3报表设置 4返回上级菜单
+------------------------------+"""
    while True:
        print(menu) #打印菜单
        option = input("请输入菜单序号:")
        if option == "1": #选择日报
            while True:
                date = input("输入查询日期，格式为(2008-08-08)，输入0则查询今天：")
                if date == "0": #如果输入0
                    hr.get_today_report() #打印今天的日报
                    break #打印完之后结束循环
                elif tool.valid_date(date): #输入日期格式有效
                    hr.get_day_report(date) #打印对应日期日报
                    break #打印完成结束循环
                else:
                    print("日期格式有误，请重新输入")
        elif option == "2":#如果选择“月报”
            while True:
                date=input("输入查询月份,格式为(2008-08)输入0则查询上个月:")
                if date == "0":#如果只输入0
                    hr.get_pre_month_report()#生成上个月的月报
                    break# 生成完毕之后结束循环
                elif tool.valid_year_month(date):#如果输入的月份格式有效
                    hr.get_month_report(date)#生成指定月份的月报
                    break#生成完毕之后结束循环
                else:
                    print("日期格式有误，请重新输入！")
        elif option == "3": #如果选择“报表设置”
            report_config()#进入“报表设置”菜单
        elif option == "4":#如果选择“返回上级菜单”
            return #退出查看记录功能菜单
        else:
            print("输入的指令有误，请重新输入！")

hr.load_emp_data() #数据初始化
tital ="""
**************************************
            智能视频打卡系统            
**************************************
"""
print(tital) #打印标题
start() #启动程序


