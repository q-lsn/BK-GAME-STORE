USE STEAM_PROJECT;
GO

-- Chèn dữ liệu mẫu vào bảng PUBLISHER
INSERT INTO PUBLISHER (publisher_id, website, name) VALUES
('PI0001', 'http://www.valvesoftware.com', 'Valve Corporation'),
('PI0002', 'http://www.ubisoft.com', 'Ubisoft'),
('PI0003', 'http://www.eagames.com', 'Electronic Arts'),
('PI0004', 'http://www.cdprojektred.com', 'CD Projekt Red'),
('PI0005', 'http://www.rockstargames.com', 'Rockstar Games');
GO

-- Chèn dữ liệu mẫu vào bảng USER
INSERT INTO [USER] (account_id, user_name, BDate, country, email, phone_number) VALUES
('UI0001', 'gaben', '1962-05-15', 'USA', 'gabe.n@valvesoftware.com', '+11234567890'),
('UI0002', 'acidlemon', '1990-10-20', 'Vietnam', 'acidlemon@example.com', '+84901234567'),
('UI0003', 'coolgamer88', '1995-07-07', 'Germany', 'gamer88@mail.de', NULL),
('UI0004', 'steamfanatic', '2000-01-30', 'UK', 'steamfan@outlook.com', '+447890123456'),
('UI0005', 'codingninja', '1985-03-11', 'Japan', 'ninja.code@domain.jp', '+818011223344');
GO

-- Chèn dữ liệu mẫu vào bảng PRODUCT
INSERT INTO PRODUCT (product_id, base_game_id, base_subgame_id, product_price, tradeable) VALUES
(1001, 'GA0001', NULL, 19.99, 1), -- Game A
(1002, 'GA0002', NULL, 59.99, 0), -- Game B
(1003, 'GA0001', 'SU0001', 4.99, 1), -- DLC for Game A
(1004, 'GA0003', NULL, 29.50, 1), -- Game C
(1005, 'GA0002', 'SU0002', 14.99, 0); -- DLC for Game B
GO

-- Chèn dữ liệu mẫu vào bảng SALES_EVENT
INSERT INTO SALES_EVENT (sales_id, sales_name, date_start, date_end) VALUES
('SI0001', 'Steam Summer Sale 2024', '2024-06-20', '2024-07-04'),
('SI0002', 'Halloween Sale 2024', '2024-10-28', '2024-11-01'),
('SI0003', 'Winter Sale 2024', '2024-12-21', '2025-01-04');
GO

-- Chèn dữ liệu mẫu vào bảng GAMES
INSERT INTO GAMES (game_id, game_name, engine, game_description, game_publisher, date_released, product_id) VALUES
('GA0001', 'Half-Life 3', 'Source 2', 'A highly anticipated first-person shooter.', 'PI0001', '2024-11-20', 1001),
('GA0002', 'Cyberpunk 2077', 'REDengine 4', 'An open-world, action-adventure RPG.', 'PI0004', '2020-12-10', 1002),
('GA0003', 'Assassins Creed Valhalla', 'AnvilNext 2.0', 'Explore the dark ages of England.', 'PI0002', '2020-11-10', 1004),
('GA0004', 'Grand Theft Auto V', 'RAGE', 'A vast open-world crime game.', 'PI0005', '2015-04-14', NULL), -- Example with NULL product_id
('GA0005', 'Dota 2', 'Source 2', 'A popular multiplayer online battle arena game.', 'PI0001', '2013-07-09', NULL); -- Example with NULL product_id
GO

-- Chèn dữ liệu mẫu vào bảng WALLET
-- wallet_id sẽ được tự động tạo (IDENTITY)
INSERT INTO WALLET (user_id, balance) VALUES
('UI0001', 1500.50),
('UI0002', 50.25),
('UI0003', 200.00),
('UI0004', 5.75),
('UI0005', 1000.00);
GO

-- Để chèn dữ liệu vào các bảng phụ thuộc vào WALLET,
-- chúng ta cần biết wallet_id được tạo tự động.
-- Trong một script tĩnh, chúng ta sẽ giả định wallet_id được tạo
-- theo thứ tự (1, 2, 3, ...) cho các user_id đã chèn ở trên.
-- User UI0001 -> wallet_id 1
-- User UI0002 -> wallet_id 2
-- User UI0003 -> wallet_id 3
-- User UI0004 -> wallet_id 4
-- User UI0005 -> wallet_id 5

