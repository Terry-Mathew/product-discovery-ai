# 🚀 Product Discovery AI

**Validate your product idea in minutes, not weeks.**

Product Discovery AI is a sophisticated multi-agent platform designed to automate deep market research. It leverages a "crew" of specialized AI agents to analyze competitors, mine customer pain signals from social media, calculate market size (TAM/SAM/SOM), and challenge your assumptions—all while you watch their live brainstorming process in a premium dashboard.

---

## 🧠 The Agent Crew

Your project is powered by **CrewAI**, orchestrating five specialized consultants:

1.  **🔍 Market Landscape Analyst**: Maps out the competitive landscape, identifying top players and their pricing/positioning.
2.  **💬 Customer Pain Analyst**: Mines Reddit for authentic customer frustrations and unmet needs using real engagement data.
3.  **📊 Opportunity Sizing Analyst**: Provides conservative, data-driven market estimates (TAM, SAM, SOM) based on industry reports.
4.  **⚠️ Risk Reviewer**: Challenges optimistic assumptions and surfaces critical unknowns.
5.  **🎯 Strategy Synthesizer**: Resolves signals to produce a final Go/No-Go recommendation with a concrete 30/60/90-day roadmap.

---

## ✨ Features

*   **Premium Gradio Dashboard**: A beautiful, intuitive interface for inputting product details and viewing results.
*   **Live Agent Thinking**: A dedicated "Agent Thinking" tab that streams the raw terminal output of the agents' brainstorming and tool usage in real-time.
*   **Structured Analysis Sections**: Rich Markdown reports for each stage of the analysis (Competition, Pain Points, Market Sizing, Risks).
*   **Social Mining**: Integrated tools to extract data from Reddit subreddits relevant to your specific target audience.

---

## 🛠️ Setup & Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

### 1. Prerequisites
- Python 3.10 to 3.13
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed on your system.

### 2. Clone and Initialize
```bash
git clone https://github.com/Terry-Mathew/Product-CrewAi.git
cd Product-CrewAi
uv sync
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your API keys:
```env
OPENAI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
REDDIT_CLIENT_ID=optional
REDDIT_CLIENT_SECRET=optional
```
> [!NOTE]
> `SERPER_API_KEY` is required for web search and competitor research.

---

## 🚀 Usage

### Launch the Dashboard
To start the interactive AI dashboard, run:
```bash
uv run app_basic.py
```
After a few seconds, the UI will be available at `http://127.0.0.1:7860`.

### Running via CLI
You can also run the crew directly from the terminal:
```bash
uv run run_crew
```

---

## 📁 Project Structure

```text
├── src/product/
│   ├── config/             # YAML configurations for agents and tasks
│   ├── tools/              # Custom tools (Reddit mining, Serper search)
│   ├── crew.py             # Agent orchestration logic
│   └── main.py             # CLI entry point
├── app_basic.py            # Enhanced Gradio Dashboard
└── pyproject.toml          # Project dependencies and metadata
```

---

## 🔗 Project Link
Check out the latest updates here: [Product-CrewAi on GitHub](https://github.com/Terry-Mathew/Product-CrewAi.git)
