import streamlit as st
import google.generativeai as genai
from PIL import Image

def configure_gemini(api_key: str) -> genai.GenerativeModel:
    genai.configure(api_key=api_keey)
    return genai.GenerativeModel(
        "gemini-2.0-flash-lite",
        generation_config=genai.GenerationConfig(
            max_output_tokens=800,
            temperature=0.3,
        ),
    )

api_key = "Enter Your API Key"

try:
    model = configure_gemini(api_keey)
except Exception as e:
    st.error(f"Failed to configure Gemini: {e}")
    st.stop()


def build_code_prompt(code: str, audience: str, optional: str) -> str:
    ctx = f" Context: {optional}" if optional.strip() else ""
    return f"""Explain this code briefly for a {audience}.{ctx} Be concise, use markdown.
```
{code}
```"""

def build_image_prompt(audience: str, optional: str) -> str:
    ctx = f" Context: {optional}" if optional.strip() else ""
    return f"""Explain the code in this image briefly for a {audience}.{ctx} Be concise, use markdown."""

def build_cni_prompt(code: str, audience: str, optional: str) -> str:
    ctx = f" Context: {optional}" if optional.strip() else ""
    code_block = f"\n```\n{code}\n```" if code.strip() else ""
    return f"""Explain the code (pasted + image) briefly for a {audience}.{ctx} Be concise, use markdown.{code_block}"""

def code():
    st.title("Code Explainer")
    st.text("Turn cryptic code into clear, understandable explanations.")
    code_input = st.text_area("Paste your code here...", height=200)
    audience = st.selectbox("Select audience level", ["Beginner ", "Intermediate", "Advanced Developer", "Expert "])
    optional = st.text_input("Additional context (optional)")
    translate = st.button("Explain Code")

    if translate:
        if not code_input.strip():
            st.warning("Please paste some code first!")
        else:
            with st.spinner("Analyzing your code…"):
                try:
                    prompt = build_code_prompt(code_input, audience, optional)
                    response = model.generate_content(prompt)
                    st.session_state["code_result"] = response.text
                except Exception as e:
                    st.error(f"Error generating explanation: {e}")

    if st.session_state.get("code_result"):
        st.markdown("---")
        st.markdown("### Explanation")
        st.markdown(st.session_state["code_result"])
        st.download_button(
            label="Download Explanation",
            data=st.session_state["code_result"],
            file_name="code_explanation.md",
            mime="text/markdown",
        )

def image():
    st.title("Image Code Reader")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image")
    audience = st.selectbox("Select audience level", ["Beginner", "Intermediate", "Advanced Developer", "Expert / Researcher"])
    optional = st.text_input("Additional context (optional)")
    translate = st.button("Explain Code")

    if translate:
        if uploaded_file is None:
            st.warning("Please upload an image first!")
        else:
            with st.spinner("Analyzing your image…"):
                try:
                    img = Image.open(uploaded_file)
                    prompt = build_image_prompt(audience, optional)
                    response = model.generate_content([prompt, img])
                    st.session_state["image_result"] = response.text
                except Exception as e:
                    st.error(f"Error generating explanation: {e}")

    if st.session_state.get("image_result"):
        st.markdown("---")
        st.markdown("### Explanation")
        st.markdown(st.session_state["image_result"])
        st.download_button(
            label="Download Explanation",
            data=st.session_state["image_result"],
            file_name="image_explanation.md",
            mime="text/markdown",
        )

def cni():
    st.title("Code & Image Analyzer")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image")
    code_input = st.text_area("Paste your code here...", height=200)
    audience = st.selectbox("Select audience level", ["Beginner", "Intermediate", "Advanced Developer", "Expert / Researcher"])
    optional = st.text_input("Additional context (optional)")
    translate = st.button("Explain Code")

    if translate:
        if not code_input.strip() and uploaded_file is None:
            st.warning("Please provide code or an image!")
        else:
            with st.spinner("Analyzing your code & image…"):
                try:
                    prompt = build_cni_prompt(
                        code_input if code_input else "", audience, optional
                    )
                    content_parts = [prompt]
                    if uploaded_file is not None:
                        img = Image.open(uploaded_file)
                        content_parts.append(img)
                    response = model.generate_content(content_parts)
                    st.session_state["cni_result"] = response.text
                except Exception as e:
                    st.error(f"Error generating explanation: {e}")

    if st.session_state.get("cni_result"):
        st.markdown("---")
        st.markdown("### Explanation")
        st.markdown(st.session_state["cni_result"])
        st.download_button(
            label="Download Explanation",
            data=st.session_state["cni_result"],
            file_name="cni_explanation.md",
            mime="text/markdown",
        )

