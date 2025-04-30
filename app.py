from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'wqphfk1h' # Change this


# LIB
USE_WINDOWS_AUTHENTICATION = False


# SETUP
# Replace with your database information
if USE_WINDOWS_AUTHENTICATION:
    db_config = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=TEST;Trusted_Connection=yes'
else:
    db_config = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=TEST;UID=sa;PWD=270205'


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







##########################################################################
##########################################################################
##########################################################################


@app.route('/data', methods=['GET'])
def list_data():
    conn = get_db_connection()
    data = []
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'username')

    if conn:
        cursor = conn.cursor()
        try:
            # Gọi thủ tục lưu trữ hoặc thực hiện truy vấn
            # ... (phần mã lấy dữ liệu từ CSDL) ...
             cursor.execute("{CALL GetUsersFilteredSorted(?, ?)}", (search_query, sort_by))
             data = cursor.fetchall()


        except pyodbc.Error as err:
            print(f"Error executing query/stored procedure: {err}")
            flash('Could not retrieve data.', 'danger')
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    else:
         flash('Could not connect to the database.', 'error')

    # Render template index.html (trang hiển thị bảng dữ liệu)
    return render_template('index.html', data=data, search_query=search_query, sort_by=sort_by)


##########################################################################
##########################################################################
##########################################################################


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_data(item_id):
    conn = get_db_connection()
    item = None # Biến để lưu dữ liệu của bản ghi cần sửa

    if conn:
        cursor = conn.cursor()
        try:
            # Lấy dữ liệu của bản ghi cần sửa dựa vào ID
            # Thay thế 'USER' và 'user_id' bằng tên bảng và tên cột ID của bạn
            sql_select = "SELECT user_id, username, password, email FROM [dbo].[USER] WHERE user_id = ?"
            cursor.execute(sql_select, (item_id,))
            item = cursor.fetchone() # Lấy một hàng duy nhất

            if item:
                 # Chuyển đổi tuple sang dictionary để dễ truy cập trong template
                column_names = [column[0] for column in cursor.description]
                item_dict = dict(zip(column_names, item))
            else:
                flash(f'Item with id {item_id} not found.', 'warning')
                return redirect(url_for('index'))


        except pyodbc.Error as err:
            print(f"Error fetching data for edit: {err}")
            flash('Could not load data for editing.', 'danger')
            return redirect(url_for('index'))
        finally:
            cursor.close()
            # Giữ kết nối mở nếu method là POST để xử lý update

    else:
        flash('Could not connect to the database.', 'error')
        return redirect(url_for('index'))


    if request.method == 'POST':
        # Lấy dữ liệu từ form đã sửa
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Lấy các trường dữ liệu khác

        # TODO: Validate dữ liệu nhập vào ở đây
        if not username or not password or not email:
            flash('Username, password, and email are required fields.', 'warning')
            # Giữ lại dữ liệu người dùng đã nhập và render lại form
            return render_template('form.html', item=request.form)


        conn = get_db_connection() # Lấy lại kết nối cho POST request
        if conn:
            cursor = conn.cursor()
            try:
                # Câu lệnh UPDATE (Thay thế 'USER', tên các cột và 'user_id')
                sql_update = "UPDATE [dbo].[USER] SET username = ?, password = ?, email = ? WHERE user_id = ?"
                val_update = (username, password, email, item_id) # Đặt dữ liệu vào tuple

                cursor.execute(sql_update, val_update)
                conn.commit() # Xác nhận thay đổi

                flash('Data updated successfully!', 'success')
                return redirect(url_for('index'))

            except pyodbc.IntegrityError as err:
                # Xử lý lỗi khi có ràng buộc toàn vẹn (ví dụ: username hoặc email bị trùng)
                print(f"Integrity error updating data: {err}")
                flash('Username or email already exists.', 'danger')
                conn.rollback() # Hoàn tác thay đổi
                 # Giữ lại dữ liệu người dùng đã nhập
                return render_template('form.html', item=request.form)

            except pyodbc.Error as err:
                print(f"Error updating data: {err}")
                flash('An error occurred while updating data.', 'danger')
                conn.rollback() # Hoàn tác thay đổi
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Could not connect to the database.', 'error')
            return render_template('form.html', item=request.form)


    # Nếu yêu cầu là GET và tìm thấy dữ liệu, hiển thị form với dữ liệu hiện có
    # item_dict đã được tạo ở phần xử lý GET
    return render_template('form.html', item=item_dict)

######################################
######################################
######################################

@app.route('/delete/<int:item_id>')
def delete_data(item_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Câu lệnh DELETE (Thay thế 'USER' và 'user_id')
            sql = "DELETE FROM [dbo].[USER] WHERE user_id = ?"
            cursor.execute(sql, (item_id,))
            conn.commit()

            # TODO: Xử lý trường hợp bản ghi không tồn tại khi xóa
            if cursor.rowcount == 0:
                 flash(f'Item with id {item_id} not found.', 'warning')
            else:
                flash('Data deleted successfully!', 'success')

        except pyodbc.IntegrityError as err:
            # Xử lý lỗi khi cố gắng xóa bản ghi đang được tham chiếu bởi khóa ngoại ở bảng khác
            print(f"Integrity error deleting data: {err}")
            flash('Cannot delete this item because it is referenced by other data.', 'danger')
            conn.rollback() # Hoàn tác thay đổi

        except pyodbc.Error as err:
            print(f"Error deleting data: {err}")
            flash('An error occurred while deleting data.', 'danger')
            conn.rollback() # Hoàn tác thay đổi
        finally:
            cursor.close()
            conn.close()
    else:
        flash('Could not connect to the database.', 'error')

    return redirect(url_for('index'))
#####################################
#####################################
#####################################

if __name__ == '__main__':
    app.run(debug=True)