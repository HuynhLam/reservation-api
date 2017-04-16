'''
Tellus API function tests for all Rooms related methods.

User resource contain:
GET /rooms/
    return code 200 + list of Rooms in database or None if there is no Room

PUT /rooms/{name} 
    return code 204 successfully modified Room info
                400 wrong request format
                404 room not found
                415 unsupported Media Type
                500 Database error

'''
import unittest, copy
import json

import flask
from flask import Flask

import reservation.resources as resources
import reservation.database as database

#Path to the database file, different from the deployment db
#Please run setup script first to make sure test database is OK.
DB_PATH = "database/tellus.db"
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
initial_rooms = 3

class RoomsTestCase(unittest.TestCase):

    url = "/tellus/api/rooms/"

    def setUp(self):
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()

    def test_get_rooms(self):
        """
        Test that GET Rooms return correct status code and data format
        """
        print "("+self.test_get_rooms.__name__+")", self.test_get_rooms.__doc__

        # Test is the return code 200
        resp = self.client.get(flask.url_for("rooms_list"))
        self.assertEquals(resp.status_code, 200)

        # Test is the return data correct 
        data = json.loads(resp.data)
        
        #Check controls
        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)

        #Check that items are correct.
        items = data["items"]
        self.assertEquals(len(items), initial_rooms)
        for item in items:
            self.assertIn("name", item)
            self.assertIn("photo", item)
            self.assertIn("resources", item)
            ## Check @control
            self.assertIn("@controls", item)
            ## Check @control self
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertEquals("http://" + local_host + item["@controls"]["self"]["href"], resources.api.url_for(resources.Room, name=item["name"]))
            ## Check @control profile
            self.assertIn("profile", item["@controls"])
            self.assertEquals(item["@controls"]["profile"]["href"], TELLUS_ROOM_PROFILE)
            ## Check @control collection
            self.assertIn("collection", item["@controls"])
            self.assertEquals("http://" + local_host + item["@controls"]["collection"]["href"], flask.url_for("rooms_list"))
            
            ## Check that add_control_edit_room is correct
            self.assertIn("edit", item["@controls"])
            edit_room_control = item["@controls"]["edit"]
            self.assertIn("title", edit_room_control)
            self.assertIn("href", edit_room_control)
            self.assertEquals("http://" + local_host + edit_room_control["href"], resources.api.url_for(resources.Room, name=item["name"]))
            self.assertIn("encoding", edit_room_control)
            self.assertEquals(edit_room_control["encoding"], "json")        
            self.assertIn("method", edit_room_control)
            self.assertEquals(edit_room_control["method"], "PUT")
            self.assertIn("schema", edit_room_control)
            #Check schema
            schema_data = edit_room_control["schema"]
            self.assertIn("type", schema_data)
            self.assertIn("properties", schema_data)
            #Check properties
            props = schema_data["properties"]
            self.assertIn("resources", props)
            self.assertIn("photo", props)
            for key, value in props.items():
                self.assertIn("description", value)
                self.assertIn("title", value)
                self.assertIn("type", value)
                self.assertEquals("string", value["type"])

            ## Check that add_control_books_room is correct
            self.assertIn("tellus:books-room", item["@controls"])
            self.assertIn("href", item["@controls"]["tellus:books-room"])
            self.assertEquals("http://" + local_host + item["@controls"]["tellus:books-room"]["href"], resources.api.url_for(resources.BookingsOfRoom, name=item["name"]))

    def test_get_rooms_mimetype(self):
        """
        Checks that GET Rooms return correct status code and data format
        """
        print "("+self.test_get_rooms_mimetype.__name__+")", self.test_get_rooms_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(flask.url_for("rooms_list"))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, TELLUS_ROOM_PROFILE))

if __name__ == "__main__":
    print "Start running tests"
    unittest.main()
