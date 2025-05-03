USE STEAM_PROJECT;
GO

CREATE OR ALTER PROCEDURE GetGamesFilteredSorted
AS
BEGIN
    SELECT 
        g.game_id,
        g.game_name,
        g.engine,
        g.game_description,
        p.name,
        g.date_released,
        pd.product_id,
        g.game_price
    FROM 
        GAMES AS g 
    JOIN    
        PUBLISHER AS p ON g.game_publisher = p.name
    JOIN 
        PRODUCT AS pd ON g.product_id = pd.product_id
    ORDER BY
        g.game_id ASC

END
GO