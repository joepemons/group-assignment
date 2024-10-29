from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from config import CONFIG
from create_db_reservation import ReservationDB
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'fonteyn123'

def get_db_connection():
    conn = sqlite3.connect(CONFIG["database"]["name"])
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def count_rows():
    try:
        with sqlite3.connect('reservation.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bookings")
            row_count = cursor.fetchone()[0]
            print(f"Total rows in the table: {row_count}")
    
    except sqlite3.Error as e:
        print("Error:", e)

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists!')
            return redirect(url_for('register'))
        finally:
            conn.close()

        flash('User registered successfully!')
        return redirect(url_for('login'))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                #flash('Logged in successfully!')
                print(f"User logged in: {user['id']}")
                print(f"User id: {session['user_id']}")
                return redirect(url_for('overview'))
            else:
                flash('Invalid username or password.')
                return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash(f"Database error: {e}")
            return redirect(url_for('login'))

@app.route('/overview')
@login_required
def overview():
    return render_template('overview.html')

@app.route("/accommodations/")
@login_required
def accommodations():
    conn = get_db_connection()
    all_accommodations = conn.execute('SELECT name, address, price, capacity FROM accommodations').fetchall()
    conn.close()
    print(f"accommodations: {all_accommodations}")
    return render_template("accomodations.html", accommodations=all_accommodations)

@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    room_name = request.args.get('room_name', '')
    room_price = float(request.args.get('price', 0))
    room_capacity = request.args.get('capacity', '')
    
    print(f"Room name from args: {room_name}")
    print(f"Room price from args: {room_price}")


    #user_id = session.get('user_id')
    #print(f"Booking for user_id: {user_id}")
    print(f"Request method: {request.method}")
    
    if request.method == "POST":
        user_id = session.get('user_id')
        print(f"User_id is: {user_id}")
        if user_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            start_date = request.form['start_date']
            end_date = request.form['end_date']

            # Calculate number of nights and total cost
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            nights = (end - start).days
            total_cost = nights * room_price

            cursor.execute('INSERT INTO bookings (user_id, room_name, start_date, end_date, total_cost) VALUES (?, ?, ?, ?, ?)',
                         (user_id, room_name, start_date, end_date, total_cost))
            print(f"Inserting booking: room_name={room_name}, total_cost={total_cost}")
            booking_id = cursor.lastrowid

            conn.execute('INSERT INTO transactions (booking_id, is_paid, payment_date, due_date) VALUES (?, ?, ?, ?)',
                         (booking_id, 'No', '', ''))
            conn.commit()
            conn.close()
            #flash('Booking made successfully!')
            return redirect(url_for('thank_you'))
        else:
            flash('You must be logged in to make a booking.')
            return redirect(url_for('login'))
    count_rows()
    return render_template("book.html", room_name=room_name, room_price=room_price, room_capacity=room_capacity)

@app.route('/thank-you', methods=['GET'])
@login_required
def thank_you():
    user_id = session.get('user_id')
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM bookings WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
        latest_booking = cursor.fetchone()

        if not latest_booking:
            flash('No booking found.')
            return redirect(url_for('overview'))

        conn.close()

        # Pass booking details to the template
        return render_template('thankyou.html', booking=latest_booking)
    else:
        flash('You must be logged in to see booking details.')
        return redirect(url_for('login'))

   


@app.route("/logout/")
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!')
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    app.run(host=CONFIG["frontend"]["listen_ip"], port=CONFIG["frontend"]["port"], debug=CONFIG["frontend"]["debug"])
