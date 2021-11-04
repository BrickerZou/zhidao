import json
import os
import time
from os.path import exists
from os import mkdir
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
# import requests
import requests.utils


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/94.0.4606.81 Safari/537.36',
}

console = Console()


def get_server_time():
    """
    智慧树发送请求服务器的时间和正常时间存在差异，所以每次发送请求需要计算一遍对应的时间
    :return:日期格式的字符串(2021-10-16T13:25:20.000Z)
    """
    tsp = time.time() - 28800
    timeArray = time.localtime(tsp)
    date = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", timeArray)
    return date


def user_folder(usernm):
    """
    检查用户记录文件夹是否存在
    :param usernm: 用户账号
    :return:
    """
    if not exists('saves'):
        console.log('不存在文件夹，正在新建[yellow]"saves"[/yellow]')
        mkdir('saves')
    if not exists('saves/{}'.format(usernm)):
        console.log('不存在文件夹，正在新建[yellow]"saves/{}"[/yellow]'.format(usernm))
        mkdir('saves/{}'.format(usernm))


def get_ticker(s):
    """
     获取本次session在智慧树服务器分配的Ticker
    :param s: requests.session
    :return: Ticker
    """
    console.log('正在尝试获取当前Session的[yellow]Ticker[/yellow]')
    url = 'https://passport.zhihuishu.com/login?service=https://onlineservice.zhihuishu.com/login/gologin'
    resp = s.get(url,headers=headers)
    # print(resp.text)
    soup = BeautifulSoup(resp.text,'lxml')
    # lt = soup.find(name="lt").attrs['value']
    lt = soup.find("input",attrs={'name': "lt"}).attrs['value']
    console.log('获取成功,当前Session的Ticker为[yellow]{}[/yellow]'.format(lt))
    return lt


def validate(s,usernm,passwd):
    """
    通过智慧树的验证api验证用户的账号密码是否正确
    :param s:requests.session
    :param usernm:用户名
    :param passwd:密码
    :return:
    """
    console.log('正在尝试验证[yellow]账号与密码[/yellow]')
    url = 'https://passport.zhihuishu.com/user/validateAccountAndPassword'
    data = {
        'account':str(usernm),
        'password':str(passwd),
    }
    resp = s.post(url,data=data)
    # resp = s.post(url,headers=headers,data=data)
    # try:
    msg = resp.json()
    # print(msg)
    if msg['status'] == -2:
        console.log('[red]账号或密码错误[/red]，请检查后重新输入\n您已输入错误[red]{}[/red]次'.format(msg['pwdErrorCount']))
        console.input('点击回车键退出程序')
        exit()
    elif msg['status'] == 1:
        console.log('[yellow]登录成功[/yellow]')
        user_folder(usernm)
        info = {
            'pwd':msg['pwd'],
            'uuid':msg['uuid'],
            'login_un':usernm,
            'login_pw':passwd,
        }
        # print(info)
        console.log('正在保存用户的[yellow]个人信息[/yellow]')
        with open('saves/{}/userinfo.json'.format(usernm),'w') as f:
            json.dump(info,f)
        console.log('userinfo.json文件[yellow]写入成功[/yellow]')
        return info
    elif msg['status'] == -4:
        console.log('[red]多次输入错误密码[/red]，请在浏览器重新输入验证成功后再返回')
        console.input('点击回车键退出程序')
        exit()
    else:
        console.log('未知状态码')
        console.log(msg)
        console.input('点击回车键退出程序')
        exit()
    # except Exception as e:
    #     console.log('出现未知错误，错误{}\n类型{}'.format(e,e.__class__))
    #     console.input('点击回车键退出程序')
    #     exit()


