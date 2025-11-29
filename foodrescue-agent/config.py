import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import logging
import time
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    """
    Robust configuration manager with validation and fallbacks.
    All methods include error handling and return reliable defaults.
    """
    
    def __init__(self):
        """Initialize configuration with comprehensive validation"""
        # Load .env explicitly from project root (same folder as this file)
        env_path = Path(__file__).parent.joinpath('.env')
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            logger.info(f"Loaded .env from {env_path}")
        else:
            # fall back to system environment
            load_dotenv()

        self.gemini_key = self._validate_gemini_key()
        self.gemini_ready = False
        self.model: Optional[genai.GenerativeModel] = None
        self.last_error = None
        self._configured = False

        # Configure API client with the key if present, but avoid instantiating
        # the heavy model until it's actually needed (lazy init).
        try:
            if self.gemini_key:
                genai.configure(api_key=self.gemini_key)
                self._configured = True
                logger.info("Gemini API client configured (lazy model init)")
        except Exception as e:
            logger.error(f"Failed to configure Gemini client: {e}")
            self.last_error = str(e)
    
    def _validate_gemini_key(self):
        """Validate Gemini API key with comprehensive checks"""
        key = os.getenv('GEMINI_API_KEY', '').strip()
        
        if not key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return None
        
        if len(key) < 30:
            logger.warning("GEMINI_API_KEY appears to be invalid (too short)")
            return None
        
        # Test if key contains obvious placeholder text
        if 'your_' in key.lower() or 'example' in key.lower():
            logger.warning("GEMINI_API_KEY contains placeholder text")
            return None
        
        logger.info("GEMINI_API_KEY validated successfully")
        return key
    
    def _setup_gemini(self):
        """Backward-compatible shim to initialize the model.

        Calls `ensure_model` which will attempt lazy initialization with retries.
        """
        return self.ensure_model()

    def ensure_model(self, max_attempts: int = 3, backoff_base: float = 0.8) -> bool:
        """Ensure the Gemini `GenerativeModel` is instantiated.

        Performs limited retries with exponential backoff and stores non-sensitive
        error messages in `self.last_error` for diagnostics.
        """
        if self.model is not None and self.gemini_ready:
            return True

        if not self.gemini_key:
            self.last_error = "No GEMINI_API_KEY present"
            logger.warning("ensure_model: no GEMINI_API_KEY present")
            self.gemini_ready = False
            return False

        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 512,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]

        attempt = 0
        while attempt < max_attempts:
            try:
                attempt += 1
                logger.info(f"Attempting Gemini model init (attempt {attempt})")
                self.model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                self.gemini_ready = True
                self.last_error = None
                logger.info("Gemini model instantiated successfully")
                return True
            except Exception as e:
                self.last_error = str(e)
                self.gemini_ready = False
                # Treat failures as warnings — Gemini is optional and we have deterministic fallbacks
                logger.warning(f"Gemini model init attempt {attempt} failed: {e}")
                time.sleep(backoff_base * (2 ** (attempt - 1)))

        logger.warning("All Gemini model initialization attempts failed")
        return False
    
    def get_fallback_report(self, total_weight, total_meals, store_count):
        """Generate fallback impact report when Gemini is unavailable"""
        return f"🍎 {total_weight:.1f} lbs rescued today, providing {total_meals:.0f} meals to {store_count} communities!"

    def generate_impact_report(self, total_weight, total_meals, store_count):
        """
        Generate impact report with comprehensive fallbacks.
        Returns reliable report even when Gemini is unavailable.
        """
        # Build the prompt used for generating the impact report
        prompt = f"""
You are an impact reporter for a food rescue organization. Create a warm, inspiring 1-2 sentence impact statement:

**Today's Numbers:**
- Total food rescued: {total_weight:.1f} pounds
- Estimated meals provided: {int(total_meals)}
- Number of stores participating: {store_count}

**Guidelines:**
- Start with one of these emojis: 🌱, 🍎, 🤝, or 💙
- Keep it under 100 characters total
- Sound human, warm, and community-focused
- Focus on real impact: meals provided, families fed
- NO technical terms, AI jargon, or robotic language
- NO mention of AI, algorithms, or systems
- ALWAYS sound like a human writing for their community

"""

        try:
            # Ensure model is available (lazy init)
            if not self.ensure_model():
                logger.warning("Using fallback impact report - Gemini not available after ensure_model")
                return self.get_fallback_report(total_weight, total_meals, store_count)

            # Try generation with retries/backoff
            attempts = 3
            backoff = 0.8
            response_text = None
            for attempt in range(1, attempts + 1):
                try:
                    resp = self.model.generate_content(prompt)
                    text = getattr(resp, 'text', None) or getattr(resp, 'result', None)
                    if text and isinstance(text, str):
                        response_text = text.strip()
                        break
                    else:
                        logger.warning(f"Gemini returned empty or unexpected response on attempt {attempt}")
                except Exception as e:
                    self.last_error = str(e)
                    # Log as warning; generation failures will fallback to deterministic text
                    logger.warning(f"Gemini generation attempt {attempt} failed: {e}")
                    time.sleep(backoff * (2 ** (attempt - 1)))

            if not response_text:
                logger.warning("All Gemini generation attempts failed or returned empty. Using fallback report.")
                return self.get_fallback_report(total_weight, total_meals, store_count)

            report = response_text

            # Validate and normalize report
            if len(report) < 10 or len(report) > 200:
                logger.warning(f"Generated report length ({len(report)}) outside expected range")
                return self.get_fallback_report(total_weight, total_meals, store_count)

            if not report.startswith(('🌱', '🍎', '🤝', '💙', '✨', '🌍', '🏆')):
                report = '🌱 ' + report

            logger.info(f"Successfully generated impact report: {report}")
            return report

        except Exception as e:
            # Non-fatal: fallback will produce a reliable report
            logger.warning(f"Impact report generation failed (final): {str(e)}")
            return self.get_fallback_report(total_weight, total_meals, store_count)
