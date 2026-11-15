import argparse
import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from indexer import index_folder
from db import get_connection, make_query, search, delete_image

console = Console()


def open_file(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])
def main():

    parser = argparse.ArgumentParser(
        description="Search text inside your screenshots."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # INDEX command
    index_parser = subparsers.add_parser(
        "index",
        help="Index screenshots from a folder."
    )

    index_parser.add_argument(
        "folder",
        help="Folder containing screenshots."
    )

    index_parser.add_argument(
        "--db",
        default="shots.db",
        help="Database file (default: shots.db)."
    )

    index_parser.add_argument(
        "--force",
        action="store_true",
        help="Re-index all images, even if unchanged."
    )
    index_parser.add_argument(
        "--lang",
        choices=["eng", "hin", "eng+hin"],
        default="eng",
        help="OCR language: eng, hin, or eng+hin (default: eng)."
    )

    # SEARCH command
    search_parser = subparsers.add_parser(
        "search",
        help="Search for text in screenshots."
    )

    search_parser.add_argument(
        "query",
        help="Text to search for."
    )

    search_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results."
    )

    search_parser.add_argument(
        "--open",
        action="store_true",
        help="Open the first matching image."
    )

    search_parser.add_argument(
        "--db",
        default="shots.db",
        help="Database file (default: shots.db)."
    )
    search_parser.add_argument(
        "--prefix",
        action="store_true",
        help="Enable partial-word search."
    )
    search_parser.add_argument(
        "--exact",
        action="store_true",
        help="Search for an exact phrase."
    )

    # STATS command
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show indexing statistics."
    )

    stats_parser.add_argument(
        "--db",
        default="shots.db",
        help="Database file (default: shots.db)."
    )

    # CLEAN command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Remove deleted images from the database."
    )

    clean_parser.add_argument(
        "--db",
        default="shots.db",
        help="Database file (default: shots.db)."
    )

    args = parser.parse_args()
    if args.command == "index":
        try:
            index_folder(
                folder=args.folder,
                db_path=args.db,
                force=args.force,
                lang=args.lang
            )
        except FileNotFoundError as error:
            console.print(f"[red]Error: {error}[/red]")
    elif args.command == "search":

        if args.limit < 1:
            parser.error("--limit must be at least 1")

        if args.exact and args.prefix:
            parser.error("--exact and --prefix cannot be used together")

        query = make_query(
            args.query,
            prefix=args.prefix,
            exact=args.exact
        )

        if not query:
            parser.error("Search query cannot be empty")

        con = get_connection(args.db)

        try:
            results = search(con, query, args.limit)
        finally:
            con.close()

        console.print(f"\nFound {len(results)} results.\n")

        if not results:
            console.print("[yellow]No matching screenshots found.[/yellow]")
            return

        table = Table(title="Screenshot Search Results")

        table.add_column("#", style="cyan", justify="right")
        table.add_column("Image", style="green")
        table.add_column("Snippet")

        for index, row in enumerate(results, start=1):
            table.add_row(
                str(index),
                Path(row["path"]).name,
                row["snippet"]
            )

        console.print(table)

        if args.open:
            open_file(results[0]["path"])
    elif args.command == "stats":

        db_path = Path(args.db)

        if not db_path.exists():
            console.print("[yellow]Database does not exist yet.[/yellow]")
            return

        con = get_connection(args.db)

        try:
            total_images = con.execute(
                "SELECT COUNT(*) FROM images"
            ).fetchone()[0]

            last_indexed = con.execute(
                "SELECT MAX(indexed_at) FROM images"
            ).fetchone()[0]

        finally:
            con.close()

        db_size = db_path.stat().st_size
        db_size_kb = db_size / 1024

        table = Table(title="Database Statistics")

        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total images indexed", str(total_images))
        table.add_row("Database size", f"{db_size_kb:.2f} KB")
        table.add_row("Last indexed", str(last_indexed or "N/A"))

        console.print(table)
    elif args.command == "clean":

        db_path = Path(args.db)

        if not db_path.exists():
            console.print("[yellow]Database does not exist yet.[/yellow]")
            return

        con = get_connection(args.db)

        removed_count = 0

        try:
            database_images = con.execute(
                "SELECT path FROM images"
            ).fetchall()

            for row in database_images:
                if not Path(row["path"]).exists():
                    delete_image(con, row["path"])
                    removed_count += 1

            con.commit()

        finally:
            con.close()

        console.print(
            f"[green]Cleanup complete! Removed {removed_count} deleted image entries.[/green]"
        )
if __name__ == "__main__":
    main()