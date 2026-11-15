
from db import (
    get_connection,
    init_db,
    add_image,
    delete_image,
    make_query,
    search
)


def create_test_db():
    con = get_connection(":memory:")
    init_db(con)
    return con


def test_insert_and_search():
    con = create_test_db()

    add_image(
        con,
        "screenshot1.png",
        12345.0,
        "hash123",
        "Hello world this is a test screenshot"
    )

    query = make_query("Hello")
    results = search(con, query)

    assert len(results) == 1
    assert results[0]["path"] == "screenshot1.png"

    con.close()


def test_search_missing_word():
    con = create_test_db()

    add_image(
        con,
        "screenshot1.png",
        12345.0,
        "hash123",
        "Hello world"
    )

    query = make_query("Elephant")
    results = search(con, query)

    assert len(results) == 0

    con.close()


def test_delete_removes_image_from_search():
    con = create_test_db()

    add_image(
        con,
        "screenshot1.png",
        12345.0,
        "hash123",
        "Python programming"
    )

    delete_image(con, "screenshot1.png")

    query = make_query("Python")
    results = search(con, query)

    assert len(results) == 0

    con.close()


def test_special_characters_do_not_crash():
    con = create_test_db()

    add_image(
        con,
        "screenshot1.png",
        12345.0,
        "hash123",
        "C++ programming and a@b.com email"
    )

    for word in ["c++", "a@b.com"]:
        query = make_query(word)
        results = search(con, query)

        assert isinstance(results, list)

    con.close()
