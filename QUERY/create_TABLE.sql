USE STEAM_PROJECT;
GO

CREATE TABLE [USER](
	account_id		varchar(6)			NOT NULL,
	user_name		varchar(20)		NOT NULL UNIQUE,
	BDate			date			NOT NULL,
	country			varchar(20)		NOT NULL,
	email			varchar(40)		NOT NULL,
	phone_number	varchar(15)		,

	PRIMARY KEY (account_id),
	CONSTRAINT idUserFormat	CHECK (account_id LIKE 'UI[0-9][0-9][0-9][0-9]'),
	CONSTRAINT emailFormat	CHECK (email LIKE '%_@__%.__%'),
    CONSTRAINT validBDate	CHECK (DATEDIFF(YEAR, BDate, GETDATE()) >= 13 AND BDate > '1900-01-01'),
	CONSTRAINT validPhone	CHECK (phone_number IS NULL OR phone_number LIKE '+[0-9]%'),
)

CREATE TABLE [PRODUCT](
    product_id			int				IDENTITY(1,1) PRIMARY KEY,
    product_type		varchar(7)		CHECK (product_type IN ('Game', 'Subgame')),
	base_id				varchar(6)		,
	final_price			decimal(10,2)	DEFAULT 0.00 CHECK (final_price >= 0),
);

CREATE TABLE [SALES_EVENT](
    sales_id			varchar(6)      NOT NULL,
    sales_name			varchar(80)     NOT NULL,
    date_start			date            NOT NULL DEFAULT GETDATE(),
    date_end			date            NOT NULL DEFAULT GETDATE(),
    
    PRIMARY KEY (sales_id),
    CONSTRAINT idSalesFormat CHECK (sales_id LIKE 'SI[0-9][0-9][0-9][0-9]'),
    CONSTRAINT validDateRange CHECK (DATEDIFF(day, date_start, date_end) BETWEEN 0 AND 30 AND date_start <= date_end),
);
CREATE TABLE [PUBLISHER](
	publisher_id		varchar(6)		NOT NULL,
	website				varchar(200)	NOT NULL UNIQUE,
	name				varchar(80)		NOT NULL UNIQUE,

	PRIMARY KEY (publisher_id),
	CONSTRAINT idPublisherFormat CHECK (publisher_id LIKE 'PI[0-9][0-9][0-9][0-9]'),
);



CREATE TABLE [GAMES](
	game_id				varchar(6)		NOT NULL,
	game_name			varchar(80)		NOT NULL,
	engine				varchar(20)		,
	game_description	varchar(2000)	,
	game_publisher		varchar(6)		NOT NULL,
	date_released		date			DEFAULT GETDATE(),
	product_id			int				NULL,
	game_price			decimal(10,2)	DEFAULT 0.00 CHECK (game_price >= 0),

	PRIMARY KEY		(game_id),
	FOREIGN KEY		(game_publisher) REFERENCES	[PUBLISHER](publisher_id) ON DELETE CASCADE, 
	FOREIGN KEY		(product_id) REFERENCES PRODUCT(product_id) ON DELETE NO ACTION,
	CONSTRAINT idGamesFormat	CHECK (game_id LIKE 'GA[0-9][0-9][0-9][0-9]'),
	CONSTRAINT dateValid		CHECK (date_released <= GETDATE())
);

CREATE TABLE [REVIEWS](
	game_review			varchar(6)			NOT NULL,
	review_id			varchar(6)			NOT NULL,
	rating_score		tinyint			CHECK (rating_score BETWEEN 1 AND 10),
	comment				varchar(800)	,
	date_posted			date			DEFAULT CAST(GETDATE() AS DATE) CHECK (date_posted <= GETDATE()),
	feedback_user		varchar(6)			,
	PRIMARY KEY (game_review,	review_id),
	FOREIGN KEY (game_review)	REFERENCES GAMES(game_id)	ON DELETE CASCADE, 
	FOREIGN KEY (feedback_user) REFERENCES [USER](account_id) ON DELETE SET NULL,

	CONSTRAINT idReviewFormat	CHECK (review_id LIKE 'GR[0-9][0-9][0-9][0-9]'),
);

CREATE TABLE [GAME_TAG](
	game_id			varchar(6),
	game_tag		varchar(20),
	PRIMARY KEY (game_id, game_tag),
	FOREIGN KEY (game_id) REFERENCES GAMES(game_id) ON DELETE CASCADE ON UPDATE CASCADE,
);

CREATE TABLE [_FOLLOW](
		follow_user varchar(6),
		publisher	varchar(6),
		PRIMARY KEY(follow_user, publisher),
		FOREIGN KEY (follow_user) REFERENCES [USER](account_id) ON DELETE CASCADE,
		FOREIGN KEY (publisher) REFERENCES PUBLISHER(publisher_id) ON DELETE CASCADE,
);

CREATE TABLE [_DISCOUNT](
	product_id			int				NOT NULL,
	sales_event			varchar(6)		NOT NULL,
	discounted_rate		tinyint			NOT NULL DEFAULT 10,
	discountable		bit				DEFAULT 0,
	PRIMARY KEY (product_id, sales_event),
	FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id) ON DELETE CASCADE,
	FOREIGN KEY (sales_event) REFERENCES SALES_EVENT(sales_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CHECK (discounted_rate BETWEEN 10 AND 100),
	CHECK (discountable IN (0,1)),
);

