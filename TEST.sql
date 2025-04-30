-- Chọn cơ sở dữ liệu của bạn
USE TEST; -- Thay YourDatabase bằng tên CSDL của bạn
GO

-- Xóa các bảng nếu chúng đã tồn tại (thận trọng khi chạy trên CSDL đã có dữ liệu)
-- DROP TABLE IF EXISTS REVIEW;
-- DROP TABLE IF EXISTS FORUM;
-- DROP TABLE IF EXISTS GAME;
-- DROP TABLE IF EXISTS PUBLISHER;
-- DROP TABLE IF EXISTS INGAME_ITEM_DLCS;
-- DROP TABLE IF EXISTS TRANSACTION;
-- DROP TABLE IF EXISTS PRODUCT;
-- DROP TABLE IF EXISTS SALES_EVENTS;
-- DROP TABLE IF EXISTS WORK_SHOP_ITEMS;
-- DROP TABLE IF EXISTS MODS;
-- DROP TABLE IF EXISTS ARTWORKS;
-- DROP TABLE IF EXISTS TRADE_BOX;
-- DROP TABLE IF EXISTS WALLET;
-- DROP TABLE IF EXISTS USER;
-- GO


-- Tạo bảng USER [cite: 1, 2]
CREATE TABLE [dbo].[USER](
    [user_id] INT IDENTITY(1,1) PRIMARY KEY,
    [username] VARCHAR(50) UNIQUE NOT NULL,
    [password] VARCHAR(100) NOT NULL, -- Lưu ý: Nên hash mật khẩu trong ứng dụng thực tế
    [email] VARCHAR(100) UNIQUE NOT NULL,
    [registration_date] DATETIME DEFAULT GETDATE(),
    [last_login] DATETIME,
    [date_of_birth] DATE, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [country] VARCHAR(50) -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của USER nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng WALLET [cite: 1, 2]
CREATE TABLE [dbo].[WALLET](
    [wallet_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT UNIQUE NOT NULL, -- Một người dùng có một ví duy nhất [cite: 1, 2]
    [balance] DECIMAL(18, 2) DEFAULT 0,
    [currency] VARCHAR(10) DEFAULT 'VND' -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của WALLET nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng TRADE_BOX [cite: 1, 2]
CREATE TABLE [dbo].[TRADE_BOX](
    [trade_box_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT UNIQUE NOT NULL, -- Một người dùng có một hộp trao đổi duy nhất [cite: 1, 2]
    [capacity] INT -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của TRADE_BOX nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng ARTWORKS [cite: 1, 2]
CREATE TABLE [dbo].[ARTWORKS](
    [artwork_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL, -- Người dùng tạo artwork [cite: 1, 2]
    [title] VARCHAR(100) NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [upload_date] DATETIME DEFAULT GETDATE(), -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [description] NVARCHAR(MAX) -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của ARTWORKS nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng MODS [cite: 1, 2]
CREATE TABLE [dbo].[MODS](
    [mod_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL, -- Người dùng tạo mod [cite: 1, 2]
    [game_id] INT NOT NULL, -- Mod cho game nào [cite: 1, 2]
    [name] VARCHAR(100) NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [version] VARCHAR(20), -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [upload_date] DATETIME DEFAULT GETDATE(), -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [description] NVARCHAR(MAX) -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của MODS nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO


-- Tạo bảng WORK_SHOP_ITEMS (Quan hệ N-N giữa USER và PRODUCT thông qua bảng trung gian?) [cite: 1, 2]
-- Dựa trên ERD, Work Shop Items có vẻ là các items được tạo bởi USER và liên quan đến PRODUCT.
-- Có thể đây là bảng trung gian cho USER và PRODUCT, hoặc là một loại PRODUCT đặc biệt.
-- Giả định đây là các items được người dùng đóng góp/tạo ra và có thể liên quan đến PRODUCT.
-- Nếu là bảng trung gian giữa USER và PRODUCT:
/*
CREATE TABLE [dbo].[USER_WORK_SHOP_ITEM](
    [user_id] INT NOT NULL,
    [product_id] INT NOT NULL,
    [contribution_date] DATETIME DEFAULT GETDATE(),
    PRIMARY KEY ([user_id], [product_id])
);
GO
*/
-- Dựa trên ERD, WORK_SHOP_ITEMS có các thuộc tính riêng (price, type, name).
-- Giả định WORK_SHOP_ITEMS là một bảng riêng, có thể liên quan đến PRODUCT.
CREATE TABLE [dbo].[WORK_SHOP_ITEMS](
     [workshop_item_id] INT IDENTITY(1,1) PRIMARY KEY,
     [user_id] INT NOT NULL, -- Người dùng nào tạo item này [cite: 1, 2]
     [name] VARCHAR(100) NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
     [price] DECIMAL(18, 2), -- Thêm thuộc tính từ ERD [cite: 1, 2]
     [type] VARCHAR(50) -- Thêm thuộc tính từ ERD [cite: 1, 2]
     -- Thêm các thuộc tính khác của WORK_SHOP_ITEMS nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO


-- Tạo bảng PRODUCT [cite: 1, 2]
CREATE TABLE [dbo].[PRODUCT](
    [product_id] INT IDENTITY(1,1) PRIMARY KEY,
    [name] VARCHAR(255) NOT NULL,
    [price] DECIMAL(18, 2) NOT NULL,
    [description] NVARCHAR(MAX),
    [release_date] DATE, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [publisher_id] INT -- Liên kết với bảng PUBLISHER [cite: 1, 2]
    -- Thêm các thuộc tính khác của PRODUCT nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng SALES_EVENTS (Quan hệ N-N giữa PRODUCT và SALES_EVENTS thông qua bảng trung gian) [cite: 1, 2]
CREATE TABLE [dbo].[SALES_EVENTS](
    [event_id] INT IDENTITY(1,1) PRIMARY KEY,
    [event_name] VARCHAR(100) NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [start_date] DATETIME NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [end_date] DATETIME NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [discount_percentage] DECIMAL(5, 2) -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của SALES_EVENTS nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Bảng trung gian cho quan hệ N-N giữa PRODUCT và SALES_EVENTS [cite: 1, 2]
CREATE TABLE [dbo].[PRODUCT_SALES_EVENT](
    [product_id] INT NOT NULL,
    [event_id] INT NOT NULL,
    PRIMARY KEY ([product_id], [event_id])
);
GO


-- Tạo bảng TRANSACTION [cite: 1, 2]
CREATE TABLE [dbo].[TRANSACTION](
    [transaction_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL, -- Người dùng thực hiện giao dịch [cite: 1, 2]
    [product_id] INT, -- Sản phẩm liên quan đến giao dịch (có thể NULL cho các loại giao dịch khác) [cite: 1, 2]
    [transaction_date] DATETIME DEFAULT GETDATE(), -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [amount] DECIMAL(18, 2) NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [transaction_type] VARCHAR(50) NOT NULL -- e.g., 'Buy', 'Sell', 'Add Fund', 'Withdraw' [cite: 1, 2]
    -- Thêm các thuộc tính khác của TRANSACTION nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng PUBLISHER [cite: 1, 2]
CREATE TABLE [dbo].[PUBLISHER](
    [publisher_id] INT IDENTITY(1,1) PRIMARY KEY,
    [name] VARCHAR(100) NOT NULL,
    [website] VARCHAR(255), -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [country] VARCHAR(50) -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của PUBLISHER nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng GAME (là một loại PRODUCT đặc biệt?) [cite: 1, 2]
-- Dựa trên ERD, GAME có vẻ là một thực thể riêng biệt nhưng có quan hệ với PUBLISHER.
-- Nó cũng có quan hệ với INGAME_ITEM_DLCS.
-- Có thể GAME là một bảng con của PRODUCT (sử dụng kế thừa trong CSDL)?
-- Tuy nhiên, để đơn giản, ta tạo GAME là một bảng riêng và liên kết với PUBLISHER.
CREATE TABLE [dbo].[GAME](
    [game_id] INT IDENTITY(1,1) PRIMARY KEY,
    [publisher_id] INT NOT NULL, -- Game thuộc về nhà phát hành nào [cite: 1, 2]
    [title] VARCHAR(255) NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [release_date] DATE, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [genre] VARCHAR(50) -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của GAME nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng INGAME_ITEM_DLCS (Quan hệ N-N giữa GAME và PRODUCT?) [cite: 1, 2]
-- Dựa trên tên, đây có thể là các Item trong game hoặc DLC (Nội dung tải xuống).
-- Nó có quan hệ với GAME. Có thể đây là các PRODUCT cụ thể thuộc về một GAME nào đó.
-- Giả định đây là một bảng riêng lưu trữ các item/DLC trong game.
CREATE TABLE [dbo].[INGAME_ITEM_DLCS](
    [item_dlc_id] INT IDENTITY(1,1) PRIMARY KEY,
    [game_id] INT NOT NULL, -- Item/DLC thuộc game nào [cite: 1, 2]
    [name] VARCHAR(100) NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [type] VARCHAR(50), -- e.g., 'Item', 'DLC' [cite: 1, 2]
    [price] DECIMAL(18, 2) -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của INGAME_ITEM_DLCS nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng FORUM [cite: 1, 2]
CREATE TABLE [dbo].[FORUM](
    [forum_id] INT IDENTITY(1,1) PRIMARY KEY,
    [game_id] INT, -- Forum có thể liên quan đến một game cụ thể (có thể NULL cho forum chung) [cite: 1, 2]
    [title] VARCHAR(255) NOT NULL, -- Thêm thuộc tính từ ERD [cite: 1, 2]
    [creation_date] DATETIME DEFAULT GETDATE() -- Thêm thuộc tính từ ERD [cite: 1, 2]
    -- Thêm các thuộc tính khác của FORUM nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Tạo bảng REVIEW [cite: 1, 2]
CREATE TABLE [dbo].[REVIEW](
    [review_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL, -- Người dùng viết review [cite: 1, 2]
    [product_id] INT, -- Review cho sản phẩm nào (có thể là Game, Ingame Item,...) [cite: 1, 2]
    [rating] INT CHECK (rating >= 1 AND rating <= 5), -- Đánh giá sao [cite: 1, 2]
    [comment] NVARCHAR(MAX), -- Nội dung review [cite: 1, 2]
    [review_date] DATETIME DEFAULT GETDATE() -- Ngày review [cite: 1, 2]
    -- Thêm các thuộc tính khác của REVIEW nếu có trong ERD chi tiết hơn [cite: 1, 2]
);
GO

-- Thêm các ràng buộc khóa ngoại (Foreign Key Constraints)

-- WALLET liên kết với USER [cite: 1, 2]
ALTER TABLE [dbo].[WALLET]
ADD CONSTRAINT FK_WALLET_USER
FOREIGN KEY ([user_id]) REFERENCES [dbo].[USER]([user_id]);
GO

-- TRADE_BOX liên kết với USER [cite: 1, 2]
ALTER TABLE [dbo].[TRADE_BOX]
ADD CONSTRAINT FK_TRADE_BOX_USER
FOREIGN KEY ([user_id]) REFERENCES [dbo].[USER]([user_id]);
GO

-- ARTWORKS liên kết với USER [cite: 1, 2]
ALTER TABLE [dbo].[ARTWORKS]
ADD CONSTRAINT FK_ARTWORKS_USER
FOREIGN KEY ([user_id]) REFERENCES [dbo].[USER]([user_id]);
GO

-- MODS liên kết với USER và GAME [cite: 1, 2]
ALTER TABLE [dbo].[MODS]
ADD CONSTRAINT FK_MODS_USER
FOREIGN KEY ([user_id]) REFERENCES [dbo].[USER]([user_id]);
GO

ALTER TABLE [dbo].[MODS]
ADD CONSTRAINT FK_MODS_GAME
FOREIGN KEY ([game_id]) REFERENCES [dbo].[GAME]([game_id]);
GO

-- WORK_SHOP_ITEMS liên kết với USER [cite: 1, 2]
ALTER TABLE [dbo].[WORK_SHOP_ITEMS]
ADD CONSTRAINT FK_WORK_SHOP_ITEMS_USER
FOREIGN KEY ([user_id]) REFERENCES [dbo].[USER]([user_id]);
GO

-- PRODUCT liên kết với PUBLISHER [cite: 1, 2]
ALTER TABLE [dbo].[PRODUCT]
ADD CONSTRAINT FK_PRODUCT_PUBLISHER
FOREIGN KEY ([publisher_id]) REFERENCES [dbo].[PUBLISHER]([publisher_id]);
GO

-- PRODUCT_SALES_EVENT liên kết với PRODUCT và SALES_EVENTS [cite: 1, 2]
ALTER TABLE [dbo].[PRODUCT_SALES_EVENT]
ADD CONSTRAINT FK_PRODUCT_SALES_EVENT_PRODUCT
FOREIGN KEY ([product_id]) REFERENCES [dbo].[PRODUCT]([product_id]);
GO

ALTER TABLE [dbo].[PRODUCT_SALES_EVENT]
ADD CONSTRAINT FK_PRODUCT_SALES_EVENT_SALES_EVENTS
FOREIGN KEY ([event_id]) REFERENCES [dbo].[SALES_EVENTS]([event_id]);
GO

-- TRANSACTION liên kết với USER và PRODUCT [cite: 1, 2]
ALTER TABLE [dbo].[TRANSACTION]
ADD CONSTRAINT FK_TRANSACTION_USER
FOREIGN KEY ([user_id]) REFERENCES [dbo].[USER]([user_id]);
GO

ALTER TABLE [dbo].[TRANSACTION]
ADD CONSTRAINT FK_TRANSACTION_PRODUCT
FOREIGN KEY ([product_id]) REFERENCES [dbo].[PRODUCT]([product_id]);
GO

-- GAME liên kết với PUBLISHER [cite: 1, 2]
ALTER TABLE [dbo].[GAME]
ADD CONSTRAINT FK_GAME_PUBLISHER
FOREIGN KEY ([publisher_id]) REFERENCES [dbo].[PUBLISHER]([publisher_id]);
GO

-- INGAME_ITEM_DLCS liên kết với GAME [cite: 1, 2]
ALTER TABLE [dbo].[INGAME_ITEM_DLCS]
ADD CONSTRAINT FK_INGAME_ITEM_DLCS_GAME
FOREIGN KEY ([game_id]) REFERENCES [dbo].[GAME]([game_id]);
GO

-- FORUM liên kết với GAME (có thể NULL) [cite: 1, 2]
ALTER TABLE [dbo].[FORUM]
ADD CONSTRAINT FK_FORUM_GAME
FOREIGN KEY ([game_id]) REFERENCES [dbo].[GAME]([game_id]);
GO

-- REVIEW liên kết với USER và PRODUCT [cite: 1, 2]
ALTER TABLE [dbo].[REVIEW]
ADD CONSTRAINT FK_REVIEW_USER
FOREIGN KEY ([user_id]) REFERENCES [dbo].[USER]([user_id]);
GO

ALTER TABLE [dbo].[REVIEW]
ADD CONSTRAINT FK_REVIEW_PRODUCT
FOREIGN KEY ([product_id]) REFERENCES [dbo].[PRODUCT]([product_id]);
GO

-- Quan hệ giữa TRADE_BOX và INGAME_ITEM_DLCS (Quan hệ N-N thông qua bảng trung gian?) [cite: 1, 2]
-- Dựa trên ERD, có vẻ TRADE_BOX chứa INGAME_ITEM_DLCS.
-- Tạo bảng trung gian TRADE_BOX_ITEM_DLC
CREATE TABLE [dbo].[TRADE_BOX_ITEM_DLC](
    [trade_box_id] INT NOT NULL,
    [item_dlc_id] INT NOT NULL,
    [quantity] INT DEFAULT 1, -- Thêm số lượng item trong trade box [cite: 1, 2]
    PRIMARY KEY ([trade_box_id], [item_dlc_id])
);
GO

-- Thêm ràng buộc khóa ngoại cho bảng TRADE_BOX_ITEM_DLC
ALTER TABLE [dbo].[TRADE_BOX_ITEM_DLC]
ADD CONSTRAINT FK_TRADE_BOX_ITEM_DLC_TRADE_BOX
FOREIGN KEY ([trade_box_id]) REFERENCES [dbo].[TRADE_BOX]([trade_box_id]);
GO

ALTER TABLE [dbo].[TRADE_BOX_ITEM_DLC]
ADD CONSTRAINT FK_TRADE_BOX_ITEM_DLC_INGAME_ITEM_DLCS
FOREIGN KEY ([item_dlc_id]) REFERENCES [dbo].[INGAME_ITEM_DLCS]([item_dlc_id]);
GO

-- Quan hệ giữa WALLET và TRANSACTION (Mỗi transaction liên quan đến wallet nào?) [cite: 1, 2]
-- TRANSACTION đã liên kết với USER, và WALLET cũng liên kết với USER.
-- Mối quan hệ giữa WALLET và TRANSACTION thường là một TRANSACTION làm thay đổi số dư trong WALLET.
-- Có thể không cần khóa ngoại trực tiếp từ TRANSACTION đến WALLET nếu đã có USER.
-- Tuy nhiên, nếu muốn theo dõi giao dịch ảnh hưởng đến ví nào cụ thể (trong trường hợp user có nhiều ví?),
-- ta có thể thêm wallet_id vào bảng TRANSACTION. Dựa trên ERD hiện tại, TRANSACTION chỉ liên kết với USER.
-- Ta giữ nguyên như ERD.

-- Quan hệ giữa ARTWORKS, MODS, WORK_SHOP_ITEMS và PRODUCT [cite: 1, 2]
-- Dựa trên ERD, các thực thể này có vẻ là các loại "sản phẩm" do người dùng đóng góp.
-- PRODUCT có quan hệ N-N với TRANSACTION, SALES_EVENTS.
-- Có thể ARTWORKS, MODS, WORK_SHOP_ITEMS là các bảng con của PRODUCT (sử dụng kế thừa)?
-- Hoặc chúng là các thực thể riêng biệt và có thể được bán/giao dịch như PRODUCT thông qua mối quan hệ khác?
-- Dựa trên cấu trúc bảng đã tạo, chúng là các bảng riêng liên kết với USER (người tạo) và có thể liên kết với GAME (đối với MODS).
-- Mối quan hệ với PRODUCT cần được làm rõ hơn từ ERD chi tiết hoặc yêu cầu đề bài.
-- Hiện tại, chúng ta tạo các bảng riêng và mối quan hệ đã rõ là với USER và GAME (cho MODS).

-- Quan hệ giữa FORUM và USER (User tạo bài viết/comment trong forum) [cite: 1, 2]
-- Quan hệ này không được thể hiện trực tiếp bằng đường nối giữa FORUM và USER trong ERD chính[cite: 1, 2].
-- Tuy nhiên, một diễn đàn thường có bài viết do người dùng tạo.
-- Nếu bạn muốn theo dõi ai là người tạo bài viết/chủ đề trong forum, bạn cần thêm một bảng Topics/Posts liên kết với USER và FORUM.

-- Quan hệ giữa REVIEW và PRODUCT [cite: 1, 2]
-- REVIEW liên kết với PRODUCT (sản phẩm được review) và USER (người review). Đã thêm ở trên.

-- Quan hệ giữa GAME và INGAME_ITEM_DLCS [cite: 1, 2]
-- GAME chứa INGAME_ITEM_DLCS. Đã thêm khóa ngoại từ INGAME_ITEM_DLCS đến GAME.

-- Quan hệ giữa PRODUCT và TRANSACTION [cite: 1, 2]
-- Một TRANSACTION có thể liên quan đến một PRODUCT. Đã thêm khóa ngoại từ TRANSACTION đến PRODUCT (có thể NULL).

-- Quan hệ giữa PRODUCT và SALES_EVENTS (N-N) [cite: 1, 2]
-- Sử dụng bảng trung gian PRODUCT_SALES_EVENT. Đã thêm ở trên.

-- Quan hệ giữa PRODUCT và WORK_SHOP_ITEMS [cite: 1, 2]
-- Mối quan hệ này không rõ ràng trong ERD chính[cite: 1, 2]. Có thể cần làm rõ thêm.
-- Hiện tại, Work_Shop_Items liên kết với USER.

-- Quan hệ giữa TRADE_BOX và TRANSACTION [cite: 1, 2]
-- Mối quan hệ này không rõ ràng trong ERD chính[cite: 1, 2]. Có thể Trade Box liên quan đến các giao dịch mua/bán item. Cần làm rõ thêm.

-- Quan hệ giữa WALLET và TRADE_BOX [cite: 1, 2]
-- Mối quan hệ này không rõ ràng trong ERD chính[cite: 1, 2]. Có thể giao dịch trong Trade Box ảnh hưởng đến Wallet. Cần làm rõ thêm.

-- Quan hệ giữa MODS và ARTWORKS [cite: 1, 2]
-- Mối quan hệ này không rõ ràng trong ERD chính[cite: 1, 2].

-- Quan hệ giữa GAME và MODS [cite: 1, 2]
-- Game có MODS. Đã thêm khóa ngoại từ MODS đến GAME.

-- Quan hệ giữa GAME và ARTWORKS [cite: 1, 2]
-- Mối quan hệ này không rõ ràng trong ERD chính[cite: 1, 2].

-- Quan hệ giữa GAME và SALES_EVENTS [cite: 1, 2]
-- Mối quan hệ này không rõ ràng trong ERD chính[cite: 1, 2]. Có thể Sales Event áp dụng cho các Game.

-- Quan hệ giữa PUBLISHER và GAME/PRODUCT [cite: 1, 2]
-- Publisher phát hành GAME và PRODUCT. Đã thêm khóa ngoại từ GAME và PRODUCT đến PUBLISHER.


PRINT 'Database schema created successfully!';
GO