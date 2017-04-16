import unittest
import json

import reservation.resources as resources
import reservation.database as database

#Path to the database file, different from the deployment db
#Please run setup script first to make sure test database is OK.
DB_PATH = "database/test_tellus.db"
ENGINE = database.Engine(DB_PATH)

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"

# Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True
# Necessary for correct translation in url_for
resources.app.config["SERVER_NAME"] = "localhost:5000"

# Database Engine utilized in our testing
resources.app.config.update({"Engine": ENGINE})

ROOM_NAME = "Stage"
WRONG_ROOM_NAME = "Room"
ROOM_REQUEST = {
    "name": ROOM_NAME,
    "resources": "Tables",
    "photo": "new_stage.jpg"
}
ROOM_WRONG_REQUEST = {
    "name": ROOM_NAME,
    "res": "Tables, Chairs"
}



class RoomTestCase(unittest.TestCase):
    # INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """
        Setup Class
        """
        print "Testing ", cls.__name__

    @classmethod
    def tearDownClass(cls):
        """TearDown Class"""
        print "Testing ENDED for ", cls.__name__

    def setUp(self):
        """
        Creates a client to use the API.
        """

        # Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        self.connection = ENGINE.connect()
        # Create a test client
        self.client = resources.app.test_client()
        self.url = resources.api.url_for(resources.Room, name=ROOM_NAME)
        self.wrong_url = resources.api.url_for(resources.Room, name=WRONG_ROOM_NAME)

    def tearDown(self):
        """
        Remove all records from database
        """
        self.app_context.pop()

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print "(" + self.test_url.__name__ + ")", self.test_url.__doc__
        with resources.app.test_request_context(self.url):
            view_point = resources.app.view_functions['room'].view_class
            self.assertEquals(view_point, resources.Room)

    def test_modify_room(self):
        """
        Modify an exsiting room and check that the room has been modified correctly in the server
        """
        print "("+self.test_modify_room.__name__+")", self.test_modify_room.__doc__
        resp = self.client.put(self.url,
                               data=json.dumps(ROOM_REQUEST),
                               headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 204)
        #Check that the room has been modified
        rooms = self.connection.get_rooms()
        room = rooms[0]
        self.assertEquals(room["picture"], ROOM_REQUEST["photo"])
        self.assertEquals(room["resources"], ROOM_REQUEST["resources"])

    def test_modify_unexisting_room(self):
        """
        Try to modify a room that does not exist
        """
        print "("+self.test_modify_unexisting_room.__name__+")", self.test_modify_unexisting_room.__doc__
        resp = self.client.put(self.wrong_url,
                                data=json.dumps(ROOM_REQUEST),
                                headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 404)

    def test_modify_wrong_type(self):
        """
        Checks that returns the correct status code if the Content-Type is wrong
        """
        print "(" + self.test_modify_wrong_type.__name__ + ")", self.test_modify_wrong_type.__doc__
        resp = self.client.put(self.url,
                                data=json.dumps(ROOM_REQUEST),
                                headers={"Content-Type": "text/html"})
        self.assertEquals(resp.status_code, 415)

    def test_modify_wrong_room(self):
        """
        Try to modify a room sending wrong data
        """
        print "("+self.test_modify_wrong_room.__name__+")", self.test_modify_wrong_room.__doc__
        resp = self.client.put(self.url,
                               data=json.dumps(ROOM_WRONG_REQUEST),
                               headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 400)

if __name__ == "__main__":
    print "Start running tests"
    unittest.main()