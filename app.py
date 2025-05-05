from flask import Flask, render_template, request, flash, jsonify, redirect, url_for
import pyodbc
from decimal import Decimal
from datetime import datetime
import json # Import json module to parse potential JSON error messages

# --- Cấu hình ứng dụng Flask ---
app = Flask(__name__)
# Đảm bảo secret_key là duy nhất và giữ bí mật
app.secret_key = 'your_super_secret_key_replace_this' # <<< THAY THẾ CHUỖI NÀY!
db_config = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-7175T46;DATABASE=STEAM_PROJECT;UID=sa;PWD=270205'

def get_db_connection():
     """Thiết lập và trả về kết nối đến cơ sở dữ liệu."""
     conn = None
     try:
          conn = pyodbc.connect(db_config)
          return conn
     except pyodbc.Error as err:
          print(f"Database connection error: {err}")
          # Extract SQL Native Client error message if available
          sqlstate = err.args[0]
          if isinstance(err.args[1], str):
              native_error_msg = err.args[1]
              # Try to find the specific SQL Server error message pattern {sqlstate: [SQL Native Client] message}
              import re
              match = re.search(r'{.*?}(.*)', native_error_msg)
              if match:
                  error_detail = match.group(1).strip()
              else:
                  error_detail = native_error_msg
          else:
               error_detail = str(err)

          flash(f'Lỗi kết nối cơ sở dữ liệu: {error_detail}', 'danger')
          return None

def parse_sql_error(err):
    """Phân tích lỗi pyodbc để lấy thông báo lỗi THROW từ SQL Server."""
    error_message = str(err)
    # Kiểm tra nếu lỗi là ProgrammingError và chứa mã lỗi 50000 từ THROW
    if isinstance(err, pyodbc.ProgrammingError) and '[50000]' in error_message:
        try:
            # Tách thông báo lỗi tùy chỉnh từ THROW
            # Định dạng thường là: ({'42000'}, 50000, b"Message", 0, 0, 0, 0)
            # Hoặc chuỗi lỗi dạng: '...[50000] Message [SQL State]'
            parts = error_message.split('[50000]')
            if len(parts) > 1:
                # Lấy phần sau [50000], loại bỏ phần mã SQL State cuối cùng nếu có
                sp_error = parts[-1].split('[')[0].strip()
                return sp_error
        except Exception as e:
            print(f"Error parsing SQL 50000 error message: {e}")
            # Fallback to full error message if parsing fails
            return error_message
    # Trả về toàn bộ thông báo lỗi nếu không phải lỗi THROW 50000
    return error_message


# --- Route Trang Chủ ---
@app.route('/')
def index():
     """Render trang chủ."""
     # Thêm route /reports vào trang chủ
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
               # Gọi SP GetGamesFilteredSorted
               cursor.execute("{CALL GetGamesFilteredSorted}");
               column_names = [column[0] for column in cursor.description]
               data = cursor.fetchall()
               data = [dict(zip(column_names, row)) for row in data]

          except pyodbc.Error as err:
               print(f"Error executing GetGamesFilteredSorted: {err}")
               flash(f'Không thể lấy dữ liệu danh sách game: {parse_sql_error(err)}', 'danger')
          finally:
               if cursor: cursor.close()
               if conn: conn.close()
     return render_template('index.html', data=data)

# --- Route API Thêm/Sửa/Xóa Game (Giữ nguyên, chỉ cập nhật cách xử lý lỗi) ---

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
          publisher_name = request.form.get('p_id', '').strip() # API nhận Publisher Name
          released_str = request.form.get('released', '').strip()

          if not g_name or not publisher_name:
               return jsonify({'success': False, 'error': 'Tên Game và Tên Nhà phát hành là bắt buộc.'}), 400

          try:
               released_date = datetime.strptime(released_str, '%Y-%m-%d').date() if released_str else None
          except ValueError:
               return jsonify({'success': False, 'error': 'Định dạng ngày phát hành không hợp lệ. Vui lòng sử dụng YYYY-MM-DD.'}), 400

          # Truyền giá trị rỗng thành None hoặc giá trị mặc định cho SP nếu cần
          g_engine_for_sp = g_engine if g_engine else None # SP có default 'Source'
          g_description_for_sp = g_description if g_description else None # SP có default 'No description.'


          sql_call = "{CALL InsertGame(?, ?, ?, ?, ?)}"
          # Tham số phải theo đúng thứ tự trong SP: @GName, @GEngine, @GDescription, @GPublisher (Name), @Released
          params = (g_name, g_engine_for_sp, g_description_for_sp, publisher_name, released_date)

          cursor.execute(sql_call, params)
          conn.commit()

          return jsonify({'success': True, 'message': f'Game "{g_name}" đã được thêm thành công!'}), 200

     except pyodbc.ProgrammingError as err:
          conn.rollback()
          sp_error = parse_sql_error(err)
          print(f"Database error calling InsertGame (API): {err}")
          # Các lỗi THROW từ SP InsertGame thường là lỗi dữ liệu/logic đầu vào
          status_code = 400 # Bad Request
          if 'Publisher not found.' in sp_error:
               status_code = 404 # Not Found
          elif 'Game already exists.' in sp_error:
               status_code = 409 # Conflict

          return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), status_code

     except pyodbc.Error as err:
          conn.rollback()
          print(f"General database error during insert (API): {err}")
          return jsonify({'success': False, 'error': f'Đã xảy ra lỗi cơ sở dữ liệu khi thêm game: {parse_sql_error(err)}'}), 500 # Internal Server Error
     finally:
          if cursor: cursor.close()
          if conn: conn.close()


