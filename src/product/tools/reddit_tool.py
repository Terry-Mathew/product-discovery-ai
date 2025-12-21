from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import feedparser
import os
import time
import re


class RedditSearchInput(BaseModel):
    """Input schema for Reddit search."""
    query: str = Field(..., description="Search query for Reddit posts")
    subreddit: str = Field(default="cscareerquestions", description="Subreddit to search")
    limit: int = Field(default=20, description="Number of results to return (max 50)")


class RedditJSONTool(BaseTool):
    name: str = "Reddit JSON Search"
    description: str = (
        "Search Reddit directly using public JSON API. "
        "Fast and reliable for finding pain points in specific subreddits. "
        "No authentication required."
    )
    args_schema: Type[BaseModel] = RedditSearchInput

    def _run(self, query: str, subreddit: str = "cscareerquestions", limit: int = 20) -> str:
        """Search Reddit using public JSON endpoint."""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ProductDiscovery/1.0"
            }
            params = {
                "q": query,
                "limit": min(limit, 50),
                "sort": "relevance",
                "t": "month",
                "restrict_sr": "1"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            posts = data.get("data", {}).get("children", [])
            
            if not posts:
                return f"No results found for '{query}' in r/{subreddit}"
            
            output = f"📊 Found {len(posts)} Reddit posts for '{query}' in r/{subreddit}:\n\n"
            
            for i, post_data in enumerate(posts[:limit], 1):
                post = post_data["data"]
                
                title = post.get("title", "")
                body = post.get("selftext", "")[:350]
                score = post.get("score", 0)
                num_comments = post.get("num_comments", 0)
                url = f"https://reddit.com{post.get('permalink', '')}"
                
                output += f"{i}. [{score}↑ {num_comments}💬] {title}\n"
                if body and len(body) > 50:
                    output += f"   Excerpt: {body}...\n"
                output += f"   Link: {url}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error with Reddit JSON API: {str(e)}"


class RedditRSSTool(BaseTool):
    name: str = "Reddit RSS Feed Search"
    description: str = (
        "Search Reddit using RSS feeds. "
        "Good for recent discussions and trending topics. "
        "Alternative method when JSON API is slow."
    )
    args_schema: Type[BaseModel] = RedditSearchInput

    def _run(self, query: str, subreddit: str = "cscareerquestions", limit: int = 20) -> str:
        """Search Reddit using RSS feeds."""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.rss?q={query}&restrict_sr=1&limit={limit}"
            
            feed = feedparser.parse(url)
            
            if not feed.entries:
                return f"No RSS results found for '{query}' in r/{subreddit}"
            
            output = f"📡 Found {len(feed.entries)} posts via RSS for '{query}' in r/{subreddit}:\n\n"
            
            for i, entry in enumerate(feed.entries[:limit], 1):
                title = entry.get("title", "")
                summary = entry.get("summary", "")[:300]
                link = entry.get("link", "")
                
                output += f"{i}. {title}\n"
                if summary:
                    # Clean HTML tags from summary
                    clean_summary = re.sub(r'<[^>]+>', '', summary)
                    output += f"   Summary: {clean_summary[:250]}...\n"
                output += f"   Link: {link}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error with Reddit RSS: {str(e)}"


class SerperRedditTool(BaseTool):
    name: str = "Google Search for Reddit Discussions"
    description: str = (
        "Use Google to find Reddit discussions across multiple subreddits. "
        "Best for broad searches and discovering relevant subreddits. "
        "Requires SERPER_API_KEY in environment."
    )
    args_schema: Type[BaseModel] = RedditSearchInput

    def _run(self, query: str, subreddit: str = "all", limit: int = 20) -> str:
        """Search Google for Reddit posts using Serper API."""
        try:
            api_key = os.getenv("SERPER_API_KEY")
            if not api_key:
                return "Error: SERPER_API_KEY not found in .env file. Please add it to use this tool."
            
            # Construct search query
            if subreddit == "all":
                search_query = f"site:reddit.com {query}"
            else:
                search_query = f"site:reddit.com/r/{subreddit} {query}"
            
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": search_query,
                "num": min(limit, 50)
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            organic_results = data.get("organic", [])
            
            if not organic_results:
                return f"No Google results found for '{query}' on Reddit"
            
            output = f"🔎 Found {len(organic_results)} Reddit discussions via Google:\n\n"
            
            for i, result in enumerate(organic_results[:limit], 1):
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                output += f"{i}. {title}\n"
                output += f"   Preview: {snippet}\n"
                output += f"   Link: {link}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error with Serper API: {str(e)}"
