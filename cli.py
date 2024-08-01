from datetime import datetime
from os import EX_IOERR
from pathlib import Path

import typer
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing_extensions import Annotated
from wasabi import msg
from rich.progress import track

from Excel2Json import ExportJson
from ValueSync import ValueList

app = typer.Typer(help="A CLI wrapper for metadata management")


@app.command()
def insert(
    file: Annotated[Path, typer.Argument(help="The Excel file to ingest")],
    connection: Annotated[
        str,
        typer.Option(
            "--connection",
            "-c",
            help="MongoDB connection string, format: 'mongodb://<user>:<pass>@<host>/'",
        ),
    ],
    target: Annotated[
        str,
        typer.Option(
            "--target",
            "-t",
            help="The target collection to write data to, format: <database>.<collection>",
        ),
    ],
    project_id: Annotated[
        str, typer.Option("--project-id", "-p", help="The project ID")
    ],
    dspace_id: Annotated[str, typer.Option("--dspace-id", "-i", help="The DSpace ID")],
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", "-d", help="Don't perform any insertion, just print the values"
        ),
    ] = False,
):
    """
    Insert metadata for research projects into MongoDB.

    Clean and wrangle the project-data provided in the Excel sheet, and insert
    into the specified MongoDB collection.

    If --dry-run is passed, it will only perform the wrangling and not insert
    anything.
    """
    parts = target.split(".")
    assert len(parts) == 2
    db_name = parts[0]
    col_name = parts[1]

    client = MongoClient(connection)

    try:
        # The ping command is cheap and does not require auth.
        client.admin.command("ping")
    except ConnectionFailure:
        msg.fail("Server not available")
        raise typer.Abort()

    msg.good("Connection established")

    msg.info(f"Ingesting file {file}")
    data = ExportJson(
        file=file, project_id=project_id, dspace_id=dspace_id, mongo_client=client
    ).run()
    msg.good("Done!")

    collection = client[db_name][col_name]

    for doc in track(data, "Setting metadata and inserting..."):
        doc["createdAt"] = datetime.now()
        doc["updatedAt"] = datetime.now()
        doc["updatedBy"] = "JaneDoe"

        if dry_run:
            continue

        collection.insert_one(doc)

    if dry_run:
        from pprint import pprint

        pprint(data)
        raise typer.Exit()

    msg.good(f"Inserted {len(data)} items.")
    raise typer.Exit()


@app.command()
def sync(
    connection: Annotated[
        str,
        typer.Option(
            "--connection",
            "-c",
            help="MongoDB connection string, format: 'mongodb://<user>:<pass>@<host>/'",
        ),
    ],
    source: Annotated[
        str,
        typer.Option(
            "--from",
            "-f",
            help="Qualified collection name to read from, format: <database>.<collection>",
        ),
    ],
    target: Annotated[
        str,
        typer.Option(
            "--target",
            "-t",
            help="Target collection in the 'dev' database to sync to, e.g. 'persons'",
        ),
    ],
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", "-d", help="Don't perform any sync, just check the values"
        ),
    ] = False,
):
    """
    Synchronise parts of the metadata with the dev-dictionaries.

    Currently supported are the 'persons' and 'institutions' dictionaries.

    If --dry-run is passed, it will only print the current and missing values
    and not synchronise any data.
    """

    parts = source.split(".")
    assert len(parts) == 2
    db_name = parts[0]
    col_name = parts[1]

    client = MongoClient(connection)

    try:
        # The ping command is cheap and does not require auth.
        client.admin.command("ping")
    except ConnectionFailure:
        msg.fail("Server not available")
        raise typer.Abort()

    msg.good("Connection established")

    values = ValueList(
        auth_string=None,
        db_name=db_name,
        col_name=col_name,
        dev_list=target,
        client=client,
    )

    msg.info(f"Values in reference collection '{source}':")
    for value in values.in_collection():
        print(f"  {value}")

    # get values missing in the MongoDB collection
    msg.info(f"Values missing in target dictionary '{target}':")
    missing = values.check_missing()
    if len(missing) == 0:
        msg.info("No missing values found, nothing to do from here")
        raise typer.Exit()

    for value in missing:
        print(f"  {value}")

    if dry_run:
        msg.warn("Running with --dry-run. Will not perform sync")
        msg.info(f"Would synchronise {len(missing)} values into {target}")
        raise typer.Exit()

    msg.info(f"Running sync now for {len(missing)} values...")
    res = values.synchronise()
    if res:
        msg.good("Sync done")
        raise typer.Exit()

    msg.fail("Sync call returned False. An error occurred. Good luck.")
    raise typer.Exit(EX_IOERR)


if __name__ == "__main__":
    app()
