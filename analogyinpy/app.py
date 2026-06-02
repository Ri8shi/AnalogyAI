import streamlit as st
import streamlit.components.v1 as components


st.sidebar.title("home")

st.title("Code translator")
st.text("Turn cryptic code into understandable sentence.")

code = st.text_area("paste your code here")
audince = st.selectbox("select type of audience", ["5 year old","20","30","40"])
optional = st.text_input("any optional prompt")
translate = st.button("translate")
