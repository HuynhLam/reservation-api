# Tellus Room Reservation API

This is an API to reserve rooms at Tellus.

## Reservation API

*Reservation part will be implemented soon.*

## Database API

We are providing an API to interact with database. Instead of interacting with 
database directly, it is possible to do changes via Python with Database API.

### Requirements

To run API, the following tools are needed:

* [Python 2.7.X](https://www.python.org/download/releases/2.7/)
* [sqlite3](https://www.sqlite.org/)

For Python the following library is needed.

* [sqlite3](https://docs.python.org/2/library/sqlite3.html)

### How to Use

* [Cloning Repo](####cloning-repo)

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

#### Using Database API

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
