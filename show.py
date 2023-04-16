import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456', db='mydata_one')
cursor = conn.cursor()
sql = "select * from users"
cursor.execute(sql)
result = cursor.fetchall()
for row in result:
    print(row)