"""
CodeXR LangChain Web Search Agent Integration
As specified: "Web Search Agent: Bing/Serper API via LangChain tool wrapper"
"""

import os
from typing import List, Dict, Any, Optional
from langchain_community.utilities import SerpAPIWrapper, BingSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentType, initialize_agent
from langchain.llms import OpenAI
from langchain.tools import Tool
from langchain.schema import Document
import requests
import json
from datetime import datetime

class CodeXRSearchAgent:
    """Web search agent for grounding AR/VR development queries"""
    
    def __init__(self, serp_api_key: Optional[str] = None, bing_api_key: Optional[str] = None):
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        self.bing_api_key = bing_api_key or os.getenv("BING_SEARCH_KEY")
        
        self.search_tools = self._initialize_search_tools()
        
    def _initialize_search_tools(self) -> List[Tool]:
        """Initialize available search tools"""
        tools = []
        
        # SERP API Tool
        if self.serp_api_key:
            serp_wrapper = SerpAPIWrapper(serpapi_api_key=self.serp_api_key)
            serp_tool = Tool(
                name="SERP_Search",
                description="Search for AR/VR development documentation and tutorials using Google Search API",
                func=serp_wrapper.run
            )
            tools.append(serp_tool)
        
        # Bing Search Tool
        if self.bing_api_key:
            bing_wrapper = BingSearchAPIWrapper(bing_subscription_key=self.bing_api_key)
            bing_tool = Tool(
                name="Bing_Search", 
                description="Search for AR/VR development resources using Bing Search API",
                func=bing_wrapper.run
            )
            tools.append(bing_tool)
        
        # DuckDuckGo Fallback (no API key required)
        ddg_search = DuckDuckGoSearchRun()
        ddg_tool = Tool(
            name="DuckDuckGo_Search",
            description="Fallback search for AR/VR development information",
            func=ddg_search.run
        )
        tools.append(ddg_tool)
        
        return tools
    
    def search_ar_vr_docs(self, query: str, category: str) -> List[Dict[str, Any]]:
        """Search for AR/VR development documentation"""
        
        # Enhance query with AR/VR specific terms
        enhanced_queries = self._build_search_queries(query, category)
        
        all_results = []
        
        for search_query in enhanced_queries[:2]:  # Limit to 2 queries to avoid rate limits
            try:
                for tool in self.search_tools:
                    results = tool.func(search_query)
                    parsed_results = self._parse_search_results(results, search_query)
                    all_results.extend(parsed_results)
                    
                    # Break after first successful search to avoid redundancy
                    if parsed_results:
                        break
                        
            except Exception as e:
                print(f"Search tool {tool.name} failed: {e}")
                continue
        
        # Rank and filter results
        return self._rank_and_filter_results(all_results, query, category)
    
    def _build_search_queries(self, query: str, category: str) -> List[str]:
        """Build enhanced search queries for AR/VR documentation"""
        
        base_terms = {
            "Unity": ["Unity3D", "XR Interaction Toolkit", "Unity VR", "Unity AR"],
            "Unreal": ["Unreal Engine", "UE4", "UE5", "Unreal VR", "Unreal AR"],
            "Shader": ["Unity Shader", "HLSL", "Shader Graph", "URP Shader"],
            "General": ["AR development", "VR development", "Mixed Reality"]
        }
        
        doc_sites = [
            "site:docs.unity3d.com",
            "site:docs.unrealengine.com", 
            "site:learn.unity.com",
            "site:developer.oculus.com",
            "site:developers.google.com/ar"
        ]
        
        enhanced_queries = []
        
        # Category-specific enhanced query
        if category in base_terms:
            for term in base_terms[category][:2]:  # Limit terms
                enhanced_queries.append(f"{query} {term} tutorial documentation")
        
        # Official documentation search
        for site in doc_sites[:3]:  # Limit sites
            enhanced_queries.append(f"{query} {site}")
            
        # Fallback general query
        enhanced_queries.append(f"AR VR development {query} official documentation")
        
        return enhanced_queries
    
    def _parse_search_results(self, results: str, query: str) -> List[Dict[str, Any]]:
        """Parse search results into structured format"""
        
        parsed_results = []
        
        try:
            # Handle different result formats from different search engines
            if isinstance(results, str):
                # Simple string results from some tools
                parsed_results.append({
                    "title": f"Search Results for: {query}",
                    "content": results[:500],  # Limit content length
                    "url": "N/A",
                    "source": "Web Search",
                    "timestamp": datetime.now().isoformat()
                })
            elif isinstance(results, list):
                # Structured results from advanced tools
                for result in results[:3]:  # Limit to top 3 results
                    parsed_results.append({
                        "title": result.get("title", "No Title"),
                        "content": result.get("snippet", result.get("content", ""))[:500],
                        "url": result.get("url", result.get("link", "N/A")),
                        "source": "Web Search",
                        "timestamp": datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"Error parsing search results: {e}")
            
        return parsed_results
    
    def _rank_and_filter_results(self, results: List[Dict[str, Any]], query: str, category: str) -> List[Dict[str, Any]]:
        """Rank and filter results by relevance"""
        
        # Priority keywords for different categories
        priority_domains = {
            "Unity": ["docs.unity3d.com", "learn.unity.com"],
            "Unreal": ["docs.unrealengine.com", "unrealengine.com"],
            "Shader": ["docs.unity3d.com", "catlikecoding.com"],
            "General": ["developer.oculus.com", "developers.google.com"]
        }
        
        scored_results = []
        
        for result in results:
            score = 0
            url = result.get("url", "").lower()
            content = result.get("content", "").lower()
            
            # Boost official documentation
            if category in priority_domains:
                for domain in priority_domains[category]:
                    if domain in url:
                        score += 10
            
            # Boost results with query terms in content
            query_words = query.lower().split()
            score += sum(1 for word in query_words if word in content)
            
            # Boost results with AR/VR terms
            ar_vr_terms = ["ar", "vr", "virtual reality", "augmented reality", "mixed reality"]
            score += sum(2 for term in ar_vr_terms if term in content)
            
            result["relevance_score"] = score
            scored_results.append(result)
        
        # Sort by score and return top results
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_results[:5]  # Return top 5 results
    
    def search_for_best_practices(self, category: str, topic: str) -> List[str]:
        """Search specifically for best practices"""
        
        query = f"{category} {topic} best practices guidelines recommendations"
        results = self.search_ar_vr_docs(query, category)
        
        best_practices = []
        for result in results[:3]:  # Top 3 results
            content = result.get("content", "")
            # Extract sentences that look like best practices
            sentences = content.split(".")
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in ["should", "must", "best", "recommended", "always", "never"]):
                    best_practices.append(sentence.strip())
                    if len(best_practices) >= 6:  # Limit best practices
                        break
            if len(best_practices) >= 6:
                break
                
        return best_practices[:6]
    
    def search_for_gotchas(self, category: str, topic: str) -> List[str]:
        """Search specifically for common problems and gotchas"""
        
        query = f"{category} {topic} common problems issues gotchas pitfalls mistakes"
        results = self.search_ar_vr_docs(query, category)
        
        gotchas = []
        for result in results[:3]:
            content = result.get("content", "")
            sentences = content.split(".")
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in ["error", "problem", "issue", "avoid", "careful", "watch out", "common mistake"]):
                    gotchas.append(sentence.strip())
                    if len(gotchas) >= 5:
                        break
            if len(gotchas) >= 5:
                break
                
        return gotchas[:5]
    
    def get_official_documentation_links(self, query: str, category: str) -> List[str]:
        """Get official documentation links for the query"""
        
        # Official documentation bases
        official_docs = {
            "Unity": [
                "https://docs.unity3d.com/Manual/",
                "https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.5/manual/",
                "https://learn.unity.com/"
            ],
            "Unreal": [
                "https://docs.unrealengine.com/5.0/en-us/",
                "https://docs.unrealengine.com/5.0/en-us/vr-development-in-unreal-engine/",
                "https://docs.unrealengine.com/5.0/en-us/multiplayer-programming-quick-start-for-unreal-engine/"
            ],
            "Shader": [
                "https://docs.unity3d.com/Manual/SL-Reference.html",
                "https://docs.unity3d.com/Manual/shader-tutorials.html"
            ],
            "General": [
                "https://developers.google.com/ar/",
                "https://developer.oculus.com/documentation/"
            ]
        }
        
        # Return category-specific links
        if category in official_docs:
            return official_docs[category]
        else:
            return official_docs["General"]

# Integration helper functions
def create_search_agent(serp_key: Optional[str] = None, bing_key: Optional[str] = None) -> CodeXRSearchAgent:
    """Factory function to create search agent"""
    return CodeXRSearchAgent(serp_key, bing_key)

def search_and_ground_query(query: str, category: str, agent: CodeXRSearchAgent) -> Dict[str, Any]:
    """Complete search and grounding pipeline"""
    
    # Main documentation search
    doc_results = agent.search_ar_vr_docs(query, category)
    
    # Best practices search
    best_practices = agent.search_for_best_practices(category, query)
    
    # Gotchas search
    gotchas = agent.search_for_gotchas(category, query)
    
    # Official documentation links
    doc_links = agent.get_official_documentation_links(query, category)
    
    return {
        "search_results": doc_results,
        "best_practices": best_practices,
        "gotchas": gotchas,
        "documentation_links": doc_links,
        "grounding_confidence": len(doc_results) / 5.0  # Confidence score
    }

# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = create_search_agent()
    
    # Test search
    results = search_and_ground_query(
        "How do I add teleport locomotion in Unity VR?", 
        "Unity", 
        agent
    )
    
    print("Search Results:", json.dumps(results, indent=2))

