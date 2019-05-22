#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:donghui

import configparser,time,gc,profile
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

IGNORED_EXCEPTIONS = (NoSuchElementException,)
TIME_OUT=30 #30秒

#解析配置
configparser = configparser.ConfigParser()
configparser.read("conf.ini",encoding='utf8')
config = {}
for section in configparser.sections():
    sectionStr={}
    config[section] = sectionStr
    for option in configparser.options(section):
        sectionStr[option] = configparser.get(section,option)

driver_type = config['driver']['driver']
driver_position = config['driver']['driver_path']+'\chromedriver.exe'
driver_env = config['driver']['driver_user_dir']

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("start-maximized");
chrome_options.add_argument('--user-data-dir=' + driver_env)
try:
    driver = webdriver.Chrome(executable_path=driver_position,chrome_options=chrome_options)
    wait = WebDriverWait(driver, TIME_OUT)
    pass
except Exception as e:
    pass
finally:
    pass

def isEmpty(str):
    if len(str) <= 0 or str=="" or str==None:
        return True
    return False

def sleep(seconds):
    time.sleep(seconds)

def open(url):
    driver.get(url);
    #driver.close() #新窗口打开旧的会自动关闭

def close():
    sleep(10000)
    driver.quit()

def switch_to_frame(input,type="ele",message='切换frame超时'):  #no such frame  sleep(1)
    end_time = time.time() + 3
    screen = None
    stacktrace = None
    while True:
        if isinstance(input,WebElement):
            driver.switch_to.frame(input)
            return
        else:
            value = WebDriverWait(driver,TIME_OUT/5).until(lambda x:x.find_element_by_id(input),message='切换'+input+'超时')
            value1 = WebDriverWait(driver,TIME_OUT/5).until(lambda x:x.find_element_by_name(input),message='切换'+input+'超时')
            if value or value1:
                if type == "ele":
                    driver.switch_to.frame(input)  # Button("navframe_def",type="id").element
                else:
                    driver.switch_to.frame(input)
                return
            sleep(0.5)
        if time.time() > end_time:
            break
    raise TimeoutException(message, screen, stacktrace)


def switch_default_content():
    driver.switch_to.default_content()

def switch_to_windows(handler):
    driver.switch_to.window(handler)

def maximize_window():
    driver.maximize_window()

def set_window_size(width,high):
    driver.set_window_size(width=width,height=high)

#ActionImpl().key_down(value,element)
class ActionImpl(object):
    def __init__(self):
        self.action = ActionChains(driver)

    def key_down(self, value, element=None):
        value = self.tran_value(value)
        self.action.key_down(value,element)

    def key_up(self, value, element=None):
        value =self.tran_value(value)
        self.action.key_up(value,element)

    def tran_value(self,value):
        if value=='KEY_ENTER':
            value=Keys.ENTER
        return value

    def send_keys(self, *keys_to_send):
        self.action.send_keys(keys_to_send)

    def __del__(self):
        self.action.perform()

class Alert(object):
    def __init__(self):
        self.alert = driver.switch_to.alert()
    def accept(self):
        self.alert.accept()  #等同于点击“确认”或“OK”'
    def dismiss(self):
        self.alert.dismiss()  #'等同于点击“取消”或“Cancel”'
    def text(self):
        self.alert.text  #'获取alert文本内容，对有信息显示的alert框'
    def send_keys(self,text):
        self.alert.send_keys(text)  #'发送文本，对有提交需求的prompt框'
    def authenticate(self,username,password):
        self.alert.authenticate(username,password) #'验证，针对需要身份验证的alert'

