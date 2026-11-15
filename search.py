
import argparse
import time

from db import get_connection, make_query, search


def main():
    parser = argparse.ArgumentParser(
        description="Search text inside your screenshots."
    )

    parser.add_argument(
        "query",
        help="Text to search for"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )

    parser.add_argument(
        "--exact",
        action="store_true",
        help="Search for the exact phrase"
    )

    parser.add_argument(
        "--prefix",
        action="store_true",
        help="Enable partial-word search"
    )

    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    if args.exact and args.prefix:
        parser.error("--exact and --prefix cannot be used together")

    query = make_query(
        args.query,
        prefix=args.prefix,
        exact=args.exact
    )
    print("Generated query:", repr(query))

    if not query:
        parser.error("Search query cannot be empty")

    con = get_connection()

    start_time = time.perf_counter()

    try:
        results = search(con, query, args.limit)
    finally:
        con.close()

    elapsed = time.perf_counter() - start_time

    print(f"\nFound {len(results)} results.")
    print(f"Search time: {elapsed * 1000:.2f} ms\n")

    if not results:
        print("No matching screenshots found.")
        print("Tip: Try a different keyword or use --prefix.")
        return

    for index, row in enumerate(results, start=1):
        print(f"{index}. {row['path']}")
        print(f"   {row['snippet']}")
        print()


if __name__ == "__main__":
    main()
