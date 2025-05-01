from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pyodbc
import os
from datetime import datetime, date

# --- Cấu hình ứng dụng Flask ---
app = Flask(__name__)
# Secret key cần thiết cho flash messages và session.
# Nên lấy từ biến môi trường và đặt một giá trị mặc định an toàn và duy nhất trong môi trường production.
app.secret_key = os.getenv('SECRET_KEY', 'a_very_secret_and_unique_fallback_key_replace_this')

# --- Cấu hình kết nối Cơ sở dữ liệu SQL Server ---
# Thay thế các giá trị trong chuỗi kết nối bằng thông tin CSDL của bạn.
# Đảm bảo tên DRIVER khớp chính xác với tên driver bạn đã cài đặt (kiểm tra bằng odbcad32.exe).
# Đảm bảo SERVER, DATABASE, UID, PWD là chính xác.
# Nếu dùng Windows Authentication, dùng: 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server_name;DATABASE=STEAM_PROJECT;Trusted_Connection=yes;'
db_config = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=TEST;UID=sa;PWD=270205'

def get_db_connection():
    """Thiết lập và trả về kết nối đến cơ sở dữ liệu."""
    conn = None
    try:
        # pyodbc.connect có thể cần thêm tham số encoding='utf-8' tùy cấu hình
        conn = pyodbc.connect(db_config)
        return conn
    except pyodbc.Error as err:
        print(f"Database connection error: {err}")
        # Đối với API routes, trả về lỗi JSON sẽ phù hợp hơn flash message.
        # Flash message chỉ phù hợp khi redirect hoặc render template thông thường.
        # flash(f"Database connection error: {err}", 'error')
        return None # Trả về None nếu kết nối thất bại

# --- Route mới cho Trang Chủ ---
@app.route('/')
def index():
    """Render trang chủ."""
    return render_template('home.html')

# --- Route cho Trang Hiển Thị Danh Sách Dữ Liệu (Game) ---
@app.route('/data', methods=['GET'])
def list_data():
    """Lấy và hiển thị danh sách game với tìm kiếm và sắp xếp."""
    conn = get_db_connection()
    data = [] # Danh sách dữ liệu game sẽ được truyền đến template
    # Lấy tham số tìm kiếm và sắp xếp từ URL query string
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'game_name') # Mặc định sắp xếp theo tên game

    # Kiểm tra tên cột sắp xếp có hợp lệ không để tránh SQL Injection
    allowed_sort_columns = ['game_name', 'date_released', 'game_price'] # Thêm các cột khác bạn muốn cho phép sắp xếp
    if sort_by not in allowed_sort_columns:
        sort_by = 'game_name' # Đặt lại mặc định nếu giá trị không hợp lệ


    if conn:
        cursor = conn.cursor()
        try:
            # --- Gọi thủ tục lưu trữ để lấy danh sách Game ---
            # Bạn cần tạo thủ tục `GetGamesFilteredSorted` trong SQL Server.
            # Thủ tục này phải nhận 2 tham số: @SearchQuery VARCHAR(100) và @SortByColumn VARCHAR(50).
            # Nó nên thực hiện JOIN với bảng PUBLISHER để lấy tên nhà phát hành.
            # Câu SELECT trong thủ tục phải trả về các cột game_id, game_name, game_price, engine, game_description, tên publisher (alias), date_released theo đúng thứ tự.
            sql_call_sp = "{CALL GetGamesFilteredSorted(?, ?)}"
            cursor.execute(sql_call_sp, (search_query, sort_by))
            data = cursor.fetchall() # Lấy tất cả các hàng kết quả

        except pyodbc.Error as err:
            print(f"Error executing query/stored procedure for game list: {err}")
            # Hiển thị thông báo lỗi trên giao diện người dùng
            flash(f'Could not retrieve game list data: {str(err)}', 'danger')
        finally:
            # Đảm bảo cursor và kết nối được đóng
            if cursor: cursor.close()
            if conn: conn.close()
    else:
         # Xử lý lỗi kết nối CSDL
         flash('Could not connect to the database.', 'error')

    # Render template hiển thị danh sách game và truyền dữ liệu cùng tham số tìm kiếm/sắp xếp
    return render_template('index.html', data=data, search_query=search_query, sort_by=sort_by)

