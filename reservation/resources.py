import json
from time import strftime, gmtime

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask_restful import Resource, Api

import database

# Constants for hypermedia formats and profiles
MASON = "application/vnd.mason+json"
JSON = "application/json"

TELLUS_USER_PROFILE = "/profiles/user_profile/"
TELLUS_ROOM_PROFILE = "/profiles/room_profile/"
TELLUS_BOOKING_PROFILE = "/profiles/booking_profile/"
ERROR_PROFILE = "/profiles/error_profile/"

# Fill these in
APIARY_PROFILES_URL = "http://docs.tellusreservationapi.apiary.io/#reference/profiles"
APIARY_RELS_URL = "http://docs.tellusreservationapi.apiary.io/#reference/link-relations"

LINK_RELATIONS_URL = "/tellus/link-relations/"

# Define the application and the api
# Set the debug is True as default but it must be set as False after testing.
app = Flask(__name__, static_folder="static", static_url_path="/.")
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
# database to be used (for instance for testing)
app.config.update({"Engine": database.Engine()})
# Start the RESTful API.
api = Api(app)


##### This class "MasonObject" is borrowed from course exercises. #####
# Orginally it is developed by Ivan Sanchez and Mika Oja.
#######################################################################
class MasonObject(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs


class ReservationObject(MasonObject):
    """
    A convenience subclass of MasonObject that defines a bunch of shorthand
    methods for inserting application specific objects into the document. This
    class is particularly useful for adding control objects that are largely
    context independent, and defining them in the resource methods would add a
    lot of noise to our code - not to mention making inconsistencies much more
    likely!

    In the forum code this object should always be used for root document as
    well as any items in a collection type resource.
    """

    def __init__(self, **kwargs):
        """
        Calls dictionary init method with any received keyword arguments. Adds
        the controls key afterwards because hypermedia without controls is not
        hypermedia.
        """

        super(ReservationObject, self).__init__(**kwargs)
        self["@controls"] = {}

    def add_control_add_user(self):
        """
        This adds the add-user link to an object. Intended for the document object.
        """

        self["@controls"]["tellus:add-user"] = {
            "title": "Add User",
            "href": "/tellus/api/users/",
            "encoding": "json",
            "method": "POST",
            "schema": {
                "type": "object",
                "properties": {
                    "username": {
                        "title": "Username",
                        "description": "Username of user",
                        "type": "string"
                    },
                    "isAdmin": {
                        "title": "Admin",
                        "description": "Account type to identify User or Admin",
                        "type": "boolean"
                    },
                    "email": {
                        "title": "E-mail",
                        "description": "E-mail of user",
                        "type": "string"
                    },
                    "familyName": {
                        "title": "Family Name",
                        "description": "Family name of the user",
                        "type": "string"
                    },
                    "givenName": {
                        "title": "Given Name",
                        "description": "Given name of the user",
                        "type": "string"
                    },
                    "telephone": {
                        "title": "Phone Number",
                        "description": "Phone Number of the user",
                        "type": "string"
                    }
                },
                "required": ["username"]
            }
        }

    def add_control_delete_user(self, username):
        """
        This adds the delete link for user to an object. Intended for the document object.
        """

        self["@controls"]["tellus:delete"] = {
            "title": "Delete this user",
            "href": api.url_for(User, username=username),
            "method": "DELETE"
        }

    def add_control_delete_booking_of_room(self, name, booking_id):
        """
        This adds the delete link for booking to an object. Intended for the document object.
        """

        self["@controls"]["tellus:delete"] = {
            "title": "Delete booking",
            "href": api.url_for(BookingOfRoom, name=name, booking_id=booking_id),
            "method": "DELETE"
        }

    def add_control_delete_booking_of_user(self, username, booking_id):
        """
        This adds the delete link for booking to an object. Intended for the document object.
        """

        self["@controls"]["tellus:delete"] = {
            "title": "Delete booking",
            "href": api.url_for(BookingOfUser, username=username, booking_id=booking_id),
            "method": "DELETE"
        }

    def add_control_edit_room(self, name):
        """
        Adds the edit control to a room object. For the schema we need
        the name of the room that we want to change.

        : param str roomName: name of the room.
        """
        self["@controls"]["edit"] = {
                    "title": "Modify Room",
                    "href": api.url_for(Room, name=name),
                    "encoding": "json",
                    "method": "PUT",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resources": {
                                "title": "Resources",
                                "description": "Resources avaible in room",
                                "type": "string"
                            },
                            "photo": {
                                "title": "Photo",
                                "description": "Photo of the room",
                                "type": "string"
                            }
                        },
                        "required": ["roomname"]
                    }
        }

    def add_control_bookings_all(self):
        """
        This adds the bookings-all link to an object. Intended for the document object.
        """

        self["@controls"]["tellus:bookings-all"] = {
            "href": api.url_for(Bookings),
            "title": "List all bookings"
        }

    def add_control_bookings_room(self, name):
        """
        This adds the bookings-room link to an object. Intended for the document object.
        """

        self["@controls"]["tellus:bookings-room"] = {
            "href": api.url_for(Bookings, name=name),
            "title": "List all bookings of Room"
        }

    def add_control_books_room(self, name):
        """
        This adds the books-room link to an object. Intended for the document object.
        """

        self["@controls"]["tellus:books-room"] = {
            "href": api.url_for(BookingsOfRoom, name=name),
        }

    def add_control_bookings_user(self, username):
        """
        This adds the bookings-user link to an object. Intended for the document object.
        """

        self["@controls"]["tellus:bookings-user"] = {
            "href": api.url_for(BookingsOfUser, username=username),
            "title": "List all bookings of User"
        }

    def add_control_edit_booking(self):
        self["@controls"]["edit"] = {
                    "title": "Modify Booking",
                    "href": "/tellus/api/bookings/",
                    "encoding": "json",
                    "method": "PUT",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {
                                "title": "User Name",
                                "description": "Username of the booking's owner",
                                "type": "string"
                            },
                            "bookingTime": {
                                "title": "Booking Time",
                                "description": "Date and time of the booking",
                                "type": "string"
                            },
                            "email": {
                                "title": "Email",
                                "description": "Email of the booking's owner",
                                "type": "string"
                            },
                            "familyName": {
                                "title": "Family Name",
                                "description": "Family Name of the booking's owner",
                                "type": "string"
                            },
                            "givenName": {
                                "title": "Given Name",
                                "description": "Given Name of the booking's owner",
                                "type": "string"
                            },
                            "telephone": {
                                "title": "Telephone",
                                "description": "Telephone number of the booking's owner",
                                "type": "string"
                            },
                            "name": {
                                "title": "Room name",
                                "description": "Room name which the booking take place",
                                "type": "string"
                            },
                        },
                        "required": ["username", "bookingTime", "name"]
                    }
        }

    def add_control_add_booking(self, name):
        """
        This adds the add-booking link to an object. Intended for the document object.
        """

        self["@controls"]["tellus:add-booking"] = {
            "title": "Create booking",
            "href": api.url_for(BookingsOfRoom, name=name),
            "encoding": "json",
            "method": "POST",
            "schema": {
                "type": "object",
                "properties": {
                    "username": {
                        "title": "User Name",
                        "description": "Username of the booking's owner",
                        "type": "string"
                    },
                    "bookingTime": {
                        "title": "Booking Time",
                        "description": "Date and time of the booking",
                        "type": "string"
                    },
                    "email": {
                        "title": "Email",
                        "description": "Email of the booking's owner",
                        "type": "string"
                    },
                    "familyName": {
                        "title": "Family Name",
                        "description": "Family Name of the booking's owner",
                        "type": "string"
                    },
                    "givenName": {
                        "title": "Given Name",
                        "description": "Given Name of the booking's owner",
                        "type": "string"
                    },
                    "telephone": {
                        "title": "Telephone",
                        "description": "Telephone number of the booking's owner",
                        "type": "string"
                    },
                    "name": {
                        "title": "Room name",
                        "description": "Room name which the booking take place",
                        "type": "string"
                    },
                },
                "required": ["username", "bookingTime", "name"]
            }
        }

    def add_control_history_bookings(self):
        """
        This adds the history-bookings link to an object. Intended for the document object.
        """

        self["@controls"]["tellus:history-bookings"] = {
            "href": api.url_for(HistoryBookings),
            "title": "History Bookings"
        }


