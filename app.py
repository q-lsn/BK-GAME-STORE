from flask import Flask, render_template, request, flash, jsonify
import pyodbc
from datetime import datetime, date

# --- Cấu hình ứng dụng Flask ---
app = Flask(__name__)
app.secret_key = 'wqphfk1h'
db_config = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=STEAM_PROJECT;UID=sa;PWD=270205'

def get_db_connection():
     """Thiết lập và trả về kết nối đến cơ sở dữ liệu."""
     conn = None
     try:
          conn = pyodbc.connect(db_config) 
          return conn
     except pyodbc.Error as err:
          print(f"Database connection error: {err}")
          flash(f'Lỗi kết nối cơ sở dữ liệu: Không thể kết nối đến máy chủ. Vui lòng kiểm tra cấu hình và đảm bảo máy chủ đang chạy. Chi tiết lỗi: {str(err)}', 'danger')
          return None


# --- Route Trang Chủ ---
@app.route('/')
def index():
     """Render trang chủ."""
     return render_template('home.html')


# --- Route Trang Hiển Thị Danh Sách Game ---
@app.route('/data', methods=['GET'])
def list_data():
     """Lấy và hiển thị danh sách game được sắp xếp mặc định theo ID."""
     conn = get_db_connection()
     data = []
     if conn:
          cursor = conn.cursor()
          try:
               cursor.execute("{CALL GetGamesFilteredSorted}");
               column_names = [column[0] for column in cursor.description]
               data = cursor.fetchall()
               data = [dict(zip(column_names, row)) for row in data]

          except pyodbc.Error as err:
               print(f"Error executing GetGamesFilteredSorted: {err}")
               flash(f'Không thể lấy dữ liệu danh sách game: {str(err)}', 'danger')
          finally:
               if cursor: cursor.close()
               if conn: conn.close()
     return render_template('index.html', data=data)

# --- Route API Thêm/Sửa/Xóa Game ---

