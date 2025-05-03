from flask import Flask, render_template, request, flash, jsonify
import pyodbc
from datetime import datetime, date

# --- Cấu hình ứng dụng Flask ---
app = Flask(__name__)
app.secret_key = 'wqphfk1h'

# --- Cấu hình kết nối Cơ sở dữ liệu SQL Server ---
db_config = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=STEAM_PROJECT;UID=sa;PWD=270205'

def get_db_connection():
     """Thiết lập và trả về kết nối đến cơ sở dữ liệu."""
     conn = None
     try:
          # Timeout = 5 giây
          conn = pyodbc.connect(db_config)
          return conn
     except pyodbc.Error as err:
          print(f"Database connection error: {err}")
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
               # Gọi thủ tục lấy danh sách game (đảm bảo trả về game_id)
               cursor.execute("{CALL GetGamesFilteredSorted}"); # Giả định SP này trả về game_id
               # Lấy tên cột và dữ liệu
               column_names = [column[0] for column in cursor.description]
               data = cursor.fetchall()
               # Chuyển đổi kết quả sang list of dictionaries
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
     # Mã xử lý thêm game bằng InsertGame
     conn = get_db_connection()
     if not conn:
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500
     cursor = conn.cursor()
     try:
          g_name = request.form.get('g_name', '').strip()
          g_price_str = request.form.get('g_price', '').strip()
          g_engine = request.form.get('g_engine', '').strip()
          g_description = request.form.get('g_description', '').strip()
          g_publisher = request.form.get('g_publisher', '').strip()
          released_str = request.form.get('released', '').strip()

          if not g_name or not g_publisher:
               return jsonify({'success': False, 'error': 'Tên Game và Tên Nhà phát hành là bắt buộc.'}), 400

          try:
               g_price = float(g_price_str) if g_price_str else 0.00
               released_date = datetime.strptime(released_str, '%Y-%m-%d').date() if released_str else None
          except ValueError:
               return jsonify({'success': False, 'error': 'Định dạng Giá hoặc Ngày phát hành không hợp lệ.'}), 400

          sql_call = "{CALL InsertGame(?, ?, ?, ?, ?, ?)}"
          params = (g_name, g_price, g_engine, g_description, g_publisher, released_date)
          cursor.execute(sql_call, params)
          conn.commit()
          return jsonify({'success': True, 'message': f'Game "{g_name}" đã được thêm thành công!'})

     except pyodbc.ProgrammingError as err:
          print(f"Database error calling InsertGame (API): {err}")
          error_message = str(err)
          if 'Cannot set release date to a future date.' in error_message:
               return jsonify({'success': False, 'error': 'Lỗi: Ngày phát hành không thể trong tương lai.'}), 400
          elif 'Publisher not found.' in error_message:
               return jsonify({'success': False, 'error': 'Lỗi: Nhà phát hành không tồn tại.'}), 400
          elif 'Game already exists.' in error_message:
               return jsonify({'success': False, 'error': 'Lỗi: Game đã tồn tại.'}), 400
          elif 'Price cannot be negative.' in error_message:
               return jsonify({'success': False, 'error': 'Lỗi: Giá không thể âm.'}), 400
          elif 'Failed to insert game.' in error_message:
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