@app.route('/api/update_game', methods=['POST'])
def update_game_api():
     """Xử lý cập nhật game bằng UpdateGameInfo SP."""
     conn = get_db_connection()
     if not conn:
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
          # Tham số theo đúng thứ tự trong SP: @GID, @GName, @GDescription
          params = (game_id, g_name_for_sp, g_description_for_sp)
          cursor.execute(sql_call, params)
          conn.commit()

          # Kiểm tra số hàng bị ảnh hưởng để xác nhận cập nhật thành công
          # (Mặc dù SP đã kiểm tra game_id tồn tại)
          # if cursor.rowcount == 0:
          #      # SP THROW Game not found sẽ bắt ở except, nên kiểm tra này có thể không cần
          #      return jsonify({'success': False, 'error': f'Không tìm thấy Game ID "{game_id}".'}), 404

          return jsonify({'success': True, 'message': f'Thông tin game "{game_id}" đã được cập nhật thành công!'}), 200

     except pyodbc.ProgrammingError as err:
          conn.rollback()
          sp_error = parse_sql_error(err)
          print(f"Database error calling UpdateGameInfo (API): {err}")
          status_code = 400 # Bad Request
          if 'Game not found.' in sp_error:
               status_code = 404 # Not Found
          elif "Game's name already used" in sp_error:
              status_code = 409 # Conflict

          return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), status_code

     except pyodbc.Error as err:
          conn.rollback()
          print(f"General database error during update (API): {err}")
          return jsonify({'success': False, 'error': f'Đã xảy ra lỗi cơ sở dữ liệu khi cập nhật game: {parse_sql_error(err)}'}), 500
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
          # API nhận item_id, tương ứng với GID trong DeleteGame SP
          item_id = request.form.get('item_id', '').strip()
          if not item_id:
               return jsonify({'success': False, 'error': 'Thiếu Game ID để xóa.'}), 400

          sql_call = "{CALL DeleteGame(?)}"
          params = (item_id,)
          cursor.execute(sql_call, params)
          conn.commit()

          # Kiểm tra số hàng bị ảnh hưởng để xác nhận xóa thành công
          # if cursor.rowcount == 0:
          #      # SP THROW Game not found sẽ bắt ở except
          #      return jsonify({'success': False, 'error': f'Không tìm thấy Game ID "{item_id}".'}), 404


          return jsonify({'success': True, 'message': f'Game "{item_id}" đã được xóa thành công!'}), 200

     except pyodbc.ProgrammingError as err:
          conn.rollback()
          sp_error = parse_sql_error(err)
          print(f"Database error calling DeleteGame (API): {err}")
          status_code = 400
          if 'Game not found.' in sp_error:
              status_code = 404 # Not Found
          elif 'Cannot delete this comment' in sp_error: # Bắt lỗi khóa ngoại từ SP DeleteComment (mặc dù API này là cho game)
               status_code = 409 # Conflict

          return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), status_code

     except pyodbc.IntegrityError as err:
          # Lỗi khóa ngoại trực tiếp từ CSDL nếu SP không bắt
          conn.rollback()
          print(f"Integrity error deleting data (API): {err}")
          return jsonify({'success': False, 'error': f'Không thể xóa game này vì nó đang được tham chiếu bởi dữ liệu khác. Chi tiết: {parse_sql_error(err)}'}), 409 # Conflict
     except pyodbc.Error as err:
          conn.rollback()
          print(f"General database error during delete (API): {err}")
          return jsonify({'success': False, 'error': f'Đã xảy ra lỗi cơ sở dữ liệu khi xóa game: {parse_sql_error(err)}'}), 500
     finally:
          if cursor: cursor.close()
          if conn: conn.close()


