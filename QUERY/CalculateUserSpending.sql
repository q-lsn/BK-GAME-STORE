USE STEAM_PROJECT;
GO

CREATE FUNCTION CalculateUserSpending
(
    @InputUserID INT,   -- input, id người dùng
    @StartDate DATE,    -- input, ngày bắt đầu
    @EndDate DATE		-- input, ngày kết thúc
)
RETURNS DECIMAL(18, 2)
AS
BEGIN
    IF NOT EXISTS (SELECT 1 FROM [USER] WHERE account_id = @InputUserID)
        -- User không tồn tại
        RETURN -1.01

    IF NOT EXISTS (SELECT 1 FROM WALLET WHERE user_id = @InputUserID)
        -- User chưa kích hoạt WALLET
        RETURN -1.02

    IF @StartDate > @EndDate
        -- Ngày bắt đầu không thể sau ngày kết thúc
        RETURN -1.03

    -- Biến cục bộ để lưu kết quả tính toán
    DECLARE @TotalSpending DECIMAL(18, 2) = 0.00;

    -- Biến lưu trữ dữ liệu từ mỗi hàng
    DECLARE @GamePrice DECIMAL(18, 2);
    DECLARE @Quantity INT;

    -- CURSOR
    DECLARE TransactionCursor CURSOR FOR
    SELECT
        pr.final_price,
        p.purchased_quantity
    FROM 
        [TRANSACTION] AS t
    JOIN
        _PURCHASE AS p ON p.transaction_id = t.transaction_id
    JOIN
        PRODUCT AS pr ON pr.product_id = p.product_id
    WHERE
        p.account_id = @InputUserID
        AND t.date_purchased >= @StartDate
        AND t.date_purchased < DATEADD(day, 1, @EndDate)
        AND t.trans_status = 'Completed'
        
    OPEN TransactionCursor;

    FETCH NEXT FROM TransactionCursor INTO @GamePrice, @Quantity;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @TotalSpending = @TotalSpending + @GamePrice * @Quantity;
        FETCH NEXT FROM TransactionCursor INTO @GamePrice, @Quantity;
    END

    CLOSE TransactionCursor;
    DEALLOCATE TransactionCursor;

    RETURN @TotalSpending;

END;