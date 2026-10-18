# 🔍 Wikipedia & arXiv Research Search Engine

An AI-powered research search engine built with Python, Gradio, LangChain, and Groq. It allows users to search Wikipedia articles, find arXiv research papers, and generate AI-powered explanations of research topics.

## 🚀 Features

* 🔎 Search Wikipedia articles.
* 📚 Search arXiv papers by paper ID.
* 🧠 Search research papers by topic.
* 🤖 Generate AI-powered research explanations.
* 🔗 Display paper details, abstracts, and source links.
* 🌐 Interactive Gradio web interface.

## 🛠️ Technologies Used

* Python
* Gradio
* LangChain
* Groq
* Requests
* BeautifulSoup
* Wikipedia API
* arXiv API

## 📂 Project Structure

```text
Wikipedia-Arxiv-Research-Search-Engine/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Ravinuthala-Venkata-Siva-Prasad/Wikipedia-Arxiv-Research-Search-Engine.git
```

### 2. Navigate to the project directory

```bash
cd Wikipedia-Arxiv-Research-Search-Engine
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Groq API key

Create a `.env` file in the project directory:

```text
GROQ_API_KEY=your_groq_api_key
```

Replace `your_groq_api_key` with your actual API key.

Get an API key from the [Groq Console](https://console.groq.com/keys).

### 5. Run the application

```bash
python app.py
```

Open the local Gradio URL displayed in your terminal.

## 💡 How to Use

1. Start the application.
2. Select a search type.
3. Enter a topic, research question, or arXiv paper ID.
4. Click **Search**.
5. Read the search results and AI-generated explanation.

### Example Searches

* `Machine Learning`
* `Retrieval Augmented Generation`
* `1706.03762`

## 🔄 Workflow

```text
User Input
    |
    v
Gradio Interface
    |
    v
Search Selection
    |
    +-------------------+
    |                   |
    v                   v
Wikipedia API         arXiv API
    |                   |
    v                   v
Article Results      Research Papers
    |                   |
    v                   v
LangChain Agent      Groq LLM
    |                   |
    v                   v
AI Explanation       AI Explanation
    |                   |
    +---------+---------+
              |
              v
        Display Results
```

## 🔐 Security

* Store API keys in a `.env` file.
* Do not upload `.env` to GitHub.
* Add `.env` to `.gitignore`.
* Keep your API keys private.

## 🔮 Future Improvements

* Add more research sources.
* Support downloading research papers.
* Add PDF summarization.
* Maintain search history.
* Improve result filtering and ranking.

