
from pathlib import Path

import streamlit as st

from db import get_connection, make_query, search

# Page configuration
st.set_page_config(
    page_title="Shot Search",
    page_icon="🔎",
    layout="wide"
)

# App heading
st.title("🔎 Shot Search")
st.caption("Search text inside your screenshots using OCR.")

# Search controls
keyword = st.text_input(
    "Search your screenshots",
    placeholder="Enter a word or phrase..."
)

col1, col2 = st.columns(2)

with col1:
    prefix = st.checkbox("Prefix search")

with col2:
    exact = st.checkbox("Exact phrase search")

limit = st.slider("Maximum results", 1, 50, 10)

# Search operation
if keyword.strip():

    query = make_query(
        keyword,
        prefix=prefix,
        exact=exact
    )

    con = get_connection()

    try:
        results = search(con, query, limit)
    finally:
        con.close()

    st.subheader(f"Found {len(results)} results")

    if results:
        columns = st.columns(3)

        for index, result in enumerate(results):
            image_path = Path(result["path"])
            snippet = result["snippet"]
            score = result["score"]

            with columns[index % 3]:
                if image_path.exists():
                    st.image(
                        str(image_path),
                        caption=image_path.name,
                        use_container_width=True
                    )
                else:
                    st.warning("Image file not found")

                st.markdown(f"**OCR match:** {snippet}")
                st.caption(f"Relevance score: {score:.4f}")

    else:
        st.info("No matching screenshots found.")

else:
    st.info("Enter a keyword to search your screenshots.")