##### This ERROR HANDLERS functions are borrowed from course exercises. #####
# Orginally it is developed by Ivan Sanchez and Mika Oja.
#############################################################################
# ERROR HANDLERS
def create_error_response(status_code, title, message=None):
    """
    Creates a: py: class:`flask.Response` instance when sending back an
    HTTP error response

    : param integer status_code: The HTTP status code of the response
    : param str title: A short description of the problem
    : param message: A long description of the problem
    : rtype:: py: class:`flask.Response`
    """

    resource_url = None
    # We need to access the context in order to access the request.path
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
    envelope = MasonObject(resource_url=resource_url)
    envelope.add_error(title, message)

    return Response(json.dumps(envelope), status_code, mimetype=MASON + ";" + ERROR_PROFILE)


@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
                                 "This resource url does not exit")


@app.errorhandler(400)
def resource_not_found(error):
    return create_error_response(400, "Malformed input format",
                                 "The format of the input is incorrect")


@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
                                 "The system has failed. Please, contact the administrator")


#### End of ERROR HANDLERS

@app.before_request
def connect_db():
    """
    Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.
    """

    g.con = app.config["Engine"].connect()


# HOOKS
@app.teardown_request
def close_connection(exc):
    """
    Closes the database connection
    Check if the connection is created. It migth be exception appear before
    the connection is created.
    """

    if hasattr(g, "con"):
        g.con.close()


