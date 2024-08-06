# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project loosely adheres to a date-based versioning scheme.

## 2024-08-06

### Changed

* [*BREAKING*] **Package!** This repo now conforms to the typical "installable package" layout, with all application code below `src/Excel2Json/`. This allows installation of the package via `pip`, and makes testing with pytest a whole lot more tractable. However, it does mean that you may have to change your import paths if you cloned this repository and used it as the root of your own project. Probably the easiest approach to integrating this package is in a virtualenv with `pip`:

```shell
$ cd your_project_dir
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install <URL_TO_HERE>
$ # hack hack hack, when done:
$ deactivate
```
* **Retain qualifier in names!** If an associated person's name contains a qualifier, such as `[group]`, this qualifier is retained in the resulting structure in MongoDB; see [the README](./README.md#name) for details
* **Handle multiple affiliations!** If an associated person's affiliation is provided as a semicolon-separated list, e.g., `ACME Corp; Giga Group`, this list is split into separate sub-parts, resulting in `["ACME Corp", "Giga Group"]`

### Added

* **Tests!** A dependency on `pytest` was added, and the changes to name-handling outlined above are covered by a unit test. More to come!

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

    
