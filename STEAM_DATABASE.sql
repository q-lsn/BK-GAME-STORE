-- CREATE DATABASE STEAM_PROJECT;

USE STEAM_PROJECT;
GO

-- Generate drop statements in correct dependency order
DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql += N'
PRINT ''Dropping ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + ''';
DROP TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + ';'
FROM sys.tables
ORDER BY 
    CASE WHEN name IN ('User', 'Wallet') THEN 0 ELSE 1 END, -- Drop dependent tables first
    name;

EXEC sp_executesql @sql;
GO

/*
**	Create [User] Table
**/
CREATE TABLE [User](
	AccountID		int				IDENTITY(1,1) PRIMARY KEY,
	UserName		varchar(32)		NOT NULL unique,
	BDate			date			,
	PhoneNumber		int				,
	Country			varchar			,
	Email			varchar			NOT NULL,
	
	CONSTRAINT validEmail CHECK (Email LIKE '%_@__%.__%'),
	CONSTRAINT validBirthDate CHECK (BDate <= cast(getdate() as Date) AND BDate > '1900-01-01'),
)

/*
**	Create [Publisher] Table
**/
CREATE TABLE [Publisher](
	PublisherID		int				IDENTITY(1,1) PRIMARY KEY,
	PName			varchar(256)	NOT NULL unique,
	Website			varchar(max)	NULL,
)

/*
**	Create [Game] Table
**/
CREATE TABLE [Game](
	GameID			int				IDENTITY(1,1) PRIMARY KEY,
	GName			varchar			NOT NULL,
	GPrice			decimal(10,2)	NOT NULL,
	Engine			varchar			NOT NULL,
	GDescription	varchar			,
	DReleased		date			,
	GamePublisher	int				FOREIGN KEY REFERENCES [Publisher](PublisherID),
	
	CONSTRAINT ValidPrice CHECK (GPrice >= 0),
)

/*
**	Create [Wallet] Table
**/

CREATE TABLE [Wallet](
    WalletID		int				IDENTITY(1,1),
    UserID			int				NOT NULL FOREIGN KEY REFERENCES [User](AccountID),
    Balance			decimal(15,2)	DEFAULT 0.00,
	PRIMARY KEY(WalletID, UserID),

	CONSTRAINT PositiveBalance CHECK (Balance >= 0),
);

/*
**	Create [Account_Bank] Table
**/
CREATE TABLE [Account_Bank](
    WalletID		int				NOT NULL,
    UserID			int				NOT NULL,
    DateActivated	date,
	BankName		varchar(32)		NOT NULL,
	PIN				int				NOT NULL,

	PRIMARY KEY(WalletID, UserID, DateActivated, BankName, PIN),
    FOREIGN KEY (WalletID, UserID) REFERENCES [Wallet](WalletID, UserID),
    CONSTRAINT ValidPIN CHECK (PIN BETWEEN 0000 AND 9999)

);

CREATE TABLE [Review](
	GameReview		int				NOT NULL FOREIGN KEY REFERENCES [Game](GameID),
	ReviewID		int				IDENTITY(1,1),
	ScoreRating		int				NOT NULL,
	PostDate		date			,
	FeedBackUser	int				NOT NULL FOREIGN KEY REFERENCES [User](AccountID),

	CONSTRAINT VaildScore CHECK (ScoreRating BETWEEN 1 AND 10),
)