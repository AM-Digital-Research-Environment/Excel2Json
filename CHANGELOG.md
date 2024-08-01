# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project loosely adheres to a date-based versioning scheme.

## 2024-07-25

### Added

* **Logo!** Because all great tools need one.
* **LoC URIs!** After the data has been read and wrangled from the Excel sheet, subject labels are indexed against the Library of Congress suggestion-API to retrieve:
  * authoritative labels
  * subject-heading URIs
* **CLI command!** The CLI wrapper `cli.py` supports the "insert" and "sync" operations covered in the examples. Call `python cli.py --help`, or one of the subcommands: `python cli.py [insert|sync] --help` to get started.

## 2024-07-24

### Added

* **Index names with qualifiers!** If a name provided in the "Title+Date"-sheet carries an optional qualifier, such as `[institutions]`, it can now be synced into the `institutions`-dev-dictionary. 
* **Docker!** Run `docker compose up` to get started, and run the examples with `docker compose run app --rm python example_insert.py`

### Deprecated

* Passing a plain connection string to `ValueList()` has been deprecated in favour of passing a pre-authenticated `pymongo.MongoClient`:
```python
from pymongo import MongoClient

client = MongoClient(...)

v = ValueList(
    auth_string=None,
    # ...other params as before...
    client=client
)
```

* `Excel2Json.mongo_dictCollection_auth()` has been deprecated in favour of passing a pre-authenticated `pymongo.MongoClient` to the constructor:
```python
from pymongo import MongoClient

client = MongoClient(...)

e2j = ExportJson(
    # ...other params as before...
    mongo_client=client
)
```
 
# Section titles (grab from here)
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

    
