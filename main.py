from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import requests

# 初始化requests.Session 用于传入selenium提供的登陆后cookie，实现接口高效率获取
s = requests.Session()

# 初始化浏览器设置
options = Options()
options.add_experimental_option("detach", True)  # 防止chorme自动退出
options.add_argument(
    "--disable-blink-features=AutomationControlled")  # 防止检测，没有这行无法登陆
wd = webdriver.Chrome(service=Service("./chromedriver"), options=options)
wd.implicitly_wait(10)  # 隐式等待：自动等待页面加载出指定元素，避免人工sleep低效率


def login(username, password):
    """通过selenium模拟登陆并获取cookie"""
    # 寻找登陆按钮
    login_element = wd.find_element(By.CLASS_NAME, "ant-btn-primary")
    login_element.click()
    # 寻找用户与密码的输入框
    account_element = wd.find_element(By.ID, "account")
    password_element = wd.find_element(By.ID, "password")
    # 键入账户密码
    account_element.clear()
    account_element.send_keys(username)
    password_element.clear()
    password_element.send_keys(password)
    # 按下登陆按钮
    login_button = wd.find_element(By.CLASS_NAME, "submit-btn")
    login_button.click()
    sleep(1)
    # 提取cookies给requests使用
    for cookie in wd.get_cookies():
        s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])


def get_courses(grade="高一"):
    """通过官方API获取课程列表"""
    resp = requests.get(
        f'https://gw.2-class.com/ws/c/content/course/homepage/list?grade={grade}&pageSize=24&pageNo=1')
    courses = resp.json()['data']
    result = []
    print(f"已获取到{courses['total']}个课程！")
    for course in courses['list']:
        print(f"课程ID: {course['courseId']} 课程标题: {course['title']}  ", end='')
        
        answer = get_answers(course['courseId'])
        if answer:
            print(f"答案：{answer}")
            result.append(course['courseId'])
        
        
        
    return result


def get_answers(courseID):
    """官方API获取答案"""
    resp = s.get(
        f"https://www.2-class.com/api/exam/getTestPaperList?courseId={courseID}")
    # print(resp.json()) #调试使用
    try:
        testpaperlist = resp.json()['data']['testPaperList']
        result = []
        for i in testpaperlist:
            result.append(i['answer'])
        return result
    except:
        print("已完成过该课时！")
        return None
    


def do_exam(courseID):
    """自动做题"""
    answers = get_answers(courseID)
    wd.get(f"https://www.2-class.com/courses/exams/{courseID}")
    start_button = wd.find_element(By.CLASS_NAME, "exam-box-start")
    start_button.click()

    
    print(answers)
    for answer in answers:
        if len(answer)!=1:
            box_list = wd.find_elements(By.CLASS_NAME, "ant-checkbox-input")
            for i in answer.split(','):
                box_list[int(i)].click()
        else:
            box_list = wd.find_elements(By.CLASS_NAME, "ant-radio-input")
            box_list[int(answer)].click()
        
        # if answer != answers[-1]:  # 未打完题目
        #     wd.find_element(By.CLASS_NAME, "exam-content-btn-next").click() #下一页
        # else:  # 打完题目提交
        wd.find_element(By.CLASS_NAME, "ant-btn-primary").click()


if __name__ == "__main__":
    
    wd.get("https://www.2-class.com/")
    login(username="linjianlin89", password="HFG12024")
    courses=get_courses(input("请输入年级："))
    for course in courses:
        do_exam(course)
    
