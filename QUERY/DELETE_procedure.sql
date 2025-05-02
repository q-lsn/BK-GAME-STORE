USE STEAM_PROJECT;
GO

CREATE OR ALTER PROCEDURE DeleteGame
	@GID			varchar(6)
AS
BEGIN
	-- Validate game exists
	IF NOT EXISTS(SELECT 1 FROM GAMES WHERE game_id = @GID)
        THROW 50000, 'Game not found.', 1;

	BEGIN TRY
		DELETE
		FROM GAMES
		WHERE game_id = @GID;

		PRINT 'Delete game successfully.';
	END TRY
	BEGIN CATCH
		THROW 50000, 'Failed to delete game.', 1;
	END CATCH;
END;