def about():
    st.title("About Code Translator")
    st.write("This project is a multi-modal code translation and analysis application built using Python, Streamlit, and the Google Gemini API. It allows developers to input source code via raw text, images (screenshots), or a combination of both, and get clear, audience-tailored explanations powered by AI.")

    st.markdown("---")
    st.markdown("### Features")
    st.markdown("""
- **Code Explanation** -- Paste any code snippet and get a detailed, audience-tailored explanation.
- **Image Code Reader** -- Upload a screenshot of code and let AI read and explain it.
- **Code & Image Analyzer** -- Combine pasted code with an image for comprehensive analysis.
- **Multiple Audience Levels** -- Get explanations suited for beginners through experts.
- **Download Results** -- Save any explanation as a Markdown file.
""")

    st.markdown("### Tech Stack")
    st.markdown("""
- **Python** -- Core programming language
- **Streamlit** -- Web application framework
- **Google Gemini API** -- AI-powered code analysis (gemini-3.5-flash)
- **Pillow (PIL)** -- Image processing for screenshot uploads
""")

    st.markdown("### How to Use")
    st.markdown("""
1. Select a tool from the sidebar: **Code**, **Image**, or **Code & Image**.
2. Provide your input (paste code, upload an image, or both).
3. Choose your audience level to control explanation depth.
4. Click **Explain Code** and wait for the AI-generated explanation.
5. Optionally download the explanation as a Markdown file.
""")

def example():
    st.title("Example Explanations")
    st.write("Here are some example code snippets you can try. Click any **Explain This** button to see how the AI breaks it down!")

    st.markdown("### Python FizzBuzz")
    example_python = """for i in range(1, 101):
    if i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)"""
    st.code(example_python, language="python")
    if st.button("Explain This", key="ex_python"):
        with st.spinner("Explaining…"):
            try:
                prompt = build_code_prompt(example_python, "5 year old", "")
                response = model.generate_content(prompt)
                st.session_state["ex_python_result"] = response.text
            except Exception as e:
                st.error(f"Error: {e}")
    if st.session_state.get("ex_python_result"):
        st.markdown(st.session_state["ex_python_result"])

    st.markdown("---")

    st.markdown("### JavaScript Fetch API")
    example_js = """async function getUser(id) {
  const response = await fetch(`https://api.example.com/users/${id}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data = await response.json();
  return data;
}"""
    st.code(example_js, language="javascript")
    if st.button("Explain This", key="ex_js"):
        with st.spinner("Explaining…"):
            try:
                prompt = build_code_prompt(example_js, "5 year old", "")
                response = model.generate_content(prompt)
                st.session_state["ex_js_result"] = response.text
            except Exception as e:
                st.error(f"Error: {e}")
    if st.session_state.get("ex_js_result"):
        st.markdown(st.session_state["ex_js_result"])

    st.markdown("---")

    st.markdown("### SQL Join Query")
    example_sql = """SELECT u.name, COUNT(o.id) AS total_orders
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2025-01-01'
GROUP BY u.name
HAVING COUNT(o.id) > 5
ORDER BY total_orders DESC;"""
    st.code(example_sql, language="sql")
    if st.button("Explain This", key="ex_sql"):
        with st.spinner("Explaining…"):
            try:
                prompt = build_code_prompt(example_sql, "5 year old", "")
                response = model.generate_content(prompt)
                st.session_state["ex_sql_result"] = response.text
            except Exception as e:
                st.error(f"Error: {e}")
    if st.session_state.get("ex_sql_result"):
        st.markdown(st.session_state["ex_sql_result"])


page_code = st.Page(code, title="Code", default=True)
page_image = st.Page(image, title="Image")
page_cni = st.Page(cni, title="Code & Image")
pabout = st.Page(about, title="About")
pexample = st.Page(example, title="Example")

pg = st.navigation({
    "Type": [page_code, page_image, page_cni, pabout, pexample]
})

pg.run()