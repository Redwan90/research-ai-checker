import streamlit as st

st.set_page_config(page_title="Scholarship AI Tool", page_icon="🎓", layout="wide")

# Sidebar layout
with st.sidebar:
    st.markdown("## 🎓 Scholarship AI Tool")

    if "user" in st.session_state:
        username = st.session_state["user"].split("@")[0].capitalize()
        st.markdown(f"Welcome, {username} 👋")

        if st.button("🔓 Logout"):
            del st.session_state["user"]
            st.rerun()
    else:
        if st.button("🔐 Login"):
            st.switch_page("pages/Login.py")

# Main content
st.markdown("## 🎓 Welcome to the Scholarship AI Tool")
st.write("Use the sidebar to explore scholarship search, AI tools, and more.")
