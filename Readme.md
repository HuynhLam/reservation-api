# Tellus Room Reservation API

This is an API to reserve rooms at Tellus.

It consists of 2 APIs, one to interact with the database and the other the main API which provides resources.
Both of them are explained below, please note that the section *How to Use* explains 
how to setup and use resources while section *Database API* explains how to setup and handle 
database interactions.

The following part explains the *Reservation API* in general, please note that it depends on 
*Database API* so, **before running `resources.py` make sure that *Database API* is working.** 

**To read more about *Database API*, please see the section [Database API](#markdown-header-database-api) in this Readme file.**

## Tellus Room Reservation API Documentation

The documentation of the API can be found in 
[Tellus Room Reservation API Documentation page.](http://docs.tellusreservationapi.apiary.io/#)

## List of Resources

The following resources are provided by the API.

![resources list](/projects/PWP14/repos/project/raw/master/documentation/resources_list.png)

## Implemented Methods

Because of the time restrictions, not all methods are implemented. 
The below table shows available methods under resources.

![implemented methods](/projects/PWP14/repos/project/raw/master/documentation/methods.png)


## Requirements

To run API, the following tools are needed:

* [Python 2.7.X](https://www.python.org/download/releases/2.7/)
* [sqlite3](https://www.sqlite.org/)

For Python the following additional libraries are needed.

* [sqlite3](https://docs.python.org/2/library/sqlite3.html)
* [Flask](http://flask.pocoo.org/)
* [Flask-RESTful](https://flask-restful.readthedocs.io/en/0.3.5/)

### How to Use

* [Cloning Repo](#markdown-header-cloning-repo)
* [Checking Structure](#markdown-header-checking-structure)
* [Creating Database Tables and Populating Them](#markdown-header-creating-database-tables-and-populating-them)
* [Database API](#markdown-header-using-database-api)
* [Using Tellus Room Reservation API](#markdown-header-using-tellus-room-reservation-api)
* [Running Tests](#markdown-header-running-tests)

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