@app.route('/api/add_game', methods=['POST'])
def add_game_api():
     """Xử lý thêm game bằng InsertGame SP."""
     conn = get_db_connection()
     if not conn:
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500
     cursor = conn.cursor()
     try:
          g_name = request.form.get('g_name', '').strip()
          g_engine = request.form.get('g_engine', '').strip()
          g_description = request.form.get('g_description', '').strip()
          publisher_name = request.form.get('p_id', '').strip()
          released_str = request.form.get('released', '').strip()

          if not g_name or not publisher_name:
               return jsonify({'success': False, 'error': 'Tên Game và Tên Nhà phát hành là bắt buộc.'}), 400

          try:
               released_date = datetime.strptime(released_str, '%Y-%m-%d').date() if released_str else None
          except ValueError:
               return jsonify({'success': False, 'error': 'Định dạng ngày phát hành không hợp lệ.'}), 400

          g_engine_for_sp = g_engine if g_engine else None
          g_description_for_sp = g_description if g_description else 'No description'

          sql_call = "{CALL InsertGame(?, ?, ?, ?, ?)}"
          params = (g_name, g_engine_for_sp, g_description_for_sp, publisher_name, released_date)
          cursor.execute(sql_call, params)
          conn.commit()

          return jsonify({'success': True, 'message': f'Game "{g_name}" đã được thêm thành công! (Lưu ý: Thông tin giá và tradeable cần cập nhật riêng).'}), 200 # 200 OK

     except pyodbc.ProgrammingError as err:
          print(f"Database error calling InsertGame (API): {err}")
          conn.rollback()
          error_message = str(err)
          if '[50000]' in error_message:
               sp_error = error_message.split('[50000]')[-1].split('[')[0].strip()
               return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), 400 # 400 Bad Request for input errors
          else:
               return jsonify({'success': False, 'error': f'Lỗi lập trình CSDL: {error_message}'}), 500

     except pyodbc.Error as err:
          print(f"General database error during insert (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': f'Đã xảy ra lỗi cơ sở dữ liệu khi thêm game: {str(err)}'}), 500 # 500 Internal Server Error
     finally:
          if cursor: cursor.close()
          if conn: conn.close()


@app.route('/api/update_game', methods=['POST'])
def update_game_api():
     """Xử lý cập nhật game bằng UpdateGameInfo SP."""
     conn = get_db_connection()
     if not conn:
          # get_db_connection đã flash lỗi, chỉ cần trả về JSON
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

     cursor = conn.cursor()
     try:
          game_id = request.form.get('game_id', '').strip()
          g_name = request.form.get('g_name', '').strip()
          g_description = request.form.get('g_description', '').strip()


          if not game_id:
               return jsonify({'success': False, 'error': 'Thiếu Game ID để cập nhật.'}), 400

          # Truyền NULL nếu giá trị rỗng để SP sử dụng giá trị mặc định (ISNULL)
          g_name_for_sp = g_name if g_name else None
          g_description_for_sp = g_description if g_description else None

          sql_call = "{CALL UpdateGameInfo(?, ?, ?)}"
          params = (game_id, g_name_for_sp, g_description_for_sp)
          cursor.execute(sql_call, params)
          conn.commit()

          return jsonify({'success': True, 'message': f'Thông tin game "{game_id}" đã được cập nhật thành công! (Lưu ý: Thông tin giá và tradeable cần cập nhật riêng).'}), 200

     except pyodbc.ProgrammingError as err:
          print(f"Database error calling UpdateGameInfo (API): {err}")
          conn.rollback()
          error_message = str(err)
          if '[50000]' in error_message:
               sp_error = error_message.split('[50000]')[-1].split('[')[0].strip()
               if 'Game not found.' in sp_error:
                    return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), 404 # 404 Not Found
               else:
                    return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), 400 # 400 Bad Request
          else:
               return jsonify({'success': False, 'error': f'Lỗi lập trình CSDL: {error_message}'}), 500

     except pyodbc.Error as err:
          print(f"General database error during update (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': f'Đã xảy ra lỗi cơ sở dữ liệu khi cập nhật game: {str(err)}'}), 500
     finally:
          if cursor: cursor.close()
          if conn: conn.close()


@app.route('/api/delete_game', methods=['POST'])
def delete_game_api():
     """Xử lý xóa game bằng DeleteGame SP."""
     conn = get_db_connection()
     if not conn:
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

     cursor = conn.cursor()
     try:
          item_id = request.form.get('item_id', '').strip()
          if not item_id:
               return jsonify({'success': False, 'error': 'Thiếu Game ID để xóa.'}), 400

          sql_call = "{CALL DeleteGame(?)}"
          params = (item_id,)
          cursor.execute(sql_call, params)
          conn.commit()


          return jsonify({'success': True, 'message': f'Game "{item_id}" đã được xóa thành công!'}), 200

     except pyodbc.ProgrammingError as err:
          print(f"Database error calling DeleteGame (API): {err}")
          conn.rollback()
          error_message = str(err)
          # Bắt các lỗi cụ thể từ THROW của SP
          if '[50000]' in error_message:
               sp_error = error_message.split('[50000]')[-1].split('[')[0].strip()
               # Lỗi "Game not found" nên trả về 404
               if 'Game not found.' in sp_error:
                    return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), 404 # 404 Not Found
               else:
                    return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), 400 # 400 Bad Request
          else:
               return jsonify({'success': False, 'error': f'Lỗi lập trình CSDL: {error_message}'}), 500

     except pyodbc.IntegrityError as err:
          print(f"Integrity error deleting data (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': f'Không thể xóa game này vì nó đang được tham chiếu bởi dữ liệu khác. Chi tiết: {str(err)}'}), 400
     except pyodbc.Error as err:
          print(f"General database error during delete (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': f'Đã xảy ra lỗi cơ sở dữ liệu khi xóa game: {str(err)}'}), 500
     finally:
          if cursor: cursor.close()
          if conn: conn.close()


# --- Route cho trang demo gọi hàm và hiển thị dữ liệu ---
@app.route('/functions_demo', methods=['GET', 'POST'])
def functions_demo():
     """Render trang demo gọi hàm và hiển thị dữ liệu."""
     conn = get_db_connection()
     if not conn:
          return render_template('functions_demo.html', func1_result=None, func2_result=None)

     cursor = conn.cursor()
     func1_result = None 
     func2_result = None
     func1_input_values = None 
     func2_input_values = None 

     if request.method == 'POST':
          action = request.form.get('action')

          if action == 'call_func1':
               user_id = request.form.get('user_id', '').strip()
               start_date_str = request.form.get('start_date', '').strip()
               end_date_str = request.form.get('end_date', '').strip()
               func1_input_values = {'user_id': user_id, 'start_date': start_date_str, 'end_date': end_date_str}

               if not user_id or not start_date_str or not end_date_str:
                    flash('Vui lòng nhập đầy đủ User ID, Ngày bắt đầu và Ngày kết thúc.', 'warning')
                    func1_result = {'success': False, 'error': 'Thiếu thông tin đầu vào.'} 
               else:
                    try:
                         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

                         sql_call = "SELECT dbo.CalculateUserSpending(?, ?, ?)"
                         params = (user_id, start_date, end_date)
                         cursor.execute(sql_call, params)

                         total_spending = cursor.fetchone()[0]

                         if total_spending == -1.01:
                              func1_result = {'success': False, 'error': f'User ID "{user_id}" không tồn tại.'}
                         elif total_spending == -1.02:
                              func1_result = {'success': False, 'error': f'User ID "{user_id}" chưa kích hoạt WALLET.'}
                         elif total_spending == -1.03:
                              func1_result = {'success': False, 'error': 'Ngày bắt đầu không thể sau ngày kết thúc.'}
                         else:
                              func1_result = {'success': True, 'total_spending': total_spending}

                    except ValueError:
                         flash('Định dạng ngày không hợp lệ. Vui lòng sử dụng YYYY-MM-DD.', 'danger')
                         func1_result = {'success': False, 'error': 'Định dạng ngày không hợp lệ.'}

                    except pyodbc.Error as err:
                         print(f"Error calling CalculateUserSpending: {err}")
                         flash(f'Đã xảy ra lỗi CSDL khi gọi hàm CalculateUserSpending: {str(err)}', 'danger')
                         func1_result = {'success': False, 'error': f'Lỗi CSDL: {str(err)}'}


          elif action == 'call_func2':
               game_id = request.form.get('game_id', '').strip()
               func2_input_values = {'game_id': game_id}

               if not game_id:
                    flash('Vui lòng nhập Game ID.', 'warning')
                    func2_result = {'success': False, 'error': 'Thiếu thông tin đầu vào.'}
               else:
                    try:
                         sql_call = "SELECT * FROM dbo.CalculateAvrgReviewScore(?)"
                         params = (game_id,)
                         cursor.execute(sql_call, params)

                         column_names = [column[0] for column in cursor.description]
                         func2_data = cursor.fetchall()
                         func2_data = [dict(zip(column_names, row)) for row in func2_data]

                         if func2_data and func2_data[0].get('GameID') == '0' and func2_data[0].get('GameName') == 'Game does not exist':
                              func2_result = {'success': False, 'error': f'Game ID "{game_id}" không tồn tại.'}
                         elif func2_data and func2_data[0].get('GameID') == '0' and func2_data[0].get('GameName') == 'Game not rated yet':
                              func2_result = {'success': False, 'error': f'Game ID "{game_id}" chưa có đánh giá nào.'}
                         else:
                              func2_result = {'success': True, 'results': func2_data}

                    except pyodbc.Error as err:
                         print(f"Error calling CalculateAvrgReviewScore: {err}")
                         flash(f'Đã xảy ra lỗi CSDL khi gọi hàm CalculateAvrgReviewScore: {str(err)}', 'danger')
                         func2_result = {'success': False, 'error': f'Lỗi CSDL: {str(err)}'} 


     if cursor: cursor.close()
     if conn: conn.close()

     return render_template('functions_demo.html',
                              func1_result=func1_result,
                              func2_result=func2_result,
                              func1_input=func1_input_values,
                              func2_input=func2_input_values)


# --- Phần chạy ứng dụng ---
if __name__ == '__main__':
    pass