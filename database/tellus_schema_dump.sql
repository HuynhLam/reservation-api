BEGIN TRANSACTION;
CREATE TABLE "User" (
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
CREATE TABLE "Room" (
	`roomID`	INTEGER NOT NULL UNIQUE,
	`roomName`	TEXT NOT NULL UNIQUE,
	`picture`	BLOB,
	`resources`	TEXT,
	PRIMARY KEY(`roomID`)
);
CREATE TABLE "Booking" (
	`bookingID`	INTEGER NOT NULL UNIQUE,
	`roomName`	TEXT NOT NULL,
	`date`	INTEGER,
	`time`	INTEGER,
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
