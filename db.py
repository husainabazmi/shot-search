import sqlite3


def get_connection(db_path="shots.db"):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def init_db(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE NOT NULL,
        mtime REAL NOT NULL,
        file_hash TEXT NOT NULL,
        indexed_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS shots_fts USING fts5(
        content,
        tokenize = 'unicode61'
    );
    """)
    con.commit()


def add_image(con, path, mtime, file_hash, text):
    cur = con.execute(
        "INSERT INTO images (path, mtime, file_hash) VALUES (?, ?, ?)",
        (path, mtime, file_hash)
    )

    image_id = cur.lastrowid

    con.execute(
        "INSERT INTO shots_fts (rowid, content) VALUES (?, ?)",
        (image_id, text)
    )



def get_image(con, path):
    return con.execute(
        "SELECT * FROM images WHERE path = ?",
        (path,)
    ).fetchone()


def delete_image(con, path):
    image = get_image(con, path)

    if image is None:
        return

    con.execute(
        "DELETE FROM shots_fts WHERE rowid = ?",
        (image["id"],)
    )

    con.execute(
        "DELETE FROM images WHERE path = ?",
        (path,)
    )



def update_image(con, path, mtime, file_hash, text):
    delete_image(con, path)
    add_image(con, path, mtime, file_hash, text)

def update_mtime(con, path, mtime):
    con.execute(
        "UPDATE images SET mtime = ? WHERE path = ?",
        (mtime, path)
    )

def make_query(user_input, prefix=False, exact=False):
    user_input = user_input.strip()

    if not user_input:
        return ""

    # Exact phrase search
    if exact:
        safe_text = user_input.replace('"', '""')
        return f'"{safe_text}"'

    # Search each term separately
    terms = user_input.split()

    safe_terms = []

    for term in terms:
        # Escape double quotes inside FTS5 quoted strings
        term = term.replace('"', '""')

        if prefix:
            safe_terms.append(f'"{term}"*')
        else:
            safe_terms.append(f'"{term}"')

    return " ".join(safe_terms)


def search(con, query, limit=10):
    sql = """
    SELECT images.path,
           snippet(shots_fts, 0, '[', ']', ' ... ', 12) AS snippet,
           bm25(shots_fts) AS score
    FROM shots_fts
    JOIN images ON images.id = shots_fts.rowid
    WHERE shots_fts MATCH ?
    ORDER BY score
    LIMIT ?
    """

    return con.execute(sql, (query, limit)).fetchall()
