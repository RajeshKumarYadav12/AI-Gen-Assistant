"""
PlannerAgent - Converts user input into structured JSON plans
"""

import logging
from typing import Dict, Any
from llm import LLMClient, PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    Converts natural language user requests into structured execution plans
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize PlannerAgent
        
        Args:
            llm_client: Configured LLM client instance
        """
        self.llm = llm_client
        logger.info("PlannerAgent initialized")
    
    def create_plan(self, user_input: str) -> Dict[str, Any]:
        """
        Convert user input into a structured JSON plan
        
        Args:
            user_input: Natural language request from user
            
        Returns:
            JSON plan with steps for execution
            
        Example output:
            {
                "steps": [
                    {
                        "tool": "github",
                        "action": "search_repos",
                        "params": {"query": "python", "limit": 3}
                    },
                    {
                        "tool": "weather",
                        "action": "get_weather",
                        "params": {"city": "Bangalore"}
                    }
                ]
            }
        """
        logger.info(f"Creating plan for: {user_input}")
        
        try:
            # Generate structured plan using LLM
            plan = self.llm.generate_json(
                prompt=f"User request: {user_input}",
                system_prompt=PLANNER_SYSTEM_PROMPT,
                temperature=0.3  # Lower temperature for structured output
            )
            
            # Validate plan structure
            if not self._validate_plan(plan):
                logger.error("Generated plan failed validation")
                raise ValueError("Invalid plan structure generated")
            
            logger.info(f"Plan created with {len(plan.get('steps', []))} steps")
            return plan
            
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            raise
    
    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Validate that plan has correct structure
        
        Args:
            plan: Generated plan to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(plan, dict):
            logger.error("Plan is not a dictionary")
            return False
        
        if "steps" not in plan:
            logger.error("Plan missing 'steps' key")
            return False
        
        if not isinstance(plan["steps"], list):
            logger.error("Plan 'steps' is not a list")
            return False
        
        for i, step in enumerate(plan["steps"]):
            if not isinstance(step, dict):
                logger.error(f"Step {i} is not a dictionary")
                return False
            
            required_keys = ["tool", "action", "params"]
            for key in required_keys:
                if key not in step:
                    logger.error(f"Step {i} missing required key: {key}")
                    return False
            
            # Validate tool names
            valid_tools = ["github", "weather"]
            if step["tool"] not in valid_tools:
                logger.error(f"Step {i} has invalid tool: {step['tool']}")
                return False
        
        return True
    
    def refine_plan(self, plan: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Refine an existing plan based on feedback
        
        Args:
            plan: Original plan
            feedback: Feedback or errors from execution
            
        Returns:
            Refined plan
        """
        logger.info("Refining plan based on feedback")
        
        refinement_prompt = f"""
        Original plan:
        {plan}
        
        Execution feedback:
        {feedback}
        
        Generate an improved plan that addresses the issues.
        """
        
        try:
            refined_plan = self.llm.generate_json(
                prompt=refinement_prompt,
                system_prompt=PLANNER_SYSTEM_PROMPT,
                temperature=0.3
            )
            
            if self._validate_plan(refined_plan):
                logger.info("Plan refined successfully")
                return refined_plan
            else:
                logger.warning("Refined plan validation failed, returning original")
                return plan
                
        except Exception as e:
            logger.error(f"Plan refinement failed: {e}")
            return plan
