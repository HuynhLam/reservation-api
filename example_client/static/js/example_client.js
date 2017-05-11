/**
 * @fileOverview Example client for Reservation API.
                 It utilizes the Reservation API to handle room and booking information
                 (retrieve rooms list, booking of rooms list,
                 as well as add and remove new bookings form the system).
 * @author <a href="mailto:onur.ozuduru@ee.oulu.fi">Onur Özüduru</a>
 //TODO add email and name
 * @author <a href="mailto:@oulu.fi">Lam</a>
 * @version 1.0
 *
 * NOTE: The documentation utilizes jQuery syntax to refer to classes and ids in
         the HTML code: # is utilized to refer to HTML elements ids while . is
         utilized to refer to HTML elements classes.
**/


/**** START CONSTANTS****/

/**
 * Set this to true to activate the debugging messages.
 * @constant {boolean}
 * @default
 */
var DEBUG = true;

/**
 * Mason+JSON mime-type
 * @constant {string}
 * @default
 */
const MASONJSON = "application/vnd.mason+json";

const PLAINJSON = "application/json";

/**
 * Link to USER_PROFILE
 * @constant {string}
 * @default
 */
const TELLUS_USER_PROFILE = "/profiles/user_profile/";

/**
 * Link to ROOM_PROFILE
 * @constant {string}
 * @default
 */
const TELLUS_ROOM_PROFILE = "/profiles/room_profile/";

/**
 * Link to BOOKING_PROFILE
 * @constant {string}
 * @default
 */
const TELLUS_BOOKING_PROFILE = "/profiles/booking_profile/";

/**
 * Link to ERROR_PROFILE
 * @constant {string}
 * @default
 */
const ERROR_PROFILE = "/profiles/error_profile/";

/**
 * Default datatype to be used when processing data coming from the server.
 * Due to JQuery limitations we should use json in order to process Mason responses
 * @constant {string}
 * @default
 */
const DEFAULT_DATATYPE = "json";

/**
 * Entry point of the application
 * @constant {string}
 * @default
 */
const ENTRYPOINT = "/tellus/api/rooms/"; //Entrypoint: Resource Rooms List

/**** END CONSTANTS****/


/**** START RESTFUL CLIENT****/

/**** Description of the functions that call Forum API by means of jQuery.ajax()
      calls. We have implemented one function per link relation in both profiles.
      Since we are not interesting in the whole API functionality, some of the
      functions does not do anything. Hence, those link relations are ignored
****/


/**
 * This function is the entrypoint to the Tellus Reservation API.
 *
 * Associated rel attribute: Rooms Mason+JSON and bookings-room
 *
 * Sends an AJAX GET request to retrive the list of all the rooms of the application
 *
 * ONSUCCESS=> Show rooms in the #room_list.
 *             After processing the response it utilizes the method {@link #appendRoomToList}
 *             to append the room to the list.
 *             Each room is an anchor pointing to the respective bookings of room url.
 * ONERROR => Show an alert to the user.
 *
 * @param {string} [apiurl = ENTRYPOINT] - The url of the Rooms instance.
**/
function getRooms(apiurl) {
    apiurl = apiurl || ENTRYPOINT;
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){
        //Remove old list of rooms
        //hide bookings
        //hide room modify page
         $("#room_list").empty();
         $("#modifyRoom").hide();
         $("#room").hide();
         $("#mainContent").hide();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        //Extract the rooms
        var rooms = data.items;
        for (var i=0; i < rooms.length; i++){
            var room = rooms[i];
            //Extract the name by getting the data values. Once obtained
            // the name use the method appendRoomToList to show the room
            // information in the UI.
            appendRoomToList(room['@controls']['tellus:bookings-room'].href, room.name);

            //Create modify form from schema
            if("edit" in room['@controls']) {

            }
        }
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Inform user about the error using an alert message.
        alert ("Could not fetch the list of rooms.  Please, try again");
    });
}

