# core/llm_client.py
"""LLM client for interacting with various language model providers."""

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import requests
from abc import ABC, abstractmethod

from config.settings import Settings


@dataclass
class LLMResponse:
    """Response from LLM service."""
    content: str
    success: bool
    error_message: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    provider: Optional[str] = None


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.extra_config = kwargs
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response from LLM."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.openai.com/v1')
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using OpenAI API."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', 4000),
            'temperature': kwargs.get('temperature', 0.1),
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=kwargs.get('timeout', 60)
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            return LLMResponse(
                content=content,
                success=True,
                usage=data.get('usage'),
                model=self.model,
                provider='openai'
            )
            
        except requests.exceptions.RequestException as e:
            return LLMResponse(
                content="",
                success=False,
                error_message=f"OpenAI API error: {str(e)}",
                provider='openai'
            )
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                provider='openai'
            )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic API provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.anthropic.com')
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Anthropic API."""
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # Convert messages format for Anthropic
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                user_messages.append(msg)
        
        payload = {
            'model': self.model,
            'max_tokens': kwargs.get('max_tokens', 4000),
            'temperature': kwargs.get('temperature', 0.1),
            'messages': user_messages
        }
        
        if system_message:
            payload['system'] = system_message
        
        try:
            response = requests.post(
                f'{self.base_url}/v1/messages',
                headers=headers,
                json=payload,
                timeout=kwargs.get('timeout', 60)
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['content'][0]['text']
            
            return LLMResponse(
                content=content,
                success=True,
                usage=data.get('usage'),
                model=self.model,
                provider='anthropic'
            )
            
        except requests.exceptions.RequestException as e:
            return LLMResponse(
                content="",
                success=False,
                error_message=f"Anthropic API error: {str(e)}",
                provider='anthropic'
            )
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                provider='anthropic'
            )


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://generativelanguage.googleapis.com/v1beta')
        
        # Clean up base_url if it contains model path (common mistake)
        if '/models/' in self.base_url and ':generateContent' in self.base_url:
            print(f"Warning: base_url contains model path, cleaning it up...")
            # Extract just the base API URL
            parts = self.base_url.split('/models/')
            self.base_url = parts[0]
            print(f"Cleaned base_url: {self.base_url}")
        
        # Validate model name
        valid_models = [
             'gemini-2.0-flash'
        ]
        
        if self.model not in valid_models:
            print(f"Warning: Model '{self.model}' may not be valid. Valid models: {valid_models}")
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Gemini API."""
        # Convert messages to Gemini format
        contents = []
        
        for msg in messages:
            if msg['role'] == 'system':
                # Gemini doesn't have system role, prepend to first user message
                if contents and contents[0]['role'] == 'user':
                    contents[0]['parts'][0]['text'] = f"{msg['content']}\n\n{contents[0]['parts'][0]['text']}"
                else:
                    contents.insert(0, {
                        'role': 'user',
                        'parts': [{'text': msg['content']}]
                    })
            elif msg['role'] == 'user':
                contents.append({
                    'role': 'user',
                    'parts': [{'text': msg['content']}]
                })
            elif msg['role'] == 'assistant':
                contents.append({
                    'role': 'model',
                    'parts': [{'text': msg['content']}]
                })
        
        payload = {
            'contents': contents,
            'generationConfig': {
                'maxOutputTokens': kwargs.get('max_tokens', 4000),
                'temperature': kwargs.get('temperature', 0.1),
            }
        }
        
        try:
            # Construct the correct URL
            url = f'{self.base_url}/models/{self.model}:generateContent'
            params = {'key': self.api_key}
            
            response = requests.post(
                url,
                params=params,
                json=payload,
                timeout=kwargs.get('timeout', 60)
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"DEBUG: Response content: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            
            if 'candidates' not in data or not data['candidates']:
                error_msg = "No response generated"
                if 'error' in data:
                    error_msg = f"API Error: {data['error'].get('message', 'Unknown error')}"
                elif 'promptFeedback' in data:
                    # Handle content filtering
                    feedback = data['promptFeedback']
                    if 'blockReason' in feedback:
                        error_msg = f"Content blocked: {feedback['blockReason']}"
                return LLMResponse(
                    content="",
                    success=False,
                    error_message=error_msg,
                    provider='gemini'
                )
            
            content = data['candidates'][0]['content']['parts'][0]['text']
            
            return LLMResponse(
                content=content,
                success=True,
                usage=data.get('usageMetadata'),
                model=self.model,
                provider='gemini'
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Gemini API error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_msg = f"Gemini API error: {error_data['error'].get('message', str(e))}"
                        # Add specific help for common errors
                        if 'API_KEY_INVALID' in error_msg:
                            error_msg += "\nPlease check your API key in the .env file"
                        elif 'not found' in error_msg.lower():
                            error_msg += f"\nModel '{self.model}' may not exist or be available"
                except:
                    pass
            return LLMResponse(
                content="",
                success=False,
                error_message=error_msg,
                provider='gemini'
            )
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                provider='gemini'
            )

class LLMClient:
    """Client for interacting with various LLM providers."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = None
        self._initialize_provider()
    
    def _initialize_provider(self) -> None:
        """Initialize the appropriate LLM provider."""
        provider_name = self.settings.llm.provider.lower()
        api_key = self.settings.llm.api_key
        model = self.settings.llm.model
        
        print(f"DEBUG: Initializing {provider_name} provider")
        print(f"DEBUG: Model: {model}")
        print(f"DEBUG: API Key set: {'Yes' if api_key else 'No'}")
        print(f"DEBUG: Base URL: {self.settings.llm.base_url}")
        
        if not api_key:
            raise ValueError(f"API key not provided for {provider_name}")
        
        # Get additional configuration from environment
        extra_config = {}
        
        if provider_name == 'openai':
            if self.settings.llm.base_url:
                extra_config['base_url'] = self.settings.llm.base_url
            self.provider = OpenAIProvider(api_key, model, **extra_config)
            
        elif provider_name == 'anthropic':
            if self.settings.llm.base_url:
                extra_config['base_url'] = self.settings.llm.base_url
            self.provider = AnthropicProvider(api_key, model, **extra_config)
            
        elif provider_name == 'gemini':
            if self.settings.llm.base_url:
                extra_config['base_url'] = self.settings.llm.base_url
            self.provider = GeminiProvider(api_key, model, **extra_config)
            
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    def generate_response(self, 
                         system_prompt: str, 
                         user_prompt: str, 
                         conversation_history: Optional[List[Dict[str, str]]] = None) -> LLMResponse:
        """Generate response from LLM."""
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user prompt
        messages.append({
            'role': 'user',
            'content': user_prompt
        })
        
        # Generate response with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.provider.generate(
                    messages=messages,
                    max_tokens=self.settings.llm.max_tokens,
                    temperature=self.settings.llm.temperature,
                    timeout=self.settings.llm.timeout
                )
                
                if response.success:
                    return response
                
                # If not successful and not the last attempt, wait and retry
                if attempt < max_retries - 1:
                    print(f"DEBUG: Attempt {attempt + 1} failed: {response.error_message}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                return response
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"DEBUG: Attempt {attempt + 1} failed with exception: {str(e)}. Retrying...")
                    time.sleep(2 ** attempt)
                    continue
                
                return LLMResponse(
                    content="",
                    success=False,
                    error_message=f"Failed after {max_retries} attempts: {str(e)}",
                    provider=self.settings.llm.provider
                )
        
        return LLMResponse(
            content="",
            success=False,
            error_message="Max retries exceeded",
            provider=self.settings.llm.provider
        )
    
    def parse_json_response(self, response: LLMResponse) -> Dict[str, Any]:
        """Parse JSON response from LLM."""
        if not response.success:
            raise ValueError(f"LLM request failed: {response.error_message}")
        
        try:
            # Try to extract JSON from response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            # Parse JSON
            return json.loads(content.strip())
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse content: {response.content}")
    
    def validate_provider_config(self) -> bool:
        """Validate provider configuration."""
        try:
            print("DEBUG: Testing LLM connection...")
            # Test with a simple request
            test_response = self.generate_response(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say 'Hello' if you can understand this message."
            )
            
            print(f"DEBUG: Test response success: {test_response.success}")
            if not test_response.success:
                print(f"DEBUG: Test response error: {test_response.error_message}")
            
            return test_response.success
        except Exception as e:
            print(f"DEBUG: Validation exception: {str(e)}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current provider."""
        return {
            'provider': self.settings.llm.provider,
            'model': self.settings.llm.model,
            'max_tokens': self.settings.llm.max_tokens,
            'temperature': self.settings.llm.temperature,
            'timeout': self.settings.llm.timeout
        }
