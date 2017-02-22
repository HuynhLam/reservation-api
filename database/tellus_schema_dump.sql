BEGIN TRANSACTION;
CREATE TABLE "User" (
	`userID`	INTEGER NOT NULL UNIQUE,
	`accountType`	TEXT,
	`username`	TEXT,
	`password`	TEXT,
	`firstName`	TEXT,
	`lastName`	TEXT,
	`email`	TEXT,
	`contactNumber`	TEXT,
	PRIMARY KEY(`userID`)
);
CREATE TABLE "Room" (
	`roomID`	INTEGER NOT NULL UNIQUE,
	`roomName`	TEXT UNIQUE,
	`picture`	BLOB,
	`resources`	TEXT,
	PRIMARY KEY(`roomID`)
);
CREATE TABLE "Booking" (
	`bookingID`	INTEGER NOT NULL UNIQUE,
	`roomName`	TEXT,
	`date`	NUMERIC,
	`time`	NUMERIC,
	`firstName`	TEXT,
	`lastName`	TEXT,
	`email`	TEXT,
	`contactNumber`	TEXT,
	PRIMARY KEY(`bookingID`),
	FOREIGN KEY(`roomName`) REFERENCES `Room`(`roomID`),
	FOREIGN KEY(`firstName`) REFERENCES `User`(`userID`),
	FOREIGN KEY(`lastName`) REFERENCES `User`(`userID`),
	FOREIGN KEY(`email`) REFERENCES `User`(`userID`),
	FOREIGN KEY(`contactNumber`) REFERENCES `User`(`userID`)
);
COMMIT;
