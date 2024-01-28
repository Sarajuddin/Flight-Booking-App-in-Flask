from flask import Flask, render_template, request, session, redirect, flash
from flask_mysqldb import MySQL
import random

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'PASSWORD'
app.config['MYSQL_DB'] = 'my_database_name'
mysql = MySQL(app)

app.secret_key = b"asdfg"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add-flight', methods=['POST', 'GET'])
def addFlight():
    return render_template('add-flight.html')

@app.route('/dashboard/bookings/')
def adminBookings():
    cur = mysql.connection.cursor()
    cur.execute("select * from bookings")
    bookings = cur.fetchall()
    mysql.connection.commit()

    return render_template('admin-bookings.html', bookings = bookings)

@app.route('/dashboard/user-lists/')
def usersList():
    cur = mysql.connection.cursor()
    cur.execute("select * from register")
    users = cur.fetchall()
    mysql.connection.commit()
    print(f"\n{users}\n")
    return render_template('users-list.html', users = users)

@app.route('/dashboard/flight-lists/')
def flightsList():
    cur = mysql.connection.cursor()
    cur.execute("select * from flights")
    flights = cur.fetchall()
    mysql.connection.commit()
    print(f"\n{flights}\n")
    return render_template('flights-list.html', flights=flights)

@app.route('/dashboard/add-flight', methods=['POST', 'GET'])
def addFlights():
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        flight_name = request.form.get('flight_name')
        flight_number = request.form.get('flight_number')
        ticket_cost = int(request.form.get('ticket_cost'))
        taxes = float(request.form.get('taxes'))
        # total_price = request.form.get('total_price')
        total_price = ticket_cost + ticket_cost*taxes/100
        flight_type = request.form.get('flight_type')
        cur = mysql.connection.cursor()
        cur.execute("insert into flights(source, destination, flight_name, flight_number, ticket_cost, taxes, total_price, flight_type) values(%s, %s, %s, %s, %s, %s, %s, %s)", (source, destination, flight_name, flight_number, ticket_cost, taxes, total_price, flight_type))
        mysql.connection.commit()

        print("\nFlight record is added...\n")
        return redirect('/dashboard')
        
    cur = mysql.connection.cursor()
    cur.execute("select * from flighttype")
    flight_types = cur.fetchall()
    mysql.connection.commit()
    return render_template('add-flight.html', flight_types=flight_types)


@app.route('/book-ticket/<string:id>', methods=['POST', 'GET'])
def bookTicket(id):
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        passengercount = request.form.get('passengercount')
        from_airport = request.form.get('from')
        to_airport = request.form.get('to')
        flightname = request.form.get('flightname')
        dep_date = request.form.get('dep_date')
        bookingclass = request.form.get('bookingclass')
        pnr_number = random.randint(10000000, 99999999)
        # print(f"\n\n{from_airport}\n{to_airport}\n{flightname}\n{bookingclass}\n")
        if from_airport == to_airport:
            flash("Source and Destination must not be same!")
            return redirect(f'/book-ticket/{id}')

        cur = mysql.connection.cursor()
        cur.execute("select total_price from flights where source = %s and destination = %s and flight_type = %s and flight_name = %s", (from_airport, to_airport, bookingclass, flightname))
        price = cur.fetchone()
        if price == None:
            return "Amount is not found.  Please Enter details carefully."
        total_price = price[0]*int(passengercount)
        print(f"\n{total_price}\n")

        cur.execute("insert into bookings(name, age, total_passenger, from_airport, to_airport, flightname, dep_date, bookingclass, pnr_number, total_price, userid) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, age, passengercount, from_airport, to_airport, flightname, dep_date, bookingclass, pnr_number, total_price, id))
        mysql.connection.commit()

        print("\nTicket is booked\n")
        return redirect('/dashboard')
    cur = mysql.connection.cursor()
    cur.execute("select * from register where username = %s", (session['username'],))
    user = cur.fetchone()
    cur.execute("select * from flights")
    flights = cur.fetchall()
    cur.execute("select * from flighttype")
    flighttypes = cur.fetchall()
    mysql.connection.commit()
    return render_template('book-ticket.html', data=user, flights=flights, flighttypes=flighttypes)

@app.route('/dashboard/')
def dashboard():
    if 'username' in session:
        if session['status']=='0':
            cur = mysql.connection.cursor()
            cur.execute("select * from register where username = %s", (session['username'],))
            data = cur.fetchone()
            cur.execute("select * from bookings where userid = %s", (data[0],))
            bookings = cur.fetchall()
            mysql.connection.commit()


            return render_template('dashboard.html', data=data, bookings=bookings)
        else:
            return render_template('admin-dashboard.html', user = session['username'])
        # return f"{session['username']}, Welcome to dashboard!"
    else:
        return 'You must login first'
        
@app.route('/register/<string:status>', methods=['POST', 'GET'])
def register(status):
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cur = mysql.connection.cursor()
        if status=='1':
            cur.execute("select * from register_admin where username = %s", (username,))
        else:
            cur.execute("select * from register where username = %s", (username,))
        user = cur.fetchone()
        if user:
            mysql.connection.commit()
            error = "User already exists! Try different username."
            return render_template('register.html', error=error)
        else:
            if status=='1':
                cur.execute("insert into register_admin(username, password) values(%s, %s)", (username, password))
            else:
                cur.execute("insert into register(username, password) values(%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        print("\ndata stored\n")
        return redirect(f'/login/{status}')
    return render_template('register.html', status=status)

@app.route('/login/<string:status>', methods=['POST', 'GET'])
def login(status):
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cur = mysql.connection.cursor()

        if status == '1':
            cur.execute("select * from register_admin where username = %s and password = %s", (username, password))
        else:
            cur.execute("select * from register where username = %s and password = %s", (username, password))
        data = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        print(f"\n{data}\n")
        if data:
            session['username'] = username
            session['status'] = status
            return redirect('/dashboard')
        else:
            error = "Record not found"
            return render_template('login.html', error=error, status=status)
    return render_template('login.html', status=status)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('status', None)
    session.pop('id', None)
    
    return redirect('/')

app.run(debug=True)
