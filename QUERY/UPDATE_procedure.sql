USE STEAM_PROJECT;
GO

CREATE OR ALTER PROCEDURE UpdateGameInfo
	@GID			varchar(6),
    @GName          varchar(80) = NULL,
    @GPrice         decimal(10,2) = NULL,          
    @GDescription   varchar(2000) = NULL
AS
BEGIN
	-- Validate game exists
	IF NOT EXISTS(SELECT 1 FROM GAMES WHERE game_id = @GID)
        THROW 50000, 'Game not found.', 1;

    -- Validate game name doesn't already exist, excluding the current game being updated
    IF EXISTS (SELECT 1 FROM GAMES WHERE game_name = @GName and game_id <> @GID)
        THROW 50000, 'Game''s name already used by another game.', 1;

    -- Validate price is not negative
    IF @GPrice < 0
        THROW 50000, 'Price cannot be negative.', 1;

	BEGIN TRY
		UPDATE GAMES
		SET 
			game_name = ISNULL(@GName, game_name),
			game_price = ISNULL(@GPrice, game_price),
			game_description = ISNULL(@GDescription, game_description)
		WHERE game_id = @GID;

		PRINT 'Update game''s information successfully.';
	END TRY
	BEGIN CATCH
		THROW 50000, 'Failed to update game''s information.', 1;
	END CATCH;
END;