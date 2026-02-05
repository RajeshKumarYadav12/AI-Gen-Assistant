"""
GitHub API Tool
Provides access to GitHub repository search and information
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional
from time import sleep

logger = logging.getLogger(__name__)


class GitHubTool:
    """
    Wrapper for GitHub REST API
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client
        
        Args:
            token: GitHub personal access token (optional but recommended)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            logger.info("GitHub API initialized with authentication")
        else:
            logger.warning("GitHub API initialized without token (rate limits apply)")
    
    def search_repos(
        self, 
        query: str, 
        limit: int = 5,
        sort: str = "stars",
        order: str = "desc",
        retry_count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search GitHub repositories
        
        Args:
            query: Search query (e.g., "python", "machine learning")
            limit: Maximum number of results to return
            sort: Sort by "stars", "forks", or "updated"
            order: "asc" or "desc"
            retry_count: Number of retries on failure
            
        Returns:
            List of repository dictionaries with name, stars, description, url
        """
        url = f"{self.BASE_URL}/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(limit, 100)
        }
        
        for attempt in range(retry_count):
            try:
                logger.info(f"Searching GitHub repos: query='{query}', limit={limit}")
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    repos = []
                    
                    for item in data.get("items", [])[:limit]:
                        repo = {
                            "name": item.get("full_name"),
                            "stars": item.get("stargazers_count", 0),
                            "description": item.get("description", "No description"),
                            "url": item.get("html_url"),
                            "language": item.get("language", "Unknown"),
                            "forks": item.get("forks_count", 0)
                        }
                        repos.append(repo)
                    
                    logger.info(f"Found {len(repos)} repositories")
                    return repos
                    
                elif response.status_code == 403:
                    # Rate limit exceeded
                    logger.warning("GitHub API rate limit exceeded")
                    if attempt < retry_count - 1:
                        sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return self._fallback_response(f"Rate limit exceeded: {response.text}")
                    
                else:
                    logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                    if attempt < retry_count - 1:
                        sleep(1)
                        continue
                    return self._fallback_response(f"API error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"GitHub API timeout (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    sleep(1)
                    continue
                return self._fallback_response("Request timeout")
                
            except Exception as e:
                logger.error(f"GitHub API request failed: {e}")
                if attempt < retry_count - 1:
                    sleep(1)
                    continue
                return self._fallback_response(str(e))
        
        return self._fallback_response("Max retries exceeded")
    
    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information dictionary
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("full_name"),
                    "stars": data.get("stargazers_count", 0),
                    "description": data.get("description", "No description"),
                    "url": data.get("html_url"),
                    "language": data.get("language", "Unknown"),
                    "forks": data.get("forks_count", 0),
                    "open_issues": data.get("open_issues_count", 0),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at")
                }
            else:
                logger.error(f"Failed to get repo info: {response.status_code}")
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Failed to get repo info: {e}")
            return {"error": str(e)}
    
    def _fallback_response(self, error_msg: str) -> List[Dict[str, Any]]:
        """Return partial/error response"""
        return [{
            "name": "Error",
            "stars": 0,
            "description": f"Failed to fetch data: {error_msg}",
            "url": "",
            "error": True
        }]
