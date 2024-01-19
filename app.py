from flask import Flask, request, jsonify, session
import MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from flask_cors import CORS
app = Flask(__name__)
app.secret_key = "prabinisfromtheplanetcalledasEarth"  # Replace with a strong secret key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
CORS(app)
# MySQL Configuration
mysql_host = '127.0.0.1'
mysql_user = 'root'
mysql_password = 'prabin'
mysql_db = 'taskManager'

# Create a MySQL connection
db = MySQLdb.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_db)
cursor = db.cursor()

# API endpoint for user registration
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Extract username and password from the request
        username = data.get('username')
        password = data.get('password')

        # Check if the user already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'status': 'error', 'message': 'Username is already taken. Please try another username'}), 400

        else:
            # Hash the password
            hashed_password = generate_password_hash(password)

            # Insert the data into the users table
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
            db.commit()

            return jsonify({'status': 'success', 'message': 'User registered'}), 200

    except Exception as e:
        print(str(e))
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500



@app.route('/login', methods=['POST'])
# logic that will look into the request and perform other task
def login():
    try:
        # request has body {'username':'prabin', 'password':'prabin'}
        # get the body of the request
        data = request.get_json()
        # grab the username and password fromt the dictionary
        username = data.get('username')
        password = data.get('password')

        # use username to make a query to the database table to retrieve the record
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        # if user is none empty, check if the password matches
        if user:
            # check if the password provided (plain text) match with the hash password
            # if there is match, store the username in the session for latter action
            if check_password_hash(user[2], password):
                session['user_id'] = user[0]
                return jsonify({'status':'success', 'message': 'login succeded'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'login failed'}), 401
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    except Exception as e:
        print(str(e))
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# API endpoint for adding task by the user that is in session
@app.route('/todos', methods=['POST'])
def add_task():
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            data = request.get_json()
            task_name = data.get('task_name')

            # Insert the task into the task table
            cursor.execute('INSERT INTO tasks (task_name, user_id) VALUES (%s, %s)', (task_name, user_id))
            db.commit()
            return jsonify({'status': 'success', 'message': 'data added'})
        else:
            return jsonify({'status': 'error', 'message': 'unauthorised attempt to add task'})
    except Exception as e:
        print(str(e))
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# API endpoint for fetching all the tasks under the user in session
@app.route('/todos', methods=['GET'])
def fetch_all_task():
    if 'user_id' in session:
        user_id = session['user_id']

        # fetch all the records for the current user
        cursor.execute('SELECT * FROM tasks WHERE user_id = %s', (user_id,))
        tasks = cursor.fetchall()
        task_list = [{'task_id': task[0], 'task_name': task[1], 'completed': task[2]} for task in tasks]
        return jsonify({'status': 'success', 'tasks': task_list}), 200
    else:
        return jsonify({'status': 'error', 'message': 'unauthorised attempt to add task'})

@app.route("/todos/<int:task_id>", methods=['GET'])
def fetch_one_task(task_id):
    try:
        if 'user_id' in session:
            user_id = session['user_id']

            # select the task with given task id and user id
            cursor.execute('SELECT * FROM tasks WHERE user_id = %s and id = %s', (user_id, task_id))
            task = cursor.fetchone()
            if task:
                task_detail = [{'task_id': task[0], 'task_name': task[1], 'completed': task[2]}]
                return jsonify({'status': 'success', 'task': task_detail})
            else:
                return jsonify({'status': 'success', 'task': 'task not found'})
        else:
            return jsonify({'status': 'error', 'message': 'unauthorised attempt to add task'})
    except Exception as e:
        print(str(e))
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route("/todos/<int:task_id>", methods=['PUT'])
def update_task(task_id):
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            data = request.get_json()
            task_name = data.get('task_name')
            cursor.execute('update tasks set task_name = %s where user_id = %s and id = %s', (task_name, user_id, task_id))
            db.commit()
            return jsonify({'status': 'success', 'message': 'task is updated'})
        else:
            return jsonify({'status': 'error', 'message': 'unauthorised attempt to update task'})
    except Exception as e:
        print(str(e))
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route("/todos/<int:task_id>", methods=['DELETE'])
def remove_task(task_id):
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            cursor.execute('DELETE FROM tasks WHERE user_id = %s AND id = %s', (user_id, task_id))
            db.commit()
            return jsonify({'status': 'success', 'message': 'task is deleted'})
        else:
            return jsonify({'status': 'error', 'message': 'unauthorised attempt to delete task'})
    except Exception as e:
        print(str(e))
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route("/logout", methods=['POST'])
def logout():
    try:
        if 'user_id' in session:
            session.pop('user_id', None)
            return jsonify({'status': 'success', 'message': 'User logged out'}), 200
        else:
            return jsonify({'status': 'success', 'message': 'User not logged in'}), 401
    except Exception as e:
        print(str(e))
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
