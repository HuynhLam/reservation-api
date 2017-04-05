import json

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask.ext.restful import Resource, Api, abort
from werkzeug.exceptions import HTTPException, NotFound

import database

# Constants for hypermedia formats and profiles
MASON = "application/vnd.mason+json"
JSON = "application/json"

# TODO 1 put profile links here, change the variable names
FORUM_USER_PROFILE = "/profiles/user-profile/"
FORUM_MESSAGE_PROFILE = "/profiles/message-profile/"
ERROR_PROFILE = "/profiles/error-profile"

# Fill these in
APIARY_PROFILES_URL = "STUDENT_APIARY_PROJECT/reference/profiles/"
APIARY_RELS_URL = "STUDENT_APIARY_PROJECT/reference/link-relations/"
## end of todo1

# TODO 2 create schemas like in the exercises in json format
USER_SCHEMA_URL = "/forum/schema/user/"
PRIVATE_PROFILE_SCHEMA_URL = "/forum/schema/private-profile/"
LINK_RELATIONS_URL = "/forum/link-relations/"
## end of todo2

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

    # TODO 3 implement mason response functions
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
            "href": api.url_for(User, username=username),
            "title": "Delete this user",
            "method": "DELETE"
        }

    def add_control_delete_booking_of_room(self, name, booking_id):
        """
        This adds the delete link for booking to an object. Intended for the document object.
        """

        self["@controls"]["tellus:delete"] = {
            "href": api.url_for(BookingOfRoom, name=name, booking_id=booking_id),
            "title": "Delete booking"
        }

    def add_control_delete_booking_of_user(self, username, booking_id):
        """
        This adds the delete link for booking to an object. Intended for the document object.
        """

        self["@controls"]["tellus:delete"] = {
            "href": api.url_for(BookingOfUser, username=username, booking_id=booking_id),
            "title": "Delete booking"
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

    def add_control_bookings_user(self, username):
        """
        This adds the bookings-user link to an object. Intended for the document object.
        """

        self["@controls"]["tellus:bookings-user"] = {
            "href": api.url_for(BookingsOfUser, username=username),
            "title": "List all bookings of User"
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

    ## end of todo3


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

    def post(self):
        pass

    def delete(self, username):
        pass


class RoomsList(Resource):
    """
    Resource Rooms List implementation
    """

    def get(self):
        pass


class Room(Resource):
    """
    Resource Room implementation
    """

    def put(self, name):
        pass


class Bookings(Resource):
    """
    Resource Bookings implementation
    """

    def get(self):
        pass


class BookingsOfRoom(Resource):
    """
    Resource Bookings of Room implementation
    """

    def get(self, name):
        pass

    def post(self, name):
        pass


class BookingsOfUser(Resource):
    """
    Resource Bookings of User implementation
    """

    def get(self, username):
        pass


class BookingOfRoom(Resource):
    """
    Resource Booking of Room implementation
    """

    def put(self, name, booking_id):
        pass

    def delete(self, name, booking_id):
        pass


class BookingOfUser(Resource):
    """
    Resource Booking of User implementation
    """

    def delete(self, username, booking_id):
        pass


class HistoryBookings(Resource):
    """
    Resource History Bookings implementation
    """

    def get(self):
        pass

#TODO 4 change them base on our thing
# Define the routes
api.add_resource(User, "/users/<username>",
                 endpoint="user")
## end of todo4


# Redirect profile
@app.route("/profiles/<profile_name>")
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)


@app.route("/forum/link-relations/<rel_name>/")
def redirect_to_rels(rel_name):
    return redirect(APIARY_RELS_URL + rel_name)


# Send our schema file(s)
@app.route("/forum/schema/<schema_name>/")
def send_json_schema(schema_name):
    return send_from_directory(app.static_folder, "schema/{}.json".format(schema_name))


# Start the application
# DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == "__main__":
    # Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
