"""
Wikipedia tool for CrewAI agents.
Returns full article summaries and sections. No API key required.
"""
from typing import Optional, Type
from pydantic import BaseModel, Field

try:
    import wikipedia
    from crewai.tools import BaseTool
except ImportError:
    raise ImportError("wikipedia and crewai are required: pip install wikipedia crewai")


class WikipediaInput(BaseModel):
    query: str = Field(..., description="Topic or entity to look up on Wikipedia.")
    sentences: Optional[int] = Field(5, description="Number of summary sentences to return (default 5).")
    full_article: Optional[bool] = Field(False, description="Return full article content instead of summary.")


class WikipediaTool(BaseTool):
    name: str = "Wikipedia"
    description: str = (
        "Look up any topic, person, place, company or concept on Wikipedia. "
        "Returns a structured summary with key facts. "
        "Use for background research, fact-checking and entity information."
    )
    args_schema: Type[BaseModel] = WikipediaInput

    def _run(self, query: str, sentences: int = 5, full_article: bool = False) -> str:
        try:
            wikipedia.set_lang("en")
            if full_article:
                page = wikipedia.page(query, auto_suggest=True)
                content = page.content[:4000]
                return f"# {page.title}\nURL: {page.url}\n\n{content}"
            else:
                summary = wikipedia.summary(query, sentences=sentences, auto_suggest=True)
                page = wikipedia.page(query, auto_suggest=True)
                return f"# {page.title}\nURL: {page.url}\n\n{summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            options = ", ".join(e.options[:8])
            return f"Ambiguous query '{query}'. Did you mean: {options}?"
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for: {query}"
        except Exception as exc:
            return f"Wikipedia lookup failed: {exc}"
