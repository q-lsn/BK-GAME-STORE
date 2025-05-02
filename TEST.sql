USE STEAM_PROJECT; -- Đảm bảo tên CSDL khớp với của bạn
GO

-- Sử dụng CREATE OR ALTER PROCEDURE để tạo hoặc sửa đổi thủ tục
CREATE OR ALTER PROCEDURE CalculateUserSpending
    @InputUserID INT, -- Tham số đầu vào: ID của người dùng
    @StartDate DATE,  -- Tham số đầu vào: Ngày bắt đầu khoảng thời gian
    @EndDate DATE,    -- Tham số đầu vào: Ngày kết thúc khoảng thời gian
    @TotalSpending DECIMAL(18, 2) OUTPUT, -- Tham số đầu ra: Tổng chi tiêu
    @BuyTransactionCount INT OUTPUT -- Tham số đầu ra: Số lượng giao dịch mua
AS
BEGIN
    SET NOCOUNT ON; -- Ngăn chặn trả về số hàng bị ảnh hưởng bởi các lệnh

    -- --- Kiểm tra tham số đầu vào ---

    -- Kiểm tra ID người dùng có hợp lệ không (tồn tại trong bảng USER)
    IF NOT EXISTS (SELECT 1 FROM [dbo].[USER] WHERE user_id = @InputUserID)
    BEGIN
        -- THROW một lỗi tùy chỉnh nếu UserID không tồn tại
        THROW 50000, 'Invalid User ID. User not found.', 1;
        RETURN; -- Thoát khỏi thủ tục
    END

    -- Kiểm tra ngày bắt đầu không lớn hơn ngày kết thúc
    IF @StartDate > @EndDate
    BEGIN
        -- THROW một lỗi tùy chỉnh
        THROW 50000, 'Start Date cannot be after End Date.', 1;
        RETURN; -- Thoát khỏi thủ tục
    END

    -- Khởi tạo các biến đầu ra
    SET @TotalSpending = 0.00;
    SET @BuyTransactionCount = 0;

    -- --- Truy vấn dữ liệu và sử dụng LOOP (CURSOR) để tính toán ---

    -- Khai báo biến để lưu dữ liệu từ mỗi hàng trong CURSOR
    DECLARE @TransactionAmount DECIMAL(18, 2);
    DECLARE @TransactionType VARCHAR(50);
    DECLARE @CurrentTransactionDate DATETIME; -- Sử dụng DATETIME vì cột transaction_date là DATETIME

    -- Khai báo CURSOR
    DECLARE TransactionCursor CURSOR FOR
    SELECT
        amount,
        transaction_type,
        transaction_date
    FROM
        [dbo].[TRANSACTION]
    WHERE
        user_id = @InputUserID
        AND transaction_date >= @StartDate
        AND transaction_date < DATEADD(day, 1, @EndDate); -- Lấy cả ngày cuối @EndDate
        -- Lưu ý: Sử dụng DATEADD(day, 1, @EndDate) và < để bao gồm toàn bộ ngày @EndDate.
        -- Hoặc nếu cột transaction_date là DATE, chỉ cần AND transaction_date <= @EndDate;

    -- Mở CURSOR
    OPEN TransactionCursor;

    -- Đọc hàng đầu tiên từ CURSOR vào các biến
    FETCH NEXT FROM TransactionCursor INTO @TransactionAmount, @TransactionType, @CurrentTransactionDate;

    -- Bắt đầu vòng lặp (LOOP) qua các hàng
    WHILE @@FETCH_STATUS = 0 -- @@FETCH_STATUS = 0 nghĩa là FETCH thành công
    BEGIN
        -- --- Sử dụng IF để kiểm tra điều kiện ---

        -- Kiểm tra nếu loại giao dịch là 'Buy'
        IF @TransactionType = 'Buy'
        BEGIN
            -- Cộng vào tổng chi tiêu (Giả định giao dịch 'Buy' có amount > 0)
            SET @TotalSpending = @TotalSpending + @TransactionAmount;

            -- Tăng số lượng giao dịch mua
            SET @BuyTransactionCount = @BuyTransactionCount + 1;
        END
        -- Bạn có thể thêm các IF/ELSE IF khác để xử lý các loại giao dịch khác nếu cần
        -- ELSE IF @TransactionType = 'Refund'
        -- BEGIN
        --     SET @TotalSpending = @TotalSpending - @TransactionAmount;
        -- END
        -- ELSE
        -- BEGIN
        --     -- Bỏ qua các loại giao dịch khác không phải Buy
        -- END

        -- Đọc hàng tiếp theo từ CURSOR
        FETCH NEXT FROM TransactionCursor INTO @TransactionAmount, @TransactionType, @CurrentTransactionDate;
    END

    -- Đóng CURSOR
    CLOSE TransactionCursor;

    -- Giải phóng tài nguyên CURSOR
    DEALLOCATE TransactionCursor;

    -- Thủ tục kết thúc. Các giá trị của @TotalSpending và @BuyTransactionCount
    -- sẽ được trả về thông qua tham số OUTPUT.
END;