# Define the resources
class User(Resource):
    """
    Resource User implementation
    """

    def post(self, username):
        """
        Adds a new User.

        REQUEST ENTITY BODY:
        * Media type: JSON
        * Profile: booking-profile
          http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/booking-profile

        RESPONSE STATUS CODE:
        * Returns 201 if User was successfully created.
        * Returns 400 if the input format for create new User is wrong or empty.
        * Return 409 Conflict if there is another User with the same username
        * Returns 415 if the input format is not JSON (unsupport media type)
        * Returns 500 if failed to create new User in database
        
        NOTE:
        * The attribute isAdmin is obtained from the column User.isAdmin
        * The attribute username is obtained from the column User.username
        * The attribute password is obtained from the column User.password
        * The attribute firstname is obtained from the column User.firstname
        * The attribute lastname is obtained from the column User.lastname
        * The attribute email is obtained from the column User.email
        * The attribute contactNumber is obtained from the column User.contactNumber
        """

        if JSON != request.headers['Content-Type']:
            return create_error_response(415, "Unsupported Media Type",
                                        "Use a JSON compatible format %s" % request.headers['Content-Type'],
                                         )
        #PARSE THE REQUEST:
        request_body = request.get_json()
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON format",
                                         )

        #It throws a BadRequest exception, and hence a 400 code if the JSON is
        #not wellformed
        try:
            isadmin = request_body["isAdmin"]
            _username = request_body["username"]
            password = request_body["password"]
            email = request_body["email"]
            firstname = request_body["firstname"]
            lastname = request_body["lastname"]
            contactnumber = request_body["contactNumber"]

        except KeyError:
            #This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Must have isAdmin, username, password, email, firstname, lastname and contactNumber in response body.")

        # Conflict if user already exist, return 409
        # filter in the list of Users.
        find_username = filter(lambda x: "username" in x and x["username"] == username, g.con.get_users())
        if find_username:
            return create_error_response(409, "Existing username",
                                            "User name: %s has been used." % username)

        #Create new user
        new_user = g.con.add_user(username, request_body)
        if not new_user:
            return create_error_response(500, "Problem with the database",
                                         "Cannot access the database")

        #Return the response
        return Response(status = 201,
            headers={"Location": api.url_for(User, username=username)})

    def delete(self, username):
        """
        Deletes 1 User from the Tellus API.

        INPUT PARAMETERS:
        :param str username: username of the User that we want to delete

        RESPONSE STATUS CODE
        * Returns 204 if the User was successfully deleted
        * Returns 404 if the username did not exist.
        """
        #PERFORM DELETE OPERATIONS
        if g.con.delete_user(username):
            return "", 204
        else:
            #Send 404 error message
            return create_error_response(404, "Unknown User",
                                     "There is no User with username %s" % username)