CREATE TABLE [WALLET](
  wallet_id			int				IDENTITY(1,1),
  user_id			varchar(6)			NOT NULL,
  balance			decimal(10,2)	DEFAULT 0.00 CHECK (balance >= 0),
  PRIMARY KEY (wallet_id, user_id),
  FOREIGN KEY (user_id) REFERENCES [USER](account_id),
  CONSTRAINT UQ_User_Wallet UNIQUE (user_id, wallet_id),
);

CREATE TABLE  [ACCOUNT_BANK](
  wallet_id			int				NOT NULL,
  user_id			varchar(6)			NOT NULL,
  date_activated	date			NOT NULL DEFAULT GETDATE(),
  bank_name			varchar(60)		NOT NULL UNIQUE,
  pin				varchar(4)		NOT NULL,
  PRIMARY KEY (wallet_id, user_id, date_activated, bank_name, pin),
  FOREIGN KEY (user_id, wallet_id) REFERENCES [WALLET](user_id, wallet_id) ON DELETE CASCADE,
  CONSTRAINT VaildPIN CHECK (pin LIKE '[0-9][0-9][0-9][0-9][0-9][0-9]'),
);

CREATE TABLE [TRANSACTION](
	transaction_id		varchar(6)		NOT NULL,
	date_purchased		date		DEFAULT GETDATE(),
	trans_status		varchar(10)	NOT NULL DEFAULT 'Pending',
	PRIMARY KEY (transaction_id),
	CONSTRAINT valid_status CHECK (trans_status IN ('Pending', 'Completed', 'Failed', 'Refunded'))
);

CREATE TABLE [_PURCHASE](
  product_id			int			NOT NULL,
  transaction_id		varchar(6)	NOT NULL,
  wallet_id				int			NOT NULL,
  account_id			varchar(6)	NOT NULL,
  purchased_quantity	int			NOT NULL DEFAULT 1 CHECK (purchased_quantity > 0),

  PRIMARY KEY (product_id, transaction_id),
  FOREIGN KEY (account_id, wallet_id) REFERENCES WALLET(user_id, wallet_id),
  FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id),
  FOREIGN KEY (transaction_id) REFERENCES [TRANSACTION](transaction_id),
);


CREATE TABLE ITEMS_AND_DLCS(
	game_id			varchar(6)		NOT NULL,
	sub_id			varchar(6)		NOT NULL,
	price			decimal(10,2)	DEFAULT 0.00 CHECK (price >= 0),
	name			varchar(80)		NOT NULL,
	type			varchar(20)		NOT NULL,
	bundle			varchar(80)		NOT NULL,
	product_id		int				NULL,

	PRIMARY KEY (game_id, sub_id),
	FOREIGN KEY (game_id)	REFERENCES	GAMES(game_id) ON DELETE CASCADE,
	FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id) ON DELETE SET NULL,
	
	UNIQUE (game_id, sub_id),
);

--CREATE TABLE WORKSHOP_ITEMS(
--  workshop_id varchar(6),
--  date_posted date,
--  description varchar(2000),
--  create_user varchar(6) NOT NULL,
--  PRIMARY KEY (workshop_id),
--  FOREIGN KEY (create_user) REFERENCES USER(account_id)
--);

--CREATE TABLE _SUBCRIBE(
--  workshop_id varchar(6),
--  user_id varchar(6),
--  PRIMARY KEY (workshop_id, user_id),
--  FOREIGN KEY (user_id) REFERENCES USER(account_id),
--  FOREIGN KEY (workshop_id) REFERENCES WORKSHOP_ITEMS(workshop_id)
--);

--CREATE TABLE _MODS(
--  workshop_id varchar(6),
--  name varchar(80) NOT NULL,
--  game_applied varchar(6) NOT NULL,
--  compatible bool NOT NULL,
--  PRIMARY KEY (workshop_id),
--  FOREIGN KEY (game_applied) REFERENCES GAMES(game_id),
--  FOREIGN KEY (workshop_id) REFERENCES WORKSHOP_ITEMS(workshop_id)
--);

--CREATE TABLE MODS_CHANGELOG(
--  workshop_id varchar(6),
--  change_log varchar(200),
--  PRIMARY KEY (workshop_id,change_log),
--  FOREIGN KEY (workshop_id) REFERENCES MODS(workshop_id)
--);

--CREATE TABLE _SHARE_INCOME(
--  publisher_id varchar(6),
--  transaction_id varchar(6),
--  percent_shared decimal(10,2) NOT NULL,
--  PRIMARY KEY (publisher_id, transaction_id),
--  FOREIGN KEY (publisher_id) REFERENCES PUBLISHER(publisher_id),
--  FOREIGN KEY (transaction_id) REFERENCES TRANSACTIONS(transaction_id),
--  CHECK ( percent_shared>=0 and percent_shared<=100)
--);

