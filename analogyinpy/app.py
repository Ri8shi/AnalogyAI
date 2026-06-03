import streamlit as st
import google.generativeai as genai
from PIL import Image

def configure_gemini(api_key: str) -> genai.GenerativeModel:
    """Configure and return the Gemini model."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-3.5-flash")

api_key = "Enter your api here"

try:
    model = configure_gemini(api_key)
except Exception as e:
    st.error(f"Failed to configure Gemini: {e}")
    st.stop()

def code():

    st.title("Code translator")
    st.text("Turn cryptic code into understandable sentence.")

    code_input = st.text_area("paste your code here")
    audince = st.selectbox("select type of audience", ["5 year old","20","30","40"])
    optional = st.text_input("any optional prompt")
    translate = st.button("translate")

def image():
    st.title("Image translator")
    image_input = st.image("jh")
    audince = st.selectbox("select type of audience", ["5 year old","20","30","40"])
    optional = st.text_input("any optional prompt")
    translate = st.button("translate")

def cni():
    st.title("Code & image translator")
    code_input = st.text_area("paste your code here")
    audince = st.selectbox("select type of audience", ["5 year old","20","30","40"])
    optional = st.text_input("any optional prompt")
    translate = st.button("translate")

def about():
    st.title("hello there is we are making our prototyoe into a working project soon son ")

def example():
    st.title("here are giving some example to try")


page_code = st.Page(code, title="Code", default=True)
page_image = st.Page(image, title="Image")
page_cni = st.Page(cni, title="Code & Image")
pabout = st.Page(about, title="About")
pexample = st.Page(example, title="Example")

pg = st.navigation({
    "Type": [page_code, page_image, page_cni, pabout, pexample]
})

pg.run()