@app.route('/api/update_game', methods=['POST'])
def update_game_api():
     # Mã xử lý cập nhật game bằng UpdateGameInfo
     conn = get_db_connection()
     if not conn:
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500
     cursor = conn.cursor()
     try:
          game_id = request.form.get('game_id', '').strip()
          g_name = request.form.get('g_name', '').strip()
          g_price_str = request.form.get('g_price', '').strip()
          g_description = request.form.get('g_description', '').strip()

          if not game_id:
               return jsonify({'success': False, 'error': 'Thiếu Game ID để cập nhật.'}), 400
          try:
               g_price = float(g_price_str) if g_price_str else None
               if g_price is not None and g_price < 0:
                    return jsonify({'success': False, 'error': 'Giá không thể âm.'}), 400
          except ValueError:
               return jsonify({'success': False, 'error': 'Định dạng Giá không hợp lệ.'}), 400

          g_name_for_sp = g_name if g_name else None
          g_description_for_sp = g_description if g_description else None

          sql_call = "{CALL UpdateGameInfo(?, ?, ?, ?)}"
          params = (game_id, g_name_for_sp, g_price, g_description_for_sp)
          cursor.execute(sql_call, params)
          conn.commit()
          return jsonify({'success': True, 'message': f'Thông tin game "{game_id}" đã được cập nhật thành công!'})

     except pyodbc.ProgrammingError as err:
          print(f"Database error calling UpdateGameInfo (API): {err}")
          error_message = str(err)
          if 'Game not found.' in error_message:
               return jsonify({'success': False, 'error': 'Lỗi: Không tìm thấy game để sửa.'}), 404
          elif 'Game''s name already used by another game.' in error_message:
               return jsonify({'success': False, 'error': 'Lỗi: Tên game đã được sử dụng bởi game khác.'}), 400
          elif 'Price cannot be negative.' in error_message:
               return jsonify({'success': False, 'error': 'Lỗi: Giá không thể âm.'}), 400
          elif "Failed to update game's information." in error_message:
               return jsonify({'success': False, 'error': 'Cập nhật game thất bại do lỗi nội bộ.'}), 500
          else:
               return jsonify({'success': False, 'error': f'Lỗi CSDL: {error_message}'}), 500

     except pyodbc.Error as err:
          print(f"General database error during update (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': 'Đã xảy ra lỗi cơ sở dữ liệu khi cập nhật game.'}), 500
     finally:
          if cursor: cursor.close()
          if conn: conn.close()


@app.route('/api/delete_game', methods=['POST'])
def delete_game_api():
     # Mã xử lý xóa game bằng DeleteGame
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
          return jsonify({'success': True, 'message': f'Game "{item_id}" đã được xóa thành công!'})

     except pyodbc.ProgrammingError as err:
          print(f"Database error calling DeleteGame (API): {err}")
          error_message = str(err)
          if 'Game not found.' in error_message:
               return jsonify({'success': False, 'error': 'Lỗi: Không tìm thấy game để xóa.'}), 404
          elif 'Failed to delete game.' in error_message:
               return jsonify({'success': False, 'error': 'Xóa game thất bại do lỗi nội bộ.'}), 500
          else:
               return jsonify({'success': False, 'error': f'Lỗi CSDL: {error_message}'}), 500

     except pyodbc.IntegrityError as err:
          print(f"Integrity error deleting data (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': 'Không thể xóa game này vì nó đang được tham chiếu bởi dữ liệu khác.'}), 400
     except pyodbc.Error as err:
          print(f"General database error during delete (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': 'Đã xảy ra lỗi cơ sở dữ liệu khi xóa game.'}), 500
     finally:
          if cursor: cursor.close()
          if conn: conn.close()

# --- Route API để xử lý cập nhật Review bằng AJAX API ---
# Nhận review_id, new_comment, new_rating_score
@app.route('/api/update_review', methods=['POST'])
def update_review_api():
     """Xử lý cập nhật review và trả về JSON."""
     conn = get_db_connection()
     if not conn:
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

     cursor = conn.cursor()
     try:
          review_id = request.form.get('review_id', '').strip()
          comment = request.form.get('comment', '').strip()
          rating_score_str = request.form.get('rating_score', '').strip()
          # --- Yêu cầu: Thêm date_posted, set là ngày hiện tại ---
          current_date = datetime.now().date() # Lấy ngày hiện tại

          if not review_id:
               return jsonify({'success': False, 'error': 'Thiếu Review ID để cập nhật.'}), 400

          # Validate và chuyển đổi điểm số
          try:
               # Schema REVIEW có rating_score là TINYINT NOT NULL, nên không cho phép NULL
               rating_score = int(rating_score_str) # Bắt buộc phải là số nguyên
               if rating_score < 1 or rating_score > 10:
                    return jsonify({'success': False, 'error': 'Điểm đánh giá phải từ 1 đến 10.'}), 400
          except ValueError:
               return jsonify({'success': False, 'error': 'Định dạng điểm đánh giá không hợp lệ (phải là số nguyên).'}), 400


          sql = "UPDATE REVIEWS SET comment = ?, rating_score = ?, date_posted = ? WHERE review_id = ?"
          params = (comment, rating_score, current_date, review_id) # Thêm current_date vào params
          cursor.execute(sql, params)
          conn.commit()
          return jsonify({'success': True, 'message': f'Review "{review_id}" đã được cập nhật thành công!'})

     except pyodbc.Error as err:
          print(f"Error during update_review (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': 'Đã xảy ra lỗi cơ sở dữ liệu khi cập nhật review.'}), 500

     finally:
          if cursor: cursor.close()
          if conn: conn.close()


# --- Route API để xử lý xóa Review bằng AJAX API ---
# Nhận review_id
@app.route('/api/delete_review', methods=['POST'])
def delete_review_api():
     """Xử lý xóa review và trả về JSON."""
     conn = get_db_connection()
     if not conn:
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

     cursor = conn.cursor()
     try:
          review_id = request.form.get('review_id', '').strip()

          if not review_id:
               return jsonify({'success': False, 'error': 'Thiếu Review ID để xóa.'}), 400

          # --- Thực hiện câu lệnh DELETE trực tiếp cho Review ---
          # Hoặc bạn có thể tạo một thủ tục lưu trữ DeleteReview và gọi ở đây.
          sql = "DELETE FROM REVIEWS WHERE review_id = ?"
          params = (review_id,)
          cursor.execute(sql, params)
          conn.commit()

          if cursor.rowcount == 0:
               return jsonify({'success': False, 'error': f'Không tìm thấy Review với ID "{review_id}" để xóa.'}), 404 # 404 Not Found
          else:
               return jsonify({'success': True, 'message': f'Review "{review_id}" đã được xóa thành công!'})

     except pyodbc.IntegrityError as err:
          print(f"Integrity error deleting review (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': 'Không thể xóa review này vì nó đang được tham chiếu bởi dữ liệu khác.'}), 400 # 400 Bad Request

     except pyodbc.Error as err:
          print(f"Error during delete_review (API): {err}")
          conn.rollback()
          return jsonify({'success': False, 'error': 'Đã xảy ra lỗi cơ sở dữ liệu khi xóa review.'}), 500

     finally:
          if cursor: cursor.close()
          if conn: conn.close()

# --- Helper function for applying search filter ---
def apply_search_filter(data, search_query, search_fields):
     """Lọc dữ liệu (list of dicts) dựa trên search_query và các trường tìm kiếm."""
     if not search_query or not data:
          return data # Trả về dữ liệu gốc nếu không có query hoặc dữ liệu

     search_lower = search_query.lower()
     filtered_data = []
     for row in data:
          # Kiểm tra xem search_query có xuất hiện trong bất kỳ search_fields nào của hàng không
          if any(
               row.get(field) is not None and search_lower in str(row[field]).lower()
               for field in search_fields if field in row # Chỉ kiểm tra các trường tồn tại trong hàng
          ):
               filtered_data.append(row)
     return filtered_data

# --- Helper function for applying sort ---
def apply_sort(data, sort_by_column, column_names):
     """Sắp xếp dữ liệu (list of dicts) dựa trên sort_by_column."""
     if not sort_by_column or not data or sort_by_column not in column_names:
          return data # Trả về dữ liệu gốc nếu không có cột sắp xếp hoặc dữ liệu

     # Xác định thứ tự sắp xếp (ví dụ: giảm dần cho điểm đánh giá)
     reverse_sort = False
     if sort_by_column == 'rating_score':
          reverse_sort = True # Điểm đánh giá sắp xếp giảm dần

     # Sắp xếp dữ liệu, xử lý giá trị None (đẩy về cuối)
     sorted_data = sorted(data, key=lambda row: (
          row.get(sort_by_column) is None, # Đẩy None values về cuối
          row.get(sort_by_column) # Sắp xếp theo giá trị thực tế
     ), reverse=reverse_sort)

     return sorted_data


# --- Route cho trang demo gọi thủ tục và hiển thị dữ liệu ---
# Xử lý GET để hiển thị form trống, POST để gọi thủ tục và hiển thị kết quả
@app.route('/procedures_demo', methods=['GET', 'POST'])
def procedures_demo():
     """Render trang demo gọi thủ tục và hiển thị dữ liệu, xử lý gọi thủ tục."""
     conn = get_db_connection()
     # Nếu không kết nối được, render trang trống và hiển thị flash message lỗi kết nối
     if not conn:
          return render_template('procedures_demo.html', best_seller_data=None, comment_filter_data=None)

     cursor = conn.cursor()
     best_seller_data = None
     comment_filter_data = None
     best_seller_input_values = None # Lưu giá trị input cho form 1
     comment_filter_input_values = None # Lưu giá trị input cho form 2

     # Lấy giá trị search/sort từ request (cho cả GET và POST) để điền lại vào form
     best_seller_search_query = request.form.get('bs_search', request.args.get('bs_search', '')).strip()
     best_seller_sort_by = request.form.get('bs_sort', request.args.get('bs_sort', 'GameName')) # Mặc định sắp xếp theo Tên Game

     comment_filter_search_query = request.form.get('cf_search', request.args.get('cf_search', '')).strip()
     comment_filter_sort_by = request.form.get('cf_sort', request.args.get('cf_sort', 'rating_score')) # Mặc định sắp xếp theo Điểm


     if request.method == 'POST':
          action = request.form.get('action') # Xác định form nào được submit

          if action == 'call_best_seller':
               # --- Xử lý gọi Thủ tục best_seller ---
               game_tags = request.form.get('game_tags', '').strip()
               g_publisher = request.form.get('g_publisher', '').strip()

               best_seller_input_values = {'game_tags': game_tags, 'g_publisher': g_publisher} # Lưu input

               # Xử lý chuỗi rỗng thành NULL cho SP (để kích hoạt logic IS NULL trong SP)
               game_tags_for_sp = game_tags if game_tags else None
               g_publisher_for_sp = g_publisher if g_publisher else None

               try:
                    # --- Gọi Thủ tục SQL best_seller ---
                    sql_call = "{CALL best_seller(?, ?)}"
                    params = (game_tags_for_sp, g_publisher_for_sp)

                    cursor.execute(sql_call, params)
                    # Lấy dữ liệu và tên cột
                    best_seller_column_names = [column[0] for column in cursor.description]
                    best_seller_data = cursor.fetchall()
                    # Chuyển đổi kết quả sang list of dictionaries
                    best_seller_data = [dict(zip(best_seller_column_names, row)) for row in best_seller_data]

                    # --- Áp dụng Search và Sort ở Python ---
                    # Các trường tìm kiếm cho best_seller: 'GameName', 'Publisher'
                    best_seller_data = apply_search_filter(best_seller_data, best_seller_search_query, ['GameName', 'Publisher'])
                    # Áp dụng sắp xếp
                    best_seller_data = apply_sort(best_seller_data, best_seller_sort_by, best_seller_column_names)


               except pyodbc.ProgrammingError as err:
                    print(f"Error calling best_seller: {err}")
                    error_message = str(err)
                    # Bắt các lỗi THROW từ SP best_seller
                    if 'Tag not found.' in error_message:
                         flash(f'Lỗi: Tag "{game_tags}" không tồn tại.', 'danger')
                    elif 'Publisher not found.' in error_message:
                         flash(f'Lỗi: Nhà phát hành "{g_publisher}" không tồn tại.', 'danger')
                    else:
                         flash(f'Lỗi CSDL khi gọi best_seller: {error_message}', 'danger')
                    best_seller_data = [] # Gán rỗng nếu có lỗi từ SP

               except pyodbc.Error as err:
                    print(f"General database error calling best_seller: {err}")
                    flash(f'Đã xảy ra lỗi CSDL khi gọi best_seller: {str(err)}', 'danger')
                    best_seller_data = [] # Gán rỗng nếu có lỗi


          elif action == 'call_comment_filter':
               # --- Xử lý gọi Thủ tục CommentFilter ---
               minimum_score_str = request.form.get('minimum_score', '').strip()
               game_name = request.form.get('game_name', '').strip()

               comment_filter_input_values = {'minimum_score': minimum_score_str, 'game_name': game_name} # Lưu input

               # Xử lý chuỗi rỗng cho Game Name
               game_name_for_sp = game_name if game_name else None # SP CommentFilter kiểm tra GameName NULL/rỗng

               try:
                    # Chuyển đổi điểm tối thiểu sang tinyint
                    minimum_score = int(minimum_score_str) if minimum_score_str else None # SP CommentFilter kiểm tra MinScore NULL
                    if minimum_score is not None and (minimum_score < 1 or minimum_score > 10):
                         flash('Điểm tối thiểu phải từ 1 đến 10.', 'warning') # Validate frontend trước
                         # Nếu validation Python thất bại, không gọi SP
                         comment_filter_data = [] # Gán rỗng để không hiển thị kết quả cũ
                    else:
                         # --- Gọi Thủ tục SQL CommentFilter (đã sửa để trả về ReviewID) ---
                         sql_call = "{CALL CommentFilter(?, ?)}"
                         params = (minimum_score, game_name_for_sp) # GameName là tham số thứ 2 trong SP CommentFilter

                         cursor.execute(sql_call, params)
                         # Lấy dữ liệu và tên cột
                         comment_filter_column_names = [column[0] for column in cursor.description]
                         comment_filter_data = cursor.fetchall()
                         # Chuy đổi kết quả sang list of dictionaries
                         comment_filter_data = [dict(zip(comment_filter_column_names, row)) for row in comment_filter_data]

                         # --- Áp dụng Search và Sort ở Python ---
                         # Các trường tìm kiếm cho CommentFilter: 'user_name', 'comment'
                         comment_filter_data = apply_search_filter(comment_filter_data, comment_filter_search_query, ['user_name', 'comment'])
                         # Áp dụng sắp xếp
                         comment_filter_data = apply_sort(comment_filter_data, comment_filter_sort_by, comment_filter_column_names)


               except ValueError:
                    flash('Định dạng Điểm tối thiểu không hợp lệ (phải là số nguyên).', 'danger')
                    comment_filter_data = [] # Gán rỗng để không hiển thị kết quả cũ

               except pyodbc.ProgrammingError as err:
                    print(f"Error calling CommentFilter: {err}")
                    error_message = str(err)
                    # Bắt các lỗi THROW từ SP CommentFilter
                    if 'Minimum score is out of range or NULL.' in error_message:
                         flash('Lỗi: Điểm tối thiểu không hợp lệ.', 'danger')
                    elif 'Game name cannot be NULL or empty.' in error_message:
                         flash('Lỗi: Tên game không được để trống.', 'danger')
                    elif 'Game not found.' in error_message:
                         flash(f'Lỗi: Game "{game_name}" không tìm thấy.', 'danger')
                    else:
                         flash(f'Lỗi CSDL khi gọi CommentFilter: {error_message}', 'danger')
                    comment_filter_data = [] # Gán rỗng nếu có lỗi từ SP


               except pyodbc.Error as err:
                    print(f"General database error calling CommentFilter: {err}")
                    flash(f'Đã xảy ra lỗi CSDL khi gọi CommentFilter: {str(err)}', 'danger')
                    comment_filter_data = [] # Gán rỗng nếu có lỗi


     # Đóng kết nối CSDL
     if cursor: cursor.close()
     if conn: conn.close()

    # Render template demo, truyền dữ liệu kết quả và giá trị input cũ
     return render_template('procedures_demo.html',
                              best_seller_data=best_seller_data,
                              comment_filter_data=comment_filter_data,
                              best_seller_input=best_seller_input_values,
                              comment_filter_input=comment_filter_input_values,
                              # Truyền lại giá trị search/sort để điền vào form sau khi submit
                              bs_search_query=best_seller_search_query,
                              bs_sort_by=best_seller_sort_by,
                              cf_search_query=comment_filter_search_query,
                              cf_sort_by=comment_filter_sort_by)

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
    # Để Flask tự động phát hiện ứng dụng, đặt FLASK_APP=app.py trong terminal
    # và chạy flask run.
    # Hoặc bỏ comment dòng dưới nếu bạn chạy trực tiếp file này (nhưng flask run tốt hơn)
    # app.run(debug=True)
    pass # Dòng này để không chạy trực tiếp khi import