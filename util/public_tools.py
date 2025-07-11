import random
import datetime
from entity import organizations as o


def randomNumber(len):
    '''
    # 随机生成长度为len的数字
    :param len: 数字长度
    :return: 长度为len的数字
    '''
    first = str(random.randint(1,9))#第一位取非零数
    last = "".join(random.sample("1234567890",len-1))#0到9随意拼接
    return first + last#拼接特征码


def randomCode():
    '''
    # 随机生成和特征码长度相等的数字
    :return: 特征码长度的数字
    '''
    return randomNumber(o.CODE_LEN)


def valid_time(str):
    '''
    # 校验时间格式
    :param str: 读入的时间
    :return: 是否符合格式
    '''
    try:
        datetime.datetime.strptime(str,"%H:%M:%S")
        return True
    except:
        return False


def valid_year_month(str):
    '''
    # 校验年月格式
    :param str: 读入的时间
    :return: 是否符合格式
    '''
    try:
        datetime.datetime.strptime(str,"%Y-%m")
        return True
    except:
        return False


def valid_date(date):
    '''
    # 校验日期格式
    :param date: 读入的时间
    :return: 是否符合格式
    '''
    try:
        datetime.datetime.strptime(date,"%Y-%m-%d")
        return True
    except:
        return False