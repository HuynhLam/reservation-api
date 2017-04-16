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
WRONG_ROOM_NAME = "room"
NEW_BOOKING_REQUEST = {
    "username": "lam",
    "bookingTime": "2017-03-01 10:00",
    "email": "lam.huynh@ee.oulu.fi",
    "familyName": "Huynh",
    "givenName": "Lam",
    "telephone": "0411322922"
}
CONFLICT_BOOKING_REQUEST = {
    "username": "lam",
    "bookingTime": "2017-03-01 12:00",
    "email": "lam.huynh@ee.oulu.fi",
    "familyName": "Huynh",
    "givenName": "Lam",
    "telephone": "0411322922"
}
WRONG_BOOKING_REQUEST = {
    "mail": "lam.huynh@ee.oulu.fi",
    "family": "Huynh",
    "givenName": "Lam",
    "telephone": "0411322922"
}



class BookingsOfRoomTestCase(unittest.TestCase):
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
        self.url = resources.api.url_for(resources.BookingsOfRoom, name=ROOM_NAME)
        self.wrong_url = resources.api.url_for(resources.BookingsOfRoom, name=WRONG_ROOM_NAME)

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
            view_point = resources.app.view_functions['bookings_of_room'].view_class
            self.assertEquals(view_point, resources.BookingsOfRoom)

    def test_get_bookings_of_room(self):
        """
        Checks that get bookings of room returns the correct status code and data format
        """
        print "(" + self.test_get_bookings_of_room.__name__ + ")", self.test_get_bookings_of_room.__doc__
        resp = self.client.get(self.url)
        self.assertEquals(resp.status_code, 200)
        data = json.loads(resp.data)

        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("tellus:bookings-all", controls)
        self.assertIn("tellus:add-booking", controls)
        self.assertIn("items", data)

        # Check add booking
        add_booking = controls["tellus:add-booking"]
        self.assertIn("title", add_booking)
        self.assertIn("href", add_booking)
        self.assertIn("encoding", add_booking)
        self.assertIn("method", add_booking)
        self.assertEqual(add_booking["method"], "POST")
        self.assertIn("schema", add_booking)

        # Check add bookings schema
        add_booking_schema = add_booking["schema"]
        self.assertIn("type", add_booking_schema)
        self.assertIn("properties", add_booking_schema)
        self.assertIn("required", add_booking_schema)

        # Check add bookings schema properties
        add_booking_schema_properties = add_booking_schema["properties"]
        self.assertIn("username", add_booking_schema_properties)
        self.assertIn("bookingTime", add_booking_schema_properties)
        self.assertIn("email", add_booking_schema_properties)
        self.assertIn("familyName", add_booking_schema_properties)
        self.assertIn("givenName", add_booking_schema_properties)
        self.assertIn("telephone", add_booking_schema_properties)
        self.assertIn("name", add_booking_schema_properties)

        # Check that items are correct.
        items = data["items"]
        for item in items:
            self.assertIn("username", item)
            self.assertIn("bookingTime", item)
            self.assertIn("name", item)
            self.assertIn("@controls", item)
            self.assertIn("tellus:delete", item["@controls"])
            self.assertIn("profile", item["@controls"])
            self.assertIn("collection", item["@controls"])
            self.assertIn("edit", item["@controls"])
            self.assertIn("method", item["@controls"]["tellus:delete"])
            self.assertEqual(item["@controls"]["tellus:delete"]["method"], "DELETE")
            self.assertIn("method", item["@controls"]["edit"])
            self.assertEqual(item["@controls"]["edit"]["method"], "PUT")
            self.assertIn("title", item["@controls"]["edit"])
            self.assertIn("schema", item["@controls"]["edit"])
            self.assertIn("href", item["@controls"]["edit"])
            self.assertIn("encoding", item["@controls"]["edit"])

    def test_get_nonexisting_bookings_of_room(self):
        """
        Try to get nonexisting bookings with wrong roomname.
        """
        print "("+self.test_get_nonexisting_bookings_of_room.__name__+")", self.test_get_nonexisting_bookings_of_room.__doc__
        resp = self.client.get(self.wrong_url)
        self.assertEquals(resp.status_code, 404)

    def test_create_booking(self):
        """
        Test create booking
        """
        print "("+self.test_create_booking.__name__+")", self.test_create_booking.__doc__
        resp = self.client.post(self.url,
                               data=json.dumps(NEW_BOOKING_REQUEST),
                               headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 201)
        #Check that the booking has been added
        bookings = self.connection.get_bookings(ROOM_NAME)
        booking = bookings[-1]
        self.assertEquals(booking["bookingTime"], NEW_BOOKING_REQUEST["bookingTime"])

    def test_add_existing_booking(self):
        """
        Try to add a booking that conflicts
        """
        print "("+self.test_add_existing_booking.__name__+")", self.test_add_existing_booking.__doc__
        resp = self.client.post(self.url,
                                data=json.dumps(CONFLICT_BOOKING_REQUEST),
                                headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 409)

    def test_add_wrong_type(self):
        """
        Checks that returns the correct status code if the Content-Type is wrong
        """
        print "(" + self.test_add_wrong_type.__name__ + ")", self.test_add_wrong_type.__doc__
        resp = self.client.post(self.url,
                                data=json.dumps(NEW_BOOKING_REQUEST),
                                headers={"Content-Type": "text/html"})
        self.assertEquals(resp.status_code, 415)

    def test_add_wrong_booking(self):
        """
        Try to add a booking sending wrong data
        """
        print "("+self.test_add_wrong_booking.__name__+")", self.test_add_wrong_booking.__doc__
        resp = self.client.post(self.url,
                               data=json.dumps(WRONG_BOOKING_REQUEST),
                               headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 400)

if __name__ == "__main__":
    print "Start running tests"
    unittest.main()