# --- Route cho trang demo gọi hàm và hiển thị dữ liệu (Giữ nguyên, chỉ cập nhật cách xử lý lỗi) ---
@app.route('/functions_demo', methods=['GET', 'POST'])
def functions_demo():
     """Render trang demo gọi hàm và hiển thị dữ liệu."""
     conn = get_db_connection()
     # Nếu không kết nối được CSDL, flash message đã được tạo trong get_db_connection
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

                         # Xử lý các giá trị trả về đặc biệt từ hàm SQL
                         if total_spending == Decimal('-1.01'):
                              func1_result = {'success': False, 'error': f'Lỗi từ CSDL: User ID "{user_id}" không tồn tại.'}
                         elif total_spending == Decimal('-1.02'):
                              func1_result = {'success': False, 'error': f'Lỗi từ CSDL: User ID "{user_id}" chưa kích hoạt WALLET.'}
                         elif total_spending == Decimal('-1.03'):
                              func1_result = {'success': False, 'error': 'Lỗi từ CSDL: Ngày bắt đầu không thể sau ngày kết thúc.'}
                         else:
                              func1_result = {'success': True, 'total_spending': total_spending}

                    except ValueError:
                         flash('Định dạng ngày không hợp lệ. Vui lòng sử dụng YYYY-MM-DD.', 'danger')
                         func1_result = {'success': False, 'error': 'Định dạng ngày không hợp lệ.'}

                    except pyodbc.Error as err:
                         print(f"Error calling CalculateUserSpending: {err}")
                         flash(f'Đã xảy ra lỗi CSDL khi gọi hàm CalculateUserSpending: {parse_sql_error(err)}', 'danger')
                         func1_result = {'success': False, 'error': f'Lỗi CSDL: {parse_sql_error(err)}'}


          elif action == 'call_func2':
               game_id = request.form.get('game_id', '').strip()
               func2_input_values = {'game_id': game_id}

               if not game_id:
                    flash('Vui lòng nhập Game ID.', 'warning')
                    func2_result = {'success': False, 'error': 'Thiếu thông tin đầu vào.'}
               else:
                    try:
                         # Hàm CalculateAvrgReviewScore trả về bảng, nên dùng SELECT * FROM dbo.FunctionName
                         sql_call = "SELECT * FROM dbo.CalculateAvrgReviewScore(?)"
                         params = (game_id,)
                         cursor.execute(sql_call, params)

                         column_names = [column[0] for column in cursor.description]
                         func2_data = cursor.fetchall()
                         func2_data = [dict(zip(column_names, row)) for row in func2_data]

                         # Xử lý các hàng kết quả đặc biệt từ hàm SQL
                         if func2_data and func2_data[0].get('GameID') == '0': # Kiểm tra GameID '0' là dấu hiệu lỗi
                             if func2_data[0].get('GameName') == 'Game does not exist':
                                 func2_result = {'success': False, 'error': f'Lỗi từ CSDL: Game ID "{game_id}" không tồn tại.'}
                             elif func2_data[0].get('GameName') == 'Game not rated yet':
                                  func2_result = {'success': False, 'error': f'Lỗi từ CSDL: Game ID "{game_id}" chưa có đánh giá nào.'}
                             else: # Trường hợp lỗi khác không rõ
                                 func2_result = {'success': False, 'error': f'Lỗi từ CSDL: {func2_data[0].get("GameName", "Lỗi không xác định")}'}
                         else:
                              func2_result = {'success': True, 'results': func2_data}

                    except pyodbc.Error as err:
                         print(f"Error calling CalculateAvrgReviewScore: {err}")
                         flash(f'Đã xảy ra lỗi CSDL khi gọi hàm CalculateAvrgReviewScore: {parse_sql_error(err)}', 'danger')
                         func2_result = {'success': False, 'error': f'Lỗi CSDL: {parse_sql_error(err)}'}


     if cursor: cursor.close()
     if conn: conn.close()

     return render_template('functions_demo.html',
                              func1_result=func1_result,
                              func2_result=func2_result,
                              func1_input=func1_input_values,
                              func2_input=func2_input_values)