class RoomsList(Resource):
    """
    Resource Rooms List implementation
    """

    def get(self):
        """
        Get list of all Rooms in Tellus API.
        
        It returns always status code 200.

        RESPONSE ENTITY BODY:
        * Media type: Mason
            https://github.com/JornWildt/Mason
        * Profile: room-profile
            http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/room-profile

        Semantic descriptions used in items: roomname
        
        NOTE:
         * The attribute picture is obtained from the column rooms.picture
         * The attribute resources is obtained from the column rooms.resources
        """

        # Extract rooms from database
        rooms_db = g.con.get_rooms()

        # Create envelope for response
        envelope = ReservationObject()
        envelope.add_namespace("tellus", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(RoomsList))

        # Add room items
        items = envelope["items"] = []

        for room in rooms_db:
            item = ReservationObject(name=room["roomname"], photo=room["picture"], resources=room["resources"])

            item.add_control("self", href=api.url_for(Room, name=room["roomname"]))
            item.add_control("profile", href=TELLUS_ROOM_PROFILE)
            item.add_control("collection", href=api.url_for(RoomsList))
            item.add_control_edit_room(room["roomname"])
            item.add_control_books_room(name=room["roomname"])
            
            items.append(item)

            # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + TELLUS_ROOM_PROFILE)


class Room(Resource):
    """
    Resource Room implementation
    """

    def put(self, name):
        """
        Modifies specified Room.

        INPUT PARAMETERS:
        :param str name: The name of the room that will be modified.

        REQUEST ENTITY BODY:
        * Media type: JSON
        * Profile: room-profile
          http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/room-profile

        OUTPUT:
         * Returns 204 if the room was successfully modified
         * Returns 400 if the input format for modify is wrong or empty.
         * Returns 404 if there is no room with this name
         * Returns 415 if the input format is not JSON
         * Returns 500 if failed to modify the room in database
        """

        # Check the room exists
        room = filter(lambda x: "roomname" in x and x["roomname"] == name, g.con.get_rooms())
        if not room:
            return create_error_response(404, "Room does not exist",
                                         "There is no a room with name %s" % name)

        # Check content-type
        if JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")

        # Parse JSON request data
        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format")

        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not wellformed
        try:
            roomName = request_body["name"]
            resources = request_body["resources"]
            picture = request_body["photo"]

        except KeyError:
            return create_error_response(400, "Wrong request format",
                                         "Must have name, resources and photo in response body.")
        else:
            # Modify the booking in the database
            if not g.con.modify_room(roomName=name, room_dict={'picture': picture, 'resources':resources}):
                return create_error_response(500, "Internal error",
                                             "Room information for %s cannot be updated" % name)
            return "", 204


class Bookings(Resource):
    """
    Resource Bookings implementation
    """

    def get(self):
        """
        Get list of all Bookings in Tellus API.
        
        It returns always status code 200.

        RESPONSE ENTITY BODY:
        * Media type: Mason
            https://github.com/JornWildt/Mason
        * Profile: booking-profile
            http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/booking-profile

        Semantic descriptions used in items: roomname, username, bookingTime
        
        NOTE:
         * The attribute contactnumber is obtained from the column bookings.contactnumber
         * The attribute email is obtained from the column bookings.email
         * The attribute firstname is obtained from the column bookings.firstname
         * The attribute lastname is obtained from the column bookings.lastname
        """

        # Extract bookings from database
        bookings_db = g.con.get_bookings()

        # Create envelope for response
        envelope = ReservationObject()
        
        envelope.add_namespace("tellus", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Bookings))
        envelope.add_control_history_bookings()

        # Add booking items
        items = envelope["items"] = []

        for booking in bookings_db:
            item = ReservationObject(   bookingID=booking["bookingID"],
                                        name=booking["roomname"],
                                        username=booking["username"],
                                        bookingTime=booking["bookingTime"])

            item.add_control("profile", href=TELLUS_BOOKING_PROFILE)
            item.add_control_delete_booking_of_room(booking["roomname"], booking["bookingID"])
            
            items.append(item)

            # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + TELLUS_BOOKING_PROFILE)


