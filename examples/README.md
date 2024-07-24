# Examples

The example scripts currently reside in the repo root, due to namespacing issues arising from this not being a "proper" package.

## Required files

In order to run at least the data-insertion example, a valid metadata-sheet in this directory is required.
The script currently assumes a name of `sample.xlsx`, but any name will do; just adapt the path in the script.

## `example_insert.py`

### Run

``` shell
$ python -W default example_insert.py
$ # when using Docker:
$ docker compose run --rm app python -W default example_insert.py
```

When running outside Docker, make sure the connection string for MongoDB points to a valid remote.

### Description

The script will read the data contained in the sheet, 

## `example_sync.py`

### Run

``` shell
$ python -W default example_sync.py
$ # when using Docker:
$ docker compose run --rm app python -W default example_sync.py
```

When running outside Docker, make sure the connection string for MongoDB points to a valid remote.
