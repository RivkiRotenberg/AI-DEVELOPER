import os
from pathlib import Path
from dataclasses import dataclass

from firecrawl import FirecrawlApp
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from langgraph.types import interrupt

from core.store import SourceStore, store
from core.sources import format_docs
from agents.prompts import SYSTEM_PROMPT


@dataclass
class Answer:
    text: str
    sources: list[str]


MODEL = "anthropic:claude-sonnet-4-6"
PROMPT_FILE = Path(__file__).parent / "system_prompt.md"
SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")

firecrawl_app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))


def _make_tools(store: SourceStore):

    @tool
    def search_sources(query: str) -> str:
        """Find passages in the active sources that are relevant to a query"""
        docs = store.search(query=query)
        if not docs:
            return "No relevant documents found in the active sources"
        return format_docs(docs)

    @tool
    def list_sources() -> str:
        """List all available sources in the notebook"""
        sources = store.list()  # === UPDATED: שימוש ב-list() במקום list_sources() ===
        if not sources:
            return "No sources found in the store"
        return "\n".join([f"- {s.id}: {s.name}" for s in sources])

    @tool
    def get_source(source_id: str) -> str:
        """Get the full content or metadata of a specific source by its ID"""
        source = store.get(source_id)  # === UPDATED: שימוש ב-get() במקום get_source() ===
        if not source:
            return f"Source with ID '{source_id}' not found"
        return format_docs(source.docs) if hasattr(source, "docs") else str(source.content)

    @tool
    def web_search(query: str) -> str:
        """Search the web for relevant pages using Firecrawl."""
        try:
            results = firecrawl_app.search(query=query)
            if not results or "data" not in results:
                return "No search results found."

            formatted_results = []
            for item in results.get("data", []):
                title = item.get("title", "No Title")
                url = item.get("url", "")
                snippet = item.get("description", "")
                formatted_results.append(
                    f"Title: {title}\nURL: {url}\nSnippet: {snippet}"
                )

            return "\n---\n".join(formatted_results)
        except Exception as e:
            return f"Error during search: {str(e)}"

    @tool
    def web_scrape(url: str) -> str:
        """Scrape markdown text content from a specific web page URL."""
        try:
            result = firecrawl_app.scrape_url(
                url, params={"formats": ["markdown"]}
            )
            if not result or "markdown" not in result:
                return f"Could not extract content from {url}"

            return result["markdown"]
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"

    @tool
    def web_crawl(url: str, limit: int = 3) -> str:
        """Crawl a website starting from a URL to extract content from sub-pages."""
        try:
            crawl_status = firecrawl_app.crawl_url(
                url,
                params={
                    "limit": limit,
                    "scrapeOptions": {"formats": ["markdown"]},
                },
            )
            if not crawl_status or "data" not in crawl_status:
                return f"Crawl failed for {url}"

            pages = []
            for page in crawl_status.get("data", []):
                page_url = page.get("metadata", {}).get("sourceURL", url)
                content = page.get("markdown", "")
                pages.append(f"URL: {page_url}\nContent:\n{content[:1500]}")

            return "\n===\n".join(pages)
        except Exception as e:
            return f"Error crawling {url}: {str(e)}"

    @tool
    def search_and_index_web(query: str) -> str:
        """Searches the web for a query, scrapes top results, and indexes them into the local vector store."""
        try:
            search_results = firecrawl_app.search(query=query)
            data = search_results.get("data", [])
            if not data:
                return f"No web results found for query: {query}"

            indexed_sources = []
            for item in data[:2]:
                url = item.get("url")
                title = item.get("title", "Web Source")

                scrape_res = firecrawl_app.scrape_url(
                    url, params={"formats": ["markdown"]}
                )
                content = scrape_res.get("markdown", "")

                if content:
                    # === NEW: שמירת התוכן הנסרק ב-VectorStore כולל סוג המקור ===
                    store.add(
                        name=f"[Web] {title}",
                        content=content,
                        source_type="web",
                    )
                    indexed_sources.append(title)

            if indexed_sources:
                return f"Successfully indexed the following web sources into vector store: {', '.join(indexed_sources)}"
            return "Failed to extract readable content from search results."

        except Exception as e:
            return f"Error during web research and indexing: {str(e)}"

    @tool
    def deep_web_research(queries: list[str]) -> str:
        """Performs deep web research across multiple query variations,
        scrapes top relevant web pages, and indexes them into the local store.
        """
        all_urls = {}

        for q in queries:
            try:
                res = firecrawl_app.search(query=q)
                data = res.get("data", [])
                for item in data[:2]:
                    url = item.get("url")
                    if url and url not in all_urls:
                        all_urls[url] = item.get("title", "Web Page")
            except Exception as e:
                continue

        if not all_urls:
            return "No relevant search results found across the provided queries."

        indexed_titles = []
        for url, title in list(all_urls.items())[:3]:
            try:
                scrape_res = firecrawl_app.scrape_url(
                    url, params={"formats": ["markdown"]}
                )
                content = scrape_res.get("markdown", "")

                if content:
                    # === NEW: אנדוקס המאמרים שנסרקו במחקר המעמיק ===
                    store.add(
                        name=f"[Web] {title}",
                        content=content,
                        source_type="web",
                    )
                    indexed_titles.append(title)
            except Exception as e:
                continue

        if indexed_titles:
            return f"Successfully researched and indexed content from: {', '.join(indexed_titles)}"

        return "Failed to extract content from the selected web pages."

    return [
        search_sources,
        list_sources,
        get_source,
        web_search,
        web_scrape,
        web_crawl,
        search_and_index_web,
        deep_web_research,
    ]


def answer(question: str, thread_id: str) -> Answer:
    agent = create_agent(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
        tools=_make_tools(store),
    )

    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}, config=config
    )

    text = result["messages"][-1].content if hasattr(result["messages"][-1], "content") else str(result["messages"][-1])

    # === NEW: שליפת המקורות הפעילים מתוך ה-Store להחזרה ב-Answer === #
    active_sources = [s.name for s in store.list() if getattr(s, "active", True)]

    return Answer(text=text, sources=active_sources)