/**
 * Sends an AJAX request to retrieve information related to a Bookings list of the room {@link http://docs.tellusreservationapi.apiary.io/#reference/bookings/bookings-of-room/rooms-list}
 *
 * Associated link relation:self (inside the booking profile), delete and add-booking
 *
 *  ONSUCCESS =>
 *              a) Create list of booking with username and bookingtime information.
 *                  Extract the information from the attribute input
 *              b) Extract associated link relations from the response
 *                    b.1) If tellus:delete: Show the #deleteBooking button. Add the href
 *                        to the list element.
 *                    b.2) If tellus:add-booking: Call the function {@link #createFormFromSchema}
 *                        and create new_booking_form.
 *
 * ONERROR =>   a) Alert the user
 *              b) Unselect the room from the list and go back to initial state
 *                (Call {@link deleselectRoom})
 *
 * @param {string} apiurl - The url of the Bookings list of room.
**/
function getRoomBookings(apiurl) {
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        // Extract bookings
        var bookings = data.items;
        for (var i=0; i < bookings.length; i++){
            var booking = bookings[i];
            $li = $('<li class="booking"></li>');
            if("username" in booking) {
                $li.append("Username: "+booking.username+" | ");
            }
            if("bookingTime" in booking) {
                $li.append("Time: "+booking.bookingTime+" | ");
            }
            var controls = booking['@controls'];
            if("tellus:delete" in controls) {
                $button = $("<a href='"+controls["tellus:delete"].href+"' class='deleteBooking'>"+controls["tellus:delete"].title+"</a>");
                $li.append($button);
            }
            $("#bookings_list").append($li);
        }
        //Prepare the new_booking_form to create a new booking
        var create_ctrl = data["@controls"]["tellus:add-booking"];
        if (create_ctrl.schema) {
            createFormFromSchema(create_ctrl.href, create_ctrl.schema, "new_booking_form");
        }
        $("input[type='button']",$("#new_booking_form")).show();

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that it cannot get info from the room.
        alert ("Cannot extract information about this room from the tellus reservation.");
        deselectRoom();
    });
}

/**
 * Sends an AJAX request to remove a booking from the system. Utilizes the DELETE method.
 *
 * Associated rel attribute: delete (in Booking profile)
 * ONSUCCESS=>
 *          a) Inform the user with an alert.
 *          b) Go to the initial state by calling the function {@link #reloadBookingsList} *
 *
 * ONERROR => Show an alert to the user
 *
 * @param {string} apiurl - The url of the Booking
 *
**/

function deleteBooking(apiurl){
    $.ajax({
       url: apiurl,
       type: "DELETE"
    }).done(function (data, textStatus, jqXHR){
       if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("The booking has been deleted from the database");
        reloadBookingsList();
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert ("The booking could not be deleted from the database");
    });
}


/**
 * Sends an AJAX request to create a new booking {@link http://docs.tellusreservationapi.apiary.io/#reference/bookings/bookings-of-room/rooms-list}
 *
 * Associated link relation: add-booking
 *
 *  ONSUCCESS =>
 *       a) Show an alert informing the user that the booking information has been added.
 *       b) Append the booking to the list of booking by calling {@link #reloadBookingsList}
 *          * {@link #reloadBookingsList} refresh the list by a new API call.
 *
 * ONERROR =>
 *      a) Show an alert informing that the new information was not stored in the database
 *
 * @param {string} apiurl - The url of the bookings of room.
 * @param {object} booking - An associative array containing the new booking's information
 *
**/
function addBooking(apiurl,booking){
    var bookingData = JSON.stringify(booking);
    return $.ajax({
        url: apiurl,
        type: "POST",
        data:bookingData,
        processData:false,
        contentType: PLAINJSON
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("Booking successfully added");
        reloadBookingsList();
    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert ("Could not create new booking:"+jqXHR.responseJSON.message);
    });
}


/**
 * Sends an AJAX request to modify the restricted profile of a user, using PUT
 *
 * NOTE: This is NOT utilizied in this application.
 *
 * Associated rel attribute: edit (user profile)
 *
 * ONSUCCESS =>
 *     a)Show an alert informing the user that the user information has been modified
 * ONERROR =>
 *     a)Show an alert informing the user that the new information was not stored in the databse
 *
 * @param {string} apiurl - The url of the intance to edit.
 * @param {object} body - An associative array containing the new data of the
 *  target user
 *
**/
function edit_user(apiurl, body){
    $.ajax({
        url: apiurl,
        type: "PUT",
        data:JSON.stringify(body),
        processData:false,
        contentType: PLAINJSON
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("User information have been modified successfully");

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        var error_message = $.parseJSON(jqXHR.responseText).message;
        alert ("Could not modify user information;\r\n"+error_message);
    });
}


/**** END RESTFUL CLIENT****/

/**** UI HELPERS ****/

/**** This functions are utilized by rest of the functions to interact with the UI ****/

/**
 * Append a new room to the #room_list. It appends a new <li> element in the #room_list
 * using the information received in the arguments.
 *
 * @param {string} bookingsUrl - The url of bookings of room to be added to the list
 * @param {string} name - The name of the room to be added to the list
 * @returns {Object} The jQuery representation of the generated <li> elements.
**/
function appendRoomToList(bookingsUrl, name) {
    var $room = $('<li>').html('<a class= "room_bookings_link" href="'+bookingsUrl+'">'+name+'</a>');
    //Add to the user list
    $("#room_list").append($room);
    return $room;
}

