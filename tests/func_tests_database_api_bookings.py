'''
Tellus API function tests for all Bookings related methods.

User resource contain:
GET /bookings/ (Booking list)
    return code 200 + list of all Bookings in database or None if there is no Booking

PUT /rooms/{name}/bookings/{booking_id} (Bookings of Room)
    return code 204 successfully modified Room info
                400 wrong request format
                404 room not found
                415 unsupported Media Type
                500 Database error

DELETE /rooms/{name}/bookings/{booking_id} (Bookings of Room)
    return code 204 successfully delete Booking
                404 Booking non-exist

'''
import unittest, copy
import json

import flask
from flask import Flask

import reservation.resources as resources
import reservation.database as database

#Path to the database file, different from the deployment db
#Please run setup script first to make sure test database is OK.
DB_PATH = "database/test_tellus.db"
ENGINE = database.Engine(DB_PATH)

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"

TELLUS_USER_PROFILE = "/profiles/user_profile/"
TELLUS_ROOM_PROFILE = "/profiles/room_profile/"
TELLUS_BOOKING_PROFILE = "/profiles/booking_profile/"
ERROR_PROFILE = "/profiles/error_profile/"

#Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True
#Necessary for correct translation in url_for
local_host = "localhost:5000"
resources.app.config["SERVER_NAME"] = local_host

#Database Engine utilized in our testing
resources.app.config.update({"Engine": ENGINE})

#init data
initial_bookings = 5

