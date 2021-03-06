'''
Database interface testing for all bookings related methods.
The booking has a data model represented by the following User dictionary:
    {
        "roomname": '',
        "username": '',
        "bookingTime": '',
        "firstname": '',
        "lastname": '',
        "email": '',
        "contactnumber": ''
    }

    where:

    * ``roomname``: Name of room to be booked.
    * ``username``: User name of the user create the booking.
    * ``bookingTime``: Date and time of the booking.
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

#CONSTANTS DEFINING DIFFERENT ROOMS AND BOOKING PROPERTIES
ROOMNAME1 = 'Stage'
ROOMNAME2 = 'Chill'
WRONG_ROOMNAME = 'Vodka'

BOOKING1 = {'bookingID': 1,
            'roomname': 'Stage',
            'username': 'onur',
            'bookingTime': '2017-03-01 12:00',
            'firstname': 'Onur',
            'lastname': 'Ozuduru',
            'email': 'onur.ozuduru@ee.oulu.fi',
            'contactnumber': '0411311911'}
BOOKING2 = {'bookingID': 2,
            'roomname': 'Chill',
            'bookingTime': '2017-03-27 16:00',
            'username': 'para',
            'firstname': 'Paramartha',
            'lastname': 'Narendradhipa',
            'email': 'paramartha.n@ee.oulu.fi',
            'contactnumber': '0417511944'}
NON_EXIST_BOOKING = {   'bookingID': 1441,
                        'roomname': 'Vodka',
                        'bookingTime': '2017-03-01 12:00',
                        'username': 'para',
                        'firstname': 'Paramartha',
                        'lastname': 'Narendradhipa',
                        'email': 'paramartha.n@ee.oulu.fi',
                        'contactnumber': '0417511944'}
NEW_BOOKING_ROOMNAME = 'Stage'
NEW_BOOKING_USERNAME = 'lam'
NEW_BOOKING_BOOKINGTIME = '2222-22-07 22:00'
NEW_BOOKING = {     'roomname': 'Chill',
                    'bookingTime': '2017-03-01 12:00',
                    'username': 'para',
                    'firstname': 'Paramartha',
                    'lastname': 'Narendradhipa',
                    'email': 'paramartha.n@ee.oulu.fi',
                    'contactnumber': '0417511944'}
MODIFY_BOOKING_BOOKINGID = 3
MODIFY_BOOKING_ROOMNAME = 'Aspire'
MODIFY_BOOKING_USERNAME = 'lam'
MODIFY_BOOKING_BOOKINGTIME = '2017-04-15 09:00'
MODIFY_BOOKING = {  'bookingID': 3,
                    'roomname': 'Aspire',
                    'bookingTime': '2018-17-07 17:00',
                    'username': 'lam',
                    'firstname': 'Lam',
                    'lastname': 'Huynh',
                    'email': 'lam.huynh@ee.oulu.fi',
                    'contactnumber': '0411322922'}
MODIFY_NONEXISTING_BOOKING_BOOKINGID = 1441
MODIFY_NONEXISTING_BOOKING_ROOMNAME = 'Vodka'
MODIFY_NONEXISTING_BOOKING_USERNAME = 'cloud'
MODIFY_NONEXISTING_BOOKING_BOOKINGTIME = '2017-03-11 25:00'
INITIAL_SIZE_BOOKING = 5


class BookingsDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Bookings from database API.
    It includes test cases for User, Room and Booking.
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

    # TESTS FOR Bookings
    # test_bookings_table_created function makes use of codes from Forum exercise
    def test_bookings_table_created(self):
        '''
        Checks that the table initially contains 5 bookings (check
        tellus_data_dump.sql). NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        # It is just to make sure there are some data in test db about Bookings.
        print '(' + self.test_bookings_table_created.__name__ + ')', \
            self.test_bookings_table_created.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM Bookings'
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
            self.assertEquals(len(users), INITIAL_SIZE_BOOKING)

    def test_get_bookings(self):
        '''
        Test that get_bookings work correctly without roomname
        '''
        print '(' + self.test_get_bookings.__name__ + ')', self.test_get_bookings.__doc__
        bookings = self.connection.get_bookings()
        # Check that the size is correct
        self.assertEquals(len(bookings), INITIAL_SIZE_BOOKING)
        # Iterate through bookings and check if the bookings with ROOMNAME1 and
        # ROOMNAME2 are correct:
        for booking in bookings:
            if booking['roomname'] == ROOMNAME1 and booking['firstname'] == BOOKING1['firstname']:
                self.assertEquals(len(booking), 8)
                self.assertDictContainsSubset(booking, BOOKING1)
            elif booking['roomname'] == ROOMNAME2 and booking['firstname'] == BOOKING2['firstname']:
                self.assertEquals(len(booking), 8)
                self.assertDictContainsSubset(booking, BOOKING2)

    def test_get_bookings_specific_roomname(self):
        '''
        Get all bookings for roomname "Chill".
        Check that it includes information for BOOKING2

        '''
        print '(' + self.test_get_bookings_specific_roomname.__name__ + ')', \
            self.test_get_bookings_specific_roomname.__doc__
        bookings = self.connection.get_bookings(roomname=ROOMNAME2)
        # Check length of the array is correct
        self.assertEquals(len(bookings), 1)
        # Check that data is correct
        self.assertDictContainsSubset(bookings[0], BOOKING2)

    def test_get_bookings_wrong_roomname(self):
        '''
        Test get_bookings with wrong roomname "Vodka"
        '''
        print '(' + self.test_get_bookings_wrong_roomname.__name__ + ')', \
            self.test_get_bookings_wrong_roomname.__doc__
        bookings = self.connection.get_bookings(roomname=WRONG_ROOMNAME)
        # Check length of the array is correct
        self.assertListEqual(bookings, [])

    def test_delete_booking(self):
        '''
        Test that booking at room: 'Stage' on 2017-03-01 10:00 with bookingID: 1 is deleted successfully
        '''
        print '(' + self.test_delete_booking.__name__ + ')', \
            self.test_delete_booking.__doc__
        resp = self.connection.delete_booking(BOOKING1['bookingID'], BOOKING1['roomname'], BOOKING1['username'], BOOKING1['bookingTime'])
        self.assertTrue(resp)
        # Check is the booking really was deleted
        # Create the SQL Statement
        query = "SELECT * FROM Bookings WHERE bookingID = ? AND roomname = ? AND username = ? AND bookingTime = ?" 
        # Connects to the database.
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Execute main SQL Statement
            pvalue = (BOOKING1['bookingID'], BOOKING1['roomname'], BOOKING1['username'], BOOKING1['bookingTime'])
            cur.execute(query, pvalue)
            bookings = cur.fetchall()
            # Assert, len(bookings)>0 means delete booking was done improperly
            self.assertEquals(len(bookings), 0)
            if len(bookings)==0:
                global INITIAL_SIZE_BOOKING
                INITIAL_SIZE_BOOKING -= 1 

    def test_delete_non_exist_booking(self):
        '''
        Test delete_booking with the non-existing booking at room: 'Vodka' on 2018-12-12,08:00
        '''
        print '(' + self.test_delete_non_exist_booking.__name__ + ')', \
            self.test_delete_non_exist_booking.__doc__
        # Test delete_booking with a non existing booking
        resp = self.connection.delete_booking(NON_EXIST_BOOKING['bookingID'], NON_EXIST_BOOKING['roomname'],\
                                            NON_EXIST_BOOKING['username'], NON_EXIST_BOOKING['bookingTime'])
        self.assertFalse(resp)

    def test_add_booking(self):
        '''
        Test that I can add new booking
        '''

        print '(' + self.test_add_booking.__name__ + ')', \
            self.test_add_booking.__doc__
        booking = self.connection.add_booking(NEW_BOOKING_ROOMNAME, NEW_BOOKING_USERNAME, NEW_BOOKING_BOOKINGTIME, NEW_BOOKING)
        global INITIAL_SIZE_BOOKING
        # Check that insert booking is not return None
        self.assertIsNotNone(booking)
        self.assertTupleEqual((INITIAL_SIZE_BOOKING+1, NEW_BOOKING_ROOMNAME, NEW_BOOKING_USERNAME, NEW_BOOKING_BOOKINGTIME), booking)
        # Check that booking is really created
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = "SELECT * FROM Bookings WHERE roomName = '%s' AND username = '%s' AND bookingTime = '%s'" % (NEW_BOOKING_ROOMNAME, NEW_BOOKING_USERNAME, NEW_BOOKING_BOOKINGTIME)
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
            booking = cur.fetchall()
            # Assert
            self.assertEquals(len(booking), 1)
            if len(booking) == 1:
                INITIAL_SIZE_BOOKING += 1

    def test_add_existing_booking(self):
        '''
        Test that I cannot add two booking with the same room name, username, and bookingTime
        '''
        print '(' + self.test_add_existing_booking.__name__ + ')', \
            self.test_add_existing_booking.__doc__
        booking = self.connection.add_booking(ROOMNAME1, BOOKING1['username'], BOOKING1['bookingTime'], BOOKING1)
        self.assertIsNone(booking)

    def test_add_booking_empty_dict(self):
        '''
        Test that I cannot add booking with empty dict
        '''
        print '(' + self.test_add_booking_empty_dict.__name__ + ')', \
            self.test_add_booking_empty_dict.__doc__
        booking = self.connection.add_booking(ROOMNAME1, BOOKING1['username'], BOOKING1['bookingTime'], {})
        self.assertIsNone(booking)

    def test_modify_booking(self):
        '''
        Test that I successfully modified a booking
        '''
        print '(' + self.test_modify_booking.__name__ + ')', \
            self.test_modify_booking.__doc__
        booking = self.connection.modify_booking(MODIFY_BOOKING_BOOKINGID, MODIFY_BOOKING_ROOMNAME, MODIFY_BOOKING_USERNAME, MODIFY_BOOKING_BOOKINGTIME, MODIFY_BOOKING)
        #Check is the modified OK
        self.assertIsNotNone(booking)
        #If it is OK, check the return values
        self.assertTupleEqual((MODIFY_BOOKING['bookingID'], MODIFY_BOOKING['roomname'], MODIFY_BOOKING['username'], MODIFY_BOOKING['bookingTime']), booking)
        # Check that booking is really modified
        # Create the SQL Statement
        query = "SELECT * FROM Bookings WHERE roomName=? AND username=? AND bookingTime=?"
        # Connects to the database.
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Execute main SQL Statement
            pvalue = (MODIFY_BOOKING['roomname'], MODIFY_BOOKING['username'], MODIFY_BOOKING['bookingTime'])
            cur.execute(query, pvalue)
            booking = cur.fetchall()
            # Assert
            self.assertEquals(len(booking), 1)
            if len(booking) == 1:
                global INITIAL_SIZE_BOOKING
                INITIAL_SIZE_BOOKING += 1

    def test_modify_nonexisting_booking(self):
        '''
        Test that I cannot modify a non existing booking
        '''
        print '(' + self.test_modify_nonexisting_booking.__name__ + ')', \
            self.test_modify_nonexisting_booking.__doc__
        booking = self.connection.modify_booking(MODIFY_NONEXISTING_BOOKING_BOOKINGID, MODIFY_NONEXISTING_BOOKING_ROOMNAME, \
                                                MODIFY_NONEXISTING_BOOKING_USERNAME, MODIFY_NONEXISTING_BOOKING_BOOKINGTIME, MODIFY_BOOKING)
        self.assertIsNone(booking)

    def test_modify_booking_empty_dict(self):
        '''
        Test that I cannot modify booking with empty dict
        '''
        print '(' + self.test_modify_booking_empty_dict.__name__ + ')', \
            self.test_modify_booking_empty_dict.__doc__
        booking = self.connection.modify_booking(BOOKING2['bookingID'], BOOKING2['roomname'], BOOKING2['username'], BOOKING2['bookingTime'], {})
        self.assertIsNone(booking)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()