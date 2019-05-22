from util import config
import pymysql,random

mysql_list = config['db']['db_con_str'].split('/')
def parseInt(string):
    return int(string)
filename = "./"+str(random.randint(100000,999999))+".py"
handler = open(filename, 'w',encoding='utf-8')
dbconfig = {
    'host': mysql_list[2],
    'port': parseInt(mysql_list[3]),
    'user': mysql_list[0].split(":")[1],
    'password': mysql_list[1],
    'db': mysql_list[-2],
    'charset': mysql_list[-1],
    'cursorclass': pymysql.cursors.DictCursor,
}

db = pymysql.connect(**dbconfig)
cur = db.cursor()
sql = "SELECT * FROM COMPONENT WHERE STATE=0 ORDER BY SEQUENCE"

try:
    cur.execute(sql)  # 执行sql语句
    results = cur.fetchall()  # 获取查询的所有记录
    # 遍历结果
    for row in results:
        handler.write(row['content'])
        handler.write('\r\n')
except Exception as e:
    raise e
finally:
    cur.close()
    db.close()
    handler.close()



