"""
Configuration settings for the Research Assistant
"""

import os
from pathlib import Path


class Config:
    """Configuration class for the voice agent"""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Ollama/LLM settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    # Whisper settings
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large

    # TTS settings
    TTS_BACKEND = os.getenv("TTS_BACKEND", "system")  # system, pyttsx3, cosyvoice
    COSYVOICE_PATH = os.getenv("COSYVOICE_PATH", "/Users/huiruzhao/github/inference/CosyVoice")
    COSYVOICE_MODEL_DIR = os.getenv(
        "COSYVOICE_MODEL_DIR",
        "/Users/huiruzhao/github/inference/CosyVoice/pretrained_models/CosyVoice-300M-SFT"
    )

    # FastAPI settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Streamlit settings
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_ROTATION = os.getenv("LOG_ROTATION", "1 day")
    LOG_RETENTION = os.getenv("LOG_RETENTION", "7 days")

    # Tool settings
    ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "3"))

    # Notion integration settings
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
    AUTO_SAVE_THRESHOLD = int(os.getenv("AUTO_SAVE_THRESHOLD", "1"))  # Trigger save after each query (1 query = 3 papers)

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.LOGS_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_config_dict(cls) -> dict:
        """Get configuration as dictionary"""
        return {
            "ollama_base_url": cls.OLLAMA_BASE_URL,
            "llm_model": cls.LLM_MODEL,
            "whisper_model": cls.WHISPER_MODEL,
            "tts_backend": cls.TTS_BACKEND,
            "api_host": cls.API_HOST,
            "api_port": cls.API_PORT,
            "arxiv_max_results": cls.ARXIV_MAX_RESULTS,
            "auto_save_threshold": cls.AUTO_SAVE_THRESHOLD,
            "notion_configured": bool(cls.NOTION_TOKEN and cls.NOTION_DATABASE_ID),
        }


# Create necessary directories on import
Config.ensure_directories()


if __name__ == "__main__":
    print("Current Configuration:")
    print("-" * 50)
    for key, value in Config.get_config_dict().items():
        print(f"{key}: {value}")
