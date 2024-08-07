# `Excel2Json`

A CLI wrapper for metadata management

**Usage**:

```console
$ Excel2Json [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `insert`: Insert metadata for research projects into...
* `sync`: Synchronise parts of the metadata with the...

## `Excel2Json insert`

Insert metadata for research projects into MongoDB.

Clean and wrangle the project-data provided in the Excel sheet, and insert
into the specified MongoDB collection.

If --dry-run is passed, it will only perform the wrangling and not insert
anything.

**Usage**:

```console
$ Excel2Json insert [OPTIONS] FILE
```

**Arguments**:

* `FILE`: The Excel file to ingest  [required]

**Options**:

* `-c, --connection TEXT`: MongoDB connection string, format: 'mongodb://<user>:<pass>@<host>/'  [required]
* `-t, --target TEXT`: The target collection to write data to, format: <database>.<collection>  [required]
* `-p, --project-id TEXT`: The project ID  [required]
* `-i, --dspace-id TEXT`: The DSpace ID  [required]
* `-d, --dry-run`: Don't perform any insertion, just print the values
* `--help`: Show this message and exit.

## `Excel2Json sync`

Synchronise parts of the metadata with the dev-dictionaries.

Currently supported are the 'persons' and 'institutions' dictionaries.

If --dry-run is passed, it will only print the current and missing values
and not synchronise any data.

**Usage**:

```console
$ Excel2Json sync [OPTIONS]
```

**Options**:

* `-c, --connection TEXT`: MongoDB connection string, format: 'mongodb://<user>:<pass>@<host>/'  [required]
* `-f, --from TEXT`: Qualified collection name to read from, format: <database>.<collection>  [required]
* `-t, --target [persons|institutions|groups]`: Target collection in the 'dev' database to sync to, e.g. 'persons'  [required]
* `-d, --dry-run`: Don't perform any sync, just check the values
* `--help`: Show this message and exit.
