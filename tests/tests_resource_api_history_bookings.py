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

LIMIT = 2
LIMIT_PARAM = "?limit=%i" % LIMIT

class HistoryBookingsTestCase(unittest.TestCase):
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
        self.url = resources.api.url_for(resources.HistoryBookings)
        self.url_w_limit = self.url + LIMIT_PARAM

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
            view_point = resources.app.view_functions['history_bookings'].view_class
            self.assertEquals(view_point, resources.HistoryBookings)

    def test_get_history_bookings(self):
        """
        Checks that get history bookings without limit returns the correct status code and data format
        """
        print "(" + self.test_get_history_bookings.__name__ + ")", self.test_get_history_bookings.__doc__
        resp = self.client.get(self.url)
        self.assertEquals(resp.status_code, 200)
        data = json.loads(resp.data)

        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("items", data)

        # Check that items are correct.
        items = data["items"]
        for item in items:
            self.assertIn("username", item)
            self.assertIn("bookingTime", item)
            self.assertIn("name", item)
            self.assertIn("@controls", item)
            self.assertIn("tellus:delete", item["@controls"])
            self.assertIn("profile", item["@controls"])
            self.assertIn("method", item["@controls"]["tellus:delete"])
            self.assertEqual(item["@controls"]["tellus:delete"]["method"], "DELETE")

    def test_get_history_bookings_with_limit(self):
        """
        Checks that get history bookings with limit of 2 returns the correct status code and data format
        """
        print "(" + self.test_get_history_bookings_with_limit.__name__ + ")", self.test_get_history_bookings_with_limit.__doc__
        resp = self.client.get(self.url_w_limit)
        self.assertEquals(resp.status_code, 200)
        data = json.loads(resp.data)

        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("items", data)

        # Check that items are correct.
        items = data["items"]
        self.assertEqual(len(items), LIMIT)
        for item in items:
            self.assertIn("username", item)
            self.assertIn("bookingTime", item)
            self.assertIn("name", item)
            self.assertIn("@controls", item)
            self.assertIn("tellus:delete", item["@controls"])
            self.assertIn("profile", item["@controls"])
            self.assertIn("method", item["@controls"]["tellus:delete"])
            self.assertEqual(item["@controls"]["tellus:delete"]["method"], "DELETE")

if __name__ == "__main__":
    print "Start running tests"
    unittest.main()