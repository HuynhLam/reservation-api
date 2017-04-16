'''
Tellus API function tests for all User related methods.

User resource contain:
GET /users/{username} (will be implement in future)
    return code 200 + list of Users in database or None if there is no User

POST /users/{username} 
    return code 201 successfully created new User
                400 wrong request format
                409 existing username
                415 unsupported Media Type
                500 Database error

DELETE /users/{username}
    return code 204 successfully delete User
                404 user non-exist

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

TELLUS_USER_PROFILE = "/profiles/user-profile/"
TELLUS_ROOM_PROFILE = "/profiles/room-profile/"
TELLUS_BOOKING_PROFILE = "/profiles/booking_profile/"
ERROR_PROFILE = "/profiles/error-profile/"

#Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True
#Necessary for correct translation in url_for
resources.app.config["SERVER_NAME"] = "localhost:5000"

#Database Engine utilized in our testing
resources.app.config.update({"Engine": ENGINE})

class UserTestCase(unittest.TestCase):
    # Full format new User.
    new_user_1 = {
        "isAdmin":"1",
        "username":"masterdick",
        "password":"maidichomuado",
        "email":"lam.huynh@ee.oulu.fi",
        "firstname":"Lam",
        "lastname":"Huynh",
        "contactNumber":"0418888888"
    }
    # Full format new User.
    new_user_2 = {
        "isAdmin":"1",
        "username":"masterdick2",
        "password":"maidichomuado",
        "email":"lam.huynh@ee.oulu.fi",
        "firstname":"Lam",
        "lastname":"Huynh",
        "contactNumber":"0418888888"
    }
    # Wrong format new User with no user's password
    wrong_format_user_1 = {
        "isAdmin":"1",
        "username":"masterdick",
        "email":"lam.huynh@ee.oulu.fi",
        "firstname":"Lam",
        "lastname":"Huynh",
        "contactNumber":"0418888888"
    }
    # Wrong format new User with no user's email
    wrong_format_user_2 = {
        "isAdmin":"1",
        "username":"masterdick",
        "password":"maidichomuado",
        "firstname":"Lam",
        "lastname":"Huynh",
        "contactNumber":"0418888888"
    }
    # Wrong format new User with no user's contactNumber
    wrong_format_user_3 = {
        "isAdmin":"1",
        "username":"masterdick",
        "password":"maidichomuado",
        "email":"lam.huynh@ee.oulu.fi",
        "firstname":"Lam",
        "lastname":"Huynh"
    }
    # New user with existing username
    existing_user = {
        "isAdmin":"0",
        "username":"lam",
        "password":"passwordmoinhe",
        "email":"emailmoi@ee.oulu.fi",
        "firstname":"Young",
        "lastname":"Uno",
        "contactNumber":"0417777777"
    }

    def setUp(self):
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()
        
        user1_username = "para"
        user2_username = "vodka"
        self.url1 = resources.api.url_for(resources.User, username=user1_username)
        self.url_wrong = resources.api.url_for(resources.User, username=user2_username)
        #print "***print url1 [%s]" % self.url1
        #print "***print url_wrong [%s]" % self.url_wrong

    def test_add_user(self):
        """
        Test that we can successfully added new User
        """
        print "("+self.test_add_user.__name__+")", self.test_add_user.__doc__

        # With a complete request
        resp = self.client.post(resources.api.url_for(resources.User, username=self.new_user_1["username"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.new_user_1)
                               )

        self.assertEquals(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        
        con = resources.app.config["Engine"].connect()
        find_username = filter(lambda x: "username" in x and x["username"] == self.new_user_1["username"], con.get_users())
        if find_username:
            print "***Successfully added user %s" % self.new_user_1["username"]

    def test_add_user_wrong_format(self):
        """
        Test that it returns error when is missing a mandatory data
        """
        print "("+self.test_add_user_wrong_format.__name__+")", self.test_add_user_wrong_format.__doc__

        # request body without user's "password"
        resp1 = self.client.post(resources.api.url_for(resources.User, username=self.wrong_format_user_1["username"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.wrong_format_user_1)
                               )
        self.assertEquals(resp1.status_code, 400)

        # request body without user's "email"
        resp2 = self.client.post(resources.api.url_for(resources.User, username=self.wrong_format_user_2["username"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.wrong_format_user_2)
                               )
        self.assertEquals(resp2.status_code, 400)
        
        # request body without user's "contactNumber"
        resp3 = self.client.post(resources.api.url_for(resources.User, username=self.wrong_format_user_3["username"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.wrong_format_user_3)
                               )
        self.assertEquals(resp3.status_code, 400)

    def test_add_existing_user(self):
        """
        Test that we can not add an User with existence username
        """
        print "("+self.test_add_existing_user.__name__+")", self.test_add_existing_user.__doc__
        resp = self.client.post(resources.api.url_for(resources.User, username=self.existing_user["username"]),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.existing_user)
                               )
        self.assertEquals(resp.status_code, 409)

    def test_add_user_wrong_media_type(self):
        """
        Test that return adequate error if sent incorrect mime type
        """
        print "("+self.test_add_user_wrong_media_type.__name__+")", self.test_add_user_wrong_media_type.__doc__
        resp = self.client.post(resources.api.url_for(resources.User, username=self.new_user_2["username"]),
                                headers={"Content-Type": "application/xml"},
                                data=json.dumps(self.new_user_2)
                               )
        self.assertEquals(resp.status_code, 415)

    def test_delete_user(self):
        """
        Test that resourses class can delete an existence User
        """
        print "("+self.test_delete_user.__name__+")", self.test_delete_user.__doc__
        # Check that delete an unexisting user, code 404
        resp = self.client.delete(self.url1)
        self.assertEquals(resp.status_code, 204)
        # DELETE is idempotent HTTP methods, so we can check was User 
        # successfully deleted by re-run DELETE with the same URL
        resp = self.client.delete(self.url1)
        self.assertEquals(resp.status_code, 404)

    def test_delete_unexisting_user(self):
        """
        Test that Delete User when given a wrong address
        """
        print "("+self.test_delete_unexisting_user.__name__+")", self.test_delete_unexisting_user.__doc__
        # Check that delete an unexisting user, code 404
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)



if __name__ == "__main__":
    print "Start running tests"
    unittest.main()
