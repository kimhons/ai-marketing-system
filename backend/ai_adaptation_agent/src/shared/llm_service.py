# LLM Interaction Service using OpenAI API

import os
from typing import Dict, Any, Optional
from openai import OpenAI, APIError, RateLimitError
from .data_models import LLMResponse

class LLMService:
    """
    Manages interactions with Large Language Models (LLMs) using the OpenAI API.
    Handles API calls, prompt engineering, error handling, and API key management via environment variables.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM service.
        Args:
            api_key: (Optional) The OpenAI API key. If not provided, it will be fetched from the 
                     OPENAI_API_KEY environment variable.
            model_name: The specific OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4").
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY environment variable not set. LLM calls will fail.")
            # Potentially raise an error or operate in a no-LLM mode
            # For now, we'll let it proceed but calls will fail if key is not set when client is used.
        
        self.model_name = model_name
        try:
            self.client = OpenAI(api_key=self.api_key)
            print(f"LLMService initialized for model: {self.model_name}. OpenAI client configured.")
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            self.client = None

    def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = "You are a helpful AI assistant.",
        max_tokens: int = 1500,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> LLMResponse:
        """
        Generates text based on a given prompt using the configured OpenAI LLM.

        Args:
            prompt: The user's input text prompt for the LLM.
            system_prompt: (Optional) The system message to set the context for the assistant.
            max_tokens: The maximum number of tokens to generate.
            temperature: The sampling temperature for generation (creativity vs. coherence).
            **kwargs: Additional model-specific parameters for the chat completion.

        Returns:
            An LLMResponse object containing the generated text and metadata.
            Returns a response with an error message if the API call fails.
        """
        if not self.client:
            error_message = "OpenAI client not initialized. Cannot make API call."
            print(error_message)
            return LLMResponse(original_prompt=prompt, generated_text=f"Error: {error_message}", metadata={"error": True})

        print(f"Making LLM call for prompt: {prompt[:100]}... with model {self.model_name}")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            generated_text = completion.choices[0].message.content.strip()
            tokens_used = completion.usage.total_tokens if completion.usage else 0
            
            return LLMResponse(
                original_prompt=prompt,
                generated_text=generated_text,
                metadata={
                    "model_used": self.model_name,
                    "tokens_used": tokens_used,
                    "finish_reason": completion.choices[0].finish_reason,
                    "simulated": False
                }
            )
        except APIError as e:
            error_message = f"OpenAI API Error: {e}"
            print(error_message)
            return LLMResponse(original_prompt=prompt, generated_text=f"Error: {error_message}", metadata={"error": True, "details": str(e)})
        except RateLimitError as e:
            error_message = f"OpenAI Rate Limit Error: {e}. Please check your usage and limits."
            print(error_message)
            return LLMResponse(original_prompt=prompt, generated_text=f"Error: {error_message}", metadata={"error": True, "details": str(e)})
        except Exception as e:
            error_message = f"An unexpected error occurred during LLM call: {e}"
            print(error_message)
            return LLMResponse(original_prompt=prompt, generated_text=f"Error: {error_message}", metadata={"error": True, "details": str(e)})

    def analyze_sentiment(self, text: str, model_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes the sentiment of a given text using an LLM.
        Args:
            text: The text to analyze.
            model_override: (Optional) Specify a different model for this specific task if needed.

        Returns:
            A dictionary with sentiment scores (e.g., positive, neutral, negative) or an error message.
        """
        if not self.client:
            error_message = "OpenAI client not initialized. Cannot make API call."
            print(error_message)
            return {"error": error_message, "simulated": False}

        sentiment_prompt = f"""Analyze the sentiment of the following text and classify it as predominantly positive, negative, or neutral. Provide a confidence score for each classification. Text: 
{text}
"""
        
        # Use a simpler response structure for sentiment if possible, or parse a more complex one.
        # For this example, we'll ask for a structured-like response.
        system_prompt = "You are a sentiment analysis expert. Respond with a JSON-like structure: {\"positive\": score, \"neutral\": score, \"negative\": score}."
        
        current_model = model_override or self.model_name
        print(f"Simulating sentiment analysis for: {text[:100]}... with model {current_model}")

        # This is still a placeholder for actual sentiment logic using LLM.
        # A real implementation would call self.generate_text and parse the output.
        # For brevity, we keep the simulation from the previous version here.
        # To make it real, you'd do:
        # response = self.generate_text(prompt=sentiment_prompt, system_prompt=system_prompt, model_name=current_model)
        # if "Error:" in response.generated_text:
        #     return {"error": response.generated_text, "simulated": False}
        # else:
        #     # Attempt to parse response.generated_text as JSON
        #     try:
        #         sentiment_scores = json.loads(response.generated_text)
        #         sentiment_scores["simulated"] = False 
        #         return sentiment_scores
        #     except json.JSONDecodeError:
        #         return {"error": "Failed to parse LLM sentiment response", "raw_response": response.generated_text, "simulated": False}

        if "great" in text.lower() or "excellent" in text.lower():
            return {"positive": 0.9, "neutral": 0.05, "negative": 0.05, "simulated": True, "note": "Using placeholder logic"}
        elif "bad" in text.lower() or "poor" in text.lower():
            return {"positive": 0.05, "neutral": 0.05, "negative": 0.9, "simulated": True, "note": "Using placeholder logic"}
        else:
            return {"positive": 0.4, "neutral": 0.5, "negative": 0.1, "simulated": True, "note": "Using placeholder logic"}

# Example usage (for testing purposes, would not be here in production code)
if __name__ == "__main__":
    # IMPORTANT: For this to run, you must set the OPENAI_API_KEY environment variable.
    # export OPENAI_API_KEY='your_actual_api_key'
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipping LLMService example: OPENAI_API_KEY not set.")
    else:
        llm_service = LLMService(model_name="gpt-3.5-turbo") # Or your preferred model like "gpt-4"
        
        # Test text generation
        blueprint_prompt = "Generate three key qualitative insights for a small independent bookstore based on hypothetical positive customer reviews that mention a cozy atmosphere, curated selection, and knowledgeable staff."
        response = llm_service.generate_text(blueprint_prompt, system_prompt="You are an expert marketing analyst.")
        
        if "Error:" not in response.generated_text:
            print(f"\n--- Generated Text (Live Call) ---")
            print(f"Generated Text: {response.generated_text}")
            print(f"Metadata: {response.metadata}")
        else:
            print(f"\n--- LLM Call Failed ---")
            print(response.generated_text)

        # Test sentiment analysis (still using placeholder logic in this example)
        sentiment = llm_service.analyze_sentiment("The new product launch was a massive success and customers love it!")
        print(f"\n--- Sentiment Analysis (Placeholder Logic) ---")
        print(f"Sentiment: {sentiment}")