--CREATE TABLE ARTWORKS(
--  workshop_id varchar(6),
--  caption varchar(200) NOT NULL,
--  PRIMARY KEY (workshop_id),
--  FOREIGN KEY (workshop_id) REFERENCES WORKSHOP_ITEMS(workshop_id)
--);

--CREATE TABLE ARTWORK_STYLE(
--  workshop_id varchar(6),
--  style varchar(20),
--  PRIMARY KEY (workshop_id,style),
--  FOREIGN KEY (workshop_id) REFERENCES ARTWORKS(workshop_id)
--);

CREATE TABLE _OWN( 
  product_id		int			,
  user_id			varchar(6)	,
  tradeable			bit			NOT NULL,
  quantity			int			CHECK (quantity > 0),
  PRIMARY KEY (product_id, user_id),
  FOREIGN KEY (user_id) REFERENCES [USER](account_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id) ON DELETE NO ACTION,
);

CREATE TABLE TRADE_BOX (
    tradebox_id VARCHAR(6) NOT NULL,
    user_id VARCHAR(6) NOT NULL,
    toffer_tradebox VARCHAR(6) NULL,
    toffer_user_id VARCHAR(6) NULL,
    date_traded DATE NULL DEFAULT NULL,
    trade_method VARCHAR(20) NULL CHECK (trade_method IN ('Direct', 'Auction', 'Exchange', 'Gift')),
    created_date DATETIME DEFAULT GETDATE(),
    
    PRIMARY KEY (user_id, tradebox_id),
    
    -- Self-referential foreign key with NO ACTION to prevent cycles
    FOREIGN KEY (toffer_user_id, toffer_tradebox) REFERENCES TRADE_BOX(user_id, tradebox_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
    
    FOREIGN KEY (user_id) REFERENCES [USER](account_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Additional constraints
    CONSTRAINT CHK_NoSelfTrade CHECK (
        (user_id <> toffer_user_id OR toffer_user_id IS NULL) AND
        (tradebox_id <> toffer_tradebox OR toffer_tradebox IS NULL)
    ),
    CONSTRAINT CHK_TradeCompletion CHECK (
        (date_traded IS NULL AND toffer_tradebox IS NULL AND toffer_user_id IS NULL) OR
        (date_traded IS NOT NULL AND toffer_tradebox IS NOT NULL AND toffer_user_id IS NOT NULL)
    ),
	UNIQUE (tradebox_id, user_id)
);

CREATE TABLE _TRADE_BOX_CONTAIN (
    product_id		INT			NOT NULL,
    user_id			VARCHAR(6)	NOT NULL,
    tradebox_id		VARCHAR(6)	NOT NULL,
    trade_quantity	INT DEFAULT 1 CHECK (trade_quantity > 0),
    
    PRIMARY KEY (product_id, tradebox_id, user_id),
    
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        
    FOREIGN KEY (tradebox_id, user_id) REFERENCES TRADE_BOX(tradebox_id, user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
);

CREATE TABLE FORUM(
	forum_id		varchar(6)		NOT NULL,
	title			varchar(80)		NOT NULL,
	forum_status	varchar(20)		NOT NULL  CHECK (forum_status IN ('Active', 'Closed', 'Archived', 'Pinned', 'Draft')),
	content			varchar(2000)	,
	media_url		varchar(200)	NULL CHECK (media_url IS NULL OR media_url LIKE 'http%'),
	create_user		varchar(6)		DEFAULT NULL,
	date_created	date			DEFAULT GETDATE(),
	game_discuss	varchar(6)		NULL,
	PRIMARY KEY (forum_id),
	FOREIGN KEY (create_user) REFERENCES [USER](account_id)		ON DELETE SET NULL ON UPDATE CASCADE,
	FOREIGN KEY (game_discuss) REFERENCES GAMES(game_id)		ON DELETE SET NULL ON UPDATE CASCADE,
);

CREATE TABLE _DISCUSS(
	discuss_forum	varchar(6)		NOT NULL,
	discuss_user	varchar(6)		NOT NULL,

	PRIMARY KEY (discuss_forum, discuss_user),
    FOREIGN KEY (discuss_forum) REFERENCES FORUM(forum_id) ON DELETE CASCADE,
    FOREIGN KEY (discuss_user) REFERENCES [USER](account_id) ON DELETE CASCADE,
	UNIQUE (discuss_forum, discuss_user),
);

CREATE TABLE _DISCUSS_REPLY(
	discuss_forum	varchar(6)		NOT NULL,
	discuss_user	varchar(6)		NOT NULL,
	media_url		varchar(200)	DEFAULT 'http%' CHECK (media_url LIKE 'http%'),
	text_reply		varchar(200)	NOT NULL,
	no_reply		int				NOT NULL,
	date_replied	date			DEFAULT GETDATE(),
  PRIMARY KEY (discuss_forum, discuss_user, media_url, text_reply, no_reply, date_replied),
  FOREIGN KEY (discuss_forum ,discuss_user) REFERENCES _DISCUSS(discuss_forum, discuss_user),
  UNIQUE(discuss_forum, discuss_user, no_reply),
);
