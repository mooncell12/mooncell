from entity import organizations as o
from util import public_tools as tool
from util import io_tools as io
import datetime
import calendar
import re

def load_emp_data():
    '''
    加载数据
    :return:
    '''
    io.checking_data_files()#文件自检
    io.load_users()#加载管理员账号
    io.load_lock_record()#加载打卡记录
    io.load_employee_info()#加载员工信息
    io.load_employee_pic()#加载员工照片
#添加新员工
def add_new_employee(name):
    '''
    :param name: 员工名称
    :return: 员工特征码
    '''
    code = tool.randomCode()#生成随机特征码
    newEmp = o.Employee(o.get_new_id(), name,code)#创建员工对象
    o.add(newEmp)#组织结构中添加新员工
    io.save_employee_all()#保存最新的员工信息
    return code#返回新员工特征码
#删除员工
def remove_employee(id):
    '''
    :param id: 员工id
    :return:
    '''
    io.remove_pics(id) #删除员工照片
    o.remove(id)#从组织结构中删除
    o.empty_list.append(id)#id加入列表重复使用
    io.save_employee_all()#保存新的员工记录
    io.save_lock_record()#保存新的打卡信息
#为指定员工添加打卡记录
def add_lock_record(name):
    '''
    :param name: 员工名称
    :return:
    '''
    record = o.LOCK_RECORD  # 所有打卡记录（全局字典）
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 当前时间
    punch_list = o.LOCK_RECORD.get(name, [])  # 该用户的打卡记录列表
    today_punch_count = 0
    # 统计今日打卡次数
    for record_time_str in punch_list:
        record_time = datetime.datetime.strptime(record_time_str, "%Y-%m-%d %H:%M:%S")
        if record_time.date() == datetime.datetime.now().date():  # 比较日期
            today_punch_count += 1
    if today_punch_count >= 2:
        print(name + "打卡已达两次，打卡失败！")
    else:
        if name in o.LOCK_RECORD.keys():  # 检查全局字典是否有该用户
            r_list = o.LOCK_RECORD[name]  # 获取该用户的打卡记录
            if len(r_list)==0:
                r_list = list()
            r_list.append(now_time)  # 添加当前打卡时间
        else:  # 用户第一次打卡
            r_list = list()
            r_list.append(now_time)  # 添加当前打卡时间
            o.LOCK_RECORD[name] = r_list  # 存入全局字典
        print(name + "打卡成功！")
        io.save_lock_record()  # 保存所有打卡记录


#所有员工信息报表
def get_employee_report():
    '''
    :return: str格式的员工信息报表
    '''
    report = "###############################\n"
    report += "员工名单如下：\n"
    i = 0 #换行计数器
    for emp in o.EMPLOYEES: #遍历所有员工
        report += "("+ str(emp.id)+")"+ emp.name + "\t"
        i += 1
        if i ==4: #四个换一行
            report +="\n"
            i = 0
    report = report.strip() #清除可能的多余换行符
    report += "\n##############################"
    return report
#检查id是否存在
def check_id(id):
    '''
    :param id: 员工id
    :return: 员工是否存在
    '''
    for emp in o.EMPLOYEES: #遍历
        if str(id) == str(emp.id): #存在对等
            return True
    return False
#通过特征码获取员工姓名
def get_name_with_code(code):
    '''

    :param code: 员工特征码
    :return: 对应员工名称
    '''
    for emp in o.EMPLOYEES: #遍历
        if str(code) == str(emp.code): #存在对等
            return emp.name #返回对应名称
#通过id获取员工特征码
def get_code_with_id(id):
    '''

    :param id: 员工id
    :return: 对应员工特征码
    '''
    for emp in o.EMPLOYEES:#遍历
        if str(id) == str(emp.id):#存在对等
            return emp.code#返回特征码

def valid_user(username,password):
    '''
    #验证管理员账号密码
    :param username: 管理员账号
    :param password: 管理员密码
    :return: 管理员登录状态
    '''
    if username in o.USERS.keys():#遍历
        if o.USERS.get(username) == password:#存在对等
            return True #标记管理员状态上线
    return False #标记失败
#保存上下班时间
def save_work_time(work_time,close_time):
    '''
    #保存上下班时间
    :param work_time: 登记上班时间
    :param close_time: 登记下班时间
    :return:
    '''
    o.WORK_TIME = work_time
    o.CLOSING_TIME = close_time
    io.save_work_time_config() #上下班时间保存到文件中

