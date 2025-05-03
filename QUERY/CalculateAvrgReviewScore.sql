USE STEAM_PROJECT;
GO

CREATE FUNCTION CalculateAvrgReviewScore
(
    @InputGameID            VARCHAR(6)  -- input, id trò chơi
)
RETURNS @Result TABLE (
    GameID                  VARCHAR(6),
    GameName                VARCHAR(80),
    AverageRaiting          DECIMAL(18, 2),
    TotalsReviews           INT,
    RatingCategory          VARCHAR(80),
    PositiveReviewPercent   DECIMAL(18, 2)
)
AS
BEGIN
    DECLARE @GameName           VARCHAR(80)
    DECLARE @TotalRating        DECIMAL(18, 2) = 0.00
    DECLARE @ReviewCount        INT = 0
    DECLARE @PositiveReviews    INT = 0
    DECLARE @CurrentRating      INT
    DECLARE @AverageRaiting     DECIMAL(18, 2)

    SELECT @GameName = game_name
    FROM GAMES
    WHERE game_id = @InputGameID

    IF @GameName IS NULL
    BEGIN
        INSERT INTO @Result VALUES (0, 'Game does not exist', 0, 0, 'Unknown', 0)
        RETURN
    END

    IF NOT EXISTS (SELECT 1 FROM REVIEWS WHERE game_review = @InputGameID)
    BEGIN
        INSERT INTO @Result VALUES (0, 'Game not rated yet', 0, 0, 'Unknown', 0)
        RETURN
    END

    DECLARE ReviewCursor CURSOR FOR 
    SELECT rating_score
    FROM REVIEWS 
    WHERE game_review = @InputGameID

    OPEN ReviewCursor
    FETCH NEXT FROM ReviewCursor INTO @CurrentRating

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @TotalRating = @TotalRating + @CurrentRating
        SET @ReviewCount = @ReviewCount + 1

        IF @CurrentRating >= 5
            SET @PositiveReviews = @PositiveReviews + 1

        FETCH NEXT FROM ReviewCursor INTO @CurrentRating
    END

    CLOSE ReviewCursor
    DEALLOCATE ReviewCursor

    IF @ReviewCount > 0
        SET @AverageRaiting = @TotalRating / @ReviewCount
    ELSE 
        SET @AverageRaiting = 0

    DECLARE @Category VARCHAR(80)
    SET @Category = CASE 
        WHEN @AverageRaiting >= 8.00 THEN '★★★★★'
        WHEN @AverageRaiting >= 6.00 THEN '★★★★'
        WHEN @AverageRaiting >= 4.00 THEN '★★★'
        WHEN @AverageRaiting >= 2.00 THEN '★★'
        ELSE '★'
    END

    DECLARE @PositivePercent DECIMAL (18, 2) = 0.00
    IF @ReviewCount > 0
        SET @PositivePercent = (@PositiveReviews * 100.00) / @ReviewCount

    INSERT INTO @Result
    VALUES (
        @InputGameID,
        @GameName,
        @AverageRaiting,
        @ReviewCount,
        @Category,
        @PositivePercent
    )

    RETURN
END