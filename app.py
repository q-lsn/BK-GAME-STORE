from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'wqphfk1h' # Change this


# LIB
USE_WINDOWS_AUTHENTICATION = False


# SETUP
# Replace with your database information
if USE_WINDOWS_AUTHENTICATION:
    db_config = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=STEAM_PROJECT;Trusted_Connection=yes'
else:
    db_config = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=STEAM_PROJECT;UID=sa;PWD=270205'


def get_db_connection():
    conn = None
    try:
        conn = pyodbc.connect(db_config)

    except pyodbc.Error as error:
        print(f"Database connection error: {error}")
        flash(f"Database connection error: {error}", 'error')
    return conn


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/add', methods= ['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        game_id = request.form['game_id']
        game_name = request.form['game_name']
        game_price = request.form['game_price']
        engine = request.form['engine']
        description = request.form['description']
        game_publisher = request.form['game_publisher']
        date_released = request.form['date_released']

        # Add some

        # TODO: Validate data here 
        # ----------------------------------------------------------

        if not username or not password or not email:
            flash('Username, password and email are required fields', 'warning')

            return render_template('form.html', item=request.form)

        # ----------------------------------------------------------

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            
    return