class BookingsOfRoom(Resource):
    """
    Resource Bookings of Room implementation
    """

    def get(self, name):
        """
        Get all list of bookings for specified room.

        INPUT parameters:
          :param str name: the name of the room.

        RESPONSE ENTITY BODY:
        * Media type: Mason
            https://github.com/JornWildt/Mason
        * Profile: booking-profile
            http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/booking-profile

        NOTE:
         * The attribute contactnumber is obtained from the column bookings.contactnumber
         * The attribute email is obtained from the column bookings.email
         * The attribute firstname is obtained from the column bookings.firstname
         * The attribute lastname is obtained from the column bookings.lastname
        """

        # Check the room exists
        room = filter(lambda x: "roomname" in x and x["roomname"] == name, g.con.get_rooms())
        if not room:
            return create_error_response(404, "Room does not exist",
                                  "There is no a room with name %s" % name)
        # Extract bookings from database
        bookings_db = g.con.get_bookings(name)

        # Create envelope for response
        envelope = ReservationObject()
        envelope.add_namespace("tellus", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(BookingsOfRoom, name=name))
        envelope.add_control_bookings_all()
        envelope.add_control_add_booking(name=name)

        # Add booking items
        items = envelope["items"] = []

        for booking in bookings_db:
            item = ReservationObject(name=booking["roomname"],
                                     username=booking["username"],
                                     bookingTime=booking["bookingTime"])
            item.add_control("profile", href=TELLUS_BOOKING_PROFILE)
            item.add_control("collection",
                             href=api.url_for(BookingsOfRoom, name=name))
            item.add_control_delete_booking_of_room(name=booking["roomname"],
                                                    booking_id=booking["bookingID"])
            item.add_control_edit_booking()
            items.append(item)

            # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + TELLUS_BOOKING_PROFILE)

    def post(self, name):
        """
        Adds a new booking to room.

        INPUT PARAMETERS:
          :param str name: the name of the room.

        REQUEST ENTITY BODY:
        * Media type: JSON:
        * Profile: booking-profile
            http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/booking-profile

        The body should be a JSON document that matches the schema for booking.

        RESPONSE HEADERS:
         * Location: Contains the URL of the booking

        RESPONSE STATUS CODE:
         * Returns 201 if the booking has been added correctly.
           The Location header contains the path of the booking
         * Returns 400 if the booking is not well formed or the entity body is
           empty.
         * Returns 409 if the booking conflicts with another booking.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the booking could not be added to database.
        """

        if JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)
        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not wellformed
        booking_dict = {}
        try:
            booking_dict['roomName'] = name
            booking_dict['username'] = request_body['username']
            booking_dict['bookingTime'] = request_body['bookingTime']
            booking_dict['firstname'] = request_body['givenName']
            booking_dict['lastname'] = request_body['familyName']
            booking_dict['email'] = request_body['email']
            booking_dict['contactnumber'] = request_body['telephone']
        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "There is something wrong with the booking format.")

        # Check if there is conflict
        bookings_db = g.con.get_bookings(name)
        for booking in bookings_db:
            if booking['bookingTime'] == booking_dict['bookingTime']:
                return create_error_response(409, "Conflict booking",
                                             "The new booking was conflicted with an existence booking")

        # Add booking
        new_booking = g.con.add_booking(name, booking_dict['username'], booking_dict['bookingTime'], booking_dict)
        if not new_booking:
            return create_error_response(500, "Internal error",
                                         "Booking cannot be added.")
        # Create the Location header.
        url = api.url_for(BookingOfRoom, name=name, booking_id=new_booking[0])

        # RENDER
        # Return the response
        return Response(status=201, headers={"Location": url})