-- Chèn dữ liệu mẫu vào bảng TRANSACTION
INSERT INTO [TRANSACTION] (transaction_id, date_purchased, trans_status) VALUES
('TR0001', '2024-06-25', 'Completed'),
('TR0002', '2024-07-01', 'Completed'),
('TR0003', '2024-07-02', 'Failed'),
('TR0004', '2024-08-15', 'Completed'),
('TR0005', '2024-08-16', 'Refunded');
GO

-- Chèn dữ liệu mẫu vào bảng REVIEWS
INSERT INTO REVIEWS (game_review, review_id, rating_score, comment, date_posted, feedback_user) VALUES
('GA0001', 'GR0001', 10, 'Amazing game! Worth the wait!', '2024-12-01', 'UI0002'),
('GA0002', 'GR0002', 7, 'Good story, but buggy at launch.', '2021-01-15', 'UI0003'),
('GA0003', 'GR0003', 8, 'Viking action is fun, lots to explore.', '2020-12-01', 'UI0004'),
('GA0001', 'GR0004', 9, 'Great gameplay and graphics!', '2024-12-05', 'UI0001'),
('GA0005', 'GR0005', 6, 'Still a classic MOBA, but steep learning curve.', '2023-05-20', NULL); -- Example with NULL feedback_user
GO

-- Chèn dữ liệu mẫu vào bảng GAME_TAG
INSERT INTO GAME_TAG (game_id, game_tag) VALUES
('GA0001', 'FPS'),
('GA0001', 'Sci-Fi'),
('GA0002', 'RPG'),
('GA0002', 'Open World'),
('GA0002', 'Cyberpunk'),
('GA0003', 'Action RPG'),
('GA0003', 'Historical'),
('GA0004', 'Open World'),
('GA0004', 'Crime'),
('GA0005', 'MOBA'),
('GA0005', 'Multiplayer');
GO

-- Chèn dữ liệu mẫu vào bảng _FOLLOW
INSERT INTO _FOLLOW (follow_user, publisher) VALUES
('UI0001', 'PI0001'),
('UI0002', 'PI0004'),
('UI0003', 'PI0002'),
('UI0004', 'PI0001'),
('UI0005', 'PI0005');
GO

-- Chèn dữ liệu mẫu vào bảng _DISCOUNT
INSERT INTO _DISCOUNT (product_id, sales_event, discounted_rate, check_discount) VALUES
(1001, 'SI0001', 50, 1), -- Half-Life 3 giảm 50% trong Summer Sale
(1003, 'SI0001', 20, 1), -- DLC cho Half-Life 3 giảm 20% trong Summer Sale
(1004, 'SI0002', 30, 1), -- AC Valhalla giảm 30% trong Halloween Sale
(1001, 'SI0003', 60, 1); -- Half-Life 3 giảm 60% trong Winter Sale
GO

-- Chèn dữ liệu mẫu vào bảng ACCOUNT_BANK
-- Giả định wallet_id 1, 2, 3, ... cho các user UI0001, UI0002, UI0003,...
INSERT INTO ACCOUNT_BANK (wallet_id, user_id, date_activated, bank_name, pin) VALUES
(1, 'UI0001', '2023-01-10', 'Techcombank', '123456'), -- UI0001 wallet_id 1
(2, 'UI0002', '2023-02-20', 'Vietcombank', '987654'), -- UI0002 wallet_id 2
(3, 'UI0003', '2023-03-05', 'Agribank', '112233'); -- UI0003 wallet_id 3
GO

-- Chèn dữ liệu mẫu vào bảng _PURCHASE
-- Giả định wallet_id 1, 2, 3, ... cho các user UI0001, UI0002, UI0003,...
INSERT INTO _PURCHASE (product_id, transaction_id, wallet_id, account_id, purchased_quantity, total_amount) VALUES
(1001, 'TR0001', 2, 'UI0002', 1, 19.99), -- UI0002 mua Product 1001
(1003, 'TR0001', 2, 'UI0002', 1, 4.99),  -- UI0002 mua Product 1003
(1002, 'TR0002', 1, 'UI0001', 1, 59.99), -- UI0001 mua Product 1002
(1004, 'TR0004', 3, 'UI0003', 1, 29.50), -- UI0003 mua Product 1004
(1001, 'TR0005', 4, 'UI0004', 1, 19.99); -- UI0004 mua Product 1001 (giao dịch hoàn tiền)
GO

