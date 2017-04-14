import sqlite3

# Default path for database
DEFAULT_DB_PATH = "database/tellus.db"


# Engine class makes use of codes from Forum exercise
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
    '''
    API to access the Tellus database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    '''
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
    # check_foreign_keys_status function makes use of codes from Forum exercise
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

    # set_foreign_keys_support function makes use of codes from Forum exercise
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

    # unset_foreign_keys_support function makes use of codes from Forum exercise
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
    # _create_user_object function makes use of codes from Forum exercise
    def _create_user_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {
                    "userid": '',
                    "accounttype": '',
                    "username": '',
                    "password": '',
                    "firstname": '',
                    "lastname": '',
                    "email": '',
                    "contactnumber": ''
                }

            where:

            * ``userid``: Unique identifying user ID.
            * ``isAdmin``: Account type to identify User or Admin.
            * ``username``: Username of user login.
            * ``password``: User's login password.
            * ``firstname``: First name of user.
            * ``lastname``: Last name of user.
            * ``email``: Email of user.
            * ``contactnumber``: Contact number of user.

            Note that all values are string if they are not otherwise indicated.

        '''
        return {
            "userID": str(row["userID"]),
            "isAdmin": str(row["isAdmin"]),
            "username": row["username"],
            "password": row["password"],
            "firstname": row["firstName"],
            "lastname": row["lastName"],
            "email": row["email"],
            "contactnumber": row["contactNumber"]
        }
    
    # _create_room_object function makes use of codes from Forum exercise
    def _create_room_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {
                    "roomid": '',
                    "roomname": '',
                    "picture": '',
                    "resources": ''
                }

            where:

            * ``roomid``: Unique identifying room ID.
            * ``roomname``: Name of room to be booked.
            * ``picture``: Image of the room.
            * ``resources``: Room equiments.

        '''
        return {
            "roomid": str(row["roomID"]),
            "roomname": row["roomName"],
            "picture": row["picture"],
            "resources": row["resources"]
        }

    # _create_booking_object function makes use of codes from Forum exercise
    def _create_booking_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {
                    "bookingID": '',
                    "roomname": '',
                    "username": '',
                    "bookingTime": '',
                    "firstname": '',
                    "lastname": '',
                    "email": '',
                    "contactnumber": ''
                }

            where:

            * ``bookingID``: ID number of the booking.
            * ``roomname``: Name of room to be booked.
            * ``username``: User name of the user create the booking.
            * ``bookingTime``: Date and time of booking.
            * ``firstname``: First name of user.
            * ``lastname``: Last name of user.
            * ``email``: Email of user.
            * ``contactnumber``: Contact number of user.

            Note that all values are string if they are not otherwise indicated.

        '''
        return {
            "bookingID": row["bookingID"],
            "roomname": row["roomName"],
            "username": str(row["username"]),
            "bookingTime": str(row["bookingTime"]),
            "firstname": row["firstName"],
            "lastname": row["lastName"],
            "email": row["email"],
            "contactnumber": row["contactNumber"]
        }

    #DATABASE API
    #User
    def get_users(self):
        '''
        Extracts all existence Users in the database.
        :return:A list of Users. Each user is a dictionary containing
                the following keys:

            *``userID``     :ID of User. INTEGER. UNIQUE.
            *``isAdmin``    :is current user admin or not. 0 mean not admin. INTEGER. UNIQUE.
            *``username``   :Username. TEXT. UNIQUE.
            *``password``   :User password. TEXT.
            *``firstName``  :First name of user. TEXT.
            *``lastname``   :Last name of user. TEXT.
            *``email``      :User's email address. TEXT.
            *``contactnumber``  :User's contact number. TEXT.

            *There is no FOREIGN KEY.
            *None is returned if the database has no Users.

        '''
        # SQL query to get the list of existence Users
        query = 'SELECT * FROM Users'
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
        users = []
        for row in rows:
            users.append(self._create_user_object(row))
        return users

    def add_user(self, username, user_dict):
        '''
        Create a new user in the database.

        :param str username: The username of the user to add
        :param dict user_dict: a dictionary with the information to be modified. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {
                        "userid": '',
                        "accounttype": '',
                        "username": '',
                        "firstname": '',
                        "lastname": '',
                        "email": '',
                        "contactnumber": ''
                    }

                where:

                * ``userid``: Unique identifying user ID.
                * ``accounttype``: Account type to identify User or Admin.
                * ``username``: Username of user login.
                * ``firstname``: First name of user.
                * ``lastname``: Last name of user.
                * ``email``: Email of user.
                * ``contactnumber``: Contact number of user.

            Note that all values are string if they are not otherwise indicated.

        :return: the username of the modified user or None if the
            ``username`` passed as parameter is already  in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
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
            # We do not do any composition and return the username
            return username
        else:
            return None

    def delete_user(self, username):
        '''
        Remove all user information of the user with the username passed in as
        argument.

        :param str username: The username of the user to remove.

        :return: True if the user is deleted, False otherwise.

        '''
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
            *``picture``    :Image of the room. BLOB.
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
        query2 = 'UPDATE Rooms SET picture = ?,resources = ? WHERE roomname = ?'
        # Check dict
        if not 'picture' in room_dict:
            return None
        if not 'resources' in room_dict:
            return None

        #temporal variables
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
            #execute the main statement
            pvalue = (_picture, _resources, roomName)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that we have modified the user
            if cur.rowcount < 1:
                return None
            return roomName

    #Booking
    def get_bookings(self, roomname=None):
        '''
        Return a list of all the bookings in the database filtered by the
        roomname if it is passed as argument.

        :param roomname: default None. Search bookings of a room with the given
            roomname. If this parameter is None, it returns the bookings of
            any room in the system.
        :type roomname: str

        :return: A list of bookings. Each booking is a dictionary containing
            the following keys:

            * ``bookingID``: ID number of the booking.
            * ``roomname``: Name of room to be booked.
            * ``username``: user name of user who create the booking.
            * ``bookingTime``: Date and time of the booking.
            * ``firstname``: First name of user.
            * ``lastname``: Last name of user.
            * ``email``: Email of user.
            * ``contactnumber``: Contact number of user.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
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

    def add_booking(self, roomname, username, bookingTime, booking_dict):
        '''
        Add the information of a booking.

        :param string roomname: The name of the room to book
        :param string username: The user name of user who create the booking
        :param string bookingTime: Date and time of the booking
        :param dict booking: a dictionary with the information to be modified.

        :return: tuple booking: a tuple which includes roomname username and bookingTime
            it returns None if booking is not added to database.

        '''
        # Create the SQL Statements
        # SQL Statement for extracting the bookingID given a bookingID
        query1 = 'SELECT bookingID from Bookings WHERE roomName = ? AND username = ? AND bookingTime = ?'
        # SQL Statement to create the row in  Bookings table
        query2 = 'INSERT INTO Bookings(roomName, username, bookingTime, firstName, lastName, email, contactNumber)\
                                        VALUES(?,?,?,?,?,?,?)'
        # Check dict
        if not 'firstname' in booking_dict:
            return None
        if not 'lastname' in booking_dict:
            return None
        if not 'email' in booking_dict:
            return None
        if not 'contactnumber' in booking_dict:
            return None

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the statement to extract the roomname, username, bookingTime associated to a bookingID
        pvalue = (roomname, username, bookingTime)
        cur.execute(query1, pvalue)
        # Returns row if already exists
        row = cur.fetchone()
        # If there is no booking add rows in Bookings and booking details
        if row is None:
            # Add the row in Bookings table
            # Execute the statement
            pvalue = (roomname, username, bookingTime, booking_dict['firstname'], booking_dict['lastname'],
                      booking_dict['email'], booking_dict['contactnumber'])
            cur.execute(query2, pvalue)
            # Get last row id (AUTO_INCREMENT)
            booking_id = cur.lastrowid
            self.con.commit()
            # We do not do any comprobation and return the booking_id, roomname, username, bookingTime
            return booking_id, roomname, username, bookingTime
        else:
            return None

    def modify_booking(self, booking_id, roomname, username, bookingTime, booking_dict):
        '''
        Modify the information of a booking.

        :param string roomname: The name of the room to book
        :param string username: The user name of user who create the booking
        :param string bookingTime: Date and bookingTime of the booking
        :param dict booking: a dictionary with the information to be modified.

        :return: tuple booking: a tuple which includes roomname username and bookingTime
            it returns None if booking is not modify in database.

        '''
        # Create the SQL Statements
        # SQL Statement for extracting the bookingID given a bookingID
        query1 = 'SELECT bookingID from Bookings WHERE bookingID = ? AND roomName = ? AND username = ? AND bookingTime = ?'
        # SQL Statement to create the row in Bookings table
        query2 = 'UPDATE Bookings SET roomName=?, username=?, bookingTime=?, firstName=?,\
                                    lastName=?, email=?, contactNumber=?\
                                    WHERE roomName = ? AND username = ? AND bookingTime = ?'

        # Check dict
        if not 'bookingID' in booking_dict:
            return None
        if not 'roomname' in booking_dict:
            return None
        if not 'username' in booking_dict:
            return None
        if not 'bookingTime' in booking_dict:
            return None
        if not 'firstname' in booking_dict:
            return None
        if not 'lastname' in booking_dict:
            return None
        if not 'email' in booking_dict:
            return None
        if not 'contactnumber' in booking_dict:
            return None

        #temporal variables
        _roomname       = booking_dict.get('roomname', None)
        _username       = booking_dict.get('username', None)
        _bookingtime    = booking_dict.get('bookingTime', None)
        _firstname      = booking_dict.get('firstname', None)
        _lastname       = booking_dict.get('lastname', None)
        _email          = booking_dict.get('email', None)
        _contactnumber  = booking_dict.get('contactnumber', None)
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the statement to extract the roomname, username, bookingTime associated to a bookingID
        pvalue = (booking_id, roomname, username, bookingTime)
        cur.execute(query1, pvalue)
        # Returns row if already exists
        row = cur.fetchone()
        # If there is no booking return None, otherwise update the existence booking
        if row is None:
            return None
        else:
            # Update the row in Bookings table
            # Execute the statement
            pvalue = (_roomname, _username, _bookingtime, _firstname, _lastname, _email, _contactnumber, roomname, username, bookingTime)
            cur.execute(query2, pvalue)
            self.con.commit()
            # We do not do any comprobation and return the booking_id, roomname, username, bookingTime
            return booking_id, _roomname, _username, _bookingtime

    def delete_booking(self, booking_id, roomName=None, username=None, bookingTime=None):
        '''
        Delete the booking with id given as parameter.
        :return: True if the booking has been deleted, False otherwise

        '''
        #Create the SQL Statements
        query = "DELETE FROM Bookings WHERE bookingID = ? AND roomName = ? AND username = ? AND bookingTime = ?"
        # Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (booking_id, roomName, username, bookingTime)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True