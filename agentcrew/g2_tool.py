"""
G2 software review tool for CrewAI agents.
Searches G2's product catalog and retrieves reviews, ratings and comparisons.
Requires G2_API_KEY env var.
"""
import json
import os
from typing import Optional, Type
from pydantic import BaseModel, Field

try:
    import httpx
    from crewai.tools import BaseTool
except ImportError:
    raise ImportError("httpx and crewai are required")

G2_API_KEY = os.environ.get("G2_API_KEY", "")
G2_BASE_URL = "https://data.g2.com/api/v1"


def _headers():
    return {
        "Authorization": f"Bearer {G2_API_KEY}",
        "Content-Type": "application/vnd.api+json",
    }


# ── Product Search ────────────────────────────────────────────────────────────

class G2ProductSearchInput(BaseModel):
    query: str = Field(..., description="Software product or category to search on G2. E.g. 'CRM', 'Salesforce', 'project management'")
    max_results: Optional[int] = Field(5, description="Max products to return.")


class G2ProductSearchTool(BaseTool):
    name: str = "G2 Product Search"
    description: str = (
        "Search G2 for software products. Returns product name, category, "
        "G2 rating, review count and pricing. Use for competitive research, "
        "software discovery and market analysis."
    )
    args_schema: Type[BaseModel] = G2ProductSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        if not G2_API_KEY:
            return "G2_API_KEY not configured."
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(
                    f"{G2_BASE_URL}/products",
                    headers=_headers(),
                    params={"filter[name]": query, "page[size]": max_results},
                )
                resp.raise_for_status()
                data = resp.json().get("data", [])

            if not data:
                return f"No G2 products found for: {query}"

            lines = [f"G2 products matching '{query}':\n"]
            for p in data[:max_results]:
                attrs = p.get("attributes", {})
                name = attrs.get("name", "Unknown")
                slug = attrs.get("slug", "")
                rating = attrs.get("g2_rating", "N/A")
                reviews = attrs.get("reviews_count", 0)
                category = attrs.get("primary_category", {}).get("name", "")
                url = f"https://www.g2.com/products/{slug}/reviews"
                lines.append(
                    f"• {name} | ⭐ {rating}/5 | {reviews} reviews | {category}\n"
                    f"  {url}"
                )
            return "\n".join(lines)

        except httpx.HTTPError as exc:
            return f"G2 API error: {exc}"
        except Exception as exc:
            return f"G2 search failed: {exc}"


# ── Product Reviews ───────────────────────────────────────────────────────────

class G2ReviewsInput(BaseModel):
    product_id: str = Field(..., description="G2 product ID (get from G2 Product Search).")
    max_results: Optional[int] = Field(5, description="Max reviews to return.")
    min_stars: Optional[int] = Field(None, description="Minimum star rating filter (1-5).")


class G2ReviewsTool(BaseTool):
    name: str = "G2 Product Reviews"
    description: str = (
        "Fetch user reviews for a software product on G2. "
        "Returns reviewer title, company size, rating, pros, cons and summary. "
        "Use for competitive intelligence and product evaluation."
    )
    args_schema: Type[BaseModel] = G2ReviewsInput

    def _run(self, product_id: str, max_results: int = 5, min_stars: int = None) -> str:
        if not G2_API_KEY:
            return "G2_API_KEY not configured."
        try:
            params = {
                "filter[product_id]": product_id,
                "page[size]": max_results,
            }
            if min_stars:
                params["filter[star_rating]"] = min_stars

            with httpx.Client(timeout=15) as client:
                resp = client.get(
                    f"{G2_BASE_URL}/reviews",
                    headers=_headers(),
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json().get("data", [])

            if not data:
                return f"No reviews found for product ID: {product_id}"

            lines = [f"G2 Reviews for product {product_id}:\n"]
            for r in data[:max_results]:
                attrs = r.get("attributes", {})
                title = attrs.get("title", "No title")
                rating = attrs.get("rating", "N/A")
                role = attrs.get("reviewer_role", "")
                company_size = attrs.get("company_size", "")
                pros = attrs.get("love", "")[:200]
                cons = attrs.get("hate", "")[:200]
                lines.append(
                    f"⭐ {rating}/5 — {title}\n"
                    f"   Role: {role} | Company size: {company_size}\n"
                    f"   ✅ Pros: {pros}\n"
                    f"   ❌ Cons: {cons}\n"
                )
            return "\n".join(lines)

        except httpx.HTTPError as exc:
            return f"G2 API error: {exc}"
        except Exception as exc:
            return f"G2 reviews fetch failed: {exc}"


# ── Category Browse ───────────────────────────────────────────────────────────

class G2CategoryInput(BaseModel):
    category: str = Field(..., description="Software category to browse on G2. E.g. 'CRM', 'Marketing Automation', 'Help Desk'")
    max_results: Optional[int] = Field(10, description="Max products to return.")


class G2CategoryTool(BaseTool):
    name: str = "G2 Category Browse"
    description: str = (
        "Browse top-rated software products in a G2 category. "
        "Returns ranked products with ratings and review counts. "
        "Use for market landscape analysis and vendor shortlisting."
    )
    args_schema: Type[BaseModel] = G2CategoryInput

    def _run(self, category: str, max_results: int = 10) -> str:
        if not G2_API_KEY:
            return "G2_API_KEY not configured."
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(
                    f"{G2_BASE_URL}/products",
                    headers=_headers(),
                    params={
                        "filter[category_ids]": category,
                        "sort": "-g2_rating",
                        "page[size]": max_results,
                    },
                )
                resp.raise_for_status()
                data = resp.json().get("data", [])

            if not data:
                return f"No products found in G2 category: {category}"

            lines = [f"Top G2 products in '{category}':\n"]
            for i, p in enumerate(data[:max_results], 1):
                attrs = p.get("attributes", {})
                name = attrs.get("name", "Unknown")
                rating = attrs.get("g2_rating", "N/A")
                reviews = attrs.get("reviews_count", 0)
                slug = attrs.get("slug", "")
                lines.append(f"{i}. {name} | ⭐ {rating}/5 | {reviews} reviews | g2.com/products/{slug}")
            return "\n".join(lines)

        except httpx.HTTPError as exc:
            return f"G2 API error: {exc}"
        except Exception as exc:
            return f"G2 category browse failed: {exc}"
