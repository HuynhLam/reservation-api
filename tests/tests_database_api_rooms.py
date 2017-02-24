'''
Database interface testing for all Rooms related methods.
The room is a dictionary that contains:
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

import unittest, sqlite3
from reservation import database

#Path to the database file, different from the deployment db
#Please run setup script first to make sure test database is OK.
DB_PATH = "database/test_tellus.db"
ENGINE = database.Engine(DB_PATH)

#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
ROOM_NAME_1 = 'Stage'
ROOM1 = {   'roomid': '1',
            'roomname': 'Stage',
            'picture': 'stage.jpg',
            'resources': 'Projector, Microphone, Speaker, Webcam, Tables, Chairs'}

ROOM_NAME_2 = 'Aspire'
MODIFY_ROOM2 = {    'roomid': 2,
                    'roomname': 'Aspire',
                    'picture': 'aspire_image_update.jpg',
                    'resources': 'TV, Webcam, Microphone, Tables, Chairs, Books, Computers, Printers'}

ROOM_NAME_3 = 'Chill'
ROOM3 = {   'roomid': '3',
            'roomname': 'Chill',
            'picture': 'chill.jpg',
            'resources': 'TV, Bean Bags'}
            
ROOM_WRONG_ROOMNAME = 'Parempaa'
INITIAL_ROOMS_SIZE = 3


class RoomsDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the database API.
    It includes test cases for Rooms.
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

    # Test init Rooms table.
    def test_rooms_table_created(self):
        '''
        Checks that the table initially contains 3 Rooms.
        (check tellus_data_dump.sql).
        NOTE: Do not use Connection instance but call directly SQL.
        '''
        print '('+self.test_rooms_table_created.__name__+')', \
              self.test_rooms_table_created.__doc__
        #Create the SQL Statement
        query = 'SELECT * FROM Rooms'
        #Connects to the database.
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Execute main SQL Statement
            cur.execute(query)
            rooms = cur.fetchall()
            #Assert
            self.assertEquals(len(rooms), INITIAL_ROOMS_SIZE)

    # Test _create_room_object method.
    def test_create_room_object(self):
        '''
        Check that the method _create_room_object works properly and 
        return adequate values for the first database row. 
        NOTE: Do not use Connection instance but call directly SQL.
        '''
        print '('+self.test_create_room_object.__name__+')', \
              self.test_create_room_object.__doc__
        #Create the SQL Statement
        query = 'SELECT * FROM Rooms'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Execute main SQL Statement
            cur.execute(query)
            #Extract the 1 row
            row = cur.fetchone()
        #Test the method _create_room_object
        room = self.connection._create_room_object(row)
        self.assertDictContainsSubset(room, ROOM1)

    #TESTS FOR Rooms
    def test_get_rooms(self):
        '''
        Test that get_rooms work correctly and extract required room info
        '''
        print '('+self.test_get_rooms.__name__+')', \
              self.test_get_rooms.__doc__
        rooms = self.connection.get_rooms()
        #Check that the size is correct
        self.assertEquals(len(rooms), INITIAL_ROOMS_SIZE)
        #Iterate through all rooms and check if the rooms with ROOM_NAME_1 and
        #ROOM_NAME_3 are correct format:
        for room in rooms:
            if room['roomname'] == ROOM_NAME_1:
                self.assertDictContainsSubset(room, ROOM1)
            elif room['roomname'] == ROOM_NAME_3:
                self.assertDictContainsSubset(room, ROOM3)

    def test_modify_room(self):
        '''
        Test that Room #2 Aspire is modifed successful
        '''
        print '('+self.test_modify_room.__name__+')', \
              self.test_modify_room.__doc__
        #Get the modified Room
        resp = self.connection.modify_room(ROOM_NAME_2, MODIFY_ROOM2)
        self.assertEquals(resp, ROOM_NAME_2)
        
        #Check that the room has been really modified
        rooms = self.connection.get_rooms()
        #Check that the size that, we modify but not ADD new room.
        self.assertEquals(len(rooms), INITIAL_ROOMS_SIZE)
        
        #Check the expected values
        room_new_picture    = rooms[1]['picture']
        room_new_resources  = rooms[1]['resources']
        self.assertEquals(MODIFY_ROOM2['picture'], room_new_picture)
        self.assertEquals(MODIFY_ROOM2['resources'], room_new_resources)
        MODIFY_ROOM2['roomid'] = '2'
        self.assertDictContainsSubset(rooms[1], MODIFY_ROOM2)

    def test_modify_room_with_no_existing_roomname(self):
        '''
        Test modify_room with roomname 'Parempaa' (no-existing-roomname)
        '''
        print '('+self.test_modify_room_with_no_existing_roomname.__name__+')', \
              self.test_modify_room_with_no_existing_roomname.__doc__
        #Test with existing Room1
        resp = self.connection.modify_room(ROOM_WRONG_ROOMNAME, ROOM1)
        self.assertIsNone(resp)


if __name__ == '__main__':
    print 'Start running Rooms tests'
    unittest.main()