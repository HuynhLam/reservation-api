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
INSERT INTO `Users` VALUES (1,1,'onur','kirbac','Onur','Ozuduru','onur.ozuduru@ee.oulu.fi','0411311911');
INSERT INTO `Users` VALUES (2,0,'lam','pwp2017','Lam','Huynh','lam.huynh@ee.oulu.fi','0411322922');
INSERT INTO `Users` VALUES (3,0,'para','paradise','Paramartha','Narendradhipa','paramartha.n@ee.oulu.fi','0417511944');
CREATE TABLE "Rooms" (
	`roomID`	INTEGER NOT NULL UNIQUE,
	`roomName`	TEXT NOT NULL UNIQUE,
	`picture`	BLOB,
	`resources`	TEXT,
	PRIMARY KEY(`roomID`)
);
INSERT INTO `Rooms` VALUES (1,'Stage','stage.jpg','Projector, Microphone, Speaker, Webcam, Tables, Chairs');
INSERT INTO `Rooms` VALUES (2,'Aspire','aspire.jpg','TV, Webcam, Microphone, Tables, Chairs');
INSERT INTO `Rooms` VALUES (3,'Chill','chill.jpg','TV, Bean Bags');
CREATE TABLE "Bookings" (
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
INSERT INTO `Bookings` VALUES (1,'Stage',20170301,1000,'Onur','Ozuduru','onur.ozuduru@ee.oulu.fi','0411311911');
INSERT INTO `Bookings` VALUES (2,'Chill',2017035,1200,'Paramartha','Narendradhipa','paramartha.n@ee.oulu.fi','0417511944');
COMMIT;
