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
    `username`  TEXT NOT NULL,
    `bookingTime`   TEXT,
	`firstName`	TEXT,
	`lastName`	TEXT,
	`email`	TEXT,
	`contactNumber`	TEXT,
	PRIMARY KEY(`bookingID`)
    FOREIGN KEY(roomName) REFERENCES Rooms(roomName) ON DELETE CASCADE,
    FOREIGN KEY(username) REFERENCES Users(username) ON DELETE CASCADE
);
COMMIT;
PRAGMA foreign_keys=ON;