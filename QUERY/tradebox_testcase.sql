USE STEAM_PROJECT;
GO

INSERT INTO [USER] (account_id, user_name, BDate, country, email, phone_number)
VALUES
('UI0001', 'JohnDoe', '1990-05-15', 'USA', 'john.doe@example.com', '+1234567890'),
('UI0002', 'JaneSmith', '1985-08-22', 'Canada', 'jane.smith@example.com', '+1987654321'),
('UI0003', 'MikeJohnson', '1995-03-10', 'UK', 'mike.johnson@example.com', '+44123456789'),
('UI0004', 'SarahWilliams', '1992-11-30', 'Australia', 'sarah.w@example.com', '+61234567890'),
('UI0005', 'DavidBrown', '1988-07-18', 'Germany', 'david.brown@example.com', '+49123456789');

INSERT INTO [PUBLISHER] (publisher_id, website, name)
VALUES
('PI0001', 'www.ea.com', 'Electronic Arts'),
('PI0002', 'www.ubisoft.com', 'Ubisoft'),
('PI0003', 'www.rockstargames.com', 'Rockstar Games'),
('PI0004', 'www.cdprojekt.com', 'CD Projekt Red'),
('PI0005', 'www.valvesoftware.com', 'Valve Corporation');

INSERT INTO [GAMES] (game_id, game_name, engine, game_description, game_publisher, date_released)
VALUES
('GA0001', 'Battlefield 2042', 'Frostbite', 'First-person shooter game', 'PI0001', '2021-11-19'),
('GA0002', 'Assassin''s Creed Valhalla', 'AnvilNext', 'Action role-playing game', 'PI0002', '2020-11-10'),
('GA0003', 'Grand Theft Auto V', 'RAGE', 'Action-adventure game', 'PI0003', '2013-09-17'),
('GA0004', 'The Witcher 3', 'REDengine', 'Action role-playing game', 'PI0004', '2015-05-19'),
('GA0005', 'Half-Life 2', 'Source', 'First-person shooter game', 'PI0005', '2004-11-16'),
('GA0006', 'Cyberpunk 2077', 'REDengine', 'Open-world RPG', 'PI0004', '2020-12-10'),
('GA0007', 'Red Dead Redemption 2', 'RAGE', 'Western action-adventure', 'PI0003', '2018-10-26'),
('GA0008', 'FIFA 23', 'Frostbite', 'Football simulation', 'PI0001', '2022-09-30'),
('GA0009', 'Call of Duty: Modern Warfare II', 'IW Engine', 'First-person shooter', 'PI0005', '2022-10-28'),
('GA0010', 'Elden Ring', 'Custom', 'Action RPG', 'PI0002', '2022-02-25'),
('GA0011', 'Stray', 'Unity', 'Adventure game', 'PI0004', '2022-07-19'),
('GA0012', 'God of War: Ragnar�k', 'Custom', 'Action-adventure', 'PI0003', '2022-11-09'),
('GA0013', 'Hogwarts Legacy', 'Unreal 4', 'Wizarding world RPG', 'PI0002', '2023-02-10'),
('GA0014', 'Starfield', 'Creation Engine 2', 'Space RPG', 'PI0001', '2023-09-06'),
('GA0015', 'Resident Evil 4 Remake', 'RE Engine', 'Survival horror', 'PI0005', '2023-03-24');

INSERT INTO ITEMS_AND_DLCS (game_id, sub_id, name, type, bundle)
VALUES
('GA0001', 'GS0001', 'Season Pass', 'DLC', 'Premium Edition'),
('GA0002', 'GS0001', 'Dawn of Ragnar�k', 'Expansion', 'Gold Edition'),
('GA0003', 'GS0001', 'GTA Online', 'Online Mode', 'Standard Edition'),
('GA0001', 'GS0002', 'Gold Skin Pack', 'Cosmetic', 'Deluxe Edition'),
('GA0004', 'GS0001', 'Hearts of Stone', 'Expansion', 'Game of the Year Edition'),
('GA0004', 'GS0002', 'Blood and Wine', 'Expansion', 'Game of the Year Edition'),
('GA0003', 'GS0002', 'Doomsday Heist', 'DLC', 'Premium Online Edition');