/**
 * ##### This function "createFormFromSchema" is borrowed from course exercises. #####
 * # Orginally it is developed by Ivan Sanchez and Mika Oja.
**/
/**
 * Populate a form with the <input> elements contained in the <i>schema</i> input parameter.
 * The action attribute is filled in with the <i>url</i> parameter. Values are filled
 * with the default values contained in the template. It also marks inputs with required property.
 *
 * @param {string} url - The url of to be added in the action attribute
 * @param {Object} schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append <input> elements in the form
 * @param {string} id - The id of the form is gonna be populated
**/
function createFormFromSchema(url,schema,id){
    $form=$('#'+ id);
    $form.attr("action",url);
    //Clean the forms
    $form_content=$(".form_content",$form);
    $form_content.empty();
    $("input[type='button']",$form).hide();
    if (schema.properties) {
        var props = schema.properties;
        Object.keys(props).forEach(function(key, index) {
            if (props[key].type == "object") {
                appendObjectFormFields($form_content, key, props[key]);
            }
            else {
                appendInputFormField($form_content, key, props[key], schema.required.includes(key));
            }

        });
    }
    return $form;
}
/**
 * ##### This function "appendInputFormField" is borrowed from course exercises. #####
 * # Orginally it is developed by Ivan Sanchez and Mika Oja.
**/
/**
 * Private class used by {@link #createFormFromSchema}
 *
 * @param {jQuery} container - The form container
 * @param {string} The name of the input field
 * @param {Object} object_schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append properties of the input
 * @param {boolean} required- If it is a mandatory field or not.
**/
function appendInputFormField($container, name, object_schema, required) {
    var input_id = name;
    var prompt = object_schema.title;
    var desc = object_schema.description;

    $input = $('<input type="text"></input>');
    $input.addClass("editable");
    $input.attr('name',name);
    $input.attr('id',input_id);
    $label_for = $('<label></label>');
    $label_for.attr("for",input_id);
    $label_for.text(prompt);
    $container.append($label_for);
    $container.append($input);

    if(desc){
        $input.attr('placeholder', desc);
    }
    if(required){
        $input.prop('required',true);
        $label = $("label[for='"+$input.attr('id')+"']");
        $label.append(document.createTextNode("*"));
    }
}
/**
 * ##### This function "appendObjectFormFields" is borrowed from course exercises. #####
 * # Orginally it is developed by Ivan Sanchez and Mika Oja.
**/
/**
 * Private class used by {@link #createFormFromSchema}. Appends a subform to append
 * input
 *
 * @param {jQuery} $container - The form container
 * @param {string} The name of the input field
 * @param {Object} object_schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append properties of the input
 * @param {boolean} required- If it is a mandatory field or not.
**/
function appendObjectFormFields($container, name, object_schema) {
    $div = $('<div class="subform"></div>');
    $div.attr("id", name);
    Object.keys(object_schema.properties).forEach(function(key, index) {
        if (object_schema.properties[key].type == "object") {
            // only one nested level allowed
            // therefore do nothing
        }
        else {
            appendInputFormField($div, key, object_schema.properties[key], false);
        }
    });
    $container.append($div);
}

/**
 * ##### This function "fillFormWithMasonData" is borrowed from course exercises. #####
 * # Orginally it is developed by Ivan Sanchez and Mika Oja.
**/
/**
 * Populate a form with the content in the param <i>data</i>.
 * Each data parameter is going to fill one <input> field. The name of each parameter
 * is the <input> name attribute while the parameter value attribute represents
 * the <input> value. All parameters are by default assigned as
 * <i>readonly</i>.
 *
 * NOTE: All buttons in the form are hidden. After executing this method adequate
 *       buttons should be shown using $(#button_name).show()
 *
 * @param {jQuery} $form - The form to be filled in
 * @param {Object} data - An associative array formatted using Mason format ({@link https://tools.ietf.org/html/draft-kelly-json-hal-07})
**/

function fillFormWithMasonData($form, data) {

    console.log(data);

    $(".form_content", $form).children("input").each(function() {
        if (data[this.id]) {
            $(this).attr("value", data[this.id]);
        }
    });

    $(".form_content", $form).children(".subform").children("input").each(function() {
        var parent = $(this).parent()[0];
        if (data[parent.id][this.id]) {
            $(this).attr("value", data[parent.id][this.id]);
        }
    });
}

