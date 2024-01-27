from datetime import datetime, timedelta
from random import random
from werkzeug.security import generate_password_hash, check_password_hash
import random
import pymysql as pymysql
from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure MySQL connection
db_config = {
    'host': '127.0.0.1',
    'port': '3308',
    'user': 'root',
    'password': '123456',
    'database': 'telephone',
}

# Function to create a MySQL connection
def create_connection():
    return mysql.connector.connect(**db_config)


# Define routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/company')
def company():
    return render_template('company.html')

@app.route('/req1')
def req1():
    search_term = request.args.get('q', '')
    database = Database()
    db = database.connect()
    suggestion = Suggestion(db)
    suggestions = suggestion.get_suggestions(search_term)
    db.close()
    return jsonify(suggestions)

class Database:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 3308
        self.db_name = 'telephone'
        self.username = 'root'
        self.password = '123456'
        self.conn = None

    def connect(self):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            db=self.db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return self.conn

class Suggestion:
    def __init__(self, db):
        self.conn = db
        self.table = 'company'

    def get_suggestions(self, search_term):
        with self.conn.cursor() as cursor:
            like_term = f"%{search_term}%"
            query = f"SELECT name, ext, mobile, dept, location FROM {self.table} WHERE name LIKE %s OR dept LIKE %s OR ext LIKE %s OR mobile LIKE %s LIMIT 100"
            cursor.execute(query, (like_term, like_term, like_term, like_term))
            result = cursor.fetchall()
            return result

@app.route('/advanced')
def advanced():
    return render_template('advanced.html')

@app.route('/newr')
def newr():
    return  render_template('new.html')

@app.route('/new', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        ext = request.form['ext']
        mobile = request.form['mobile']
        dept = request.form['dept']
        location = request.form['location']

        # Insert data into the 'users' table
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute('INSERT INTO company (Name, ext,mobile, dept,location) VALUES (%s, %s, %s, %s, %s)', (name, ext, mobile, dept , location))

        connection.commit()
        connection.close()

        return redirect(url_for('home'))


@app.route('/send', methods=['POST'])
def receive_message():
    try:
        # Get data from the POST request
        data = request.json
        message = data.get('message')
        ip = request.remote_addr
        date = datetime.utcnow() + timedelta(hours=6)
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')

        connection = create_connection()
        cursor = connection.cursor()

        # Insert data into the 'Messages' table
        sql = "INSERT INTO Messages (messages, ip, date) VALUES (%s, %s, %s)"
        values = (message, ip, date_str)
        cursor.execute(sql, values)
        connection.commit()
        connection.close()

        return "Message sent"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/req2')
def req2():
    # Get the q, d, and l parameters from the GET request
    q = request.args.get('q', '')
    d = request.args.get('d', '')
    l = request.args.get('l', '')

    # Prepare the SQL query
    query = "SELECT Name, ext, mobile, Dept, location FROM company WHERE (Name LIKE %s AND Dept LIKE %s)"
    search_q = f"%{q}%"
    search_d = f"%{d}%"

    with conn.cursor() as cursor:
        # Execute the query
        cursor.execute(query, (search_q, search_d))

        # Get the result
        result = cursor.fetchall()

    # Fetch all rows as an associative array
    suggestions = [{'Name': row[0], 'ext': row[1], 'mobile': row[2], 'Dept': row[3], 'location': row[4]} for row in result]

    # Return the suggestions as a JSON object
    return jsonify(suggestions)

db_host = '127.0.0.1'
db_port = 3308
db_username = 'root'
db_password = '123456'
db_name = 'telephone'

# Create database connection
conn = pymysql.connect(
    host=db_host,
    port=db_port,
    user=db_username,
    password=db_password,
    database=db_name
)

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/login', methods=['POST'])
def login():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        user = request.json['user']
        password = request.json['pass']

        # Use prepared statement to prevent SQL injection
        query = "SELECT * FROM teleuseradmin WHERE user = %s AND password = %s"
        cursor.execute(query, (user, password))
        result = cursor.fetchone()

        if result:
            # Password is correct, generate and store token
            random_value = random.randint(1, 100000)
            token = str(random_value)

            # Insert token into the 'token' table
            query = "INSERT INTO token (token) VALUES (%s)"
            cursor.execute(query, (token,))
            connection.commit()

            return jsonify({'status': 'success', 'message': 'Login successful', 'token': token})
        else:
            return jsonify({'status': 'error', 'message': 'Login unsuccessful'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/update', methods=['POST'])
def update():
    try:
        # Get data from the POST request
        token = request.form['token']

        connection = create_connection()
        cursor = connection.cursor()

        # Use prepared statement to prevent SQL injection
        query = "SELECT * FROM token WHERE token = %s"
        cursor.execute(query, (token,))
        result = cursor.fetchall()

        # Check the credentials
        if len(result) > 0:
            return render_template('update.html')  # You can create a separate HTML file for this response
        else:
            return 'PLEASE LOGIN'

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        connection.close()

class Suggestion:
    def __init__(self, db):
        self.conn = db
        self.table = 'company'

    def get_suggestions(self, search_term):
        with self.conn.cursor() as cursor:
            like_term = f"%{search_term}%"
            query = f"SELECT id, name, ext, mobile, dept, location FROM {self.table} WHERE name LIKE %s OR dept LIKE %s LIMIT 100"
            cursor.execute(query, (like_term, like_term))
            result = cursor.fetchall()
            return result

@app.route('/req3')
def req3():
    search_term = request.args.get('q', '')
    database = create_connection()
    suggestion = Suggestion(database)
    suggestions = suggestion.get_suggestions(search_term)
    database.close()
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
