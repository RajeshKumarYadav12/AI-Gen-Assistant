AI Operations Assistant


A production-ready multi-agent AI system that plans, executes, and verifies real API calls using LLM-powered agents.
Designed to demonstrate agent orchestration, API integrations, and clean backend architecture.


🚀 Quick Start
# 1. Go to project
cd ai_ops_assistant


# 2. Install dependencies
pip install -r requirements.txt


# 3. Configure environment
cp .env.example .env
# Add: GROQ_API_KEY, WEATHER_API_KEY (GitHub token optional)


# 4. Run CLI
python main.py "Find top 3 Python repos and weather in Bangalore" --provider groq


# OR start API server
python main.py --api
# Visit: http://localhost:8000/docs


🎯 Overview

This project showcases a multi-agent AI Operations system where:

PlannerAgent → Converts user query into a structured JSON plan

ExecutorAgent → Executes real API calls (GitHub, Weather)

VerifierAgent → Validates results and formats final output

The system supports CLI and API modes, multiple LLM providers, and production-grade error handling.


✨ Key Features

Multi-agent architecture (Planner / Executor / Verifier)

Real API integrations (GitHub + OpenWeatherMap)

Supports Groq, OpenAI, Gemini

Retry logic with exponential backoff

CLI + FastAPI server

Structured JSON outputs

Environment-based configuration

Clean, extensible architecture


🏗️ Architecture Flow
User Query
   ↓
PlannerAgent (LLM → JSON Plan)
   ↓
ExecutorAgent (API Calls + Retries)
   ↓
VerifierAgent (Validation + Formatting)
   ↓
Final Structured Response

📁 Project Structure
ai_ops_assistant/
├── agents/
│   ├── planner.py
│   ├── executor.py
│   └── verifier.py
├── tools/
│   ├── github_tool.py
│   └── weather_tool.py
├── llm/
│   ├── client.py
│   └── prompts.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md


🔑 Environment Variables
# LLM (choose one)
GROQ_API_KEY=...
OPENAI_API_KEY=...
GEMINI_API_KEY=...


# Required
WEATHER_API_KEY=...


# Optional (rate limits)
GITHUB_TOKEN=...


🔐 API Key Sources

Groq: https://console.groq.com/keys

OpenWeatherMap: https://openweathermap.org/api

GitHub Token: https://github.com/settings/tokens

OpenAI: https://platform.openai.com/api-keys

Gemini: https://makersuite.google.com/app/apikey


💻 Running the Project
CLI Mode
python main.py "Find top 3 Python repos and weather in Bangalore" --provider groq
python main.py "Weather in Delhi" --provider groq
python main.py --interactive --provider groq
API Mode (FastAPI)
python main.py --api

Endpoints:

GET / → Health check

POST /query → Submit query

GET /health → Service status

GET /docs → Swagger UI


📊 Example Output
{
  "status": "success",
  "results": {
    "github_repos": [
      {
        "name": "vinta/awesome-python",
        "stars": 281540,
        "language": "Python"
      }
    ],
    "weather": {
      "city": "Bengaluru",
      "temperature": 23.7,
      "condition": "Clouds",
      "units": "°C"
    }
  },
  "errors": []
}


🧠 Design Decisions

Agent separation → clear responsibility boundaries

Structured JSON plans → safe, auditable execution

LLM abstraction → switch providers easily

Retry & fallback logic → resilient API calls

Single codebase → CLI + API from same logic


🧪 Testing
python main.py "Find Python repos" --provider groq
python main.py "Weather in Tokyo" --provider groq
python main.py --api


🐛 Common Issues

API key not found

Ensure .env exists

Verify key activation (Weather API may take 2–4 hours)

GitHub rate limit

Add GITHUB_TOKEN

Invalid JSON from LLM

Use --provider groq

Ensure stable internet


🔮 Future Improvements

Parallel API execution

Response caching

Async support

More tools (DB, Email, Slack)

Cost tracking

Circuit breakers


📄 License

MIT License

Built with ❤️ using Python, FastAPI, Groq/OpenAI/Gemini, and real-world backend practices
