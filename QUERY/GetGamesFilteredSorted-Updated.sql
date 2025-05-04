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
        g.game_publiser,
        g.date_released,
        g.product_id

    FROM
        GAMES AS g
    JOIN PUBLISHER AS p ON g.game_publisher = p.publisher_id 
    LEFT JOIN PRODUCT AS prod ON g.product_id = prod.product_id 

    ORDER BY
        g.game_id ASC; 
END;
GO