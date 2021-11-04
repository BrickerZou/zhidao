import src.user.login as login
import src.course.show as show
import src.video.load as load
import src.video.watch as watch
import schedule
import requests
import time
import  datetime
from rich.console import Console

console = Console()


# if __name__ == '__main__':
def job():
    s = requests.session()
    usernm, info, uuid, schoolid, schoolnm, sharecourses = login.login_main(s)
    match = show.show_course(s, sharecourses, usernm)
    all_videos, lessons, finished = load.load_all(s, match['secret'], uuid, match['recruitid'], usernm)
    watch.watch_all(s, all_videos, lessons, match['courseid'], match['recruitid'], uuid, finished, match['secret'])
    console.print("此次观看结束 -{}".format(datetime.date.today()))


schedule.every().day.at('07:00').do(job)  # 定时七点执行任务。
while True:
    schedule.run_pending()
    time.sleep(1)  # 检查部署的情况，如果任务准备就绪，就开始执行任务。