/**
 * ##### This function "serializeFormTemplate" is borrowed from course exercises. #####
 * # Orginally it is developed by Ivan Sanchez and Mika Oja.
**/
/**
 * Serialize the input values from a given form (jQuery instance) into a
 * JSON document.
 *
 * @param {Object} $form - a jQuery instance of the form to be serailized
 * @returs {Object} An associative array in which each form <input> is converted
 * into an element in the dictionary.
**/
function serializeFormTemplate($form){
    var envelope={};
    // get all the inputs into an array.
    var $inputs = $form.find(".form_content input");
    $inputs.each(function() {
        envelope[this.id] = $(this).val();
    });

    var subforms = $form.find(".form_content .subform");
    subforms.each(function() {

        var data = {}

        $(this).children("input").each(function() {
            data[this.id] = $(this).val();
        });

        envelope[this.id] = data
    });
    return envelope;
}


/**
 * Helper method that unselects any room from the #room_list and go back to the
 * initial state by hiding the "#mainContent".
**/
function deselectRoom() {
    $("#room_list li.selected").removeClass("selected");
    $("#mainContent").hide();
}

/**
 * Helper method to reload current room's bookings by making a new API call
 * Internally it makes click on the href of the selected user.
**/
function reloadBookingsList() {
    var selected = $("#room_list li.selected a");
    selected.click();
}

/**
 * ##### This function "getDate" is borrowed from course exercises. #####
 * # Orginally it is developed by Ivan Sanchez and Mika Oja.
**/
/**
 * Transform a date given in a UNIX timestamp into a more user friendly string
 *
 * @param {number} timestamp - UNIX timestamp
 * @returns {string} A string representation of the UNIX timestamp with the
 * format: 'dd.mm.yyyy at hh:mm:ss'
**/
function getDate(timestamp){
    // create a new javascript Date object based on the timestamp
    // multiplied by 1000 so that the argument is in milliseconds, not seconds
    var date = new Date(timestamp*1000);
    // hours part from the timestamp
    var hours = date.getHours();
    // minutes part from the timestamp
    var minutes = date.getMinutes();
    // seconds part from the timestamp
    var seconds = date.getSeconds();

    var day = date.getDate();

    var month = date.getMonth()+1;

    var year = date.getFullYear();

    // will display time in 10:30:23 format
    return day+"."+month+"."+year+ " at "+ hours + ':' + minutes + ':' + seconds;
}

/**** END UI HELPERS ****/

/**** BUTTON HANDLERS ****/


/**
 * Uses the API to create a new booking with the form attributes in the present form.
 *
 * TRIGGER: #createBooking
**/
function handleCreateBooking(event){
    if (DEBUG) {
        console.log ("Triggered handleCreateBooking");
    }
    var $form = $(this).closest("form");
    var template = serializeFormTemplate($form);
    var url = $form.attr("action");
    addBooking(url, template);
    reloadBookingsList();
    return false; //Avoid executing the default submit
}

/**
 * Uses the API to retrieve bookings of room information from the clicked room. In addition,
 * this function modifies the selected room in the #room_list (removes the .selected
 * class from the old room and add it to the current room)
 *
 * TRIGGER: click on #room_list li a
**/
function handleGetBookings(event) {
    if (DEBUG) {
        console.log ("Triggered handleBookings");
    }
    event.preventDefault();
    if($("#room_list").find("li.selected").length) {
        $("#room_list").find("li.selected").removeClass("selected");
    }
    $(this).parent().addClass("selected");
    $("#bookings_list").empty();
    $("#roomname").text($(this).parent().text());
    $("#mainContent").show();
    var url = $(this).attr("href");
    console.log(url);
    getRoomBookings(url);

    return false; //IMPORTANT TO AVOID <A> BUBLING
}

/**
 * Uses the API to delete the associated booking
 *
 * TRIGGER: .deleteBooking
**/
function handleDeleteBooking(event){
    if (DEBUG) {
        console.log ("Triggered handleDeleteBooking");
    }
    event.preventDefault();
    var bookingurl = $(this)[0].href;
    console.log("Delete Url: " + bookingurl);
    deleteBooking(bookingurl);

}
/**** END BUTTON HANDLERS ****/

/*** START ON LOAD ***/
//This method is executed when the webpage is loaded.
$(function(){

    // Handlers are listed below with their objects:
    // #bookings_list li.booking a.deleteBooking -> handleDeleteBooking
    // #room_list li a -> handleGetBookings
    // #createBooking -> handleCreateBooking
    $('#bookings_list').on('click', 'li.booking a.deleteBooking', handleDeleteBooking);
    $('#room_list').on('click', 'li a', handleGetBookings);
    $('#createBooking').click(handleCreateBooking);


    //Retrieve list of rooms from the server
    getRooms(ENTRYPOINT);
});
/*** END ON LOAD**/