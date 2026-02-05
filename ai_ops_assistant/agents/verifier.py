"""
VerifierAgent - Validates execution results and formats output
"""

import logging
from typing import Dict, Any, List
from llm import LLMClient, VERIFIER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class VerifierAgent:
    """
    Validates execution results, checks for missing data, and formats final output
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize VerifierAgent
        
        Args:
            llm_client: Configured LLM client instance
        """
        self.llm = llm_client
        logger.info("VerifierAgent initialized")
    
    def verify_and_format(
        self, 
        execution_results: Dict[str, Any],
        original_request: str = ""
    ) -> Dict[str, Any]:
        """
        Verify execution results and format final output
        
        Args:
            execution_results: Raw results from ExecutorAgent
            original_request: Original user request for context
            
        Returns:
            Validated and formatted response
        """
        logger.info("Verifying and formatting execution results")
        
        # First do basic validation without LLM
        basic_validation = self._basic_validation(execution_results)
        
        # If results are simple and complete, return formatted version
        if basic_validation["status"] == "success":
            logger.info("Results passed basic validation")
            return self._format_results(execution_results, basic_validation)
        
        # For complex cases or missing data, use LLM for validation
        try:
            logger.info("Using LLM for advanced verification")
            llm_validation = self._llm_verification(execution_results, original_request)
            return llm_validation
        except Exception as e:
            logger.error(f"LLM verification failed: {e}, falling back to basic validation")
            return self._format_results(execution_results, basic_validation)
    
    def _basic_validation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform basic validation without LLM
        
        Args:
            results: Execution results
            
        Returns:
            Validation status dictionary
        """
        validation = {
            "status": "success",
            "missing_fields": [],
            "errors": []
        }
        
        steps_executed = results.get("steps_executed", 0)
        steps_failed = results.get("steps_failed", 0)
        
        if steps_failed > 0:
            validation["status"] = "partial"
            validation["errors"].append(f"{steps_failed} step(s) failed")
        
        if steps_executed == 0:
            validation["status"] = "failed"
            validation["errors"].append("No steps executed successfully")
        
        # Check for error indicators in results
        for key, value in results.get("results", {}).items():
            if isinstance(value, dict) and value.get("error"):
                if validation["status"] == "success":
                    validation["status"] = "partial"
                validation["errors"].append(f"{key}: {value.get('message', 'Unknown error')}")
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                if value[0].get("error"):
                    if validation["status"] == "success":
                        validation["status"] = "partial"
                    validation["errors"].append(f"{key}: {value[0].get('description', 'Unknown error')}")
        
        return validation
    
    def _format_results(
        self, 
        execution_results: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format results into final output structure
        
        Args:
            execution_results: Raw execution results
            validation: Validation metadata
            
        Returns:
            Formatted output
        """
        formatted = {
            "status": validation["status"],
            "results": {},
            "missing_fields": validation["missing_fields"],
            "errors": validation["errors"]
        }
        
        raw_results = execution_results.get("results", {})
        
        # Organize results by category
        github_repos = []
        weather_data = {}
        
        for key, value in raw_results.items():
            if "github" in key:
                if isinstance(value, list):
                    github_repos.extend(value)
                elif isinstance(value, dict):
                    github_repos.append(value)
            elif "weather" in key:
                if isinstance(value, dict):
                    weather_data = value
        
        if github_repos:
            formatted["results"]["github_repos"] = github_repos
        
        if weather_data:
            formatted["results"]["weather"] = weather_data
        
        return formatted
    
    def _llm_verification(
        self, 
        execution_results: Dict[str, Any],
        original_request: str
    ) -> Dict[str, Any]:
        """
        Use LLM to verify and format results
        
        Args:
            execution_results: Raw execution results
            original_request: Original user request
            
        Returns:
            LLM-validated and formatted output
        """
        verification_prompt = f"""
        Original user request: {original_request}
        
        Execution results:
        {execution_results}
        
        Analyze these results and provide:
        1. Status (success/partial/failed)
        2. Clean, formatted results organized by category
        3. List of any missing fields or incomplete data
        4. List of any errors encountered
        
        Format the output as valid JSON following the schema in the system prompt.
        """
        
        try:
            verified_output = self.llm.generate_json(
                prompt=verification_prompt,
                system_prompt=VERIFIER_SYSTEM_PROMPT,
                temperature=0.3
            )
            
            # Ensure required fields exist
            if "status" not in verified_output:
                verified_output["status"] = "partial"
            if "results" not in verified_output:
                verified_output["results"] = {}
            
            return verified_output
            
        except Exception as e:
            logger.error(f"LLM verification failed: {e}")
            raise
    
    def retry_failed_steps(
        self, 
        verification_result: Dict[str, Any],
        executor
    ) -> Dict[str, Any]:
        """
        Identify and retry failed steps
        
        Args:
            verification_result: Result from verification
            executor: ExecutorAgent instance to retry steps
            
        Returns:
            Updated verification result after retry
        """
        logger.info("Checking for failed steps to retry")
        
        if verification_result["status"] == "success":
            logger.info("No retry needed - all steps successful")
            return verification_result
        
        # This is a placeholder for retry logic
        # In a production system, you would:
        # 1. Parse which steps failed
        # 2. Re-execute those steps
        # 3. Merge new results
        # 4. Re-verify
        
        logger.info("Retry logic not implemented yet")
        return verification_result
