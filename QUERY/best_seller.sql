--get best sellers based on tags, publisher
USE STEAM_PROJECT
GO
CREATE OR ALTER PROCEDURE best_seller
	@game_tags varchar(20),
	@g_publisher varchar(80)
AS 
BEGIN
	IF @game_tags IS NOT NULL AND NOT EXISTS (SELECT 1 FROM GAME_TAG WHERE game_tag = @game_tags)
		THROW 5000, 'Tag not found.', 1;
	IF @g_publisher IS NOT NULL AND NOT EXISTS (SELECT 1 FROM PUBLISHER WHERE name = @g_publisher)
		THROW 5000, 'Publisher not found.', 1;

	SELECT g.game_id, g.game_name AS GameName, g.game_price AS Price, g.date_released AS date_released, g.game_publisher AS Publisher, SUM(_OWN.quantity) AS unit_sold
	FROM (
		[GAMES] g LEFT JOIN [PRODUCT] pro ON g.product_id = pro.product_id
		LEFT JOIN _OWN ON g.product_id = _OWN.product_id
		LEFT JOIN [GAME_TAG] tag ON tag.game_id = g.game_id
		LEFT JOIN [PUBLISHER] p ON g.game_publisher = p.publisher_id
	)
	WHERE (@game_tags IS NULL OR tag.game_tag = @game_tags) AND (@g_publisher IS NULL OR @g_publisher = p.name)
	GROUP BY g.game_id
	ORDER BY unit_sold DESC;
END;