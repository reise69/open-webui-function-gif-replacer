"""
Giphy GIF Replacer Filter for Open WebUI

Author: Alban
GitHub: https://github.com/reise69
Installation instructions: https://github.com/reise69/open-webui-function-gif-replacer
Version: 1.0.0

Description:
Add some fun in your chat. A comprehensive filter that replaces /gif "query" commands with random GIFs from Giphy.


Features:
- Random GIF selection
- Configurable max results
- Debug mode

Requirements:
- Giphy API key


required_open_webui_version: 0.3.30

"""

import os
import re
import random
import requests
from pydantic import BaseModel, Field
from typing import Optional, Callable, Any, Awaitable

class Filter:
    """
    A filter to replace text commands with random GIFs from Giphy
    """
    class Valves(BaseModel):
        """
        Configuration settings for the filter
        """
        GIPHY_API_KEY: str = Field(
            default="", 
            description="Giphy API key for searching GIFs"
        )
        DEBUG_MODE: bool = Field(
            default=False, 
            description="Enable detailed debug logging"
        )
        PRIORITY: int = Field(
            default=5, 
            description="Filter processing priority"
        )
        MAX_GIF_RESULTS: int = Field(
            default=10, 
            description="Maximum number of GIFs to retrieve per search"
        )

    class UserValves(BaseModel):
        """
        User-configurable settings
        """
        ENABLE_GIF_REPLACE: bool = Field(
            default=True, 
            description="Enable GIF replacement functionality"
        )
        RANDOM_GIF: bool = Field(
            default=True, 
            description="Select a random GIF from search results"
        )

    def __init__(self):
        """
        Initialize filter with default configurations
        """
        self.valves = self.Valves(
            GIPHY_API_KEY=os.getenv("GIPHY_API_KEY", "")
        )
        self.user_valves = self.UserValves()
        self.gif_cache = {}  # Cache to store search results

    def _find_gif_commands(self, content: str) -> list:
        """
        Find all /gif "query" commands in the content
        
        Args:
            content (str): Text to search for GIF commands

        Returns:
            list: Found GIF query commands
        """
        pattern = r'/gif\s*"([^"]*)"'
        return re.findall(pattern, content)

    def _get_gif_url(self, query: str) -> str:
        """
        Retrieve a GIF URL from Giphy with randomization strategy
        
        Args:
            query (str): Search term for GIF

        Returns:
            str: URL of a selected GIF
        """
        if not self.valves.GIPHY_API_KEY:
            return f"Error: Giphy API key missing for query: {query}"

        # Use cache if available
        if query in self.gif_cache:
            gifs = self.gif_cache[query]
        else:
            params = {
                "api_key": self.valves.GIPHY_API_KEY,
                "q": query,
                "limit": self.valves.MAX_GIF_RESULTS,
                "rating": "g",
            }
            try:
                response = requests.get(
                    "https://api.giphy.com/v1/gifs/search", 
                    params=params
                )
                data = response.json()
                
                if data.get("data"):
                    gifs = [
                        gif["images"]["fixed_width"]["url"]
                        for gif in data["data"]
                        if gif.get("images", {}).get("fixed_width", {}).get("url")
                    ]
                    
                    self.gif_cache[query] = gifs
                else:
                    return f"No GIF found for: {query}"
            except Exception as e:
                return f"GIF search error: {e}"

        if not gifs:
            return f"No GIF found for: {query}"
        
        if self.user_valves.RANDOM_GIF:
            # Random selection
            return random.choice(gifs)
        else:
            # Sequential rotation
            gif_url = gifs[0]
            self.gif_cache[query] = gifs[1:] + [gif_url]
            return gif_url

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        Pre-processing method (currently a pass-through)
        
        Args:
            body (dict): Incoming message body
            __user__ (dict, optional): User information

        Returns:
            dict: Processed message body
        """
        if not self.user_valves.ENABLE_GIF_REPLACE:
            return body
        return body

    async def outlet(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> dict:
        """
        Post-processing method to replace GIF commands
        
        Args:
            body (dict): Message body
            __user__ (dict, optional): User information
            __event_emitter__ (Callable, optional): Event emission function

        Returns:
            dict: Processed message body
        """
        if not self.user_valves.ENABLE_GIF_REPLACE:
            return body

        messages = body.get("messages", [])
        if not messages:
            return body

        last_message = messages[-1]
        
        # Process text content
        if isinstance(last_message.get("content"), str):
            content = last_message["content"]
            gif_commands = self._find_gif_commands(content)
            
            for query in gif_commands:
                gif_url = self._get_gif_url(query)
                content = content.replace(f'/gif "{query}"', f"![GIF]({gif_url})")
            
            last_message["content"] = content

        # Process list content
        elif isinstance(last_message.get("content"), list):
            for item in last_message["content"]:
                if item.get("type") == "text":
                    text = item["text"]
                    gif_commands = self._find_gif_commands(text)
                    
                    for query in gif_commands:
                        gif_url = self._get_gif_url(query)
                        text = text.replace(f'/gif "{query}"', f"![GIF]({gif_url})")
                    
                    item["text"] = text

        # Emit debug status
        if self.valves.DEBUG_MODE and __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "GIF Filter: Commands processed",
                        "done": True,
                    },
                }
            )

        return body