import logging
import aiohttp
import asyncio
import os
import re
from dotenv import load_dotenv
from search_agent.providers.model_provider import ModelProvider
from search_agent.providers.search_provider import SearchProvider
from sentient_agent_framework import (
    AbstractAgent,
    DefaultServer,
    Session,
    Query,
    ResponseHandler)
from typing import AsyncIterator, List


load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SearchAgent(AbstractAgent):
    def __init__(
            self,
            name: str
    ):
        super().__init__(name)

        model_api_key = os.getenv("MODEL_API_KEY")
        if not model_api_key:
            raise ValueError("MODEL_API_KEY is not set")
        self._model_provider = ModelProvider(api_key=model_api_key)

        search_api_key = os.getenv("TAVILY_API_KEY")
        if not search_api_key:
            raise ValueError("TAVILY_API_KEY is not set") 
        self._search_provider = SearchProvider(api_key=search_api_key)

    async def rank_urls(
    self,
    model_provider: ModelProvider,
    prompt: str,
    urls: List[str],
    top_k: int = 5
) -> List[str]:
        """
        Use an LLM to score and rank URLs by relevance to the prompt.
        """
        # 1. Build the scoring prompt
        url_list = "\n".join(f"{i+1}. {url}" for i, url in enumerate(urls))
        scoring_prompt = (
            f"Rate the relevance of each URL from 0 to 1 for answering the query:\n"
            f"Query: {prompt}\n"
            f"URLs:\n{url_list}\n"
            f"Respond with lines in the format: '<index>. <score> - <url>'."
        )

        # 2. Call the model with temperature=0 for deterministic scores
        response = await model_provider.query(
            scoring_prompt
        )

        # 3. Parse the model’s output into (url, score) tuples
        scored: List[tuple[str, float]] = []
        for line in response.splitlines():
            match = re.match(r"(\d+)\.\s*([0-1](?:\.\d+)?)\s*-\s*(.+)", line)
            if match:
                idx = int(match.group(1)) - 1
                score = float(match.group(2))
                url = match.group(3).strip()
                scored.append((url, score))

        # 4. Sort by score descending and return the top_k URLs
        scored.sort(key=lambda x: x[1], reverse=True)
        return [url for url, _ in scored][:top_k]

    # Implement the assist method as required by the AbstractAgent class
    async def assist(
            self,
            session: Session,
            query: Query,
            response_handler: ResponseHandler
    ):
        """Search the internet for information."""
        # Search for information
        await response_handler.emit_text_block(
            "SEARCH", "Searching internet for results..."
        )

        refinement_prompt = f'''Create a concise web search query for: {query.prompt}. 
        Response must be less than 400 characters.  
        If the prompt asks for links, only return a maxiumum of three links.
        Check to make sure the response has more than 200 characters and does not exceed 400 characters before returning a response.'''

        refined_query = await self._model_provider.query(refinement_prompt)
        # print(f"Refiend query: {len(refined_query)} | ", refined_query)  # <-- Debug printout
        
        while len(refined_query) > 400:
            refinement_prompt = f'''The length of the query is too long. shorten the web search query forcefully under 100 characters (including spaces) for: {refined_query}. 
***Response must be less than 100 characters or less including spaces.***  
If the prompt asks for links, only return a maxiumum of three links.'''  
            refined_query = await self._model_provider.query(refinement_prompt)
            # print(f"Refiend query: {len(refined_query)} | ", refined_query) # <-- Debug printout
            
        search_results = await self._search_provider.search(refined_query)

        print("\n[DEBUG] Raw URLs in search_results['results']:")
        for res in search_results.get("results", []):
            print(res.get("url", "(no url found)"))

        # Filter valid URLs in parallel
        urls_to_check = [res["url"] for res in search_results["results"] if "url" in res]

        print("\n[DEBUG] URLs being passed into _verify_url:")
        for url in urls_to_check:
            print(url)

        async with aiohttp.ClientSession() as session:
            # Run all verifications concurrently
            verification_results = await asyncio.gather(
                *[self._verify_url(session, url) for url in urls_to_check]
            )

        # Create a set of valid URLs for quick filtering
        valid_urls_set = {url for url, is_valid in verification_results if is_valid}

        # Filter only results with verified URLs
        search_results["results"] = [
            res for res in search_results["results"]
            if res.get("url") in valid_urls_set
]

        if len(search_results["results"]) > 0:
            # Use response handler to emit JSON to the client
            await response_handler.emit_json(
                "SOURCES", {"results": search_results["results"]}
            )
        if len(search_results["images"]) > 0:
            # Use response handler to emit JSON to the client
            await response_handler.emit_json(
                "IMAGES", {"images": search_results["images"]}
            )

        # urls = [res["url"] for res in search_results["results"]]

        # Apply the ranking function to pick the best 5 URLs
        # top_urls = await self.rank_urls(self._model_provider, query.prompt, urls, top_k=5)

        # extracted = await self._search_provider.extract(
        #     top_urls
        # )

        # Process search results
        # Use response handler to create a text stream to stream the final 
        # response to the client
        final_response_stream = response_handler.create_text_stream(
            "FINAL_RESPONSE"
            )
        
        # Combine the content snippets for LLM synthesis
        # combined_content = "\n\n".join(
        #     f"Source: {url}\n{content}"
        #     for url, content, images in extracted['results']
        # )

