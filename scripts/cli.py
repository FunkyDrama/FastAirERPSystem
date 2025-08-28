import asyncio
import click

from services.users_service.app.db.settings import db_settings as users_db_settings
from scripts.seed.users_seed import seed_users_db
from scripts.seed.staff_seed import seed_staff_db


@click.group(help="FastAir seeding & utilities CLI")
def cli() -> None:
    """
    FastAir seeding & utilities Command Line Interface (CLI).

    This CLI tool provides functionalities for seeding and other utilities specifically
    designed for the FastAir application. It groups related commands and offers a cohesive
    way to manage CLI operations effectively.

    :return: None
    """
    pass


@cli.command("seed")
@click.option(
    "--db",
    type=click.Choice(["users", "staff", "all"], case_sensitive=False),
    default="users",
    show_default=True,
)
@click.option("--flush", is_flag=True)
@click.option("--flights", default=40, show_default=True)
@click.option("--days", default=10, show_default=True)
def seed_cmd(db: str, flush: bool, flights: int, days: int) -> None:
    """
    Seeds the database with sample user and/or staff data. This command allows for
    selection of the database type to seed, whether to flush existing data before
    seeding, the number of flights to simulate, and the time window in days for
    the data.

    :param db: The type of database to seed. Possible values are "users",
        "staff", or "all".
    :param flush: Determines whether to flush existing data before seeding.
    :param flights: The number of flight records to generate.
    :param days: The number of days for the generated flight data's time window.
    :return: This function does not return a value.
    """

    async def _run():
        if db in ("users", "all"):
            await seed_users_db(
                dsn=users_db_settings.DATABASE_URL,
                flush=flush,
                flights_count=int(flights),
                days_window=int(days),
            )

        if db in ("staff", "all"):
            await seed_staff_db(
                # dsn=staff_db_settings.DATABASE_URL,
                flush=flush,
                flights_count=int(flights),
                days_window=int(days),
            )

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
