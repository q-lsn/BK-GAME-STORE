USE STEAM_PROJECT;
GO

--CREATE SEQUENCE Auto_Generated_GameID
--    START WITH 1		-- Starting number
--    INCREMENT BY 1		-- Increment value
--    MINVALUE 1			-- Minimum value
--    CYCLE;				-- Restart after reaching max
--GO

CREATE OR ALTER PROCEDURE InsertGame
    @GName          varchar(80),
    @GPrice         decimal(10,2) = 0.00,    
    @GEngine        varchar(20) = 'Source',        
    @GDescription   varchar(2000) = 'No description.',    
    @GPublisher     varchar(80),
    @Released       date = NULL
AS
BEGIN
    -- Set default release date if not provided
    IF @Released IS NULL
        SET @Released = CAST(GETDATE() AS DATE);

    -- Validate release date is not in future
    IF @Released > CAST(GETDATE() AS DATE)
        THROW 50000, 'Cannot set release date to a future date.', 1;

    -- Validate publisher exists
    IF NOT EXISTS (SELECT 1 FROM PUBLISHER WHERE name = @GPublisher)
        THROW 50000, 'Publisher not found.', 1;

    -- Validate game name doesn't already exist
    IF EXISTS (SELECT 1 FROM GAMES WHERE game_name = @GName)
        THROW 50000, 'Game already exists.', 1;

    -- Validate price is not negative
    IF @GPrice < 0
        THROW 50000, 'Price cannot be negative.', 1;

	BEGIN TRY
		-- Generate the new game ID
		DECLARE @GID char(6);
		DECLARE @num INT = NEXT VALUE FOR Auto_Generated_GameID;
		SET @GID = 'GA' + RIGHT('0000' + CAST(@num AS VARCHAR(4)), 4);

        -- Get publisher ID
        DECLARE @PID varchar(6);
        SELECT @PID = publisher_id FROM PUBLISHER WHERE name = @GPublisher;

		-- Insert the new game
		INSERT INTO GAMES(game_id, game_name, game_price, engine, game_description, game_publisher, date_released) VALUES
		(	@GID,
			@GName,
			@GPrice,
			@GEngine,
			@GDescription,
			@PID, 
			@Released
		);
		PRINT 'Insert game successfully.';
    END TRY
    BEGIN CATCH
        THROW 50000, 'Failed to insert game.', 1;
    END CATCH;
END;
GO