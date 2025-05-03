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

    g_name_for_sp = g_name if g_name else None
    g_description_for_sp = g_description if g_description else None


    conn = get_db_connection()
    if not conn:
         return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

    cursor = conn.cursor()
    try:
        # --- Gọi thủ tục lưu trữ UpdateGameInfo ---
        sql_call = "{CALL UpdateGameInfo(?, ?, ?, ?)}"
        params = (
             game_id,
             g_name_for_sp, 
             g_price,      
             g_description_for_sp 
        )

        cursor.execute(sql_call, params)
        conn.commit() 

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


# --- Route xóa dữ liệu ---
@app.route('/api/delete_game', methods=['POST']) # Sử dụng POST cho request xóa từ form nhỏ
def delete_game_api():
    """Xử lý xóa game bằng cách gọi thủ tục DeleteGame và trả về JSON."""
    conn = get_db_connection()
    if not conn:
         return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

    cursor = conn.cursor()
    try:
        # Lấy Game ID từ dữ liệu gửi qua AJAX
        item_id = request.form.get('item_id', '').strip() # @GID varchar(6)

        if not item_id:
             return jsonify({'success': False, 'error': 'Thiếu Game ID để xóa.'}), 400

        # --- Gọi thủ tục lưu trữ DeleteGame ---
        # Tham số: @GID
        sql_call = "{CALL DeleteGame(?)}"
        params = (item_id,)

        cursor.execute(sql_call, params)
        conn.commit() # Xác nhận thay đổi

        return jsonify({'success': True, 'message': f'Game "{item_id}" đã được xóa thành công!'})


    # --- Bắt các lỗi THROW từ thủ tục SQL Server ---
    except pyodbc.ProgrammingError as err:
        print(f"Database error calling DeleteGame (API): {err}")
        error_message = str(err)
        # Kiểm tra các thông báo lỗi cụ thể từ thủ tục DeleteGame
        if 'Game not found.' in error_message:
             return jsonify({'success': False, 'error': 'Lỗi: Không tìm thấy game để xóa.'}), 404 # 404 Not Found
        elif 'Failed to delete game.' in error_message: # Lỗi từ CATCH cuối cùng
             return jsonify({'success': False, 'error': 'Xóa game thất bại do lỗi nội bộ.'}), 500
        else:
             return jsonify({'success': False, 'error': f'Lỗi CSDL: {error_message}'}), 500

    # --- Bắt lỗi ràng buộc khóa ngoại (nếu SP không xử lý) ---
    # SP DeleteGame của bạn không có TRY...CATCH cho IntegrityError, nên lỗi này sẽ bị bắt ở đây nếu xảy ra
    except pyodbc.IntegrityError as err:
         print(f"Integrity error deleting data (API): {err}")
         conn.rollback()
         return jsonify({'success': False, 'error': 'Không thể xóa game này vì nó đang được tham chiếu bởi dữ liệu khác.'}), 400 # 400 Bad Request

    except pyodbc.Error as err:
        print(f"General database error during delete (API): {err}")
        conn.rollback()
        return jsonify({'success': False, 'error': 'Đã xảy ra lỗi cơ sở dữ liệu khi xóa game.'}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# --- Route mới cho trang demo gọi hàm SQL ---
@app.route('/functions_demo', methods=['GET', 'POST'])
def functions_demo():
    """Render trang demo hàm SQL và xử lý gọi hàm."""
    conn = get_db_connection()
    if not conn:
         # Nếu không kết nối được CSDL, chỉ render trang trống với thông báo lỗi từ flash
         # Pass None cho kết quả và input values để template không cố gắng hiển thị chúng
         return render_template('functions_demo.html',
                                func1_result=None, func2_result=None,
                                func1_input=None, func2_input=None)

    cursor = conn.cursor()
    func1_result = None # Kết quả cho hàm CalculateUserSpending
    func2_result = None # Kết quả cho hàm CalculateAvrgReviewScore
    func1_input_values = None # Giá trị input cho hàm 1 để hiển thị lại trên form
    func2_input_values = None # Giá trị input cho hàm 2 để hiển thị lại trên form


    if request.method == 'POST':
        action = request.form.get('action') # Xác định form nào được submit

        if action == 'call_func1':
            # --- Xử lý gọi Hàm CalculateUserSpending ---
            user_id = request.form.get('user_id', '').strip()
            start_date_str = request.form.get('start_date', '').strip()
            end_date_str = request.form.get('end_date', '').strip()

            func1_input_values = {'user_id': user_id, 'start_date': start_date_str, 'end_date': end_date_str} # Lưu input để hiển thị lại

            # Validate và chuyển đổi kiểu dữ liệu
            if not user_id:
                 flash('Vui lòng nhập User ID cho Hàm 1.', 'warning')
            else:
                 try:
                      # Chuyển đổi chuỗi ngày sang đối tượng date
                      start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
                      end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

                      # --- Gọi Hàm SQL CalculateUserSpending ---
                      # Hàm trả về một giá trị scalar
                      # Các mã lỗi: -1.01 User không tồn tại, -1.02 Wallet không kích hoạt, -1.03 Ngày không hợp lệ
                      sql_call = "SELECT dbo.CalculateUserSpending(?, ?, ?)"
                      params = (user_id, start_date, end_date)

                      cursor.execute(sql_call, params)
                      # Hàm vô hướng trả về một hàng với một cột
                      result_row = cursor.fetchone()

                      if result_row:
                           func1_result_value = result_row[0] # Lấy giá trị từ cột đầu tiên
                           # Kiểm tra các mã lỗi đặc biệt
                           if func1_result_value == -1.01:
                               func1_result = {'error': 'User không tồn tại.'}
                           elif func1_result_value == -1.02:
                                func1_result = {'error': 'User chưa kích hoạt WALLET.'}
                           elif func1_result_value == -1.03:
                                func1_result = {'error': 'Ngày bắt đầu không thể sau ngày kết thúc.'}
                           else:
                                func1_result = {'success': True, 'total_spending': func1_result_value} # Kết quả thành công

                      else:
                          func1_result = {'error': 'Hàm không trả về kết quả.'} # Trường hợp không mong đợi

                 except ValueError:
                      flash('Định dạng ngày không hợp lệ cho Hàm 1.', 'danger')
                      func1_result = {'error': 'Định dạng ngày không hợp lệ.'}
                 except pyodbc.Error as err:
                      print(f"Error calling CalculateUserSpending: {err}")
                      flash(f'Lỗi CSDL khi gọi Hàm 1: {str(err)}', 'danger')
                      func1_result = {'error': f'Lỗi CSDL: {str(err)}'}


        elif action == 'call_func2':
             # --- Xử lý gọi Hàm CalculateAvrgReviewScore ---
             game_id = request.form.get('game_id', '').strip()
             func2_input_values = {'game_id': game_id} # Lưu input để hiển thị lại

             if not game_id:
                  flash('Vui lòng nhập Game ID cho Hàm 2.', 'warning')
             else:
                  try:
                       # --- Gọi Hàm SQL CalculateAvrgReviewScore ---
                       # Hàm trả về một bảng (Table-Valued Function)
                       sql_call = "SELECT * FROM dbo.CalculateAvrgReviewScore(?)"
                       params = (game_id,)

                       cursor.execute(sql_call, params)
                       # Hàm trả về bảng, fetchall sẽ lấy tất cả các hàng
                       result_rows = cursor.fetchall()

                       if result_rows:
                            # Lấy tên cột từ cursor description
                           column_names = [column[0] for column in cursor.description]
                           # Chuyển đổi kết quả sang list of dictionaries để dễ dàng hiển thị trong template
                           func2_result_list = [dict(zip(column_names, row)) for row in result_rows]

                           # Kiểm tra trường hợp lỗi từ hàm (dòng đầu tiên có GameID = 0)
                           if func2_result_list[0].get('GameID') == '0':
                                # Dòng lỗi đặc biệt từ hàm
                                func2_result = {'error': func2_result_list[0].get('GameName')} # Sử dụng GameName làm thông báo lỗi
                           else:
                                func2_result = {'success': True, 'results': func2_result_list} # Kết quả thành công

                       else:
                            # Hàm không trả về hàng nào (có thể xảy ra nếu có lỗi hoặc không có đánh giá sau validate nội bộ)
                            # Dựa trên logic hàm bạn gửi, nó luôn trả về ít nhất 1 hàng, kể cả lỗi hoặc không có đánh giá.
                            # Trường hợp này ít xảy ra nếu hàm đúng như script bạn gửi.
                            func2_result = {'error': 'Hàm không trả về dữ liệu bảng.'}

                  except pyodbc.Error as err:
                       print(f"Error calling CalculateAvrgReviewScore: {err}")
                       flash(f'Lỗi CSDL khi gọi Hàm 2: {str(err)}', 'danger')
                       func2_result = {'error': f'Lỗi CSDL: {str(err)}'}

        # Nếu không có action hoặc action không hợp lệ, không làm gì cả, chỉ hiển thị form trống (hoặc với input values cũ)


    # Đóng kết nối CSDL sau khi xử lý xong POST hoặc nếu là GET request
    if cursor: cursor.close()
    if conn: conn.close()

    # Render template demo, truyền kết quả và giá trị input cũ
    return render_template('functions_demo.html',
                           func1_result=func1_result,
                           func2_result=func2_result,
                           func1_input=func1_input_values,
                           func2_input=func2_input_values)


# --- Phần chạy ứng dụng ---
if __name__ == '__main__':
    # Chạy ứng dụng Flask ở chế độ debug
    # Host='0.0.0.0' cho phép truy cập từ mạng cục bộ (cẩn thận khi expose ra internet)
    # Nếu chỉ chạy cục bộ trên máy mình, có thể bỏ host='0.0.0.0'
    # port=5000 là port mặc định, có thể thay đổi
    app.run(debug=True)