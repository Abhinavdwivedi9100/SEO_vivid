import gradio as gr
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import re
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
openai_api_key=(os.getenv("OPENAI_API_KEY"))

def generate_titles(main_keyword):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": f"Generate 5 suitable blog titles for the keyword: {main_keyword}"}],
        max_tokens=150,
        n=5,
        temperature=0.2,
        model="gpt-4"
    )
    titles = [response.choices[x].message.content for x in range(1)]
    titles = re.findall(r'"\s*(.*?)\s*"', " ".join(titles))
    return titles

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

def generate_blog(main_keyword, selected_title, language, article_size, tone_of_voice, ai_model, point_of_view, seo_keywords, hook_type, search_query):
    search_results = fetch_search_results(os.getenv("zenserp_api_key"), search_query)
    relevant_info = extract_relevant_info(search_results)
    search_content = ""
    for info in relevant_info:
        search_content += f"Title: {info['title']}\nDescription: {info['description']}\nContent: {info['content'][:1000]}...\n\n"  

    prompt = f"""
    Generate a blog post with the following details:
    Title: {selected_title}
    Language: {language}
    Article Size: {article_size}    "X-Small: (600-1200 words, 2-5 H2 headings)",
                                    "Small: (1200-2400 words, 5-8 H2 headings)",
                                    "Medium: (2400-3600 words, 9-12 H2 headings)",
                                    "Large: (3600-5200 words, 13-16 H2 headings)"
    Tone of Voice: {tone_of_voice}
    AI Model: {ai_model}
    Point of View: {point_of_view}
    SEO Keywords: {seo_keywords}
    Hook Type: {hook_type}
    Search Results: {search_content}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.2
    )
    blog_content = response.choices[0].message.content
    return blog_content

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# SEO Writing App")
    logo_path = "C:/Users/HP/SEO_vivid/seo logo.jpg"
    gr.Image(logo_path, width=175)

    main_keyword = gr.Textbox(label="Enter the Main Keyword")
    selected_title = gr.Dropdown(choices=[], label="Select a Title")
    language = gr.Dropdown(choices=["English", "Spanish", "French", "German", "Chinese"], label="Language")
    article_size = gr.Dropdown(choices=["X-Small", "Small", "Medium", "Large"], label="Article Size")
    tone_of_voice = gr.Dropdown(choices=["Friendly", "Professional", "Informational", "Transactional", "Inspirational", "Neutral", "Witty", "Casual", "Authoritative", "Encouraging", "Persuasive", "Poetic"], label="Tone of Voice")
    ai_model = gr.Dropdown(choices=["Anthropic Claude 3 Haiku", "GPT-4"], label="AI Model")
    point_of_view = gr.Dropdown(choices=["First person singular (I, me, my, mine)", "First person plural (we, us, our, ours)", "Second person (you, your, yours)", "Third person (he, she, it, they)"], label="Point of View")
    seo_keywords = gr.Textbox(label="Enter SEO Keywords (comma-separated)")
    hook_type = gr.Dropdown(choices=["Question", "Statistical or Fact", "Quotation", "Personal or Emotional"], label="Type of Hook")
    search_query = gr.Textbox(label="Enter Search Query for Real-Time Search")

    generate_button = gr.Button("Generate Blog")

    def update_titles(main_keyword):
        titles = generate_titles(main_keyword)
        return gr.update(choices=titles, value=titles[0] if titles else "")

    main_keyword.change(update_titles, inputs=main_keyword, outputs=selected_title)

    generate_button.click(
        generate_blog,
        inputs=[main_keyword, selected_title, language, article_size, tone_of_voice, ai_model, point_of_view, seo_keywords, hook_type, search_query],
        outputs=gr.Markdown()
    )

demo.launch(share=True)