# --- Route và API cho trang Báo cáo (Reports) ---
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    """Render trang báo cáo và xử lý gọi SP BestSeller/CommentFilter."""
    conn = get_db_connection()
    # Nếu không kết nối được CSDL, flash message đã được tạo
    if not conn:
        return render_template('reports.html', best_seller_results=None, comment_filter_results=None)

    cursor = conn.cursor()
    best_seller_results = None
    comment_filter_results = None
    best_seller_input = {} # Lưu trữ giá trị input để giữ lại trên form sau POST
    comment_filter_input = {} # Lưu trữ giá trị input để giữ lại trên form sau POST

    if request.method == 'POST':
        action = request.form.get('action') # Hidden input để xác định form nào được submit

        if action == 'call_best_seller':
            game_tags = request.form.get('game_tags', '').strip()
            g_publisher = request.form.get('g_publisher', '').strip()

            best_seller_input = {'game_tags': game_tags, 'g_publisher': g_publisher}

            # Validation cơ bản trên server (ngoài SP)
            # Không có trường nào bắt buộc trong SP BestSeller, nhưng có thể thêm validation nếu muốn
            # if not game_tags and not g_publisher:
            #     flash('Vui lòng nhập ít nhất Tag game hoặc Tên nhà phát hành.', 'warning')
            #     # best_seller_results = {'success': False, 'error': 'Thiếu thông tin đầu vào.'}
            # else:
            try:
                sql_call = "{CALL best_seller(?, ?)}"
                # Truyền None cho các tham số rỗng để SP xử lý IS NULL
                params = (game_tags if game_tags else None, g_publisher if g_publisher else None)

                cursor.execute(sql_call, params)
                column_names = [column[0] for column in cursor.description]
                results_data = cursor.fetchall()
                best_seller_results = [dict(zip(column_names, row)) for row in results_data]

                # best_seller_results = {'success': True, 'data': results_data} # Có thể đóng gói trong dict nếu muốn

            except pyodbc.ProgrammingError as err:
                print(f"Database error calling best_seller: {err}")
                sp_error = parse_sql_error(err)
                flash(f'Lỗi khi gọi thủ tục Best Seller: {sp_error}', 'danger')
                # best_seller_results = {'success': False, 'error': sp_error}

            except pyodbc.Error as err:
                 print(f"General database error calling best_seller: {err}")
                 flash(f'Đã xảy ra lỗi CSDL khi gọi Best Seller: {parse_sql_error(err)}', 'danger')
                 # best_seller_results = {'success': False, 'error': parse_sql_error(err)}


        elif action == 'call_comment_filter':
            minimum_score_str = request.form.get('minimum_score', '').strip()
            game_name = request.form.get('game_name', '').strip()

            comment_filter_input = {'minimum_score': minimum_score_str, 'game_name': game_name}

            # Validation cơ bản trên server
            if not minimum_score_str or not game_name:
                 flash('Vui lòng nhập đầy đủ Điểm đánh giá tối thiểu và Tên game.', 'warning')
                 # comment_filter_results = {'success': False, 'error': 'Thiếu thông tin đầu vào.'}
            else:
                try:
                    minimum_score = int(minimum_score_str)
                    # SP CommentFilter có validation cho range 1-10, nhưng validate ở đây giúp bắt lỗi sớm
                    # if minimum_score < 1 or minimum_score > 10:
                    #      flash('Điểm đánh giá tối thiểu phải từ 1 đến 10.', 'warning')
                    # else:

                    sql_call = "{CALL CommentFilter(?, ?)}"
                    params = (minimum_score, game_name)

                    cursor.execute(sql_call, params)
                    column_names = [column[0] for column in cursor.description]
                    results_data = cursor.fetchall()
                    comment_filter_results = [dict(zip(column_names, row)) for row in results_data]

                    # comment_filter_results = {'success': True, 'data': results_data} # Có thể đóng gói trong dict nếu muốn

                except ValueError:
                    flash('Điểm đánh giá tối thiểu phải là một số nguyên hợp lệ.', 'warning')
                    # comment_filter_results = {'success': False, 'error': 'Định dạng điểm không hợp lệ.'}
                except pyodbc.ProgrammingError as err:
                    print(f"Database error calling CommentFilter: {err}")
                    sp_error = parse_sql_error(err)
                    flash(f'Lỗi khi gọi thủ tục Comment Filter: {sp_error}', 'danger')
                    # comment_filter_results = {'success': False, 'error': sp_error}
                except pyodbc.Error as err:
                     print(f"General database error calling CommentFilter: {err}")
                     flash(f'Đã xảy ra lỗi CSDL khi gọi Comment Filter: {parse_sql_error(err)}', 'danger')
                     # comment_filter_results = {'success': False, 'error': parse_sql_error(err)}


    if cursor: cursor.close()
    if conn: conn.close()

    return render_template('reports.html',
                           best_seller_results=best_seller_results,
                           comment_filter_results=comment_filter_results,
                           best_seller_input=best_seller_input,
                           comment_filter_input=comment_filter_input)


