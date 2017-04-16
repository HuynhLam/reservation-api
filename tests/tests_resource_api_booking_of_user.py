import unittest, copy
import json

import flask

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

USER_NAME = "onur"
BOOKINGID = "1"
BOOKINGID_WRONG = "111111"


class BookingOfUserTestCase(unittest.TestCase):
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
        self.url = resources.api.url_for(resources.BookingOfUser, username=USER_NAME, booking_id=BOOKINGID)
        self.wrong_url = resources.api.url_for(resources.BookingOfUser, username=USER_NAME, booking_id=BOOKINGID_WRONG)

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
            view_point = resources.app.view_functions['booking_of_user'].view_class
            self.assertEquals(view_point, resources.BookingOfUser)

    def test_delete_booking(self):
        """
        Test deleting booking
        """
        print "("+self.test_delete_booking.__name__+")", self.test_delete_booking.__doc__
        resp = self.client.delete(self.url)
        self.assertEquals(resp.status_code, 204)

    def test_delete_nonexisting_booking(self):
        """
        Try to delete nonexisting booking with wrong bookingid.
        """
        print "("+self.test_delete_nonexisting_booking.__name__+")", self.test_delete_nonexisting_booking.__doc__
        resp = self.client.delete(self.wrong_url)
        self.assertEquals(resp.status_code, 404)

if __name__ == "__main__":
    print "Start running tests"
    unittest.main()