import os

from rich.console import Console
from rich.table import Table

console = Console()


def trans(s,secret):
    """
    将智慧树各个域名的cookies统一传递
    :param s: session.requests
    :param secret: 用户secret信息
    :return:
    """
    url = 'http://studyservice.zhihuishu.com/login/gologin?fromurl=https://studyh5.zhihuishu.com/videoStudy.html#/studyVideo?recruitAndCourseId='+secret
    s.get(url)
    url = 'https://studyh5.zhihuishu.com/videoStudy.html'
    s.get(url)
    url = 'https://studyservice.zhihuishu.com/login/gologin?fromurl='\
    'https://studyh5.zhihuishu.com/videoStudy.html#/studyVideo?recruitAndCourseId='+secret
    s.get(url)
    url = 'http://passport.zhihuishu.com/?service='\
          'http%3A%2F%2Fstudyservice.zhihuishu.com%2Flogin%2Fgologin%3Ffromurl%3Dhttps%253A%252F%252Fstudyh5.zhihuishu.com%252FvideoStudy.html%2523%252FstudyVideo%253FrecruitAndCourseId%253D' + secret
    s.get(url)
    url = 'https://passport.zhihuishu.com/login?service='\
    'http%3A%2F%2Fstudyservice.zhihuishu.com%2Flogin%2Fgologin%3Ffromurl%3Dhttps%253A%252F%252Fstudyh5.zhihuishu.com%252FvideoStudy.html%2523%252FstudyVideo%253FrecruitAndCourseId%253D' + secret
    s.get(url)
    url = 'http://studyservice.zhihuishu.com/login/gologin?fromurl='\
    'https%3A%2F%2Fstudyh5.zhihuishu.com%2FvideoStudy.html%23%2FstudyVideo%3FrecruitAndCourseId%3D' + secret
    s.get(url)
    console.log("Cookies数据[yellow]传递完毕[/yellow]")






def show_course(s,detail,usernm):
    """
    交互用户选择要查询的共享课
    :param s: requests.session
    :param detail: 共享课列表
    :param usernm: 用户名
    :return:
    """
    dirs = os.listdir("saves/{}".format(usernm))
    dirs.remove('courseinfo.json')
    dirs.remove('userinfo.json')

    console.log("开始显示用户的所有[yellow]共享课内容[/yellow]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", style="dim")
    table.add_column("课程名")
    table.add_column("老师")
    table.add_column("正在学习")
    table.add_column("学习进度")
    table.add_column("开始时间")
    table.add_column("结束时间")
    table.add_column("存在记录")


    for data in detail:
        exist = '不存在'
        if data['courseid'] in dirs:
            exist = '存在'
        table.add_row(str(detail.index(data) + 1), str(data['coursenm']), str(data['teachernm']),
                      str(data['ongoingnum']) + str(data['ongoing']), str(data['progress']), str(data['starttime']),
                      str(data['endtime']),str(exist))
    console.rule("共享课列表", align="center")
    console.print(table)
    num = console.input('请输入您要查询的课程序号')
    try:
        match = detail[int(num) - 1]
    except Exception as e:
        console.log("出现未知错误，错误内容:{};错误类型:{}".format(e, e.__class__))
        console.input('请按回车键退出程序')
        exit()

    trans(s,match['secret'])
    console.log("开始读取[yellow]课程信息[/yellow]:'{}'".format(match['coursenm']))
    return match
