# Tellus Room Reservation API

## Info about Project and Course

This was our project with [Lam Huynh](https://github.com/HuynhLam) for Programmable Web Project Course (PWP).
The project idea was designing and implementing a reservation API for study center (Tellus) in University of Oulu.
We used design first approach for this project, in this repo we only share the code part.

Please be aware that this was a course project so **all functionality could not be implemented, because of time restrictions**
point was to learn how to make a web project. Implemented methods are listed under [Implemented Methods](#implemented-methods)
section.

In the course, it was allowed to barrow code snippets from exercises. We marked them inside the code with comments,
these parts belong to course instructors 
[Iván Sánchez](http://www.oulu.fi/cse/personnel/iv%C3%A1n-s%C3%A1nchez) and 
[Mika Oja](http://www.oulu.fi/cse/personnel/mika-oja).

All codes and the below explanations are submitted as code work for the project and published
after end of the course and grading.

**Developers:**

- [Onur Özüduru](https://github.com/HuynhLam)
- [Lam Huynh](https://github.com/HuynhLam)

# Room Reservation API

It consists of 2 APIs, one to interact with the database and the other the main API which provides resources.
Both of them are explained below, please note that the section *How to Use* explains 
how to setup and use resources while section *Database API* explains how to setup and handle 
database interactions.

The following part explains the *Reservation API* in general, please note that it depends on 
*Database API* so, **before running `resources.py` make sure that *Database API* is working.** 

An example client is provided in this project. Since focus is on API, details about example client 
can be found under the section *Example Client*.

**To read more about *Database API*, please see the section [Database API](#database-api) in this Readme file.**

## Tellus Room Reservation API Documentation

The documentation of the API can be found in 
[Tellus Room Reservation API Documentation page.](http://docs.tellusreservationapi.apiary.io/#)

## List of Resources

The following resources are provided by the API.

![resources list](https://github.com/onurozuduru/reservation-api/blob/master/documentation/resources_list.png)

## Implemented Methods

Because of the time restrictions, not all methods are implemented. 
The below table shows available methods under resources.

![implemented methods](https://github.com/onurozuduru/reservation-api/blob/master/documentation/methods.png)


## Requirements

To run API, the following tools are needed:

* [Python 2.7.X](https://www.python.org/download/releases/2.7/)
* [sqlite3](https://www.sqlite.org/)

For Python the following additional libraries are needed.

* [sqlite3](https://docs.python.org/2/library/sqlite3.html)
* [Flask](http://flask.pocoo.org/)
* [Flask-RESTful](https://flask-restful.readthedocs.io/en/0.3.5/)

### How to Use

* [Cloning Repo](#cloning-repo)
* [Checking Structure](#checking-structure)
* [Creating Database Tables and Populating Them](#creating-database-tables-and-populating-them)
* [Database API](#using-database-api)
* [Using Tellus Room Reservation API](#using-tellus-room-reservation-api)
* [Running Tests](#running-tests)

#### Cloning Repo

The easiest way to download code is cloning the repo directly from source 
with `git clone` command.

We are providing some _bash scripts_ to make developers' life easier.
If you want to use them, you must give execute permissions to these scripts.

```bash
    $ cd project
    $ chmod +x check_file_structure.sh
    $ chmod +x create_and_populate_db.sh
    $ chmod +x run_tests.sh
    $ chmod +x run_tests_api_resources.sh
    $ chmod +x check_client_file_structure.sh
```

_project_ is the name of the folder which includes all codes.

#### Checking Structure

To make sure that every folder and file are in the right place, the script
named **check_file_structure.sh** can be run.

```bash
    $ ./check_file_structure.sh
```

It gives error message if one of the important file is missing and it inform 
user with a warning if file is missing but API can work without it.

> **Please note that, this script only checks for API files.**
> **To check structure of client part, please read _Check File Structure of Client_ under section _Example Client_**.

#### Creating Database Tables and Populating Them

Database tables can be created from **tellus_schema_dump.sql** under database
folder. And after that it can be populated with **tellus_data_dump.sql**.
We recommend to use **create_and_populate_db.sh** script for doing this.

```bash
    $ ./create_and_populate_db.sh
```

However, it is also possible to do these manually.

```bash
    $ cat database/tellus_schema_dump.sql | sqlite3 tellus.db
    $ cat database/tellus_data_dump.sql | sqlite3 tellus.db
```


#### Database API

We are providing an API to interact with database. Instead of interacting with 
database directly, it is possible to do changes via Python with Database API.

##### Using Database API

To interact with database, it is needed to create `Engine` object and to make
changes on database a _connection_ is needed. `Engine` object takes database 
path as argument. An example usage is given below under python shell.

```python
    >>> import reservation.database as database
    >>> engine = database.Engine()
    >>> con = engine.connect()
```

After the connection object created, it is possible to interact with database.
For example, a user can be removed from database as follows.

```python
    >>> con.delete_user(username='Trump')
```

#### Using Tellus Room Reservation API

To run API, it is needed to run `resources.py` via `python` command. 

```bash
    $ python reservation/resources.py
```

An example output of the above command can be like that:

```bash
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger pin code: 204-872-798
```

As it can be recognize from the example output, API runs in debug mode 
automatically. To turn off debug mode, following line in `resources.py` 
must be modified as `app.debug = False`

```python
    app.debug = True
```

> **Warning**
>
> Debug mode should never be used in a production environment!

After application run in the command-line, it will run under `port 5000` in `localhost`.

URL to access the API is **`/tellus/api/`**

For example if you visit `http://localhost:5000/tellus/api/bookings/` 
in your browser, or send GET request via `curl`, it will return list of bookings.

```bash
    $ curl http://localhost:5000/tellus/api/bookings/
```

#### Running Tests

Tests are places under _tests_ directory. We highly recommend to use 
**run_tests.sh** script to run tests, since before running each test file
it is needed to create a test database. Test database includes initial elements 
of _tellus.db_ so, it can be created from **tellus_schema_dump.sql** and 
**tellus_data_dump.sql** with the name **test_tellus.db**.

To run tests easily, you can call **run_tests.sh** script from terminal.

```bash
    $ ./run_tests.sh
```

##### Running Only the Resource Tests

Other than **run_tests.sh** which runs all tests including Database API tests, 
we are providing **run_tests_api_resources.sh** which only runs tests that 
are related with `resources.py`. The reason why to provide this script is 
providing a clear output for resource tests.

```bash
    $ ./run_tests_api_resources.sh
```

### Example Client

In addition to backend code, example client is also provided. Since client does 
not affect of running API, it will be explained in this section. **Please note that, 
this is just an example client which only uses 4 resources from the API.**

The point of having this client is giving an example to work with API and 
showing that it is okay to work with hypermedia responses. Therefore, it is a hypermedia 
client which means it creates possible next stages based on `controls` under response.

The code can be found under `example_client` folder.

In addition the client uses Chuck Norris jokes database RESTful API to provide random jokes. 
It is provided by `https://api.icndb.com` as entrypoint of the API. Documentation can be found 
in [http://www.icndb.com/api/](http://www.icndb.com/api/).

The `getJoke(apiurl)` function under `example_client.js` uses this additional API to 
fetch one random joke and to put it to header of page.

#### Dependencies

The client code depends:

* [jQuery](https://jquery.com/)

The compressed edition of version jQuery 3.2.1 has already provided under `example_client/js/` 
folder. If it cannot be found its place, it is possible to download from 
[jQuery download page](https://jquery.com/download/).

#### Used Resources

The below table shows which resources and methods are used by which functions 
under `example_client.js`.

Resource Name | HTTP Method | Function Name
------------- | ----------- | -------------
Rooms List | GET | `getRooms`
Bookings of Room | GET | `getRoomBookings`
Bookings of Room | POST | `addBooking`
Booking of Room | DELETE | `deleteBooking`
Room | PUT | `modifyRoom`


#### Check File Structure of Client

To make sure that every folder and file are in the right place for the client, the script
named **check_client_file_structure.sh** can be run.

First give it to execute permission.

```bash
    $ cd project
    $ chmod +x check_client_file_structure.sh
```

_project_ is the name of the folder which includes all codes.

Then run it with the following command.

```bash
    $ ./check_client_file_structure.sh
```

It gives error message if one of the important file is missing for client and it inform 
user with a warning if file is missing but Client can work without it.

#### How to Run API with Client

The client is static and creates possible next step codes dynamically from responses 
via javascript. Therefore, middleware dispatcher is needed to run client and server codes 
at the same time.

To run client with API backend, it is needed to run `run_with_client.py` with `python` command.


```bash
    $ python run_with_client.py
```

An example output of the above command can be like that:

```bash
     * Running on http://localhost:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger pin code: 294-477-169
```

It is same output with running only the API part, however if the page `index.html` opens 
in web browser with going `http://localhost:5000/example_client/index.html`, the below 
example output might be given by server. This means that, it serves client and API 
at the same time.

```bash
    127.0.0.1 - - [11/May/2017 21:50:20] "GET /example_client/index.html HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2017 21:50:20] "GET /example_client/css/ui.css HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2017 21:50:20] "GET /example_client/js/jquery-3.2.1.min.js HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2017 21:50:20] "GET /example_client/js/example_client.js HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2017 21:50:20] "GET /tellus/api/rooms/ HTTP/1.1" 200 -
```

##### Screenshots of Example Client

Some screenshots can be found below.

![screenshot0_of_client](https://github.com/onurozuduru/reservation-api/blob/master/example_client/screenshots/screenshot0.png)

![screenshot1_of_client](https://github.com/onurozuduru/reservation-api/blob/master/example_client/screenshots/screenshot1.png)