-- Chèn dữ liệu mẫu vào bảng ITEMS_AND_LCS
INSERT INTO ITEMS_AND_DLCS (game_id, sub_id, name, type, bundle, product_id) VALUES
('GA0001', 'SU0001', 'Episode One', 'DLC', 'Half-Life 3 Season Pass', 1003),
('GA0002', 'SU0002', 'Phantom Liberty', 'DLC', 'Cyberpunk 2077 Expansion', 1005),
('GA0003', 'SU0003', 'Wrath of the Druids', 'DLC', 'Valhalla Season Pass', NULL), -- Example NULL product_id
('GA0005', 'SU0004', 'Battle Pass 2024', 'Item', 'Compendium', NULL); -- Example NULL product_id
GO

-- Chèn dữ liệu mẫu vào bảng _OWN
INSERT INTO _OWN (product_id, user_id, quantity) VALUES
(1001, 'UI0002', 1), -- User UI0002 owns Product 1001
(1003, 'UI0002', 1), -- User UI0002 owns Product 1003
(1002, 'UI0001', 1), -- User UI0001 owns Product 1002
(1004, 'UI0003', 1), -- User UI0003 owns Product 1004
(1001, 'UI0004', 1); -- User UI0004 owns Product 1001
GO

-- Chèn dữ liệu mẫu vào bảng TRADE_BOX (bước 1: chèn hộp giao dịch ban đầu)
INSERT INTO TRADE_BOX (user_id, tradebox_id, date_traded, trade_method, created_date, trade_status) VALUES
('UI0002', 'TB0001', NULL, NULL, GETDATE(), 'Pending'), -- Hộp giao dịch của UI0002
('UI0003', 'TB0002', NULL, NULL, GETDATE(), 'Pending'), -- Hộp giao dịch của UI0003
('UI0004', 'TB0003', NULL, NULL, GETDATE(), 'Pending'); -- Hộp giao dịch của UI0004
GO

-- Bước 2: Cập nhật để tạo liên kết tự tham chiếu (giao dịch giữa các hộp)
UPDATE TRADE_BOX
SET toffer_tradebox = 'TB0002', toffer_user_id = 'UI0003', date_traded = '2024-08-20', trade_method = 'Exchange', trade_status = 'Success'
WHERE user_id = 'UI0002' AND tradebox_id = 'TB0001';

UPDATE TRADE_BOX
SET toffer_tradebox = 'TB0001', toffer_user_id = 'UI0002', date_traded = '2024-08-20', trade_method = 'Exchange', trade_status = 'Success'
WHERE user_id = 'UI0003' AND tradebox_id = 'TB0002';

UPDATE TRADE_BOX
SET date_traded = '2024-09-01', trade_method = 'Gift', trade_status = 'Completed' -- Hộp tặng quà, không có toffer
WHERE user_id = 'UI0004' AND tradebox_id = 'TB0003';
GO

-- Chèn dữ liệu mẫu vào bảng _TRADE_BOX_CONTAIN
-- Sử dụng các user_id và tradebox_id từ bảng TRADE_BOX
INSERT INTO _TRADE_BOX_CONTAIN (product_id, user_id, tradebox_id, trade_quantity) VALUES
(1001, 'UI0002', 'TB0001', 1), -- Product 1001 trong hộp TB0001 của UI0002
(1004, 'UI0003', 'TB0002', 1), -- Product 1004 trong hộp TB0002 của UI0003
(1003, 'UI0004', 'TB0003', 2); -- Product 1003 (số lượng 2) trong hộp TB0003 của UI0004
GO

-- Chèn dữ liệu mẫu vào bảng FORUM
INSERT INTO FORUM (forum_id, title, forum_status, content, media_url, create_user, date_created, game_discuss) VALUES
('FO0001', 'Half-Life 3 General Discussion', 'Active', 'Discuss anything about HL3 here!', NULL, 'UI0001', '2024-10-01', 'GA0001'),
('FO0002', 'Cyberpunk 2077 Bug Reports', 'Active', 'Post bugs you encounter in CP2077.', NULL, 'UI0003', '2020-12-15', 'GA0002'),
('FO0003', 'Dota 2 Strategy Guide', 'Pinned', 'Tips and tricks for Dota 2 players.', 'http://example.com/dota2guide.jpg', 'UI0005', '2023-08-10', 'GA0005'),
('FO0004', 'Off-Topic Chat', 'Active', 'Chat about anything not game related.', NULL, 'UI0002', '2024-01-20', NULL); -- Example NULL game_discuss
GO

