'''
Database interface testing for all bookings related methods.
The booking has a data model represented by the following User dictionary:
    {
        "roomname": '',
        "date": '',
        "time": '',
        "firstname": '',
        "lastname": '',
        "email": '',
        "contactnumber": ''
    }

    where:

    * ``roomname``: Name of room to be booked.
    * ``date``: Date of booking.
    * ``time``: Time of booking.
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

BOOKING1 = {'roomname': 'Stage',
            'date': '20170301',
            'time': '1000',
            'firstname': 'Onur',
            'lastname': 'Ozuduru',
            'email': 'onur.ozuduru@ee.oulu.fi',
            'contactnumber': '0411311911'}
BOOKING2 = {'roomname': 'Chill',
            'date': '2017035',
            'time': '1200',
            'firstname': 'Paramartha',
            'lastname': 'Narendradhipa',
            'email': 'paramartha.n@ee.oulu.fi',
            'contactnumber': '0417511944'}
NON_EXIST_BOOKING = {   'roomname': 'Vodka',
                        'date': '20181212',
                        'time': '0800',
                        'firstname': 'Paramartha',
                        'lastname': 'Narendradhipa',
                        'email': 'paramartha.n@ee.oulu.fi',
                        'contactnumber': '0417511944'}
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
    def test_bookings_table_created(self):
        '''
        Checks that the table initially contains 2 bookings (check
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
            if booking['roomname'] == ROOMNAME1:
                self.assertEquals(len(booking), 7)
                self.assertDictContainsSubset(booking, BOOKING1)
            elif booking['roomname'] == ROOMNAME2:
                self.assertEquals(len(booking), 7)
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

    def test_zdelete_booking(self):
        '''
        Test that booking at room: 'Stage' on 2017-03-01 10:00 is deleted successfully
        '''
        print '(' + self.test_zdelete_booking.__name__ + ')', \
            self.test_zdelete_booking.__doc__
        resp = self.connection.delete_booking(BOOKING1['roomname'], int(BOOKING1['date']), int(BOOKING1['time']))
        self.assertTrue(resp)
        # Check is the booking really was deleted
        # Create the SQL Statement
        query = "SELECT * FROM Bookings WHERE roomname = ? AND date = ? AND time = ?" 
        # Connects to the database.
        con = self.connection.con
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Execute main SQL Statement
            pvalue = (BOOKING1['roomname'], BOOKING1['date'], BOOKING1['time'])
            cur.execute(query, pvalue)
            bookings = cur.fetchall()
            # Assert, len(bookings)>0 means delete booking was done improperly
            self.assertEquals(len(bookings), 0)

    def test_zdelete_non_exist_booking(self):
        '''
        Test delete_booking with the non-existing booking at room: 'Vodka' on 2018-12-12,08:00
        '''
        print '(' + self.test_zdelete_non_exist_booking.__name__ + ')', \
            self.test_zdelete_non_exist_booking.__doc__
        # Test delete_booking with a non existing booking
        resp = self.connection.delete_booking(NON_EXIST_BOOKING['roomname'], NON_EXIST_BOOKING['date'], NON_EXIST_BOOKING['time'])
        self.assertFalse(resp)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()