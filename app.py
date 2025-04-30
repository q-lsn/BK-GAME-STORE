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
        g_name = request.form.get('g_name') 
        g_price_str = request.form.get('g_price')
        g_engine = request.form.get('g_engine') 
        g_description = request.form.get('g_description') 
        g_publisher = request.form.get('g_publisher')
        released_str = request.form.get('released')
        # Add some

        # TODO: Validate data here 
        # ----------------------------------------------------------

        if not g_name:
            flash('Game name is required.', 'warning')
            return render_template('form.html', item=request.form)
        
        if not g_publisher:
            flash('Publisher name is required.', 'warning')
            return render_template('form.html', 'warning')
        # ----------------------------------------------------------

        try:
            g_price = float(g_price_str) if g_price_str else 0.00
        except ValueError:
            flash('Invalid price format.', 'warning')
            return render_template('form.html', 'warning')
        
        released_date = None
        if released_str:
            try:
                from datetime import datetime
                released_date = datetime.strptime(released_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid release day format. Please use YYYY-MM-DD.', 'warning')
                return render_template('form.html', item=request.form)
            
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql_call = "{CALL InsertGame(?, ?, ?, ?, ?, ?)}"

                params = (
                    g_name,
                    g_price,
                    g_engine if g_engine else 'Source',
                    g_description if g_description else 'No description.',
                    g_publisher,
                    released_date
                )

                cursor.execute(sql_call, params)
                conn.commit()

                flash('Game added successfully!', 'success')
                return redirect(url_for('list_data'))
        
            except pyodbc.ProgrammingError as error:
                print(f"Database error calling InsertGame: {error}")
                error_message = str(error)

                if 'Cannot set release date to a future date.' in error_message:
                    flash('Error: Release date cannot be in the future.', 'danger')
                elif 'Publisher not found.' in error_message:
                    flash('Error: Publisher not found. Please check the publisher name.', 'danger')
                elif 'Game already exists.' in error_message:
                    flash('Error: A game with this name already exists.', 'danger')
                elif 'Price cannot be negative.' in error_message:
                    flash('Error: Price cannot be negative.', 'danger')
                else:
                    flash(f'An unexpected database error occurred: {error_message}', 'danger')

                conn.rollback()
                return render_template('form.html', item=request.form)
            
            except pyodbc.Error as error:
                print(f"General database error: {error}")
                flash(f'An error occurred: {str(error)}', 'danger')

                conn.rollback() 
                return render_template('form.html', item=request.form)

            finally:
                if cursor: cursor.close()
                if conn: conn.close()
        
        else:
            return render_template('form.html', item=request.form)
    
    return render_template('form.html')