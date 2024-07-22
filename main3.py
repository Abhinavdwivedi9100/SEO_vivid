import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import re
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
openai_api_key=(os.getenv("OPENAI_API_KEY"))


logo_path = r"SEO_vivid\seo logo.jpg"
st.image(logo_path, width=175)  # Adjust the width as needed

# Use st.markdown to combine the title and logo
st.markdown(
    """
    <div style="display: flex; align-items: left;">
        <img src="file://SEO_vivid\seo logo.jpg" width="50" style="margin-right: 0px;">
        <h1 style="margin: 0;">SEO Writing App</h1>
    </div>
    """,
    unsafe_allow_html=True
)
main_keyword = st.text_input("Enter the Main Keyword")

if main_keyword:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": f"Generate 5 suitable blog titles for the keyword: {main_keyword}"}],
        max_tokens=150,
        n=5,
        temperature=0.2,
        model="gpt-4"
    )
    titles = [response.choices[x].message.content for x in range(1)]

    titles = re.findall(r'"\s*(.*?)\s*"', " ".join(titles))
    selected_title = st.radio("Select a Title", titles)

    st.write(f"Selected title: {selected_title}")

st.header("Core Settings")

language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Chinese"])

article_size = st.selectbox("Article Size", ["Small", "Medium", "Large"])

tone_of_voice = st.selectbox("Tone of Voice", ["Friendly", "Professional", "Informational", "Transactional", "Inspirational", "Neutral", "Witty", "Casual", "Authoritative", "Encouraging", "Persuasive", "Poetic"])

ai_model = st.selectbox("AI Model", ["Anthropic Claude 3 Haiku", "GPT-4o"])

point_of_view = st.selectbox("Point of View", ["First person singular (I, me, my, mine)", "First person plural (we, us, our, ours)", "Second person (you, your, yours)", "Third person (he, she, it, they)"])

st.header("SEO")

seo_keywords = st.text_area("Enter SEO Keywords (comma-separated)")

st.header("Structure")

hook_type = st.selectbox("Type of Hook", ["Question", "Statistical or Fact", "Quotation", "Personal or Emotional"])

st.header("Connect to Web")

web_connection = st.selectbox("Select Web Connection Type", ["Basic Web", "Deep Web"])

def fetch_search_results(api_key, query):
    headers = {"apikey": api_key}
    params = {"q": query}
    response = requests.get("https://app.zenserp.com/api/v2/search", headers=headers, params=params)
    return response.json()

def extract_relevant_info(search_results):
    extracted_info = []
    for item in search_results.get("organic", []):
        title = item.get('title')
        description = item.get('description')
        url = item.get('url')
        if title and description and url:
            content = fetch_page_content(url)
            extracted_info.append({
                "title": title,
                "description": description,
                "url": url,
                "content": content
            })
    return extracted_info

def fetch_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all('p')
        page_content = " ".join([p.get_text() for p in paragraphs])
        return page_content
    except requests.RequestException as e:
        return f"Error fetching page content: {e}"

if 'search_results' not in st.session_state:
    st.session_state.search_results = None

if web_connection == "Basic Web":
    zenserp_api_key = os.getenv("zenserp_api_key")
    search_query = st.text_input("Enter Search Query for Real-Time Search")
    if search_query:
        st.session_state.search_results = fetch_search_results(zenserp_api_key, search_query)
        st.write(st.session_state.search_results)

if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

if st.button("Generate Blog", disabled=st.session_state.button_clicked):
    st.session_state.button_clicked = True
    if st.session_state.search_results:
        relevant_info = extract_relevant_info(st.session_state.search_results)
        search_content = ""
        for info in relevant_info:
            search_content += f"Title: {info['title']}\nDescription: {info['description']}\nContent: {info['content'][:1000]}...\n\n"  

        prompt = f"""
        Generate a blog post with the following details:
        Title: {selected_title}
        Language: {language}
        Article Size: {article_size}
        Tone of Voice: {tone_of_voice}
        AI Model: {ai_model}
        Point of View: {point_of_view}
        SEO Keywords: {seo_keywords}
        Hook Type: {hook_type}
        Search Results: {search_content}
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.2
        )
        blog_content = response.choices[0].message.content

        final_output = f"## {selected_title}\n\n{blog_content}"
        st.write(final_output)
