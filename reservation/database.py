import sqlite3

# Default path for database
DEFAULT_DB_PATH = "database/tellus.db"


class Engine(object):
    '''
        Abstraction of the database.

        It includes tools to connect to the sqlite file. You can access the Connection
        instance.
        :py:meth:`connection`.

        :Example:

        > engine = Engine()
        > con = engine.connect()

        :param db_path: The path of the database file (always with respect to the
            calling script. If not specified, the Engine will use the file located
            at *database/tellus.db*

    '''
    def __init__(self, db_path=None):
        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return Connection(self.db_path)


class Connection(object):
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()

    # FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        try:
            # Create a cursor to receive the database values
            cur = self.con.cursor()
            # Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            # We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print "Foreign Keys status: %s" % 'ON' if is_activated else 'OFF'
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            # execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    def unset_foreign_keys_support(self):
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            # execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    # Helpers
    def _create_user_object(self, row):
        return {
            "userid": row["userID"],
            "accounttype": row["accountType"],
            "username": row["username"],
            "firstname": row["firstName"],
            "lastname": row["lastName"],
            "email": row["email"],
            "contactnumber": row["contactNumber"]
        }

    def _create_room_object(self, row):
        return {
            "roomid": row["roomID"],
            "roomname": row["roomName"],
            "picture": row["picture"],
            "resources": row["resources"]
        }

    def _create_booking_object(self, row):
        return {
            "roomname": row["roomName"],
            "date": row["date"],
            "time": row["time"],
            "firstname": row["firstName"],
            "lastname": row["lastName"],
            "email": row["email"],
            "contactnumber": row["contactNumber"]
        }

    #DATABASE API
    #User
    def add_user(self, username, user_dict):
        # Create the SQL Statements
        # SQL Statement for extracting the userID given a username
        query1 = 'SELECT userID from Users WHERE username = ?'
        # SQL Statement to create the row in  User table
        query2 = 'INSERT INTO Users(isAdmin, username, password, firstName, lastName, email, contactNumber)\
                                  VALUES(?,?,?,?,?,?,?)'
        # temporal variables for user table
        _isadmin = user_dict.get('isadmin', 0)
        _password = user_dict.get('password', None)
        _firstname = user_dict.get('firstname', None)
        _lastname = user_dict.get('lastname', None)
        _email = user_dict.get('email', None)
        _contactnumber = user_dict.get('contactnumber', None)

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the statement to extract the id associated to a username
        pvalue = (username,)
        cur.execute(query1, pvalue)
        # No value expected (no other user with that username expected)
        row = cur.fetchone()
        # If there is no user add rows in user and user profile
        if row is None:
            # Add the row in users table
            # Execute the statement
            pvalue = (_isadmin, username, _password, _firstname, _lastname,
                      _email, _contactnumber)
            cur.execute(query2, pvalue)
            self.con.commit()
            # We do not do any comprobation and return the username
            return username
        else:
            return None

    def delete_user(self, username):
        # Create the SQL Statements
        # SQL Statement for deleting the user information
        query = 'DELETE FROM Users WHERE username = ?'
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the statement to delete
        pvalue = (username,)
        cur.execute(query, pvalue)
        self.con.commit()
        # Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    #Room
    def get_rooms(self):
        '''
        Extracts all existence rooms in the database.
        :return:A list of Rooms. Each Room is a dictionary containing
                the following keys:

            *``roomID``     :ID of the room. INTEGER. UNIQUE.
            *``roomName``   :Name of the room. TEXT. UNIQUE.
            *``picture``    :Image for the room. BLOB.
            *``resources``  :Room equiments. TEXT.

            *There is no FOREIGN KEY.
            *None is returned if the database has no rooms.

        '''
        # SQL query to get the list of existence rooms
        query = 'SELECT * FROM Rooms'
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        cur.execute(query)
        # Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        # Build the return object
        rooms = []
        for row in rows:
            rooms.append(self._create_room_object(row))
        return rooms

    def modify_room(self, roomName, room_dict):
        '''
        Modify the information of a room.

        :param string roomName: The name of the room to modify
        :param dict rpom: a dictionary with the information to be modified.

        :return: roomName of the modified room 
                 None if ``roomName`` parameter is not in the database.

        '''
        #Create the SQL Statements
        #SQL Statement for extracting the roomID from given a roomName
        query1 = 'SELECT roomID from Rooms WHERE roomName = ?'
        #SQL Statement to update the Rooms table
        query2 = 'UPDATE Rooms SET picture = ?,resources = ? WHERE room_id = ?'
        #temporal variables
        room_id = None
        _picture = room_dict.get('picture', None)
        _resources = room_dict.get('resources', None)
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a roomName
        pvalue = (roomName,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return None
        else:
            room_id = row["roomID"]
            #execute the main statement
            pvalue = (_picture, _resources, room_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that we have modified the user
            if cur.rowcount < 1:
                return None
            return roomName

    #Booking
    def get_bookings(self, roomname=None):
        # Create the SQL Statement build the string depending on the existence
        # of roomname argument.
        query = 'SELECT * FROM Bookings'
        # Nickname restriction
        if roomname is not None:
            query += " WHERE roomName = '%s'" % roomname
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        cur.execute(query)
        # Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        # Build the return object
        bookings = []
        for row in rows:
            bookings.append(self._create_booking_object(row))
        return bookings

    def add_booking(self, booking_dict):
        pass

    def modify_booking(self, roomname, date, time, booking_dict):
        pass

    def delete_booking(self, roomname, date, time, booking_dict):
        '''
        Delete the booking with id given as parameter.
        :return: True if the booking has been deleted, False otherwise

        '''
        #Create the SQL Statements
        query = "DELETE FROM Bookings WHERE roomname=?, date=?, time=?"
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (roomname, date, time,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True