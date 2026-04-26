"""Google Scholar data fetcher with JSON caching for Alexander Benlian."""

import json
import os
import time
from datetime import datetime
from typing import Optional

CACHE_FILE = os.path.join(os.path.dirname(__file__), "scholar_cache.json")
CACHE_MAX_AGE = 24 * 3600  # seconds


def _clean_interests(raw) -> list[str]:
    if not raw:
        return []
    result = []
    for item in raw:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            result.append(item.get("title", ""))
    return [x for x in result if x]


def _serialize(author: dict) -> dict:
    pubs = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        year_raw = bib.get("pub_year") or bib.get("year")
        try:
            year = int(year_raw)
        except (TypeError, ValueError):
            year = None
        pubs.append(
            {
                "title": bib.get("title", "Unknown"),
                "year": year,
                "citations": int(pub.get("num_citedby", 0) or 0),
                "venue": (
                    bib.get("journal")
                    or bib.get("venue")
                    or bib.get("conference")
                    or bib.get("booktitle")
                    or ""
                ),
            }
        )
    pubs.sort(key=lambda x: x["citations"], reverse=True)

    return {
        "name": author.get("name", ""),
        "affiliation": author.get("affiliation", ""),
        "email_domain": author.get("email_domain", ""),
        "interests": _clean_interests(author.get("interests", [])),
        "total_citations": int(author.get("citedby", 0) or 0),
        "hindex": int(author.get("hindex", 0) or 0),
        "i10index": int(author.get("i10index", 0) or 0),
        "total_citations5y": int(author.get("citedby5y", 0) or 0),
        "hindex5y": int(author.get("hindex5y", 0) or 0),
        "i10index5y": int(author.get("i10index5y", 0) or 0),
        "cites_per_year": {
            str(k): int(v)
            for k, v in (author.get("cites_per_year") or {}).items()
        },
        "publications": pubs,
        "fetched_at": time.time(),
        "fetched_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def load_cache() -> Optional[dict]:
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
        if time.time() - data.get("fetched_at", 0) < CACHE_MAX_AGE:
            return data
    except Exception:
        pass
    return None


def save_cache(data: dict) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


SCHOLAR_ID = "_X39PbsAAAAJ"  # Alexander Benlian's Google Scholar user ID


def fetch_author_data(
    author_name: str = "Alexander Benlian",
    force_refresh: bool = False,
) -> dict:
    """
    Return Google Scholar metrics for *author_name*.

    Tries fetching by Scholar ID first (more reliable), then falls back to
    name search.  Uses a 24-hour JSON cache; set force_refresh=True to bypass.
    Raises RuntimeError when scraping fails and no cache exists.
    """
    if not force_refresh:
        cached = load_cache()
        if cached:
            return cached

    try:
        from scholarly import scholarly as _s  # type: ignore

        # Prefer direct ID lookup — faster and more precise
        try:
            author_stub = _s.search_author_id(SCHOLAR_ID)
        except Exception:
            author_stub = next(_s.search_author(author_name))

        author = _s.fill(
            author_stub,
            sections=["basics", "indices", "counts", "publications"],
        )
        data = _serialize(author)
        save_cache(data)
        return data

    except StopIteration:
        raise RuntimeError(
            f"Author '{author_name}' not found on Google Scholar."
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch Scholar data: {exc}") from exc
