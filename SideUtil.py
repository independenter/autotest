import json, profile, unittest,re
import profile #测试性能，只能在控制台运行

#信息找不到
class InfoNotFoundException(Exception):
    pass

#不是一个list
class NotListException(Exception):
    pass

IGNORED_CMDS=('mouseDownAt','mouseUpAt','mouseOver','selectFrame','mouseOut',)

# __import__(module_name)  side解析器
class SideParser(object):
    #初始化方法
    def __init__(self, filename):
        self.handler = open(filename+'.side','r',encoding='utf-8')
        self.side_info = json.load(self.handler)
        self.base_url = self.get_base_url()
        self.exec_handler = open(filename+'.py', 'w', encoding='utf-8')
        self.exec_handler.write('from util import *\n')
        #self.click = False

    def get_side_info(self):
        return self.side_info;

    def get_ip(self,url):
        result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", url)
        if len(result)>0:
            return result[0]
        raise InfoNotFoundException(url+' not has ip')

    def is_vaild(self,ip):
        if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",ip):
            return True
        return False

    def get_tests(self):
        if self.isDict(self.side_info):
            return self.side_info['tests']
        raise  InfoNotFoundException('tests not found')

    #根据名称获得测试组件
    def get_test(self,component):
        if self.isDict(self.side_info):
            for test in self.side_info['tests']:
                if self.isDict(test) and test['name']==component:
                    self.temp_component = test
                    return test
        raise  InfoNotFoundException(component+' component not found')

    def get_ignroed_cmds(self,test):
        result = []
        if self.isDict(test):
            for cmd in test['commands']:
                if self.isDict(cmd) and cmd['command'] not in IGNORED_CMDS:
                    result.append(cmd)
            return result
        raise  InfoNotFoundException('commands not found')

    def get_all_cmds(self, test):
        if self.isDict(test):
            return test['commands']
        raise InfoNotFoundException('commands not found')

    #返回list 运行条件
    def get_suites(self):
        if self.isDict(self.side_info):
            return self.side_info['suites']
        raise  InfoNotFoundException('suites not found')

    #获得端口
    def get_port(self,url):
        result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,6}\b", url)
        list = result[0].split(':') if len(result) > 0 else []
        if len(list)==2:
            return list[1]
        raise InfoNotFoundException(url + ' not has ip')

    # 获得基本网址
    def get_base_url(self):
        if self.isDict(self.side_info):
            return self.side_info['url']
        raise  InfoNotFoundException('base url not found')

    # 获得批量网址
    def get_batch_urls(self):
        if self.isDict(self.side_info):
            return self.side_info['urls']
        raise  InfoNotFoundException('batch urls not found')

    # 获得批量插件
    def get_plugins(self):
        if self.isDict(self.side_info):
            return self.side_info['plugins']
        raise  InfoNotFoundException('plugins not found')

    # 获得selenium版本信息
    def get_side_version(self):
        if self.isDict(self.side_info):
            return self.side_info['version']
        raise  InfoNotFoundException('version not found')

    # 判断是否是字典
    def isDict(self,obj):
        if isinstance(obj,dict):
            return True
        return False

    def isList(self,obj):
        if isinstance(obj,list):
            return True
        return False

    def isInt(self, obj):
        if isinstance(obj, int):
            return True
        return False

    def __del__(self):
        self.handler.close()
        self.exec_handler.close()

    def __call__(self, *args, **kwargs):
        pass

    def write(self,*args):
        for arg in args:
            self.exec_handler.write(arg)

    def get_button(self,cmd,type='xpath:attributes'):
        for target in cmd['targets']:
            if type in target:
                selector = target[0].split("=", 1)[1]
                selector = selector.replace('\'', '\\\'')
                value = cmd['value']
                btn = '''Button('%s', type='%s')''' % (selector, type.split(":")[0])
                return btn
        raise InfoNotFoundException('Button not found ')

    '''open,setWindowSize,click,type,mouseDownAt,mouseUpAt,mouseOver,selectFrame,mouseOut,,'''
    def translate_cmd(self,cmd,type='xpath:attributes'):
        action = '#初始化'+cmd['id']+'\n'
        if cmd['command']=='open':
            url = self.get_base_url()+cmd['target']
            action= '''open("%s")\n''' % url
        elif cmd['command']=='setWindowSize':
            size = cmd['target'].split("x")
            width = size[0]
            high = size[1]
            action = 'set_window_size(%s,%s)\n' % (width,high)
        elif cmd['command']=='click':
            for target in cmd['targets']:
                for item in target:
                    if item.find('input')>-1:
                        action = action.replace('初始化', '设置聚焦输入状态 ')
                        self.click = True
                        break
            if ~self.click:
                for target in cmd['targets']:
                    if type in target:
                        selector = target[0].split("=", 1)[1]
                        selector = selector.replace('\'', '\\\'')
                        value = cmd['value']
                        action = '''Button('%s', type='%s').click()\n''' % (selector, type.split(":")[0])
        elif cmd['command']=='type' and hasattr(self,'click') and self.click:
            for target in cmd['targets']:
                if type in target:
                    selector = target[0].split("=",1)[1]
                    selector = selector.replace('\'', '\\\'')
                    value = cmd['value']
                    action = '''Button('%s', type='%s').input('%s')\n''' % (selector, type.split(":")[0], value)
            self.click = False
        elif cmd['command']=='sendKeys':
            for target in cmd['targets']:
                if type in target:
                    selector = target[0].split("=",1)[1]
                    selector = selector.replace('\'', '\\\'')
                    value = cmd['value']  # ${KEY_ENTER}
                    value = re.findall(r'\w+', value)[0] if len(re.findall(r'\w+', value))>1 else 'KEY_ENTER'
                    if cmd['opensWindow']:
                        self.windowHandleName = cmd['windowHandleName']
                        self.windowTimeout = cmd['windowTimeout']
                    action = '''ActionImpl().key_down('%s',%s.element)\n''' % (value,self.get_button(cmd,type))
        elif cmd['command']=='mouseDownAt':
            url = self.get_base_url()+cmd['target']
            action= '''open("%s")\n''' % url
        elif cmd['command']=='mouseUpAt':
            url = self.get_base_url()+cmd['target']
            action= '''open("%s")\n''' % url
        elif cmd['command']=='mouseOver':
            url = self.get_base_url()+cmd['target']
            action= '''open("%s")\n''' % url
        elif cmd['command']=='selectFrame':
            url = self.get_base_url()+cmd['target']
            action= '''open("%s")\n''' % url
        elif cmd['command']=='mouseOut':
            url = self.get_base_url()+cmd['target']
            action= '''open("%s")\n''' % url
        return action

def test():
    parser = SideParser('autotest')
    url = parser.get_base_url()
    test = parser.get_test("saleactive_qry");  #获得测试案例
    cmds = parser.get_ignroed_cmds(test)
    for cmd in cmds:
        exec_str = ''
        exec_str = parser.translate_cmd(cmd)
        parser.write(exec_str)




if __name__ == '__main__':
    test()