def get_record_all():
    '''
    #输出打卡记录
    :return: str格式的打卡记录
    '''
    with open(io.RECORD_FILE, "r", encoding="utf-8") as file:
        records = []
        for line in file:
            line = line.strip()  # 去除换行符和空格
            if not line:  # 跳过空行
                continue
            parts = line.split(",")  # 分割姓名和打卡时间
            name = parts[0].strip()
            punch_times = [t.strip() for t in parts[1:] if t.strip()]  # 过滤空时间
            # 格式化为 "姓名:\n  时间1\n  时间2\n..."
            formatted_record = f"{name}:\n" + "\n".join(f"  {time}" for time in punch_times)
            records.append(formatted_record)
        return "\n".join(records)  # 用换行符连接所有记录

# 打印指定日期的打卡日报
def get_day_report(date):
    '''
    打印指定日期的打卡日报
    :param date:
    :return:
    '''
    io.load_work_time_config()
    #当天0点
    earliest_time = datetime.datetime.strptime(date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    #当天中午12点
    noon_time = datetime.datetime.strptime(date + " 12:00:00", "%Y-%m-%d %H:%M:%S")
    #今晚0点之前
    latest_time = datetime.datetime.strptime(date + " 23:59:59", "%Y-%m-%d %H:%M:%S")
    #上班时间
    work_time = datetime.datetime.strptime(date + " " + o.WORK_TIME, "%Y-%m-%d %H:%M:%S")
    closing_time = datetime.datetime.strptime(date + " " + o.CLOSING_TIME, "%Y-%m-%d %H:%M:%S")#上班时间
    late_list = []#迟到名单
    left_early = []#早退名单
    absent_list = []#缺席名单
    for emp in o.EMPLOYEES:#遍历所有员工
        if emp.name in o.LOCK_RECORD.keys():#如果该员工有打卡记录
            emp_lock_list = o.LOCK_RECORD.get(emp.name)#获取该员工的打卡记录
            today_locks = []
            for lock_time_str in emp_lock_list:
                if lock_time_str.startswith(date):  # 直接匹配日期部分
                    today_locks.append(datetime.datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S"))
            today_locks.sort()  # 按时间排序
            is_absent = True#缺席状态
            for lock_time_str in emp_lock_list:
                lock_time = datetime.datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")#打卡记录转为日期格式
                if today_locks:#如果当天有打卡记录
                    is_absent = False#不缺席
                    if today_locks[0] > work_time:#上班时间后，中午之前打卡
                        late_list.append(emp.name)#加入迟到名单
                    if today_locks[-1] < closing_time:#中午之后、下班时间之前打卡
                        left_early.append(emp.name)#加入早退名单
            if is_absent:#如果仍然是缺席状态
                absent_list.append(emp.name)#加入缺席名单
        else:#该员工没有打卡记录
            absent_list.append(emp.name)#加入缺席名单
    emp_count = len(o.EMPLOYEES)#员工总人数
    print("--------" + date + "--------")
    print("应到人数：" + str(emp_count))
    print("缺席人数：" + str(len(absent_list)))
    absent_name = ""#缺席名单
    if len(absent_list) == 0:#如果没有缺席的
        absent_name = "（空）"
    else:#有缺席的
        for name in absent_list:#遍历缺席列表
            absent_name += name + " "#拼接名字
    print("缺席名单：" + absent_name)
    print("迟到人数：" + str(len(set(late_list))))
    late_name = ""#迟到名单
    if len(set(late_list)) == 0:#如果没有迟到的
        late_name = "（空）"
    else:#有迟到的
        for name in set(late_list):#遍历迟到列表
            late_name += name + " "#拼接名字
    print("迟到名单：" + str(late_name))
    print("早退人数：" + str(len(set(left_early))))
    early_name = ""#早退名单
    if len(set(left_early)) == 0:#如果没有早退的
        early_name = "（空）"
    else:#有迟到的
        for name in set(left_early):#遍历早退列表
            early_name += name + " "#拼接名字
    print("早退名单：" + early_name)


def get_today_report():
    '''
    打印当天报表
    :return:
    '''
    date = datetime.datetime.now().strftime("%Y-%m-%d")    # 当天的日期
    get_day_report(str(date)) #打印当日报表


# 创建指定月份的打卡记录月报
def get_month_report(month):
    '''
    创建指定月份的打卡记录月报
    :param month:
    :return:
    '''
    io.load_work_time_config()#上下班时间
    date = datetime.datetime.strptime(month, "%Y-%m")#月份转为时间对象
    monthRange = calendar.monthrange(date.year, date.month)[1]#天数
    month_first_day = datetime.date(date.year, date.month, 1)#第一天
    month_last_day = datetime.date(date.year, date.month, monthRange)#最后一天

    clock_in = "I"#正常上班
    clock_out = "O"#正常下班
    late = "L"#迟到
    left_early = "E"#早退
    absent = "A"#缺席

    lock_report = dict()

    for emp in o.EMPLOYEES:
        emp_lock_data = []
        if emp.name in o.LOCK_RECORD.keys():
            emp_lock_list = o.LOCK_RECORD.get(emp.name)
            index_day = month_first_day
            while index_day <= month_last_day:
                is_absent = True
                earlist_time = datetime.datetime.strptime(str(index_day) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                noon_time = datetime.datetime.strptime(str(index_day) + " 12:00:00", "%Y-%m-%d %H:%M:%S")
                latest_time = datetime.datetime.strptime(str(index_day) + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                work_time = datetime.datetime.strptime(str(index_day) + " " + o.WORK_TIME, "%Y-%m-%d %H:%M:%S")
                closing_time = datetime.datetime.strptime(str(index_day) + " " + o.CLOSING_TIME, "%Y-%m-%d %H:%M:%S")
                emp_today_data = ""

                for lock_time_str in emp_lock_list:
                    lock_time = datetime.datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
                    #如果当前日期有打卡记录
                    if earlist_time < lock_time < latest_time:
                        is_absent = False
                        if lock_time <=work_time:
                            emp_today_data += clock_in
                        elif lock_time >= closing_time:
                            emp_today_data += clock_out
                        #上班时间后、中午之前打卡
                        elif work_time < lock_time <= noon_time:
                            emp_today_data += late
                        #中午之后、下班之前打卡
                        elif noon_time < lock_time < closing_time:
                            emp_today_data += left_early
                    if is_absent:#如果缺席
                        emp_today_data = absent
                    emp_lock_data.append(emp_today_data)
                    index_day = index_day + datetime.timedelta(days=1)
        else:
            index_day = month_first_day
            while index_day <= month_last_day:
                emp_lock_data.append(absent)
                index_day = index_day + datetime.timedelta(days=1)
        lock_report[emp.name] = emp_lock_data

    report = "\"姓名/日期\""
    index_day = month_first_day
    while index_day <= month_last_day:
        report += ",\"" + str(index_day) + "\""
        index_day = index_day + datetime.timedelta(days=1)
    report += "\n"

    for emp in lock_report.keys():
        report += "\"" + emp + "\""
        data_list = lock_report.get(emp)
        for data in data_list:
            text = ""
            if absent == data:
                text = "【缺席】"
            elif clock_in in data and clock_out in data:
                text = ""
            else:
                if late in data and clock_out in data:
                    text += "【迟到】"
                if left_early in data and clock_out not in data:
                    text += "【早退】"
                if clock_out not in data and left_early not in data:
                    text += "【下班未打卡】"
                if clock_in not in data and late not in data:
                    text += "【上班未打卡】"
            report += "\"" + text + "\""
        report += "\n"
    #csv文件标题日期
    title_date = month_first_day.strftime("%Y{y}%m{m}").format(y="年", m="月")
    file_name = title_date + "考勤月报"
    io.create_CSV(file_name, report)
# 创建上个月打卡记录月报
def get_pre_month_report():
    '''
    创建上个月打卡记录月报
    :return:
    '''
    today = datetime.datetime.today()
    pre_month_first_day = datetime.date(today.year, today.month -1, 1)
    pre_month = pre_month_first_day.strftime("%Y-%m")
    get_month_report(pre_month)

def save_users(users):
    '''
    保存管理员信息
    :param users: 管理员名称
    :return:
    '''
    with open(io.USER_PASSWORD, "w", encoding="utf-8") as f:#打开文件 写入
        for username, password in users.items():
            f.write(f"{username}:{password}\n")

def add_user(username):
    '''
    添加管理员
    :param username: 管理员名称
    :return:
    '''
    if username in o.USERS:#判断不存在同名管理
        print(f"用户 '{username}' 已存在！")
        return
    password = input("请输入管理员密码:")
    o.USERS[username] = password #添加管理员
    save_users(o.USERS)#保存