class Button(object):
    def __init__(self,selector,type="xpath",flag=0):
        self.driver = driver
        self.initElement(selector,type,flag)
        self.selector = selector
        self.type = type
        self.flag = flag

    def initElement(self,selector,type,flag):
        if type=="id":
            #self.element = self.driver.find_element_by_id(selector);
            self.element = wait.until(lambda x: x.find_element_by_id(selector),message='定位'+selector+'元素超时')
        elif type=="class":
            self.element = wait.until(lambda x: x.find_element_by_class_name(selector),message='定位'+selector+'元素超时')
        elif type=="css":
            self.element = wait.until(lambda x: x.find_element_by_css_selector(selector),message='定位'+selector+'元素超时');
        elif type == "tag":
            self.element = wait.until(lambda x: x.find_element_by_tag_name(selector),message='定位'+selector+'元素超时');
        elif type == "xpath":
            if flag>0:
                #print("1" + selector + ":%s" % element.is_displayed())
                self.until_not(lambda x:x.find_element_by_xpath('//*[@id="wade_ld_div"]/div[1]'),message='判断加载框超时')
                self.until(lambda x: x.find_elements_by_xpath(selector+'/option'), count=flag,message='定位' + selector + '的option元素超时');
                #self.until(EC.presence_of_all_elements_located((By.XPATH,selector+'/option')), message='定位' + selector + '的option元素超时')
                #wait.until(lambda x: x.find_elements_by_xpath(selector+"/option"), message='定位' + selector + '的option元素超时')
            self.element = wait.until(lambda x: x.find_element_by_xpath(selector),message='定位'+selector+'元素超时');
        elif type == "name":
            self.element = wait.until(lambda x: x.find_element_by_name(selector),message='定位'+selector+'元素超时');
        else:
            self.element = wait.until(lambda x: x.find_elements_by_xpath(selector),message='定位'+selector+'元素超时')

    def clear(self):
        self.element.clear()
    def input(self,input):
        self.clear()
        self.element.send_keys(input)
    def until_not(self, method, message=''):
        """Calls the method provided with the driver as an argument until the \
        return value is False."""
        end_time = time.time() + TIME_OUT
        while True:
            try:
                value = method(self.driver)
                if not value or not value.is_displayed():
                    return value
            except IGNORED_EXCEPTIONS:
                return True
            time.sleep(0.5)
            if time.time() > end_time:
                break
        raise TimeoutException(message)
    def until(self, method,count=10, message=''):
        """Calls the method provided with the driver as an argument until the \
        return value is not False."""
        screen = None
        stacktrace = None

        end_time = time.time() + TIME_OUT
        flag = False
        while True:
            try:
                value = method(self.driver)
                print('%s' % (value))  #打桩返回
                j=0
                if isinstance(value,list):
                    for i in value:
                        if i.is_displayed():
                            j=j+1
                    if j == len(value) and len(value)>=count:
                        flag = True
                    else:
                        flag = False
                else:
                    flag=True
                if value and flag:
                    return value
            except IGNORED_EXCEPTIONS as exc:
                screen = getattr(exc, 'screen', None)
                stacktrace = getattr(exc, 'stacktrace', None)
            time.sleep(0.5)
            if time.time() > end_time:
                break
        raise TimeoutException(message, screen, stacktrace)
    def click(self):
        if self.type == "xpath":
            self.until(EC.element_to_be_clickable((By.XPATH,self.selector)),"判断点击事件超时")
        self.element.click()
    def double_click(self):
        action = ActionChains(self.driver)
        action.double_click(self.element).perform();
    def submit(self):
        self.element.submit()
    def isSelected(self):
        return self.element.is_selected()
    def isEnabled(self):
        return self.element.is_enabled()
    def isDisplay(self):
        return self.element.is_displayed()
    def text(self):
        return self.element.text;
    def attr(self,name):
        return self.element.get_attribute(name)
    def property(self,name):
        return self.element.get_property(name)
    def checked(self):
        self.element.send_keys(Keys.SPACE) #点击复选框 单选框
    def select(self,input,type='index'):  #下拉选  #只能在self.element之前等待
        selector = Select(self.element)
        if type == "index":
            selector.select_by_index(input)
        elif type == "value":
            selector.select_by_value(input)
        elif type == "text":
            selector.select_by_visible_text(input)

    def deselect(self,input,type='index'):  #下拉选
        selector = Select(self.element)
        if type=="index":
            selector.deselect_by_index(input)
        elif type=="value":
            selector.deselect_by_value(input)
        elif type=="text":
            selector.deselect_by_visible_text(input)
        else:
            selector.deselect_all()

