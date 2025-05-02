USE STEAM_PROJECT;
GO

CREATE OR ALTER PROCEDURE CommentFilter
	@MinimumScore	tinyint,
	@GameName		varchar(80)
AS
BEGIN
	-- Validate parameters
	IF @MinimumScore NOT BETWEEN 1 AND 10
		THROW 50000, 'Minimum score is out of range.', 1;
    IF NOT EXISTS (SELECT 1 FROM GAMES WHERE game_name = @GameName)
        THROW 50000, 'Game not found.', 1;

	SELECT ISNULL(user_name, '[Deleted Account]') AS user_name, comment, rating_score
	FROM(
		GAMES JOIN REVIEWS ON game_id = game_review
		LEFT JOIN [USER] ON feedback_user = account_id
	)
	WHERE game_name = @GameName AND rating_score >= @MinimumScore
	ORDER BY rating_score DESC;
	PRINT 'Comment filtering sucessfully.';
END;