def need_auth(s, uuid):
    """
    检查是否需要验证登录，大多数需要验证的情况都源于异地登陆
    :param s: requests.session
    :param uuid: 用户在智慧树对应的唯一uuid
    :return:
    """
    url = 'https://appcomm-user.zhihuishu.com/app-commserv-user/userInfo/checkNeedAuth'
    data = {
        'uuid':uuid
    }
    # resp = s.post(url,headers=headers,data=data)
    resp = s.post(url,data=data)
    msg = resp.json()
    if msg['msg'] == '请求成功' and msg['rt']['needAuth'] == 0:
        console.log('登录请求[yellow]发送成功[/yellow]，无需验证')
    else:
        console.log('发现[red]异地登录问题[/red]，请在网页端自行登录后再试')
        console.input('点击回车键退出程序')
        exit()



def do_login(s,usernm,passwd,lt):
    """
    在本次Session中发出登录请求
    :param s: requests.session
    :param usernm: 用户名
    :param passwd: 密码
    :param lt: Ticker
    :return:
    """
    console.log('开始[yellow]尝试登录[/yellow]')
    url = 'https://passport.zhihuishu.com/login'
    data = {'lt': lt,
            'execution': 'e1s1',
            '_eventId': 'submit',
            'username': usernm,
            'password': passwd,
            'clCode': '',
            'clPassword': '',
            'tlCode': '',
            'tlPassword': '',
            'remember': 'on', }
    resp = s.post(url,data=data)
    # resp = s.post(url,headers=headers,data=data)

    soup = BeautifulSoup(resp.content.decode('utf8'),'lxml')

    if soup.title.string != '智慧树在线教育_全球大型的学分课程运营服务平台':
        console.log('[yellow]登录成功[/yellow]')
        # print(resp.text)
    else:
        print(resp.content.decode('utf8'))
        console.log('[red]出现问题[/red]\n请在GITHUB页面发起ISSUE')
        console.input('点击回车键退出程序')
        exit()


def get_login_userinfo(usernm,s):
    """
    获取已登录用户的信息数据并写入本地文件
    :param usernm: 用户名
    :param s: requests.session
    :return:
    """
    console.log('正在获取登录用户的[yellow]个人信息[/yellow]')
    url = 'https://onlineservice.zhihuishu.com/login/getLoginUserInfo'
    # resp = s.get(url,headers=headers)
    resp = s.get(url)
    # print(resp.text)
    msg = resp.json()['result']
    console.log('获取成功，正在写入文件')
    with open('saves/{}/userinfo.json'.format(usernm),'r') as f:
        userinfo = json.loads(f.read())
    userinfo['name'] = msg['realName']
    userinfo['usernm'] = msg['username']
    with open('saves/{}/userinfo.json'.format(usernm), 'w') as f:
        json.dump(userinfo,f)
    console.log('当前登录用户：[yellow]{}[/yellow]'.format(userinfo['name']))


def get_share_course(s,uuid,usernm):
    """
    获取登录用户所有的共享课课程列表
    :param s: requests.session
    :param uuid: 用户在智慧树的唯一用户uuid
    :param usernm: 用户名
    :return: 共享课列表
    """
    console.log('开始获取[yellow]共享课课程列表[/yellow]')
    sharecourse_info = []
    page = 1
    url = 'https://onlineservice.zhihuishu.com/student/course/share/queryShareCourseInfo'
    while True:
        data = {'status': '0',
                'pageNo': page,
                'pageSize': '10',
                'uuid': uuid,
                'date': get_server_time(), }
        resp = s.post(url,data=data)
        # resp = s.post(url,headers=headers,data=data)
        r = resp.json()['result']
        if r['totalCount'] != 0:
            courses_raw = r['courseOpenDtos']
            for course in courses_raw:
                course_dic = {}
                course_dic['courseid'] = course['courseId'] # 1000006414
                course_dic['coursenm'] = course['courseName'] # 可再生能源与低碳社会
                course_dic['teachernm'] = course['teacherName'] # 肖立新
                course_dic['ongoing'] = course['lessonName'] # 低碳及实现低碳社会的承诺
                course_dic['ongoingnum'] = course['lessonNum']  # 1.3
                course_dic['progress'] = course['progress']  # 3.6%
                course_dic['recruitid'] = course['recruitId'] 
                course_dic['secret'] = course['secret'] 
                course_dic['starttime'] = course['courseStartTime'] 
                course_dic['endtime'] = course['courseEndTime'] 
                sharecourse_info.append(course_dic)
        else:
            break
        page += 1
    console.log('获取完毕，正在[yellow]写入本地文件[/yellow]')
    with open('saves/{}/courseinfo.json'.format(usernm),'w') as f:
        json.dump(sharecourse_info,f)
    console.log('[yellow]写入成功[/yellow]')
    return sharecourse_info


