import pymysql
from flask import Flask, render_template


app = Flask(__name__)
conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456', db='mydata_one')
cursor = conn.cursor()


@app.route('/')
def check():
    cursor.execute("select * from users")
    result = cursor.fetchall()
    return render_template('check.html', info=result)


if __name__ == '__main__':
    app.run(debug=True)