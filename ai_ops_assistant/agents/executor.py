"""
ExecutorAgent - Executes plan steps by calling appropriate tools
"""

import logging
from typing import Dict, Any, List
from tools import GitHubTool, WeatherTool

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """
    Executes plan steps by mapping tools to functions and calling APIs
    """
    
    def __init__(self, github_tool: GitHubTool, weather_tool: WeatherTool):
        """
        Initialize ExecutorAgent
        
        Args:
            github_tool: Configured GitHub API client
            weather_tool: Configured Weather API client
        """
        self.github = github_tool
        self.weather = weather_tool
        
        # Map tool names to tool instances
        self.tools = {
            "github": self.github,
            "weather": self.weather
        }
        
        # Map actions to methods
        self.action_map = {
            "github": {
                "search_repos": self.github.search_repos,
                "get_repo_info": self.github.get_repo_info
            },
            "weather": {
                "get_weather": self.weather.get_weather,
                "get_forecast": self.weather.get_weather_forecast
            }
        }
        
        logger.info("ExecutorAgent initialized")
    
    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all steps in a plan
        
        Args:
            plan: Structured plan from PlannerAgent
            
        Returns:
            Execution results for all steps
        """
        logger.info(f"Executing plan with {len(plan.get('steps', []))} steps")
        
        results = {
            "steps_executed": 0,
            "steps_failed": 0,
            "results": {}
        }
        
        for i, step in enumerate(plan.get("steps", [])):
            logger.info(f"Executing step {i + 1}: {step.get('tool')}.{step.get('action')}")
            
            try:
                result = self._execute_step(step)
                
                # Store result with descriptive key
                result_key = f"{step['tool']}_{step['action']}"
                if result_key in results["results"]:
                    # Handle multiple calls to same tool/action
                    result_key = f"{result_key}_{i}"
                
                results["results"][result_key] = result
                results["steps_executed"] += 1
                
                # Check if step failed
                if isinstance(result, dict) and result.get("error"):
                    results["steps_failed"] += 1
                    logger.warning(f"Step {i + 1} completed with errors")
                elif isinstance(result, list) and result and result[0].get("error"):
                    results["steps_failed"] += 1
                    logger.warning(f"Step {i + 1} completed with errors")
                else:
                    logger.info(f"Step {i + 1} completed successfully")
                    
            except Exception as e:
                logger.error(f"Step {i + 1} execution failed: {e}")
                results["results"][f"error_step_{i}"] = {
                    "error": True,
                    "message": str(e),
                    "step": step
                }
                results["steps_failed"] += 1
        
        logger.info(f"Plan execution complete: {results['steps_executed']} executed, {results['steps_failed']} failed")
        return results
    
    def _execute_step(self, step: Dict[str, Any]) -> Any:
        """
        Execute a single step
        
        Args:
            step: Step dictionary with tool, action, and params
            
        Returns:
            Result from the tool execution
        """
        tool_name = step.get("tool")
        action_name = step.get("action")
        params = step.get("params", {})
        
        # Validate tool exists
        if tool_name not in self.action_map:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Validate action exists
        if action_name not in self.action_map[tool_name]:
            raise ValueError(f"Unknown action '{action_name}' for tool '{tool_name}'")
        
        # Get the method to call
        method = self.action_map[tool_name][action_name]
        
        # Execute the method with parameters
        try:
            result = method(**params)
            return result
        except TypeError as e:
            logger.error(f"Invalid parameters for {tool_name}.{action_name}: {e}")
            return {
                "error": True,
                "message": f"Invalid parameters: {e}"
            }
    
    def execute_single_step(
        self, 
        tool: str, 
        action: str, 
        params: Dict[str, Any]
    ) -> Any:
        """
        Execute a single step directly (for testing or manual execution)
        
        Args:
            tool: Tool name
            action: Action name
            params: Parameters dictionary
            
        Returns:
            Result from the tool execution
        """
        step = {
            "tool": tool,
            "action": action,
            "params": params
        }
        return self._execute_step(step)
