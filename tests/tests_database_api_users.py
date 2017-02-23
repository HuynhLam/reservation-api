'''
Database interface testing for all users related methods.
The user has a data model represented by the following User dictionary:
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

'''
import unittest, sqlite3
from reservation import database

#Path to the database file, different from the deployment db
#Please run setup script first to make sure test database is OK.
DB_PATH = "database/test_tellus.db"
ENGINE = database.Engine(DB_PATH)

#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
NEW_USER = "newuser"
NEW_USER1 = "donut"
USER_DICT_CORRECT_DATA = {'isadmin': 0,
                          'password': 'test_pass',
                          'firstname': 'firstname0',
                          'lastname': 'lastname0',
                          'email': 'john@example.com',
                          'contactnumber': '69696969'}
USER_EMPTY_ROW = (0, u'donut', None, None, None, None, None)
EXSISTING_USER = "para"
NOT_EXSISTING_USER = "CrazyBoy95"
INITIAL_SIZE_USER = 4

class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Users from database API.
    It includes test cases for Users.
    '''
    #INITIATION METHODS
    def setUp(self):
        '''
        Populates the database
        '''
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection.
        '''
        self.connection.close()

    # Test for Users table.
    def test_users_table_created(self):
        '''
        Checks that the table initially contains 3 users (check
        tellus_data_dump.sql). NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        # It is just to make sure there are some data in test db about Users.
        print '('+self.test_users_table_created.__name__+')', \
              self.test_users_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM Users'
        #Connects to the database.
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            users = cur.fetchall()
            #Assert
            self.assertEquals(len(users), INITIAL_SIZE_USER)

    #TESTS FOR Users
    def test_add_user(self):
        '''
        Test that I can add new user
        '''
        print '(' + self.test_add_user.__name__ + ')', \
            self.test_add_user.__doc__
        username = self.connection.add_user(NEW_USER, USER_DICT_CORRECT_DATA)
        self.assertIsNotNone(username)
        self.assertEquals(username, NEW_USER)
        #Check that user is really created
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = "SELECT * FROM Users WHERE username = '%s'" % NEW_USER
        # Connects to the database.
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            cur.execute(query)
            users = cur.fetchall()
            # Assert
            self.assertEquals(len(users), 1)

    def test_add_existing_user(self):
        '''
        Test that I cannot add two users with the same username
        '''
        print '(' + self.test_add_existing_user.__name__ + ')', \
            self.test_add_existing_user.__doc__
        username = self.connection.add_user(EXSISTING_USER, USER_DICT_CORRECT_DATA)
        self.assertIsNone(username)

    def test_add_user_with_empty_user_dict(self):
        '''
        Test that I can add new user with empty dict (predefined data)
        '''
        print '(' + self.test_add_user_with_empty_user_dict.__name__ + ')', \
            self.test_add_user_with_empty_user_dict.__doc__
        username = self.connection.add_user(NEW_USER1, {})
        self.assertIsNotNone(username)
        self.assertEquals(username, NEW_USER1)
        #Check that user is really created
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = "SELECT * FROM Users WHERE username = '%s'" % NEW_USER1
        # Connects to the database.
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            cur.execute(query)
            users = cur.fetchall()
            # Assert
            self.assertEquals(len(users), 1)
            # Check data is same with predefined
            r_list = list(users[0])
            self.assertListEqual(r_list[1:8], list(USER_EMPTY_ROW))

    def test_delete_user(self):
        '''
        Test that the user "para" is deleted
        '''
        print '(' + self.test_delete_user.__name__ + ')', \
            self.test_delete_user.__doc__
        resp = self.connection.delete_user(EXSISTING_USER)
        self.assertTrue(resp)
        # Check that the user has been really deleted from db
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = "SELECT * FROM Users WHERE username = '%s'" % EXSISTING_USER
        # Connects to the database.
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            cur.execute(query)
            users = cur.fetchall()
            # Assert
            self.assertEquals(len(users), 0)

    def test_delete_user_noexistingnickname(self):
        '''
        Test delete_user with the non-existing user "CrazyBoy95"
        '''
        print '(' + self.test_delete_user_noexistingnickname.__name__ + ')', \
            self.test_delete_user_noexistingnickname.__doc__
        # Test with an existing user
        resp = self.connection.delete_user(NOT_EXSISTING_USER)
        self.assertFalse(resp)

if __name__ == '__main__':
    print 'Start running Users tests'
    unittest.main()