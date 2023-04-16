from flask import Flask, render_template, request, redirect, url_for
import pymysql
import hashlib as hash

app = Flask(__name__)
conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456', db='mydata_one')
cursor = conn.cursor()
sql = "CREATE TABLE if not exists Users\
 (username CHAR(10) NOT NULL PRIMARY KEY,\
 password VARCHAR(200) NOT NULL," \
      "tel CHAR(11) NOT NULL);"
conn.ping(reconnect=True)
cursor.execute(sql)
conn.close()


def encryption(password):
    password = hash.md5(password.encode("utf8"))
    password.update("@#$%^&*".encode('utf8'))
    password = password.hexdigest()
    return password


@app.route('/')
def index():
    return redirect(url_for('main'))


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login/')
def login():
    return render_template('login.html')


@app.route('/menu/')
def menu():
    return render_template('menu.html')


@app.route('/main/')
def main():
    return render_template('main.html')


@app.route('/search/')
def search():
    return render_template('search.html')


@app.route('/modify/')
def modify():
    return render_template('modify.html')


@app.route('/register', methods=['POST'])
def signup():
    cursor = conn.cursor()
    # 获取用户提交的注册信息
    username = request.form['username']
    tel = request.form['tel']
    password = request.form['password']
    password = encryption(password)
    # 将用户信息插入到 MySQL 数据库中
    conn.ping(reconnect=True)
    cursor.execute("INSERT INTO users (username, password, tel) VALUES (%s, %s, %s)", (username, password, tel))
    conn.commit()
    cursor.close()

    return redirect(url_for('main'))


@app.route('/login/', methods=['POST'])
def signin():
    cursor = conn.cursor()
    username = request.form['username']
    password = request.form['password']
    password = encryption(password)
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    conn.ping(reconnect=True)
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        return '用户名不存在'

    return redirect(url_for('menu'))


@app.route('/search/', methods=['POST'])
def seek():
    cursor = conn.cursor()
    username = request.form['username']
    query = "SELECT * FROM users WHERE username = %s"
    conn.ping(reconnect=True)
    cursor.execute(query, (username))
    result = cursor.fetchall()
    cursor.close()
    return render_template('search.html', info=result, username=username)


@app.route('/update', methods=['POST'])
def update():
    # 获取表单数据
    username = request.form['name']
    password = request.form['pw']
    password = encryption(password)
    update_type = request.form['submit']
    if update_type == '更改用户名':
        new_name = request.form['name']

        # 检查该用户名是否已经存在于数据库中
        check_query = "SELECT * FROM users WHERE password = %s and username = %s"
        conn.ping(reconnect=True)
        cursor.execute(check_query, (new_name, password, username))
        result = cursor.fetchone()
        if result:
            cursor.close()
            return '用户名重复'
        else:
            query = "UPDATE users SET username = %s WHERE password = %s"
            cursor.execute(query, (new_name, password))
            conn.commit()
            cursor.close()
            return redirect(url_for('menu'))

    elif update_type == '更改手机号':
        new_phone = request.form['telephone']
        query = "UPDATE users SET tel = %s WHERE password = %s"
        conn.ping(reconnect=True)
        cursor.execute(query, (new_phone, password))
        conn.commit()
        cursor.close()
        return redirect(url_for('menu'))

    elif update_type == '更改密码':
        new_password = request.form['password']
        new_password = encryption(new_password)
        confirm_password = request.form['confirm_password']
        confirm_password = encryption(confirm_password)
        if new_password != confirm_password:
            cursor.close()
            return '密码不符，请重新输入'
        else:
            query = "UPDATE users SET password = %s WHERE password = %s"
            cursor.execute(query, (new_password, password))
            conn.ping(reconnect=True)
            conn.commit()
            cursor.close()

            return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
