import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="Rambo AI TV — مرتّب قنوات التليفزيون",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Remove Streamlit's default padding/menu/footer so the embedded page looks
# exactly like the original standalone HTML file, with no Streamlit chrome
# around it.
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
            max-width: 100%;
        }
        iframe {
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

html_path = Path(__file__).parent / "rambo-ai-tv.html"
html_content = html_path.read_text(encoding="utf-8")

# Height is generous so the whole tool (including the priority panel and
# transfer page) is visible without an inner scrollbar on most screens.
# scrolling=True keeps it usable if the content is taller than the viewport.
components.html(html_content, height=2200, scrolling=True)
