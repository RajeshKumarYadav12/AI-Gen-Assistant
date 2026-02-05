"""
AI Operations Assistant - Main Entry Point
Supports both CLI and FastAPI modes
"""

import os
import sys
import json
import logging
import argparse
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import agents and tools
from agents import PlannerAgent, ExecutorAgent, VerifierAgent
from tools import GitHubTool, WeatherTool
from llm import LLMClient


class AIOperationsAssistant:
    """
    Main orchestrator for the AI Operations Assistant
    """
    
    def __init__(
        self, 
        llm_provider: str = "openai",
        llm_model: Optional[str] = None
    ):
        """
        Initialize the AI Operations Assistant
        
        Args:
            llm_provider: LLM provider ("openai", "gemini", "groq")
            llm_model: Specific model name (optional)
        """
        logger.info(f"Initializing AI Operations Assistant with {llm_provider}")
        
        # Initialize LLM client
        self.llm_client = LLMClient(provider=llm_provider, model=llm_model)
        
        # Initialize tools
        self.github_tool = GitHubTool()
        self.weather_tool = WeatherTool()
        
        # Initialize agents
        self.planner = PlannerAgent(self.llm_client)
        self.executor = ExecutorAgent(self.github_tool, self.weather_tool)
        self.verifier = VerifierAgent(self.llm_client)
        
        logger.info("AI Operations Assistant initialized successfully")
    
    def process_request(self, user_input: str) -> dict:
        """
        Process a user request end-to-end
        
        Args:
            user_input: Natural language request from user
            
        Returns:
            Final formatted response
        """
        logger.info(f"Processing request: {user_input}")
        
        try:
            # Step 1: Create plan
            logger.info("Step 1: Planning...")
            plan = self.planner.create_plan(user_input)
            logger.info(f"Plan created: {json.dumps(plan, indent=2)}")
            
            # Step 2: Execute plan
            logger.info("Step 2: Executing...")
            execution_results = self.executor.execute_plan(plan)
            logger.info(f"Execution complete: {execution_results['steps_executed']} steps executed")
            
            # Step 3: Verify and format results
            logger.info("Step 3: Verifying and formatting...")
            final_output = self.verifier.verify_and_format(
                execution_results, 
                original_request=user_input
            )
            logger.info(f"Verification complete: Status = {final_output['status']}")
            
            return final_output
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "results": {},
                "errors": [str(e)],
                "missing_fields": []
            }


def cli_mode():
    """Run in CLI mode"""
    parser = argparse.ArgumentParser(
        description="AI Operations Assistant - Multi-agent system for API orchestration"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language query (e.g., 'Find top Python repos and weather in Delhi')"
    )
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "gemini", "groq"],
        help="LLM provider to use (default: openai)"
    )
    parser.add_argument(
        "--model",
        help="Specific LLM model to use (optional)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Initialize assistant
    try:
        assistant = AIOperationsAssistant(
            llm_provider=args.provider,
            llm_model=args.model
        )
    except Exception as e:
        logger.error(f"Failed to initialize assistant: {e}")
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have set the required API keys in .env file:")
        print("  - OPENAI_API_KEY (for OpenAI)")
        print("  - GEMINI_API_KEY (for Gemini)")
        print("  - GROQ_API_KEY (for Groq)")
        print("  - GITHUB_TOKEN (optional but recommended)")
        print("  - WEATHER_API_KEY (required for weather queries)")
        sys.exit(1)
    
    # Interactive mode
    if args.interactive:
        print("\n🤖 AI Operations Assistant - Interactive Mode")
        print("=" * 60)
        print("Type your queries or 'exit' to quit\n")
        
        while True:
            try:
                query = input("You: ").strip()
                if not query:
                    continue
                if query.lower() in ["exit", "quit", "q"]:
                    print("\nGoodbye! 👋")
                    break
                
                print("\n⚙️  Processing...\n")
                result = assistant.process_request(query)
                print("\n📊 Result:")
                print(json.dumps(result, indent=2))
                print("\n" + "=" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\n❌ Error: {e}\n")
    
    # Single query mode
    elif args.query:
        print(f"\n🤖 Processing query: {args.query}\n")
        result = assistant.process_request(args.query)
        print("\n📊 Result:")
        print(json.dumps(result, indent=2))
    
    # No query provided
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print('  python main.py "Find top 3 Python repos and weather in Bangalore"')
        print('  python main.py --interactive')
        print('  python main.py "Show me popular machine learning repositories" --provider groq')


def api_mode():
    """Run as FastAPI server"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
        from pydantic import BaseModel
        import uvicorn
    except ImportError:
        logger.error("FastAPI not installed. Install with: pip install fastapi uvicorn")
        print("\n❌ Error: FastAPI not installed")
        print("Install with: pip install fastapi uvicorn")
        sys.exit(1)
    
    app = FastAPI(
        title="AI Operations Assistant",
        description="Multi-agent system for API orchestration",
        version="1.0.0"
    )
    
    # Initialize assistant (will be created on first request to allow for different configs)
    assistant = None
    
    class QueryRequest(BaseModel):
        query: str
        provider: str = "openai"
        model: Optional[str] = None
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize assistant on startup"""
        global assistant
        try:
            assistant = AIOperationsAssistant()
            logger.info("FastAPI server started")
        except Exception as e:
            logger.error(f"Failed to initialize assistant: {e}")
    
    @app.get("/")
    async def root():
        """Health check endpoint"""
        return {
            "status": "running",
            "service": "AI Operations Assistant",
            "version": "1.0.0"
        }
    
    @app.post("/query")
    async def process_query(request: QueryRequest):
        """Process a user query"""
        global assistant
        
        try:
            # Reinitialize if provider changed
            if assistant is None or assistant.llm_client.provider != request.provider:
                assistant = AIOperationsAssistant(
                    llm_provider=request.provider,
                    llm_model=request.model
                )
            
            result = assistant.process_request(request.query)
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Detailed health check"""
        return {
            "status": "healthy",
            "llm_provider": assistant.llm_client.provider if assistant else "not initialized",
            "tools": ["github", "weather"]
        }
    
    # Run server
    print("\n🚀 Starting FastAPI server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 Documentation at: http://localhost:8000/docs")
    print("\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Check if running as API server
    if "--api" in sys.argv or os.getenv("RUN_MODE") == "api":
        api_mode()
    else:
        cli_mode()
