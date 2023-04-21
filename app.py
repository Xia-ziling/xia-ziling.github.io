from flask import Flask, render_template, request, redirect, url_for
import pymysql
import hashlib as hash
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.conn = pymysql.connect(host=os.getenv("DB_HOST"), port=3306, user=os.getenv("DB_USER"),
                                    password=os.getenv("DB_PASSWORD"), db='mydata_one')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def execute(self, query, values):
        self.conn.ping(reconnect=True)
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor

    def get_one(self, query, values):
        self.conn.ping(reconnect=True)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result

    def get_all(self, query, values):
        self.conn.ping(reconnect=True)
        self.cursor.execute(query, values)
        result = self.cursor.fetchall()
        return result

    def drop(self, query, values):
        self.conn.ping(reconnect=True)
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor

    def renew(self, query, values):
        self.conn.ping(reconnect=True)
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(query, values)
                self.conn.commit()
                return cursor
            except Exception as e:
                print(f"Error {e.args[0]}: {e.args[1]}")
                self.conn.rollback()


class User:
    def __init__(self, username=None, tel=None, password=None, new_name=None, new_password=None, new_phone=None,
                 confirm_password=None):
        self.db = None
        self.username = username
        self.tel = tel
        self.password = password
        self.new_name = new_name
        self.new_password = new_password
        self.new_phone = new_phone
        self.confirm_password = confirm_password

    def encryption(self):
        password_hash = hash.md5(self.password.encode('utf-8'))
        password_hash.update("@#$%^&*".encode('utf8'))
        self.password = password_hash.hexdigest()


class WebApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.db = None

    def run(self):
        self.app.run(debug=True)

    def setup_database(self):
        self.db = Database()

    def register_routes(self):
        @self.app.route('/')
        def index():
            return redirect(url_for('main'))

        @self.app.route('/register')
        def register():
            return render_template('register.html')

        @self.app.route('/main/')
        def main():
            return render_template('main.html')

        @self.app.route('/login/')
        def login():
            return render_template('login.html')

        @self.app.route('/menu/')
        def menu():
            return render_template('menu.html')

        @self.app.route('/search/')
        def search():
            return render_template('search.html')

        @self.app.route('/delete')
        def delete():
            return render_template('delete.html')

        @self.app.route('/modify/')
        def modify():
            return render_template('modify.html')

        @self.app.route('/register', methods=['POST'])
        def signup():  # 用户注册
            user = User()
            # 获取用户提交的注册信息
            user.username = request.form['username']
            user.tel = request.form['tel']
            user.password = request.form['password']
            user.encryption()
            query = "SELECT * FROM users WHERE username = %s"
            values = (user.username,)
            result = self.db.get_all(query, values)
            if result:
                if result:
                    return '用户名重复'
                else:
                    # 将用户信息插入到 MySQL 数据库中
                    query = "INSERT INTO users (username, password, tel) VALUES (%s, %s, %s)"
                    values = (user.username, user.password, user.tel)
                    self.db.execute(query, values)
                    return redirect(url_for('main'))

        @self.app.route('/login/', methods=['POST'])
        def signin():
            user = User()  # 用户登录
            # 获取用户填写的信息
            user.username = request.form['username']
            user.password = request.form['password']
            user.encryption()
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            values = (user.username, user.password)
            result = self.db.get_one(query, values)
            if not result:
                return '用户不存在'
            return redirect(url_for('menu'))

        @self.app.route('/search/', methods=['POST'])
        def seek():  # 查询用户信息
            user = User()
            user.username = request.form['username']
            query = "SELECT * FROM users WHERE username = %s"
            values = (user.username,)
            result = self.db.get_all(query, values)
            return render_template('search.html', info=result, username=user.username)

        @self.app.route('/delete/', methods=['POST'])
        def cut_out():  # 删除用户信息
            user = User()
            user.username = request.form['username']
            query = "DELETE FROM users WHERE username = %s"
            values = (user.username,)
            self.db.execute(query, values)
            return redirect(url_for('menu'))

        @self.app.route('/update', methods=['POST'])
        def update():  # 修改用户数据
            # 获取表单数据
            user = User()
            user.username = request.form['name']
            user.password = request.form['pw']
            user.encryption()
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            values = (user.username, user.password)
            result = self.db.get_all(query, values)
            if result:
                update_type = request.form['submit']
                if update_type == '更改用户名':
                    user.new_name = request.form['newname']
                    user.password = request.form['pw']
                    # 检查该用户名是否已经存在于数据库中
                    query = "SELECT * FROM users WHERE username = %s"
                    values = (user.new_name,)
                    result = self.db.get_all(query, values)
                    if result:
                        return '用户名重复'
                    else:
                        query = "UPDATE users SET username = %s WHERE username = %s AND password = %s"
                        values = (user.new_name, user.username, user.password)
                        self.db.renew(query, values)
                        return redirect(url_for('menu'))

                elif update_type == '更改手机号':
                    user.new_phone = request.form['telephone']
                    query = "UPDATE users SET tel = %s WHERE username = %s AND password = %s"
                    values = (user.new_phone, user.username, user.password)
                    self.db.renew(query, values)
                    return redirect(url_for('menu'))

                elif update_type == '更改密码':
                    user.password = request.form['pw']
                    user.new_password = request.form['password']
                    user.encryption()
                    user.confirm_password = request.form['confirm_password']
                    user.encryption()
                    if user.new_password != user.confirm_password:
                        return '密码不符，请重新输入'
                    else:
                        query = "UPDATE users SET password = %s WHERE username = %s AND password = %s"
                        values = (user.new_password, user.username, user.password)
                        self.db.renew(query, values)

                        return redirect(url_for('login'))
            else:
                return '用户不存在'

    def setup(self):
        self.setup_database()
        self.register_routes()


if __name__ == '__main__':
    webapp = WebApp()
    webapp.setup()
    webapp.run()