class BookingsOfUser(Resource):
    """
    Resource Bookings of User implementation
    """

    def get(self, username):
        """
        Get all list of bookings for specified user.

        INPUT parameters:
          :param str username: the username of the user.

        RESPONSE ENTITY BODY:
        * Media type: Mason
            https://github.com/JornWildt/Mason
        * Profile: booking-profile
            http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/booking-profile

        NOTE:
         * The attribute contactnumber is obtained from the column bookings.contactnumber
         * The attribute email is obtained from the column bookings.email
         * The attribute firstname is obtained from the column bookings.firstname
         * The attribute lastname is obtained from the column bookings.lastname
        """

        # Check the user exists
        find_username = filter(lambda x: "username" in x and x["username"] == username, g.con.get_users())
        if not find_username:
            return create_error_response(404, "User does not exist",
                                          "There is no a user with username %s" % username)

        # Extract bookings from database
        bookings_db = filter(lambda x: "username" in x and x["username"] == username, g.con.get_bookings())

        # Create envelope for response
        envelope = ReservationObject()
        envelope.add_namespace("tellus", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(BookingsOfUser, username=username))
        envelope.add_control_bookings_all()

        # Add booking items
        items = envelope["items"] = []

        for booking in bookings_db:
            item = ReservationObject(name=booking["roomname"],
                                     username=booking["username"],
                                     bookingTime=booking["bookingTime"])
            item.add_control("profile", href=TELLUS_BOOKING_PROFILE)
            item.add_control("collection",
                             href=api.url_for(BookingsOfUser, username=username))
            item.add_control_delete_booking_of_user(username=booking["username"],
                                                    booking_id=booking["bookingID"])
            items.append(item)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + TELLUS_BOOKING_PROFILE)


class BookingOfRoom(Resource):
    """
    Resource Booking of Room implementation
    """

    def put(self, booking_id, name):
        """
        Modifies bookingTime of one booking by a specific User of a specific Room.

        INPUT PARAMETERS:
        :param str booking_id: The booking ID of the booking we want to modify
        :param str name: The name of the room contant the booking we want to modify

        REQUEST ENTITY BODY:
        * Media type: JSON
        * Profile: booking-profile
          http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/booking-profile

        OUTPUT:
         * Returns 204 if the booking was successfully modified
         * Returns 400 if the input format for modify is wrong or empty.
         * Returns 404 if there is no booking with booking_id in that room name
         * Returns 415 if the input format is not JSON (unsupport media type)
         * Returns 500 if failed to modify the booking in database

        NOTE:
         * The attribute contactnumber is obtained from the column bookings.contactnumber
         * The attribute email is obtained from the column bookings.email
         * The attribute firstname is obtained from the column bookings.firstname
         * The attribute lastname is obtained from the column bookings.lastname

        """

        #CHECK THAT BOOKING EXISTS
        # filter in the list of booking by room name.
        find_booking_id = filter(lambda x: "bookingID" in x and x["bookingID"] == int(booking_id), g.con.get_bookings(name))
        # if the booking ID not found, return 404, no existence booking
        if not find_booking_id:
            return create_error_response(404, "Booking not found",
                                         "There is no Booking with Booking ID: %(bookingID)s in Room: %(roomName)s | find_booking_id = %(v3)s" % {"bookingID":booking_id, "roomName":name, "v3":find_booking_id})
        
        # Access the headers content-type
        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")

        # Parsing JSON request data, ignored mimetype
        request_body = request.get_json()
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         )
        #It throws a BadRequest exception, and hence a 400 code if the JSON is
        #not wellformed
        try:
            _username       = request_body['username']
            _bookingtime    = request_body['bookingTime']
            _firstname      = request_body['firstname']
            _lastname       = request_body['lastname']
            _email          = request_body['email']
            _contactnumber  = request_body['contactnumber']

        except KeyError:
            return create_error_response(400, "Wrong request format",
                                         "Must have username, bookingTime, firstname, lastname, email, contactNumber in response body.")
        else:
            # Modify the booking in the database
            mod = g.con.modify_booking(int(booking_id), name, _username, _bookingtime, request_body)
            if not mod:
                return create_error_response(500, "Internal error",
                                         "Booking information for %(v1)s cannot be updated in database |mod = %(v2)s" % {"v1":booking_id, "v2":mod}
                                        )
            return "", 204

    def delete(self, name, booking_id):
        """
        Deletes 1 Booking of a specific Room from the Tellus API.

        INPUT PARAMETERS:
        :param str name: name of the Room, which contain the Booking we want to remove.
        :param str booking_id: Booking ID of the Booking we want to remove.

        RESPONSE STATUS CODE
         * Returns 204 if the Booking was successfully deleted
         * Returns 404 if the Booking did not exist.
        """

        #PERFORM DELETE OPERATIONS
        if g.con.delete_booking(int(booking_id), name):
            return "", 204
        else:
            #Send 404 error message
            return create_error_response(404, "Unknown Booking", 
                                         "There is no booking with bookingID: %(bookingID)s, in room: %(roomName)s" % {"bookingID":booking_id, "roomName":name})