# --- Route API Cập nhật Bình luận ---
@app.route('/api/update_comment', methods=['POST'])
def update_comment_api():
     """Xử lý cập nhật bình luận bằng UpdateComment SP."""
     conn = get_db_connection()
     if not conn:
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

     cursor = conn.cursor()
     try:
          review_id = request.form.get('review_id', '').strip()
          new_comment = request.form.get('new_comment', '').strip()
          new_rating_str = request.form.get('new_rating', '').strip()

          if not review_id:
               return jsonify({'success': False, 'error': 'Thiếu Review ID để cập nhật.'}), 400

          # Chuyển đổi rating sang int, cho phép rỗng nếu không muốn cập nhật rating
          new_rating = None
          if new_rating_str:
               try:
                    new_rating = int(new_rating_str)
                    if new_rating < 1 or new_rating > 10:
                        return jsonify({'success': False, 'error': 'Điểm đánh giá phải từ 1 đến 10.'}), 400
               except ValueError:
                    return jsonify({'success': False, 'error': 'Định dạng điểm đánh giá không hợp lệ.'}), 400

          # Truyền None nếu giá trị rỗng để SP không cập nhật trường đó
          new_comment_for_sp = new_comment if new_comment else None
          new_rating_for_sp = new_rating


          sql_call = "{CALL UpdateComment(?, ?, ?)}"
          # Tham số theo đúng thứ tự trong SP: @ReviewID, @NewComment, @NewRating
          params = (review_id, new_comment_for_sp, new_rating_for_sp)

          cursor.execute(sql_call, params)
          conn.commit()

          return jsonify({'success': True, 'message': f'Bình luận "{review_id}" đã được cập nhật thành công!'}), 200

     except pyodbc.ProgrammingError as err:
          conn.rollback()
          sp_error = parse_sql_error(err)
          print(f"Database error calling UpdateComment (API): {err}")
          status_code = 400
          if 'Comment not found.' in sp_error:
              status_code = 404 # Not Found
          return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), status_code

     except pyodbc.Error as err:
          conn.rollback()
          print(f"General database error during update comment (API): {err}")
          return jsonify({'success': False, 'error': f'Đã xảy ra lỗi cơ sở dữ liệu khi cập nhật bình luận: {parse_sql_error(err)}'}), 500
     finally:
          if cursor: cursor.close()
          if conn: conn.close()


# --- Route API Xóa Bình luận ---
@app.route('/api/delete_comment', methods=['POST'])
def delete_comment_api():
     """Xử lý xóa bình luận bằng DeleteComment SP."""
     conn = get_db_connection()
     if not conn:
          return jsonify({'success': False, 'error': 'Could not connect to the database.'}), 500

     cursor = conn.cursor()
     try:
          # API nhận item_id, tương ứng với ReviewID trong DeleteComment SP
          item_id = request.form.get('item_id', '').strip()
          if not item_id:
               return jsonify({'success': False, 'error': 'Thiếu Review ID để xóa.'}), 400

          sql_call = "{CALL DeleteComment(?)}"
          params = (item_id,)
          cursor.execute(sql_call, params)
          conn.commit()

          return jsonify({'success': True, 'message': f'Bình luận "{item_id}" đã được xóa thành công!'}), 200

     except pyodbc.ProgrammingError as err:
          conn.rollback()
          sp_error = parse_sql_error(err)
          print(f"Database error calling DeleteComment (API): {err}")
          status_code = 400
          if 'Comment not found.' in sp_error:
              status_code = 404 # Not Found
          elif 'Cannot delete this comment' in sp_error:
              status_code = 409 # Conflict (lỗi khóa ngoại giả định)
          return jsonify({'success': False, 'error': f'Lỗi từ CSDL: {sp_error}'}), status_code

     except pyodbc.IntegrityError as err:
          # Lỗi khóa ngoại trực tiếp từ CSDL nếu SP không bắt
          conn.rollback()
          print(f"Integrity error deleting comment (API): {err}")
          return jsonify({'success': False, 'error': f'Không thể xóa bình luận này vì nó đang được tham chiếu bởi dữ liệu khác. Chi tiết: {parse_sql_error(err)}'}), 409 # Conflict
     except pyodbc.Error as err:
          conn.rollback()
          print(f"General database error during delete comment (API): {err}")
          return jsonify({'success': False, 'error': f'Đã xảy ra lỗi cơ sở dữ liệu khi xóa bình luận: {parse_sql_error(err)}'}), 500
     finally:
          if cursor: cursor.close()
          if conn: conn.close()


# --- Phần chạy ứng dụng ---
if __name__ == '__main__':
    # Thêm debug=True để dễ dàng phát triển
    app.run(debug=True)