class BookingsTestCase(unittest.TestCase):

    # Full format Booking.
    modify_booking_1 = {
        "bookingID": "1",
        "roomname":"Stage",
        "username":"onur",
        "bookingTime": "3333-12-12 02:00",
        "firstname": "Young",
        "lastname": "Uno",
        "email": "dark_vader@your.father",
        "contactnumber": "114"
    }
    # Wrong format Booking, with no username
    wrong_booking_format_1 = {
        "bookingID": "1",
        "roomname":"Stage",
        "bookingTime": "3333-12-12 02:00",
        "firstname": "Young",
        "lastname": "Uno",
        "email": "dark_vader@your.father",
        "contactnumber": "114"
    }
    # Wrong format Booking, with no bookingTime
    wrong_booking_format_2 = {
        "bookingID": "1",
        "roomname":"Stage",
        "username":"onur",
        "firstname": "Young",
        "lastname": "Uno",
        "email": "dark_vader@your.father",
        "contactnumber": "114"
    }
    # Non-existing booking
    non_existing_booking = {
        "bookingID": "1000",
        "roomname":"Chill",
        "username":"onur",
        "bookingTime": "3333-12-12 02:00",
        "firstname": "Young",
        "lastname": "Uno",
        "email": "dark_vader@your.father",
        "contactnumber": "114"
    }
    url = "/tellus/api/bookings/"

    def setUp(self):
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()
        
        roomname_1 = "Aspire"
        booking_id_1 = 3
        roomname_2 = "Chill"
        booking_id_2 = 12
        
        self.url1 = resources.api.url_for(resources.BookingOfRoom, booking_id=booking_id_1, name=roomname_1)
        self.url_wrong = resources.api.url_for(resources.BookingOfRoom, booking_id=booking_id_2, name=roomname_2)
        #print "***print url1 [%s]" % self.url1
        #print "***print url_wrong [%s]" % self.url_wrong

    def test_get_bookings(self):
        """
        Test that GET Rooms return correct status code and data format
        """
        print "("+self.test_get_bookings.__name__+")", self.test_get_bookings.__doc__

        # Test is the return code 200
        resp = self.client.get(flask.url_for("bookings"))
        self.assertEquals(resp.status_code, 200)

        # Test is the return data correct 
        data = json.loads(resp.data)
        
        #Check controls
        controls = data["@controls"]
        ## Check self
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)
        ## Check history-booking
        self.assertIn("tellus:history-bookings", controls)
        self.assertIn("href", controls["tellus:history-bookings"])
        self.assertEquals("http://" + local_host + controls["tellus:history-bookings"]["href"], flask.url_for("history_bookings"))

        #Check that items are correct.
        items = data["items"]
        self.assertEquals(len(items), initial_bookings)
        for item in items:
            self.assertIn("bookingID", item)
            self.assertIn("name", item)
            self.assertIn("username", item)
            self.assertIn("bookingTime", item)
            ## Check @control item
            self.assertIn("@controls", item)
            ## Check @control item _ profile
            self.assertIn("profile", item["@controls"])
            self.assertEquals(item["@controls"]["profile"]["href"], TELLUS_BOOKING_PROFILE)

            ## Check that add_control_delete_booking_of_room is correct
            self.assertIn("tellus:delete", item["@controls"])
            self.assertIn("title", item["@controls"]["tellus:delete"])
            self.assertIn("href", item["@controls"]["tellus:delete"])
            self.assertIn("method", item["@controls"]["tellus:delete"])
            self.assertEquals("http://" + local_host + item["@controls"]["tellus:delete"]["href"], resources.api.url_for(resources.BookingOfRoom, booking_id=item["bookingID"], name=item["name"]))

    def test_get_bookings_mimetype(self):
        """
        Checks that GET Rooms return correct status code and data format
        """
        print "("+self.test_get_bookings_mimetype.__name__+")", self.test_get_bookings_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(flask.url_for("bookings"))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, TELLUS_BOOKING_PROFILE))

    def test_modify_booking_of_room(self):
        """
        Test that we can successfully modify booking of room
        """
        print "("+self.test_modify_booking_of_room.__name__+")", self.test_modify_booking_of_room.__doc__

        # With a complete request
        resp = self.client.put(resources.api.url_for(resources.BookingOfRoom, booking_id=int(self.modify_booking_1["bookingID"]), name=self.modify_booking_1["roomname"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.modify_booking_1)
                               )

        self.assertEquals(resp.status_code, 204)
        
        con = resources.app.config["Engine"].connect()
        find_booking = filter(lambda x: "username" in x and x["username"] == self.modify_booking_1["username"] and "bookingTime" in x and x["bookingTime"] == self.modify_booking_1["bookingTime"], con.get_bookings(self.modify_booking_1["roomname"]))
        if find_booking:
            print "***Successfully modify booking_id %s" % self.modify_booking_1["bookingID"]

    def test_modify_booking_of_room_wrong_format(self):
        """
        Test that it returns error when is missing a mandatory data
        """
        print "("+self.test_modify_booking_of_room_wrong_format.__name__+")", self.test_modify_booking_of_room_wrong_format.__doc__

        # request body without username
        resp1 = self.client.put(resources.api.url_for(resources.BookingOfRoom, booking_id=int(self.wrong_booking_format_1["bookingID"]), name=self.wrong_booking_format_1["roomname"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.wrong_booking_format_1)
                               )
        self.assertEquals(resp1.status_code, 400)

        # request body without bookingTime
        resp2 = self.client.put(resources.api.url_for(resources.BookingOfRoom, booking_id=int(self.wrong_booking_format_2["bookingID"]), name=self.wrong_booking_format_2["roomname"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.wrong_booking_format_2)
                               )
        self.assertEquals(resp1.status_code, 400)

    def test_modify_non_existing_booking_of_room(self):
        """
        Test that we can not modify an existence booking in a specific room
        """
        print "("+self.test_modify_non_existing_booking_of_room.__name__+")", self.test_modify_non_existing_booking_of_room.__doc__
        resp = self.client.put(resources.api.url_for(resources.BookingOfRoom, booking_id=int(self.non_existing_booking["bookingID"]), name=self.non_existing_booking["roomname"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.non_existing_booking)
                               )
        self.assertEquals(resp.status_code, 404)

    def test_modify_booking_of_room_wrong_media_type(self):
        """
        Test that return adequate error if sent incorrect mime type
        """
        print "("+self.test_modify_booking_of_room_wrong_media_type.__name__+")", self.test_modify_booking_of_room_wrong_media_type.__doc__
        resp = self.client.put(resources.api.url_for(resources.BookingOfRoom, booking_id=int(self.modify_booking_1["bookingID"]), name=self.modify_booking_1["roomname"]),
                                headers={"Content-Type": "application/xml"},
                                data=json.dumps(self.modify_booking_1)
                               )
        self.assertEquals(resp.status_code, 415)

    def test_delete_booking_of_room(self):
        """
        Test that resourses class can delete an existence Booking of a specific room
        """
        print "("+self.test_delete_booking_of_room.__name__+")", self.test_delete_booking_of_room.__doc__
        # Check that delete an unexisting user, code 404
        resp = self.client.delete(self.url1)
        self.assertEquals(resp.status_code, 204)
        # DELETE is idempotent HTTP methods, so we can check was User 
        # successfully deleted by re-run DELETE with the same URL
        resp = self.client.delete(self.url1)
        self.assertEquals(resp.status_code, 404)
        if resp.status_code == 404:
            global initial_bookings
            initial_bookings -= 1

    def test_delete_unexisting_booking_of_room(self):
        """
        Test that Delete User when given a wrong address
        """
        print "("+self.test_delete_unexisting_booking_of_room.__name__+")", self.test_delete_unexisting_booking_of_room.__doc__
        # Check that delete an unexisting user, code 404
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

if __name__ == "__main__":
    print "Start running tests"
    unittest.main()
