USE STEAM_PROJECT; -- Đảm bảo tên CSDL khớp với của bạn
GO

-- Xóa hàm nếu tồn tại
IF OBJECT_ID('dbo.CountGamesReleasedInYearWithDummyLoop', 'FN') IS NOT NULL
    DROP FUNCTION dbo.CountGamesReleasedInYearWithDummyLoop;
GO

-- Tạo Hàm vô hướng
-- Đếm số lượng game phát hành trong một năm cụ thể và bao gồm một vòng lặp WHILE minh họa.
CREATE FUNCTION dbo.CountGamesReleasedInYearWithDummyLoop
(
    @InputYear INT -- Tham số đầu vào: Năm cần đếm
)
RETURNS INT -- Hàm trả về một giá trị kiểu INT (số lượng)
AS
BEGIN
    -- Khai báo biến để lưu kết quả đếm
    DECLARE @GameCount INT;
    -- Khai báo biến cho vòng lặp minh họa
    DECLARE @LoopCounter INT = 1;
    DECLARE @DummyValue INT = 0; -- Biến này sẽ được thay đổi trong vòng lặp minh họa

    -- --- Kiểm tra tham số đầu vào ---
    -- Sử dụng IF để kiểm tra năm đầu vào có hợp lệ không (ví dụ: lớn hơn năm 1900 và nhỏ hơn hoặc bằng năm hiện tại + 1)
    IF @InputYear < 1900 OR @InputYear > YEAR(GETDATE()) + 1
    BEGIN
        -- Nếu năm không hợp lệ, trả về 0 ngay.
        RETURN 0;
    END

    -- --- Truy vấn dữ liệu và tính toán chính (sử dụng Set-Based Count) ---
    -- Đếm số lượng game trong bảng GAMES có năm phát hành khớp với @InputYear
    -- Chỉ thực hiện nếu năm hợp lệ
    SELECT
        @GameCount = COUNT(*)
    FROM
        [dbo].[GAMES]
    WHERE
        -- Sử dụng hàm YEAR() để trích xuất năm từ cột date_released
        YEAR(date_released) = @InputYear
        AND date_released IS NOT NULL; -- Đảm bảo ngày phát hành không NULL

    -- Nếu không có game nào trong năm đó, COUNT(*) sẽ trả về 0, không phải NULL, nên không cần ISNULL cho trường hợp này.

    -- --- Vòng lặp WHILE minh họa (Dummy Loop) ---
    -- Vòng lặp này chỉ để đáp ứng yêu cầu về cấu trúc LOOP trong hàm.
    -- Nó không tham gia vào việc tính toán @GameCount.
    WHILE @LoopCounter <= 5 -- Lặp lại 5 lần
    BEGIN
        -- Thực hiện một thao tác đơn giản (không ảnh hưởng đến CSDL hoặc kết quả chính)
        SET @DummyValue = @DummyValue + @LoopCounter; -- Ví dụ: cộng dồn bộ đếm
        SET @LoopCounter = @LoopCounter + 1; -- Tăng bộ đếm vòng lặp
    END
    -- Sau khi vòng lặp kết thúc, @DummyValue chứa tổng từ 1 đến 5, nhưng chúng ta không sử dụng nó.

    -- --- Trả về kết quả ---
    -- Trả về số lượng game đã đếm
    RETURN @GameCount;

END;
GO

-- --- Ví dụ cách gọi Hàm trong SSMS ---
/*
-- Thay thế 2024 bằng một năm có game phát hành trong CSDL của bạn
SELECT dbo.CountGamesReleasedInYearWithDummyLoop(2024) AS GamesIn2024;

-- Ví dụ với năm không hợp lệ (sẽ trả về 0)
SELECT dbo.CountGamesReleasedInYearWithDummyLoop(1800) AS GamesIn1800;
SELECT dbo.CountGamesReleasedInYearWithDummyLoop(3000) AS GamesIn3000;
*/