class BookingOfUser(Resource):
    """
    Resource Booking of User implementation
    """

    def delete(self, username, booking_id):
        """
        Deletes a booking of a specific user from the Tellus API.

        INPUT PARAMETERS:
        :param str username: username of the user.
        :param str booking_id: Booking ID of the Booking we want to remove.

        RESPONSE STATUS CODE
         * Returns 204 if the Booking was successfully deleted
         * Returns 404 if the Booking did not exist.
        """
        bookings_db = filter(lambda x: "bookingID" in x and x["bookingID"] == int(booking_id), g.con.get_bookings())
        if not bookings_db:
            # Send 404 error message
            return create_error_response(404, "Unknown Booking",
                                         "There is no Booking with Booking ID: %s" % booking_id)
        booking = bookings_db[0]
        # PERFORM DELETE OPERATIONS
        if g.con.delete_booking(int(booking_id), booking["roomname"], booking["username"], booking["bookingTime"]):
            return "", 204
        else:
            # Send 404 error message
            return create_error_response(404, "Unknown Booking",
                                         "There is no Booking with Booking ID: %s" % booking_id)


class HistoryBookings(Resource):
    """
    Resource History Bookings implementation
    """

    def get(self):
        """
        Get all list of past bookings.

        INPUT parameters:
          The query parameters are:
          * limit: The maximum number of bookings to return.

        RESPONSE ENTITY BODY:
        * Media type: Mason
            https://github.com/JornWildt/Mason
        * Profile: booking-profile
            http://docs.tellusreservationapi.apiary.io/#reference
            /profiles/booking-profile
        """
        # Extract query parameters
        parameters = request.args
        limit = int(parameters.get('limit', 30))

        # Extract bookings from database
        bookings_db = filter(
            lambda x: "bookingTime" in x
                      and x["bookingTime"] < strftime("%Y-%m-%d %H:%M", gmtime()),
            g.con.get_bookings())
        bookings_db = bookings_db[:limit]

        # Create envelope for response
        envelope = ReservationObject()
        envelope.add_namespace("tellus", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(HistoryBookings))

        # Add booking items
        items = envelope["items"] = []

        for booking in bookings_db:
            item = ReservationObject(name=booking["roomname"],
                                     username=booking["username"],
                                     bookingTime=booking["bookingTime"])
            item.add_control("profile", href=TELLUS_BOOKING_PROFILE)
            item.add_control_delete_booking_of_room(name=booking["roomname"],
                                                    booking_id=booking["bookingID"])
            items.append(item)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + TELLUS_BOOKING_PROFILE)

# Define the routes
api.add_resource(User, "/tellus/api/users/<username>/",
                 endpoint="user")
api.add_resource(RoomsList, "/tellus/api/rooms/",
                 endpoint="rooms_list")
api.add_resource(Room, "/tellus/api/rooms/<name>/",
                 endpoint="room")
api.add_resource(Bookings, "/tellus/api/bookings/",
                 endpoint="bookings")
api.add_resource(BookingsOfRoom, "/tellus/api/rooms/<name>/bookings/",
                 endpoint="bookings_of_room")
api.add_resource(BookingsOfUser, "/tellus/api/users/<username>/bookings/",
                 endpoint="bookings_of_user")
api.add_resource(BookingOfRoom, "/tellus/api/rooms/<name>/bookings/<booking_id>/",
                 endpoint="booking_of_room")
api.add_resource(BookingOfUser, "/tellus/api/users/<username>/bookings/<booking_id>/",
                 endpoint="booking_of_user")
api.add_resource(HistoryBookings, "/tellus/api/bookings/history/",
                 endpoint="history_bookings")


# Redirect profile
@app.route("/profiles/<profile_name>")
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)


@app.route("/tellus/link-relations/<rel_name>/")
def redirect_to_rels(rel_name):
    return redirect(APIARY_RELS_URL + rel_name)


# Start the application
# DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == "__main__":
    # Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
