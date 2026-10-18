import os
import requests
import time
import xml.etree.ElementTree as ET
import gradio as gr

from urllib.parse import quote
from bs4 import BeautifulSoup
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from your .env file")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=api_key
)


# -------- WIKIPEDIA SEARCH --------

@tool
def machine_learning_search(query: str) -> str:
    """Search Wikipedia and return article summaries and URLs."""

    url = "https://en.wikipedia.org/w/api.php"

    try:
        response = requests.get(
            url,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 3
            },
            headers={"User-Agent": "AIResearchAssistant/1.0"},
            timeout=30
        )

        response.raise_for_status()
        results = response.json().get("query", {}).get("search", [])

        if not results:
            return f"No Wikipedia results found for: {query}"

        output = []

        for item in results:
            title = item.get("title", "Unknown")
            snippet = BeautifulSoup(
                item.get("snippet", ""),
                "html.parser"
            ).get_text(" ", strip=True)

            article_url = (
                "https://en.wikipedia.org/wiki/"
                + quote(title.replace(" ", "_"), safe="()")
            )

            output.append(
                f"Title: {title}\n"
                f"Information: {snippet}\n"
                f"Source: {article_url}"
            )

        return "\n\n".join(output)

    except requests.RequestException as e:
        return f"Wikipedia API error: {e}"


# -------- ARXIV SEARCH --------

@tool
def arxiv_paper_search(query: str) -> str:
    """Search arXiv by paper ID or research topic."""

    query = query.strip()

    if not query:
        return "Please enter a paper ID or research topic."

    paper_id = query

    if paper_id.lower().startswith("arxiv:"):
        paper_id = paper_id[6:].strip()

    if "/abs/" in paper_id:
        paper_id = paper_id.split("/abs/", 1)[1].strip()

    is_id = (
        "." in paper_id
        and " " not in paper_id
        and "/" not in paper_id
    )

    params = {
        "start": 0,
        "max_results": 1 if is_id else 5
    }

    if is_id:
        params["id_list"] = paper_id
    else:
        params["search_query"] = f'all:"{query}"'
        params["sortBy"] = "relevance"
        params["sortOrder"] = "descending"

    for attempt in range(3):
        try:
            response = requests.get(
                "https://export.arxiv.org/api/query",
                params=params,
                headers={"User-Agent": "AIResearchAssistant/1.0"},
                timeout=40
            )

            if response.status_code in (429, 500, 502, 503, 504):
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue

            response.raise_for_status()
            root = ET.fromstring(response.content)
            break

        except requests.RequestException as e:
            if attempt == 2:
                return f"arXiv API error: {e}"
            time.sleep(3 * (attempt + 1))

        except ET.ParseError:
            return "arXiv returned invalid XML."

    else:
        return "Could not retrieve arXiv results."

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)

    if not entries:
        return "No arXiv papers found."

    output = []

    for paper in entries:
        title = paper.findtext(
            "atom:title", default="Unknown", namespaces=ns
        ).strip()

        abstract = paper.findtext(
            "atom:summary", default="", namespaces=ns
        ).strip()

        published = paper.findtext(
            "atom:published", default="Unknown", namespaces=ns
        )

        authors = [
            author.findtext("atom:name", default="", namespaces=ns)
            for author in paper.findall("atom:author", ns)
        ]

        paper_url = paper.findtext(
            "atom:id", default="", namespaces=ns
        )

        short_id = paper_url.rstrip("/").split("/")[-1]

        output.append(
            f"### {title}\n\n"
            f"**Paper ID:** {short_id}\n\n"
            f"**Authors:** {', '.join(authors)}\n\n"
            f"**Published:** {published[:10]}\n\n"
            f"**Paper:** {paper_url}\n\n"
            f"**PDF:** https://arxiv.org/pdf/{short_id}\n\n"
            f"**Abstract:** {abstract}"
        )

    return "\n\n---\n\n".join(output)


# -------- RESEARCH AGENT --------

def create_research_agent():
    return create_agent(
        model=llm,
        tools=[machine_learning_search],
        system_prompt=(
            "You are an AI research assistant. "
            "Use Wikipedia search for Wikipedia questions. "
            "Explain topics clearly with headings, examples, "
            "applications, and source links. Do not invent facts."
        )
    )


# -------- SEARCH FUNCTION --------

def search_research(option, query):

    if not query or not query.strip():
        return "Please enter a search query.", ""

    query = query.strip()

    try:
        if option == "Wikipedia Search":

            agent = create_research_agent()

            result = agent.invoke({
                "messages": [{
                    "role": "user",
                    "content": f"Search Wikipedia for {query} and explain the results."
                }]
            })

            answer = result["messages"][-1].content

            if isinstance(answer, list):
                answer = "\n".join(
                    block["text"]
                    for block in answer
                    if isinstance(block, dict)
                    and block.get("type") == "text"
                )

            return str(answer), ""

        raw_result = arxiv_paper_search.invoke({"query": query})

        if raw_result.startswith("arXiv API error"):
            return raw_result, ""

        if raw_result == "No arXiv papers found.":
            return raw_result, ""

        answer = llm.invoke(
            "Explain these arXiv research papers clearly. "
            "Preserve titles, IDs, authors, dates, URLs, and abstracts. "
            "Do not invent facts.\n\n"
            + raw_result
        )

        return raw_result, answer.content

    except Exception as e:
        return f"Search failed: {type(e).__name__}: {e}", ""


# -------- GRADIO INTERFACE --------

with gr.Blocks(title="Wikipedia & arXiv Research Engine") as demo:

    gr.Markdown("# 🔍 Wikipedia & arXiv Research Paper Search Engine")
    gr.Markdown("Search Wikipedia topics and arXiv research papers.")

    option = gr.Radio(
        choices=[
            "Wikipedia Search",
            "arXiv Paper ID Search",
            "arXiv Topic Search"
        ],
        value="Wikipedia Search",
        label="Choose Search Type"
    )

    query = gr.Textbox(
        label="Search Query",
        placeholder="Machine Learning or 1706.03762",
        lines=2
    )

    button = gr.Button("🔍 Search", variant="primary")

    result = gr.Markdown(label="Search Results")
    explanation = gr.Markdown(label="AI Explanation")

    button.click(
        search_research,
        inputs=[option, query],
        outputs=[result, explanation]
    )

    query.submit(
        search_research,
        inputs=[option, query],
        outputs=[result, explanation]
    )


if __name__ == "__main__":
    demo.launch()