INSERT INTO [PRODUCT] (product_id, product_type, base_id, product_price, tradeable)
VALUES
(1, 'Game', 'GA0001', 1400000, 1),   
(2, 'Game', 'GA0002', 1200000, 1),   
(3, 'Game', 'GA0003', 900000, 0),
(4, 'Subgame', 'GA0001', 250000, 1),
(5, 'Subgame', 'GA0002', 350000, 1),
(6, 'Game', 'GA0004', 700000, 1),
(7, 'Game', 'GA0005', 500000, 1),     
(8, 'Subgame', 'GA0003', 120000, 0), 
(9, 'Game', 'GA0006', 1200000, 1),
(10, 'Game', 'GA0007', 1100000, 1),
(11, 'Game', 'GA0008', 1400000, 0),
(12, 'Game', 'GA0009', 1500000, 1),
(13, 'Game', 'GA0010', 1300000, 1),
(14, 'Game', 'GA0011', 800000, 1),
(15, 'Game', 'GA0012', 1600000, 1),
(16, 'Game', 'GA0013', 1700000, 1),
(17, 'Game', 'GA0014', 1800000, 1),
(18, 'Game', 'GA0015', 1200000, 1);


INSERT INTO _OWN (product_id, user_id, quantity)
VALUES
(1, 'UI0001', 1),
(2, 'UI0001', 1),
(3, 'UI0002', 1),
(4, 'UI0001', 1),
(5, 'UI0003', 1),
(6, 'UI0004', 1),
(7, 'UI0005', 1),
(8, 'UI0002', 1),
(2, 'UI0005', 1),
(3, 'UI0003', 1),
(9, 'UI0001', 1),   -- John owns Cyberpunk
(10, 'UI0002', 1),  -- Jane owns RDR2
(11, 'UI0003', 1),  -- Mike owns FIFA 23
(12, 'UI0004', 1),  -- Sarah owns COD
(13, 'UI0005', 1),  -- David owns Elden Ring
(14, 'UI0001', 1),  -- John owns Stray
(15, 'UI0002', 1),  -- Jane owns God of War
(16, 'UI0003', 1),  -- Mike owns Hogwarts
(17, 'UI0004', 1),  -- Sarah owns Starfield
(18, 'UI0005', 1),  -- David owns RE4
(9, 'UI0003', 1),   -- Mike also owns Cyberpunk
(12, 'UI0001', 1);  -- John owns COD too

INSERT INTO TRADE_BOX (tradebox_id, user_id)
VALUES
('TB0001', 'UI0001'),
('TB0002', 'UI0002'),
('TB0003', 'UI0003'),
('TB0004', 'UI0001'),
('TB0005', 'UI0002'),
('TB0006', 'UI0003'),
('TB0007', 'UI0004'),
('TB0008', 'UI0005'),
('TB0009', 'UI0001'),
('TB0010', 'UI0002'),
('TB0011', 'UI0003'),
('TB0012', 'UI0004'),
('TB0013', 'UI0005'),
('TB0014', 'UI0001'),
('TB0015', 'UI0002');


--INSERT INTO _TRADE_BOX_CONTAIN (product_id, user_id, tradebox_id)
--VALUES
--(4, 'UI0001', 'TB0001'),
--(5, 'UI0003', 'TB0003'),
--(8, 'UI0002', 'TB0002'),
--(1, 'UI0001', 'TB0004'),
--(2, 'UI0002', 'TB0005'),
--(6, 'UI0004', 'TB0007'),
--(7, 'UI0005', 'TB0008');