import requests
import time
from rich.console import Console

console = Console()


def get_load_studyinfo_data(recruitid, uuid, big, small):
    data = {}
    i = 0
    while i < len(big):
        data['lessonIds[{}]'.format(i)] = big[i]['id']
        i += 1
    i = 0
    while i < len(small):
        data['lessonVideoIds[{}]'.format(i)] = small[i]['id']
        i += 1
    data['recruitId'] = recruitid
    data['uuid'] = uuid
    data['dateFormate'] = str(int(time.time())) + str('000')
    return data


def load_studyinfo(s, recruitid, uuid, big, small):
    lessons = {}
    url = 'https://studyservice.zhihuishu.com/learning/queryStuyInfo'
    data = get_load_studyinfo_data(recruitid, uuid, big, small)
    resp = s.post(url, data=data)
    for i in resp.json()['data']['lesson']:
        lessons[str(i)] = resp.json()['data']['lesson'][str(i)]
    for t in resp.json()['data']['lv']:
        lessons[str(t)] = resp.json()['data']['lv'][str(t)]
    l = {}
    finished = 0
    for lesson in lessons:
        if lessons[lesson]['watchState'] != 1:
            l[lesson] = lessons[lesson]
        else:
            finished += 1
    return l, finished


def load_videolist(s, secret, uuid):
    console.log("开始获取[yellow]所有视频[/yellow]的详细信息")
    url = 'https://studyservice.zhihuishu.com/learning/videolist'
    data = {
        'recruitAndCourseId': str(secret),
        'uuid': str(uuid),
        'dateFormate': str(int(time.time())) + str('000')
    }
    resp = s.post(url, data=data)
    result = resp.json()
    return result


def process_videolist(videolist):
    console.log("开始处理获取得到的videolist")
    small_lessons = []
    big_lessons = []
    chapterdtos = videolist['data']['videoChapterDtos']  # 所有的章节
    for chapterdto in chapterdtos:
        chapterid = chapterdto['id']  # 章节id
        chapternm = chapterdto['name']  # 章节名
        videolessons = chapterdto['videoLessons']  # 所有的大lesson分类
        for videolesson in videolessons:
            if 'videoSmallLessons' in videolesson:  # 存在小lesson，当前大lesson为小章节
                lessonid = videolesson['id']
                smalllessons = videolesson['videoSmallLessons']  # 所有的小lesson
                for smalllesson in smalllessons:  # 每个小lesson
                    smalllesson['lessonid'] = lessonid
                    smalllesson['chapterid'] = chapterid
                    smalllesson['chapternm'] = chapternm
                    smalllesson['type'] = 'small'
                    small_lessons.append(smalllesson)
            else:
                videolesson['chapterid'] = chapterid
                videolesson['chapternm'] = chapternm
                videolesson['type'] = 'big'
                big_lessons.append(videolesson)
    return small_lessons, big_lessons


def load_all(s, secret, uuid, recruit, usernm):
    videolist = load_videolist(s, secret, uuid)
    small, big = process_videolist(videolist)
    lessons, finished = load_studyinfo(s, recruit, uuid, big, small)
    all_videos = []
    for i in small:
        all_videos.append(i)
    for i in big:
        all_videos.append(i)
    return all_videos, lessons, finished
