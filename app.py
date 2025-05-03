from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pyodbc
from datetime import datetime, date

# --- Cấu hình ứng dụng Flask ---
app = Flask(__name__)
app.secret_key = 'wqphfk1h'

# --- Cấu hình kết nối Cơ sở dữ liệu SQL Server ---
# Thay thế các giá trị trong chuỗi kết nối bằng thông tin CSDL của bạn.
# Đảm bảo tên DRIVER khớp chính xác với tên driver bạn đã cài đặt (kiểm tra bằng odbcad32.exe).
# Đảm bảo SERVER, DATABASE, UID, PWD là chính xác.
# Nếu dùng Windows Authentication, dùng: 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server_name;DATABASE=STEAM_PROJECT;Trusted_Connection=yes;'
db_config = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=STEAM_PROJECT;UID=sa;PWD=270205'

def get_db_connection():
    """Thiết lập và trả về kết nối đến cơ sở dữ liệu."""
    conn = None
    try:
        conn = pyodbc.connect(db_config)
        return conn
    except pyodbc.Error as err:
        print(f"Database connection error: {err}")
        return None

# --- Route mới cho Trang Chủ ---
@app.route('/')
def index():
    """Render trang chủ."""
    return render_template('home.html')

# --- Route cho Trang Hiển Thị Danh Sách Dữ Liệu (Game) ---
@app.route('/data', methods=['GET'])
def list_data():
    conn = get_db_connection()
    data = []
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("{CALL GetGamesFilteredSorted}")
            data = cursor.fetchall()

        except pyodbc.Error as err:
            print(f"Error executing query/stored procedure for game list: {err}")
            flash(f'Could not retrieve game list data: {str(err)}', 'danger')
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    else:
         flash('Could not connect to the database.', 'error')

    return render_template('index.html', data=data)

