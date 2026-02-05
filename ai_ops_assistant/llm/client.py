"""
LLM Client Abstraction
Supports multiple LLM providers (OpenAI, Gemini, Groq)
"""

import os
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM client that can work with different providers
    """
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            provider: LLM provider ("openai", "gemini", "groq")
            model: Specific model name (uses default if None)
        """
        self.provider = provider.lower()
        self.model = model
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider"""
        try:
            if self.provider == "openai":
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                self._client = OpenAI(api_key=api_key)
                self.model = self.model or "gpt-4o-mini"
                
            elif self.provider == "gemini":
                import google.generativeai as genai
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY not found in environment")
                genai.configure(api_key=api_key)
                self.model = self.model or "gemini-pro"
                self._client = genai.GenerativeModel(self.model)
                
            elif self.provider == "groq":
                from groq import Groq
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise ValueError("GROQ_API_KEY not found in environment")
                self._client = Groq(api_key=api_key)
                self.model = self.model or "llama-3.3-70b-versatile"
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
            logger.info(f"Initialized {self.provider} client with model {self.model}")
            
        except ImportError as e:
            logger.error(f"Failed to import {self.provider} library: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {e}")
            raise
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using the LLM
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
            elif self.provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self._client.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens
                    }
                )
                return response.text
                
            elif self.provider == "groq":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def generate_json(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[Any, Any]:
        """
        Generate and parse JSON response
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature (lower for JSON)
            
        Returns:
            Parsed JSON object
        """
        response = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        # Clean response (remove markdown code blocks if present)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"LLM did not return valid JSON: {e}")
