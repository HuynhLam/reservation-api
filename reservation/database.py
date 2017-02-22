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

    #DATABASE API
    #User
    def add_user(self, username, user_dict):
        pass

    def modify_user(self, username, user_dict):
        pass

    #Room
    def get_rooms(self):
        pass

    def modify_room(self, roomname, room_dict):
        pass

    #Booking
    def get_bookings(self):
        pass

    def add_booking(self, booking_dict):
        pass

    def modify_booking(self, roomname, date, time, booking_dict):
        pass

    def delete_booking(self, roomname, date, time, booking_dict):
        pass