from os import EX_IOERR
import typer
from typing_extensions import Annotated
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from wasabi import msg

from ValueSync import ValueList

app = typer.Typer()


@app.command()
def insert(connection: str):
    pass


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

    parts = source.split(".")
    assert len(parts) == 2
    db_name = parts[0]
    col_name = parts[1]

    client = MongoClient(connection)

    try:
        # The ping command is cheap and does not require auth.
        client.***REMOVED***.command("ping")
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