# --- Route API để lấy dữ liệu chi tiết của 1 Game theo ID ---
# Endpoint này được gọi bằng AJAX từ index.html khi nhấp Sửa
@app.route('/api/games/<string:game_id>', methods=['GET'])
def get_game_api(game_id):
     """Lấy dữ liệu chi tiết của một game theo ID và trả về dưới dạng JSON."""
     conn = get_db_connection()
     if not conn:
          # Trả về lỗi JSON nếu không kết nối được CSDL
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

     # Sử dụng pyodbc.Row factory để dễ dàng truy cập dữ liệu cột bằng tên
     # Cần cấu hình row_factory sau khi kết nối hoặc khi tạo cursor
     # Cách khác là lấy tên cột từ cursor.description sau khi execute và tạo dictionary thủ công
     # Let's use the manual dictionary creation approach for broader compatibility
     cursor = conn.cursor()
     game_dict = None # Dictionary để lưu dữ liệu game

     try:
         # Câu lệnh SQL để lấy dữ liệu game theo ID
         # JOIN với bảng PUBLISHER để lấy tên nhà phát hành
         # Đảm bảo tên bảng GAMES, PUBLISHER và tên cột khớp với schema của bạn
         sql_select = """
         SELECT g.game_id, g.game_name, g.game_price, g.engine, g.game_description, p.name AS publisher_name, g.date_released
         FROM GAMES g
         LEFT JOIN PUBLISHER p ON g.game_publisher = p.publisher_id
         WHERE g.game_id = ?
         """
         cursor.execute(sql_select, (game_id,))
         game_row = cursor.fetchone() # Lấy một hàng duy nhất

         if game_row:
              # Lấy tên cột từ cursor description
             column_names = [column[0] for column in cursor.description]
              # Tạo dictionary từ tên cột và dữ liệu hàng
             game_dict = dict(zip(column_names, game_row))

             # Chuyển đổi đối tượng date/datetime sang string định dạng YYYY-MM-DD cho input type="date"
             if game_dict.get('date_released') and isinstance(game_dict['date_released'], (datetime, date)):
                 game_dict['date_released'] = game_dict['date_released'].strftime('%Y-%m-%d')
             else:
                 game_dict['date_released'] = None # Đảm bảo là None hoặc chuỗi rỗng nếu không có ngày

             # Trả về dữ liệu game dưới dạng JSON thành công
             return jsonify({'success': True, 'game': game_dict})
         else:
             # Trả về lỗi JSON nếu không tìm thấy game
             return jsonify({'success': False, 'error': 'Game not found.'}), 404 # HTTP status 404 Not Found

     except pyodbc.Error as err:
         print(f"Error fetching game data (API): {err}")
         # Trả về lỗi JSON nếu có lỗi CSDL khi lấy dữ liệu
         return jsonify({'success': False, 'error': 'Error fetching game data.'}), 500 # HTTP status 500 Internal Server Error
     finally:
         if cursor: cursor.close()
         if conn: conn.close()

# --- Route API để xử lý thêm game bằng AJAX API ---
# Nhận POST request từ form thêm mới trong modal
@app.route('/api/add_game', methods=['POST'])
def add_game_api():
    """Xử lý thêm game mới bằng cách gọi thủ tục InsertGame và trả về JSON."""
    # Lấy dữ liệu từ form gửi qua AJAX (FormData)
    g_name = request.form.get('g_name', '').strip()
    g_price_str = request.form.get('g_price', '').strip()
    g_engine = request.form.get('g_engine', '').strip()
    g_description = request.form.get('g_description', '').strip()
    g_publisher = request.form.get('g_publisher', '').strip()
    released_str = request.form.get('released', '').strip()

    # --- Validate dữ liệu cơ bản ở backend ---
    # Nên validate các trường bắt buộc sớm
    if not g_name or not g_publisher:
         # Trả về JSON báo lỗi nếu validate thất bại
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

    # Chuẩn bị giá trị cho các tham số có giá trị mặc định trong SP
    # Truyền None hoặc chuỗi rỗng sẽ tùy thuộc vào cách SP xử lý ISNULL và default
    # Dựa trên SP InsertGame, nó có default values và IS NULL check cho @Released
    # Nó không dùng ISNULL cho các tham số khác, nên nếu bạn truyền '', nó sẽ insert ''.
    # Let's align with SP parameters.
    g_engine_for_sp = g_engine if g_engine else 'Source' # Gán giá trị mặc định ở Python
    g_description_for_sp = g_description if g_description else 'No description.' # Gán giá trị mặc định ở Python


    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

    cursor = conn.cursor()
    try:
        # --- Gọi thủ tục lưu trữ InsertGame ---
        # Đảm bảo tên thủ tục và số lượng/thứ tự/kiểu tham số khớp chính xác
        sql_call = "{CALL InsertGame(?, ?, ?, ?, ?, ?)}"
        params = (
            g_name,
            g_price,
            g_engine_for_sp,
            g_description_for_sp,
            g_publisher,
            released_date # pyodbc sẽ chuyển Python date/None sang SQL date/NULL
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
        user_error_message = 'An unexpected database error occurred.' # Thông báo lỗi chung mặc định

        # Kiểm tra các thông báo lỗi cụ thể từ thủ tục SQL Server
        # Dựa vào cách thủ tục THROW lỗi (trước hoặc trong TRY/CATCH)
        if 'Cannot set release date to a future date.' in error_message:
             user_error_message = 'Error: Release date cannot be in the future.'
        elif 'Publisher not found.' in error_message:
             user_error_message = 'Error: Publisher not found. Please check the publisher name.'
        elif 'Game already exists.' in error_message:
             user_error_message = 'Error: A game with this name already exists.'
        elif 'Price cannot be negative.' in error_message: # Mặc dù đã validate ở Python, lỗi từ SP vẫn có thể xảy ra
             user_error_message = 'Error: Price cannot be negative.'
        elif 'Failed to insert game.' in error_message: # Thông báo lỗi từ CATCH cuối cùng trong SP
             user_error_message = 'Failed to add game due to an internal database error.'
        else:
            # Nếu có lỗi khác không được bắt bởi các kiểm tra trên
            user_error_message = f'A database error occurred: {error_message}'

        conn.rollback() # Hoàn tác thay đổi
        # Trả về JSON báo lỗi cùng thông báo lỗi cụ thể
        return jsonify({'success': False, 'error': user_error_message}), 400 # HTTP status 400 Bad Request cho lỗi nghiệp vụ/validate từ SP


    except pyodbc.Error as err:
        print(f"General database error during insert (API): {err}")
        conn.rollback()
        # Trả về JSON báo lỗi chung cho các lỗi CSDL khác
        return jsonify({'success': False, 'error': 'A database error occurred during insertion.'}), 500 # HTTP status 500 Internal Server Error

    finally:
        # Đảm bảo cursor và kết nối được đóng
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