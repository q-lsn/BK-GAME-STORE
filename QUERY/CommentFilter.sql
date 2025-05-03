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

	SELECT r.review_id, ISNULL(u.user_name, '[Deleted Account]') AS user_name, r.comment, r.rating_score
	FROM(
		GAMES g JOIN REVIEWS r ON g.game_id = r.game_review
		LEFT JOIN [USER] u ON r.feedback_user = u.account_id
	)
	WHERE g.game_name = @GameName AND rating_score >= @MinimumScore
	ORDER BY r.rating_score DESC;
	PRINT 'Comment filtering sucessfully.';
END;