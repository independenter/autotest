from util import *

#

#登陆
open("http://10.135.204.227:9090/ngboss")
Button("STAFF_ID", type="id").input("SUPERUSR")
Button("STAFF_PWD", type="id").input("lc")
Button("login_btn", type="id").click()

#点击到测试界面 有个iframe
switch_to_frame("navframe_def")
Button('#UI-tab > li:nth-child(3)',type='css').click()  #更多
Button('//*[@id="navSubsysList"]/div/ul/li[1]',type='xpath').click() #CRM
Button('//*[@id="navMenu_L1_NCM"]/div/ul/li[1]',type='xpath').click()  #个人业务
Button('//*[@id="navMenu_L2_crm9000"]/div/ul/li[4]',type='xpath').click() #开户业务
Button('#crm9325 > .main',type='css').click()  #测试界面

#测试界面逻辑运行
switch_default_content()
switch_to_frame(Button("navframe_71",type="id").element)
Button('SERIAL_NUMBER',type='id').input("18706895777")
Button('query_BTN',type='id').click()

#关闭浏览器
sleep(10)
close()