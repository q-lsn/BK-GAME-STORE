USE STEAM_PROJECT;
GO

CREATE OR ALTER PROCEDURE best_seller
    @game_tags varchar(20),
    @g_publisher varchar(80) 
AS
BEGIN

    IF @game_tags IS NOT NULL AND NOT EXISTS (SELECT 1 FROM GAME_TAG WHERE game_tag = @game_tags)
        THROW 50000, 'Tag not found.', 1; 
    IF @g_publisher IS NOT NULL AND NOT EXISTS (SELECT 1 FROM PUBLISHER WHERE name = @g_publisher)
        THROW 50000, 'Publisher not found.', 1; 

    SELECT
         g.game_id, 
         g.game_name AS game_name,
         g.date_released AS date_released,
         p.name AS PublisherName,
         SUM(_OWN.quantity) AS unit_sold,
         prod.product_id AS product_id,
         prod.product_price AS product_price 

    FROM
        GAMES AS g
    LEFT JOIN PUBLISHER AS p ON g.game_publisher = p.publisher_id
    LEFT JOIN PRODUCT AS prod ON g.product_id = prod.product_id 
    LEFT JOIN _OWN ON prod.product_id = _OWN.product_id
    LEFT JOIN [GAME_TAG] tag ON tag.game_id = g.game_id 

    WHERE (@game_tags IS NULL OR tag.game_tag = @game_tags) AND (@g_publisher IS NULL OR @g_publisher = p.name) -- Lọc theo tên publisher
    GROUP BY
         g.game_id,
         g.game_name,
         g.date_released,
         p.name,
         prod.product_id,
         prod.product_price 

    ORDER BY unit_sold DESC;
END;
GO