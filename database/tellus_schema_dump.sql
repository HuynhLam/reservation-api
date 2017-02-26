PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE "Users" (
	`userID`	INTEGER NOT NULL UNIQUE,
	`isAdmin`	INTEGER,
	`username`	TEXT NOT NULL UNIQUE,
	`password`	TEXT,
	`firstName`	TEXT,
	`lastName`	TEXT,
	`email`	TEXT,
	`contactNumber`	TEXT,
	PRIMARY KEY(`userID`)
);
CREATE TABLE "Rooms" (
	`roomID`	INTEGER NOT NULL UNIQUE,
	`roomName`	TEXT NOT NULL UNIQUE,
	`picture`	BLOB,
	`resources`	TEXT,
	PRIMARY KEY(`roomID`)
);
CREATE TABLE "Bookings" (
	`bookingID`	INTEGER NOT NULL UNIQUE,
	`roomName`	TEXT NOT NULL,
	`date`	INTEGER,
	`time`	INTEGER,
	`firstName`	TEXT,
	`lastName`	TEXT,
	`email`	TEXT,
	`contactNumber`	TEXT,
	PRIMARY KEY(`bookingID`)
);
COMMIT;
PRAGMA foreign_keys=ON;