def get_school(s,uuid,usernm):
    """
    获取用户的学校id以及学校名字
    :param s: requests.session
    :param uuid: 用户在智慧树的唯一用户uuid
    :param usernm: 用户名
    :return: 用户学校id,学校名字
    """
    url = 'https://onlineservice.zhihuishu.com/student/home/index/getCertificateInfo?uuid='+str(uuid)+'&date='+get_server_time()
    resp = s.get(url)
    # resp = s.get(url,headers=headers)
    schoolid = resp.json()['result']['schoolId']
    url2 = 'https://onlineservice.zhihuishu.com/student/home/index/background?schoolId='+str(schoolid)+'&uuid='+str(uuid)+'&date='+get_server_time()
    resp = s.get(url2)
    # resp = s.get(url2,headers=headers)
    schoolnm = resp.json()['result']['schoolName']
    with open('saves/{}/userinfo.json'.format(usernm),'r') as f:
        userinfo = json.loads(f.read())
    userinfo['schoolid'] = schoolid
    userinfo['schoolnm'] = schoolnm
    with open('saves/{}/userinfo.json'.format(usernm), 'w') as f:
        json.dump(userinfo,f)
    return schoolid, schoolnm


def get_local_user(s,lt):
    """
    交互获取用户要登录的用户名和密码
    :param s: requests.session
    :param lt: Ticker
    :return: usernm, info, uuid, schoolid, schoolnm, sharecourses
    """
    dirs = os.listdir('saves')
    console.log("正在读取本地[yellow]已存在用户[/yellow]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", style="dim")
    table.add_column("手机号")
    table.add_column("姓名")
    table.add_column("学校名")
    for dir in dirs:
        with open('saves/{}/userinfo.json'.format(dir),'r') as f:
            userinfo = json.loads(f.read())
        table.add_row(str(dirs.index(dir) + 1), str(userinfo['login_un']), str(userinfo['name']), str(userinfo['schoolnm']))
    console.rule("本地用户列表", align="center")
    console.print(table)
    num = console.input("请输入你要登录的用户序号，添加请输0")
    if int(num) == 0:
        usernm, passwd = get_unpw()
    elif int(num) <= len(dirs):
        with open('saves/{}/userinfo.json'.format(dirs[int(num)-1]),'r') as f:
            userinfo = json.loads(f.read())
        usernm = userinfo['login_un']
        passwd = userinfo['login_pw']
    else:
        console.log("您的输入有误")
        console.input("点击回车键退出程序")
        exit()
    return get_online_user(s, lt, usernm, passwd)


def get_unpw():
    """
    用户输入账号密码
    :return:
    """
    usernm = console.input('请输入账号')
    passwd = console.input('请输入密码')
    return usernm,passwd

def get_online_user(s,lt,usernm,passwd):
    """
    调用智慧树接口获取所有需要的信息并存至本地文件
    :param s: requests.session
    :param lt: Ticker
    :param usernm: 用户名
    :param passwd: 密码
    :return:
    """
    info = validate(s,usernm,passwd)
    uuid = info['uuid']
    need_auth(s,uuid)
    do_login(s,usernm,passwd,lt)
    get_login_userinfo(usernm,s)
    schoolid, schoolnm = get_school(s,uuid,usernm)
    sharecourses = get_share_course(s,uuid,usernm)
    return usernm, info, uuid, schoolid, schoolnm, sharecourses

def login_main(s):
    if not os.path.exists('saves'):
        mkdir('saves')
    lt = get_ticker(s)
    return get_local_user(s,lt)