# Feed into the LLM for final answer generation
        synthesis_prompt = (
            f"Using the following content excerpts, answer the user's question:\n\n"
            f"{search_results}\n\nQuestion: {query.prompt}"
        )
        async for chunk in self._model_provider.query_stream(synthesis_prompt):
            await final_response_stream.emit_chunk(chunk)
        # Mark the text stream as complete
        await final_response_stream.complete()
        # Mark the response as complete
        await response_handler.complete()
    

    async def __process_search_results(
            self,
            prompt: str,
            search_results: dict
    ) -> AsyncIterator[str]:
        """Process the search results."""
        process_search_results_query = f"Summarise the provided search results and use them to answer the provided prompt. Only cite and use search results directly relevant to the user's question(s). Prompt: {prompt}. Search results: {search_results}"
        async for chunk in self._model_provider.query_stream(process_search_results_query):
            yield chunk
    
    async def _verify_url(self, session: aiohttp.ClientSession, url: str) -> tuple[str, bool]:
        """Check if URL is reachable and not a soft 404. Returns (url, is_valid)."""
        try:
            # Try HEAD request first
            async with session.head(url, timeout=5) as response:
                if response.status >= 400:
                    print(f"[HEAD FAIL] {url} | Status: {response.status}")
                    return url, False

            # Try GET to detect soft 404s
            async with session.get(url, timeout=5) as response:
                text = await response.text()
                text_lower = text.lower()

                # Soft 404 signals
                not_found_signals = [
                    "404 not found", "error 404", "page not found",
                    "this page was snatched",
                    "we couldn’t find the page", "page is missing", 
                    "404 error", "try another page"
                ]

                # Extra fallback: loose "404" match with context
                # if "404" in text_lower and any(w in text_lower for w in ["page", "error", "not found"]):
                #     print(f"[404] {url}")
                #     return url, False

                if any(signal in text_lower for signal in not_found_signals):
                    print(f"[404] {url}")
                    return url, False

                print(f"[200] {url}")
                return url, True

        except Exception as e:
            print(f"[EXCEPTION] {url} | {e}")
            return url, False


if __name__ == "__main__":
    # Create an instance of a SearchAgent
    agent = SearchAgent(name="Vera")
    # Create a server to handle requests to the agent
    server = DefaultServer(agent)
    # Run the server
    port = int(os.environ.get("PORT", 8080))
    server.run(port = port)