# --- Route API để xử lý thêm game bằng AJAX API ---
@app.route('/api/add_game', methods=['POST'])
def add_game_api():
    g_name = request.form.get('g_name', '').strip()
    g_price_str = request.form.get('g_price', '').strip()
    g_engine = request.form.get('g_engine', '').strip()
    g_description = request.form.get('g_description', '').strip()
    g_publisher = request.form.get('g_publisher', '').strip()
    released_str = request.form.get('released', '').strip()

    # --- Validate dữ liệu cơ bản ở backend ---
    if not g_name or not g_publisher:
        return jsonify({'success': False, 'error': 'Game Name and Publisher Name are required.'}), 400

    # Validate và chuyển đổi giá
    try:
        g_price = float(g_price_str) if g_price_str else 0.00
        if g_price < 0: # Kiểm tra giá âm
             return jsonify({'success': False, 'error': 'Price cannot be negative.'}), 400
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid price format.'}), 400

    # Validate và chuyển đổi ngày phát hành
    released_date = None
    if released_str:
        try:
            released_date = datetime.strptime(released_str, '%Y-%m-%d').date()
            if released_date > date.today(): # Kiểm tra ngày phát hành không ở tương lai
                 return jsonify({'success': False, 'error': 'Release date cannot be in the future.'}), 400
        except ValueError:
             return jsonify({'success': False, 'error': 'Invalid release date format. Please use YYYY-MM-DD.'}), 400


    g_engine_for_sp = g_engine if g_engine else 'Source' # Gán giá trị mặc định ở Python
    g_description_for_sp = g_description if g_description else 'No description.' # Gán giá trị mặc định ở Python


    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

    cursor = conn.cursor()
    try:
        # --- Gọi thủ tục lưu trữ InsertGame ---
        sql_call = "{CALL InsertGame(?, ?, ?, ?, ?, ?)}"
        params = (
            g_name,
            g_price,
            g_engine_for_sp,
            g_description_for_sp,
            g_publisher,
            released_date 
        )

        cursor.execute(sql_call, params)
        conn.commit() # Xác nhận thay đổi

        # Thủ tục có thể in thông báo hoặc trả về GameID mới.
        # Chúng ta dựa vào việc không có lỗi THROW để xác định thành công.

        # Trả về JSON báo thành công
        return jsonify({'success': True, 'message': 'Game added successfully!'})

    # --- Bắt các lỗi THROW từ thủ tục SQL Server ---
    except pyodbc.ProgrammingError as err:
        print(f"Database error calling InsertGame (API): {err}")
        error_message = str(err)
        # Kiểm tra các thông báo lỗi cụ thể từ thủ tục InsertGame
        if 'Cannot set release date to a future date.' in error_message:
             return jsonify({'success': False, 'error': 'Lỗi: Ngày phát hành không thể trong tương lai.'}), 400
        elif 'Publisher not found.' in error_message:
             return jsonify({'success': False, 'error': 'Lỗi: Nhà phát hành không tồn tại.'}), 400
        elif 'Game already exists.' in error_message:
             return jsonify({'success': False, 'error': 'Lỗi: Game đã tồn tại.'}), 400
        elif 'Price cannot be negative.' in error_message: # Mặc dù đã validate ở Python
             return jsonify({'success': False, 'error': 'Lỗi: Giá không thể âm.'}), 400
        elif 'Failed to insert game.' in error_message: # Lỗi từ CATCH cuối cùng
             return jsonify({'success': False, 'error': 'Thêm game thất bại do lỗi nội bộ.'}), 500
        else:
            return jsonify({'success': False, 'error': f'Lỗi CSDL: {error_message}'}), 500


    except pyodbc.Error as err:
        print(f"General database error during insert (API): {err}")
        conn.rollback()
        return jsonify({'success': False, 'error': 'Đã xảy ra lỗi cơ sở dữ liệu khi thêm game.'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# --- Route API để xử lý cập nhật game bằng AJAX API ---
# Nhận POST request từ form sửa trong modal
@app.route('/api/update_game', methods=['POST'])
def update_game_api():
    """Xử lý cập nhật game bằng cách gọi thủ tục UpdateGameInfo và trả về JSON."""
    # Lấy dữ liệu từ form sửa gửi qua AJAX (FormData)
    game_id = request.form.get('game_id', '').strip() # Lấy Game ID từ input hidden
    g_name = request.form.get('g_name', '').strip()
    g_price_str = request.form.get('g_price', '').strip()
    g_description = request.form.get('g_description', '').strip()

    # --- Validate dữ liệu cơ bản ở backend ---
    # Game ID là bắt buộc
    if not game_id:
         return jsonify({'success': False, 'error': 'Game ID is missing for update.'}), 400

    # Validate và chuyển đổi giá (cho phép rỗng, nên dùng None nếu rỗng)
    g_price = None
    if g_price_str:
        try:
            g_price = float(g_price_str)
            if g_price < 0: # Kiểm tra giá âm
                 return jsonify({'success': False, 'error': 'Price cannot be negative.'}), 400
        except ValueError:
             return jsonify({'success': False, 'error': 'Invalid price format.'}), 400

    # Các trường GName, GDescription có thể rỗng hoặc NULL.
    # Thủ tục UpdateGameInfo sử dụng ISNULL(@Param, old_value).
    # Để ISNULL hoạt động, chúng ta cần truyền NULL từ Python.
    # Tuy nhiên, nếu người dùng muốn cập nhật thành chuỗi rỗng '', chúng ta cần truyền ''.
    # Dựa trên SP, nếu truyền NULL, nó giữ giá trị cũ. Nếu truyền '', nó cập nhật thành ''.
    # Let's transmit '' if the user entered '', and None if the user cleared the field entirely?
    # Or, pass the value as is, and let the SP handle ISNULL? Yes, pass the stripped string.
    # If the user sends an empty string '', the SP will get ''. If they clear the field and it's not sent,
    # or sent as None by FormData (unlikely for text input), SP might see NULL.
    # Let's send the stripped string. The SP uses ISNULL(@GName, game_name) - this means
    # if @GName is NULL, keep old name. If @GName is '', update to ''.
    # To allow clearing a field (setting to NULL) via form, it's complex.
    # For simplicity, let's send the stripped string. If it's '', SP updates to ''.
    # If you want to allow setting to NULL, you'd need checkboxes or specific indicators in the form.
    # Let's stick to the SP's ISNULL behavior with stripped strings.
    # A blank input sends ''.
    g_name_for_sp = g_name # Send stripped string
    g_description_for_sp = g_description # Send stripped string


    conn = get_db_connection()
    if not conn:
         return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

    cursor = conn.cursor()
    try:
        # --- Gọi thủ tục lưu trữ UpdateGameInfo ---
        # Đảm bảo tên thủ tục và số lượng/thứ tự/kiểu tham số khớp chính xác
        sql_call = "{CALL UpdateGameInfo(?, ?, ?, ?)}"
        params = (
             game_id,
             g_name_for_sp, # Truyền chuỗi (có thể rỗng) hoặc None
             g_price,       # Truyền float hoặc None
             g_description_for_sp # Truyền chuỗi (có thể rỗng) hoặc None
        )

        cursor.execute(sql_call, params)
        conn.commit() # Xác nhận thay đổi

        # Thủ tục có thể in thông báo. Dựa vào việc không có lỗi THROW để xác định thành công.

        # Trả về JSON báo thành công
        return jsonify({'success': True, 'message': f'Game {game_id} updated successfully!'})


    # --- Bắt các lỗi THROW từ thủ tục SQL Server ---
    except pyodbc.ProgrammingError as err:
        print(f"Database error calling UpdateGameInfo (API): {err}")
        error_message = str(err)
        user_error_message = 'An unexpected database error occurred.'

        # Kiểm tra các thông báo lỗi cụ thể từ thủ tục
        if 'Game not found.' in error_message:
            user_error_message = 'Error: Game not found.'
        elif 'Game already exists.' in error_message: # Lỗi trùng tên game (trừ game hiện tại)
            user_error_message = 'Error: A game with this name already exists.'
        elif 'Price cannot be negative.' in error_message: # Mặc dù đã validate ở Python
            user_error_message = 'Error: Price cannot be negative.'
        elif "Failed to update game's information." in error_message: # Thông báo lỗi từ CATCH cuối cùng
             user_error_message = "Failed to update game due to an internal database error."
        else:
             # Nếu có lỗi khác không được bắt bởi các kiểm tra trên
             user_error_message = f"A database error occurred: {error_message}"


        conn.rollback() # Hoàn tác thay đổi
        # Trả về JSON báo lỗi
        return jsonify({'success': False, 'error': user_error_message}), 400 # HTTP status 400 Bad Request cho lỗi nghiệp vụ/validate từ SP

    except pyodbc.Error as err:
        print(f"General database error during update (API): {err}")
        conn.rollback()
        # Trả về JSON báo lỗi chung cho các lỗi CSDL khác
        return jsonify({'success': False, 'error': 'A database error occurred during update.'}), 500 # HTTP status 500 Internal Server Error

    finally:
        # Đảm bảo cursor và kết nối được đóng
        if cursor: cursor.close()
        if conn: conn.close()


# --- Route xóa dữ liệu (Giữ nguyên) ---
# Xử lý xóa game bằng cách gọi DELETE
@app.route('/delete/<string:item_id>') # Game ID là varchar(6), nên nhận là string
def delete_data(item_id):
     """Xử lý xóa game theo ID."""
     conn = get_db_connection()
     # Sử dụng flash và redirect cho route xóa đơn giản này
     if not conn:
         flash('Could not connect to the database.', 'error')
         return redirect(url_for('list_data'))

     cursor = conn.cursor()
     try:
         # Câu lệnh DELETE trực tiếp (hoặc có thể gọi thủ tục xóa nếu có)
         sql = "DELETE FROM GAMES WHERE game_id = ?"
         cursor.execute(sql, (item_id,))
         conn.commit()

         # Kiểm tra số hàng bị ảnh hưởng để biết xóa thành công không
         if cursor.rowcount == 0:
              flash(f'Game with ID {item_id} not found.', 'warning')
         else:
             flash(f'Game {item_id} deleted successfully!', 'success')

     except pyodbc.IntegrityError as err:
         print(f"Integrity error deleting data: {err}")
         # Lỗi khi bản ghi bị khóa ngoại tham chiếu
         flash('Cannot delete this game because it is referenced by other data.', 'danger')
         conn.rollback()

     except pyodbc.Error as err:
         print(f"Error deleting data: {err}")
         flash('An error occurred while deleting data.', 'danger')
         conn.rollback()
     finally:
         if cursor: cursor.close()
         if conn: conn.close()

     # Redirect về trang danh sách sau khi xóa
     return redirect(url_for('list_data'))

# --- Route gốc cho form thêm/sửa riêng (Có thể bỏ qua nếu chỉ dùng modal) ---
# Nếu bạn muốn giữ form.html làm trang riêng (fallback), bạn cần thêm logic xử lý
# GET và POST cho route này. Hiện tại, các route API đã xử lý POST cho modal.
# @app.route('/add', methods=['GET', 'POST'])
# def add_data_page():
#     """(Tùy chọn) Route cho trang thêm mới dữ liệu riêng."""
#     # Logic để hiển thị form.html trên URL /add
#     if request.method == 'GET':
#          return render_template('form.html')
#     # Logic xử lý POST nếu form này được submit trực tiếp (không qua AJAX modal)
#     # else:
#          # Có thể gọi lại logic từ add_game_api hoặc viết riêng
#          # flash messages và redirect ở đây thay vì trả về JSON

# @app.route('/edit/<string:item_id>', methods=['GET', 'POST'])
# def edit_data_page(item_id):
#     """(Tùy chọn) Route cho trang sửa dữ liệu riêng."""
#     # Logic để hiển thị form.html với dữ liệu game trên URL /edit/ID
#     # Logic xử lý POST nếu form này được submit trực tiếp

# --- Phần chạy ứng dụng ---
if __name__ == '__main__':
    # Chạy ứng dụng Flask ở chế độ debug
    # Host='0.0.0.0' cho phép truy cập từ mạng cục bộ (cẩn thận khi expose ra internet)
    # Nếu chỉ chạy cục bộ trên máy mình, có thể bỏ host='0.0.0.0'
    # port=5000 là port mặc định, có thể thay đổi
    app.run(debug=True)