#查询营销活动
def saleactive_qry():
    # 登陆
    if driver.current_url.find('chrome') < 0:
        switch_default_content()
        Button('//*[@id="tab_ct_ul"]/li/div[@class="fn"]/div[3]', type='xpath').click()  # 关闭页面
    else:
        open("http://10.131.156.155:9090/ngboss")
        Button("STAFF_ID", type="id").input("SUPERUSR")
        Button("STAFF_PWD", type="id").input("lc")
        Button("login_btn", type="id").click()

    # 点击到测试界面 有个iframe
    switch_default_content()
    switch_to_frame("navframe_def")
    Button('#UI-tab > li:nth-child(3)', type='css').click()  # 更多 这是一个蒙面元素，有时会出现不可点击，可用sleep处理
    Button('//*[@id="navSubsysList"]/div/ul/li[1]', type='xpath').click()  # CRM
    Button('//*[@id="navMenu_L1_NCM"]/div/ul/li[1]', type='xpath').click()  # 个人业务
    Button('//*[@id="navMenu_L2_crm9000"]/div/ul/li[4]', type='xpath').click()  # 开户业务
    Button('#crm9325 > .main', type='css').click()  # 测试界面

    # 测试界面逻辑运行
    switch_default_content()
    switch_to_frame(Button('//*[@id="main_ct"]/iframe[2]', type="xpath").element)
    Button('SERIAL_NUMBER', type='id').input("18706895777")
    Button('query_BTN', type='id').click()

    # 关闭浏览器
    # sleep(10)
    # close()

#营销活动受理
def saleactive_reg():
    # 登陆
    if driver.current_url.find('chrome') < 0:
        switch_default_content()
        Button('//*[@id="tab_ct_ul"]/li/div[@class="fn"]/div[3]', type='xpath').click()  # 关闭页面
    else:
        open("http://10.131.156.155:9090/ngboss")
        Button("STAFF_ID", type="id").input("SUPERUSR")
        Button("STAFF_PWD", type="id").input("lc")
        Button("login_btn", type="id").click()

    # 点击到测试界面 有个iframe
    switch_default_content()
    switch_to_frame("navframe_def")
    Button('//*[@id="UI-tab"]/li[3]', type='xpath').click()  # 更多
    Button('//*[@id="navSubsysList"]/div/ul/li[1]', type='xpath').click()  # CRM
    Button('//*[@id="navMenu_L1_NCM"]/div/ul/li[1]', type='xpath').click()  # 个人业务
    Button('//*[@id="navMenu_L2_crm9000"]/div/ul/li[4]', type='xpath').click()  # 开户业务
    Button('#crm9321 > .main', type='css').click()  # 营销活动受理界面

    # 测试界面逻辑运行
    switch_default_content()
    switch_to_frame(Button('//*[@id="main_ct"]/iframe[2]', type="xpath").element)
    Button('AUTH_SERIAL_NUMBER', type='id').input("18706895777")
    Button('AUTH_SUBMIT_BTN', type='id').click()
    switch_default_content()
    switch_to_frame(Button('//*[@id="main_ct"]/iframe[2]', type="xpath").element) #加载完成后页面进行了一次刷新，需要重新获得dom
    ele = driver.find_element_by_xpath('//*[@id="wade_ld_div"]/div[1]')
    Button('//*[@id="SALE_CAMPN_TYPE"]', type='xpath',flag=10).select("YUCN",type="value") #获得select 有可能没有option
    # elements = driver.find_element_by_id("SALE_CAMPN_TYPE").find_elements_by_tag_name("option")
    # elements[3].click()

    Button('//*[@id="SALE_PRODUCT_ID"]', type='xpath',flag=3).select(1)#营销方案
    Button('SALE_ACTIVE_QRY_BTN', type='id').click()
    Button('//*[@id="69900002_69932501"]/span', type='xpath').click()#营销活动
    # Button('CSSUBMIT_Button', type='id').click() #提交

    # 关闭浏览器
    # sleep(10)
    # close()


if __name__=='__main__':
    #pass

    start = time.clock()
    saleactive_qry()
    print("营销活动查询:本次测试案例用时%.2fs" % (time.clock() - start))
    start = time.clock()
    saleactive_reg()
    print("营销活动受理:本次测试案例用时%.2fs" % (time.clock() - start))
    #
    # try:
    #     start = time.clock()
    #     saleactive_qry()
    #     print("营销活动查询:本次测试案例用时%.2fs" % (time.clock() - start))
    #     start = time.clock()
    #     saleactive_reg()
    #     print("营销活动受理:本次测试案例用时%.2fs" % (time.clock() - start))
    # except Exception as e:
    #     print(e)
    # finally:
    #     close()
    #     quit()  #会退出驱动

