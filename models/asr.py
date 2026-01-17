"""
ASR Module: VoiceTranscriber using Whisper
Handles speech-to-text conversion with hardware acceleration support
"""

import os
import warnings
from typing import Optional
from loguru import logger
from utils.logger import log_tool_call
from utils.hardware import get_device

# Suppress FutureWarnings from torch.load
warnings.filterwarnings("ignore", "You are using `torch.load` with `weights_only=False`*", FutureWarning)

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.error("Whisper not available. Install with: pip install openai-whisper")


class VoiceTranscriber:
    """
    Voice transcription service using OpenAI Whisper.
    Handles audio-to-text conversion with hardware acceleration support.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: Optional[str] = None
    ):
        """
        Initialize the voice transcriber.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large, large-v3)
            device: Target device (None=auto-detect, "cuda", "cpu", "mps")
        """
        if not WHISPER_AVAILABLE:
            raise RuntimeError("Whisper not available. Install with: pip install openai-whisper")

        self.model_size = model_size
        self.device = device or get_device()
        self.model = None

        logger.info(f"Initializing VoiceTranscriber: model={model_size}, device={self.device}")
        self._load_model()

    def _load_model(self):
        """Load the Whisper model"""
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"✓ Whisper model loaded: {self.model_size}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    @log_tool_call
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None
    ) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file
            language: Target language (None=auto-detect)
            initial_prompt: Initial prompt to guide transcription (useful for technical jargon)

        Returns:
            Transcribed text
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            result = self.model.transcribe(
                audio_path,
                language=language,
                initial_prompt=initial_prompt,
                fp16=(self.device == "cuda")  # Use FP16 on CUDA for speed
            )

            text = result["text"].strip()
            detected_lang = result.get("language", "unknown")

            logger.info(f"Detected language: {detected_lang}")
            logger.info(f"Transcription: {text[:100]}...")

            return text

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def transcribe_from_bytes(
        self,
        audio_bytes: bytes,
        temp_suffix: str = ".wav"
    ) -> str:
        """
        Transcribe audio from bytes.

        Args:
            audio_bytes: Audio data as bytes
            temp_suffix: Temporary file suffix

        Returns:
            Transcribed text
        """
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=temp_suffix, delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        try:
            text = self.transcribe(temp_path)
            return text
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    # Test the transcriber
    print("VoiceTranscriber Test")
    print("-" * 50)

    transcriber = VoiceTranscriber(model_size="base")
    print(f"Model loaded: {transcriber.model_size}")
    print(f"Device: {transcriber.device}")
    print("\nReady for transcription!")
