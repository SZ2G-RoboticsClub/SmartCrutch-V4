import base64
import logging
import re
import subprocess
import time
from datetime import datetime

import requests
import simplejson

import os

logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', level='INFO')
logger = logging.getLogger('CourseElector')

SCHOOL_ID = 'ff8081816b5ed9f5016b6961bf393919'

def get_cookies(username: str, password: str) -> requests.sessions.RequestsCookieJar:
    url = "https://www.521ke.com/sso/doStudNoAjaxLogin"
    data = {'schoId': SCHOOL_ID, 'userName': username, 'password': password}

    r = requests.post(url, data=data)

    if not r.json()['success']:
        logger.error("登录失败: " + r.json()['message'])
        os.system("pause")
        exit(1)
    else:
        logger.info("登录成功!")
        return r.cookies


def get_basic_info(cookies: requests.sessions.RequestsCookieJar):
    url = "https://www.521ke.com/electiveCourse/studentChoice"
    r = requests.get(url, cookies=cookies).text
    name = re.findall(r"<span id='stuName'>(.*?)<\/span>", r)[0]
    class_ = re.findall(r"<span id='className'>，班级：(.*?)<\/span>", r)[0]
    configId = re.findall(r'var currConfigId = "(.*?)";', r)[0]
    startTime = re.findall("""showChoicetimesHtmlInfo\("(.*?)年(.*?)月(.*?)日 (.*?)时(.*?)分",""", r)[0]

    logger.info(f"学生姓名: {name}, 班级: {class_}")
    return configId, datetime(*[int(i) for i in startTime])


def get_courses_list(cookies: requests.sessions.RequestsCookieJar, configId: str):
    url = f"https://www.521ke.com/electiveCourse/getStuCourseDefault/{configId}"
    r = requests.get(url, cookies=cookies)
    try:
        return [(i['subN'] + ' ' + i['tName'], i['subid']) for i in r.json()['optCourseSubjectlist']]
    except KeyError:
        logger.error("获取选课列表失败，请稍后重试")
        os.system("pause")
        exit(1)


def elect_course(configId: str, courseId: str, cookies: requests.sessions.RequestsCookieJar):
    url = f"https://www.521ke.com/electiveCourse/addSelCourseLockStudVer/{configId}/{courseId}/1"

    while True:
        r = requests.post(url, data={}, cookies=cookies)
        try:
            if r.status_code != 200:
                logger.warning(f"服务器响应错误! StatusCode:{r.status_code}")

            state = r.json()['success']

            if state == 'success':
                logger.info('选课成功！')
                return
            elif state == 'error0':
                logger.warning("未到选课时间！")
                time.sleep(0.3)
            elif state == 'error1':
                logger.info("选课已完成！")
                return
            elif state == 'error4':
                logger.error("选课失败: 选课人数已满")
                return
            else:
                logger.warning("其它错误: " + r.json()['success'])
                time.sleep(0.3)

        except simplejson.errors.JSONDecodeError:
            logger.error('Cookie 无效')
            return


if __name__ == '__main__':

    print("\n521ke Course Elector\n"
          "本脚本仅供编程学习交流使用，严禁用于商业用途，请于24小时内删除！\n"
          "程序使用单线程进行选课请求，不会对服务器造成影响\n"
          "@Author: DeltaZero\n"
          "@Time: 2021/02/27\n"
          "@Version: beta-0.2\n")

    # verificate()

    username = input("输入学号: ").strip()
    password = input("输入密码: ").strip()
    print('')

    cookies = get_cookies(username, password)
    configId, startTime = get_basic_info(cookies)
    courseList = get_courses_list(cookies, configId)

    print("\n选课列表:")
    for idx, (courseName, _) in enumerate(courseList):
        print(f"    [{idx + 1}] {courseName}")
    idx = int(input("\n请输入课程编号: ").strip()) - 1

    courseId = courseList[idx][1]
    logger.info(f"已选择{courseList[idx][0]}，CourseId: {courseId}")

    if startTime > datetime.now():
        waitTime = (startTime - datetime.now()).seconds - 3
    else:
        waitTime = 0

    logger.info(f"开始选课时间: {startTime.strftime('%y-%m-%d %I:%M:%S')}，将在选课开始前3s开始请求")

    while waitTime > 0:
        logger.info(f"开始选课时间: {startTime.strftime('%y-%m-%d %I:%M:%S')}, "
                    f"现在时间: {datetime.now().strftime('%y-%m-%d %I:%M:%S')}, "
                    f"将在 {waitTime}s 后开始请求，等待期间请勿关闭窗口！")
        time.sleep(min(waitTime, 120))
        waitTime -= 120

    logger.warning("开始发送选课请求...")

    elect_course(configId, courseId, cookies)
    os.system("pause")