-- Chèn dữ liệu mẫu vào bảng _DISCUSS
INSERT INTO _DISCUSS (discuss_forum, discuss_user) VALUES
('FO0001', 'UI0001'),
('FO0001', 'UI0002'),
('FO0001', 'UI0004'),
('FO0002', 'UI0003'),
('FO0002', 'UI0002'),
('FO0003', 'UI0005'),
('FO0004', 'UI0002'),
('FO0004', 'UI0005');
GO

-- Chèn dữ liệu mẫu vào bảng _DISCUSS_REPLY
-- Đảm bảo tính duy nhất của PK (discuss_forum, discuss_user, media_url, text_reply, no_reply, date_replied)
INSERT INTO _DISCUSS_REPLY (discuss_forum, discuss_user, media_url, text_reply, no_reply, date_replied) VALUES
('FO0001', 'UI0002', 'http://example.com/reply1.png', 'Cant wait!', 1, '2024-10-02'),
('FO0001', 'UI0004', 'http://example.com/reply2.jpg', 'Hope the story is good.', 2, '2024-10-03'),
('FO0001', 'UI0002', 'http://example.com/reply3.gif', 'Me neither!', 3, '2024-10-04'), -- Same user, different reply, no_reply, date
('FO0002', 'UI0003', 'http://example.com/bug1.jpg', 'Found a quest bug near the market.', 1, '2020-12-16'),
('FO0003', 'UI0005', 'http://example.com/tip1.png', 'Always ward the river!', 1, '2023-08-11');
GO

-- Chèn dữ liệu mẫu vào bảng WORKSHOP_ITEMS
INSERT INTO WORKSHOP_ITEMS (workshop_id, date_posted, description, create_user) VALUES
('WI0001', '2023-05-10', 'Custom map for Dota 2.', 'UI0005'),
('WI0002', '2024-01-25', 'High-resolution textures for CP2077.', 'UI0003'),
('WI0003', '2024-03-15', 'Fan art of HL3 character.', 'UI0002');
GO

-- Chèn dữ liệu mẫu vào bảng _SUBCRIBE
INSERT INTO _SUBCRIBE (workshop_id, user_id) VALUES
('WI0001', 'UI0001'),
('WI0001', 'UI0004'),
('WI0002', 'UI0001'),
('WI0002', 'UI0002'),
('WI0003', 'UI0001');
GO

-- Chèn dữ liệu mẫu vào bảng _MODS
-- workshop_id WI0001 và WI0002 từ WORKSHOP_ITEMS được dùng làm mod
INSERT INTO _MODS (workshop_id, name, game_applied, compatible) VALUES
('WI0001', 'Dota 2 Custom Arena', 'GA0005', 1), -- WI0001 là mod cho GA0005
('WI0002', 'CP2077 Texture Pack', 'GA0002', 1); -- WI0002 là mod cho GA0002
GO

-- Chèn dữ liệu mẫu vào bảng MODS_CHANGELOG
-- workshop_id WI0001 và WI0002 từ _MODS được dùng
INSERT INTO MODS_CHANGELOG (workshop_id, change_log) VALUES
('WI0001', 'Initial release.'),
('WI0001', 'Fixed minor bugs.'),
('WI0002', 'Added support for new DLC.'),
('WI0002', 'Improved performance.');
GO

-- Chèn dữ liệu mẫu vào bảng _SHARE_INCOME
INSERT INTO _SHARE_INCOME (publisher_id, transaction_id, percent_shared) VALUES
('PI0004', 'TR0002', 70.00), -- CD Projekt Red chia sẻ 70% doanh thu từ TR0002 (mua CP2077)
('PI0002', 'TR0004', 65.00); -- Ubisoft chia sẻ 65% doanh thu từ TR0004 (mua AC Valhalla)
GO

-- Chèn dữ liệu mẫu vào bảng ARTWORKS
-- workshop_id WI0003 từ WORKSHOP_ITEMS được dùng làm artwork
INSERT INTO ARTWORKS (workshop_id, caption) VALUES
('WI0003', 'Fan art of Gordon Freeman.'); -- WI0003 là artwork
GO

-- Chèn dữ liệu mẫu vào bảng ARTWORK_STYLE
-- workshop_id WI0003 từ ARTWORKS được dùng
INSERT INTO ARTWORK_STYLE (workshop_id, style) VALUES
('WI0003', 'Digital Painting'),
('WI0003', 'Character Art');
GO
