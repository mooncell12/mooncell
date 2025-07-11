LOCK_RECORD = dict() #打卡记录字典
EMPLOYEES = list()#员工列表
MAX_ID = 0#最大ID
CODE_LEN = 6#特征码长度
WORK_TIME = ""#上班时间
CLOSING_TIME = ""#下班时间
USERS = dict()#管理员账号密码
empty_list = list()#已删除未使用员工编号
#员工类
class Employee:
    def __init__(self,id,name,code):
        self.name = name#员工名称
        self.id = id#员工编号
        self.code =code#员工特征码

#加
def add(e:Employee):
    '''
    添加员工
    :param e: 员工对象
    :return:
    '''
    EMPLOYEES.append(e)
#减
def remove(id):
    '''
    删除员工
    :param id: 员工id
    :return:
    '''
    for emp in EMPLOYEES:
         if str(id) == str(emp.id):
            EMPLOYEES.remove(emp)#删员工
            if emp.name in LOCK_RECORD.keys():#存在记录
                del LOCK_RECORD[emp.name]#删记录
            break
#获取新ID
def get_new_id():
    '''
    获取新id
    :return: 不存在对应员工的id
    '''
    global MAX_ID
    # MAX_ID += 1
    # return MAX_ID
    if not empty_list:#没有未被使用的已删除员工编号
        MAX_ID += 1#最大加一
        return MAX_ID
    else:
        return empty_list.pop(0)#使用未被使用的已删除员工编号的第一个