"""
TTS Module: VoiceSynthesizer using CosyVoice or fallback TTS
Handles text-to-speech conversion with voice cloning support
"""

import os
import sys
import subprocess
from typing import Optional
from loguru import logger
from utils.logger import log_tool_call
from utils.hardware import get_device

# Try to import pyttsx3 as fallback
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available")

# Try to import CosyVoice
try:
    import torch
    COSYVOICE_PATH = os.getenv("COSYVOICE_PATH", "/Users/huiruzhao/github/inference/CosyVoice")
    if os.path.exists(COSYVOICE_PATH) and COSYVOICE_PATH not in sys.path:
        sys.path.insert(0, COSYVOICE_PATH)

    from cosyvoice.cli.cosyvoice import CosyVoice as CosyVoiceModel
    COSYVOICE_AVAILABLE = True
    logger.info(f"CosyVoice available at: {COSYVOICE_PATH}")
except ImportError as e:
    COSYVOICE_AVAILABLE = False
    logger.warning(f"CosyVoice not available: {e}")


class VoiceSynthesizer:
    """
    Text-to-speech service with multiple backends:
    - system: macOS 'say' command or platform-specific TTS
    - pyttsx3: Cross-platform TTS library
    - cosyvoice: Advanced voice cloning (GPU recommended)
    """

    def __init__(
        self,
        backend: str = "system",
        model_dir: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Initialize the voice synthesizer.

        Args:
            backend: TTS backend ("system", "pyttsx3", "cosyvoice")
            model_dir: Path to CosyVoice model directory (for cosyvoice backend)
            device: Target device (None=auto-detect)
        """
        self.backend = backend
        self.device = device or get_device()
        self.model = None
        self.engine = None

        logger.info(f"Initializing VoiceSynthesizer: backend={backend}, device={self.device}")
        self._initialize_backend(model_dir)

    def _initialize_backend(self, model_dir: Optional[str] = None):
        """Initialize the selected TTS backend"""
        if self.backend == "cosyvoice":
            if not COSYVOICE_AVAILABLE:
                logger.warning("CosyVoice not available, falling back to system TTS")
                self.backend = "system"
            else:
                self._load_cosyvoice(model_dir)

        elif self.backend == "pyttsx3":
            if not PYTTSX3_AVAILABLE:
                logger.warning("pyttsx3 not available, falling back to system TTS")
                self.backend = "system"
            else:
                self._load_pyttsx3()

        if self.backend == "system":
            logger.info("Using system TTS (macOS 'say' command)")

    def _load_cosyvoice(self, model_dir: Optional[str] = None):
        """Load CosyVoice model"""
        try:
            if model_dir is None:
                model_dir = os.getenv(
                    "COSYVOICE_MODEL_DIR",
                    "/Users/huiruzhao/github/inference/CosyVoice/pretrained_models/CosyVoice-300M-SFT"
                )

            self.model = CosyVoiceModel(model_dir)
            logger.info(f"✓ CosyVoice model loaded from: {model_dir}")
        except Exception as e:
            logger.error(f"Failed to load CosyVoice: {e}")
            logger.warning("Falling back to system TTS")
            self.backend = "system"

    def _load_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            # Configure voice properties
            self.engine.setProperty('rate', 175)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            logger.info("✓ pyttsx3 engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            self.backend = "system"

    @log_tool_call
    def speak(self, text: str) -> bool:
        """
        Speak text using the selected backend.

        Args:
            text: Text to speak

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.backend == "cosyvoice":
                return self._speak_cosyvoice(text)
            elif self.backend == "pyttsx3":
                return self._speak_pyttsx3(text)
            else:
                return self._speak_system(text)
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return False

    def _speak_system(self, text: str) -> bool:
        """Speak using system TTS (macOS 'say' command)"""
        try:
            subprocess.run(["say", text], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"System TTS failed: {e}")
            return False

    def _speak_pyttsx3(self, text: str) -> bool:
        """Speak using pyttsx3"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"pyttsx3 TTS failed: {e}")
            return False

    def _speak_cosyvoice(self, text: str, reference_audio: Optional[str] = None) -> bool:
        """Speak using CosyVoice (placeholder - needs audio output implementation)"""
        logger.warning("CosyVoice speak() not fully implemented - use synthesize_to_file()")
        return False

    @log_tool_call
    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        reference_audio: Optional[str] = None
    ) -> bool:
        """
        Synthesize text to audio file.

        Args:
            text: Text to synthesize
            output_path: Output audio file path
            reference_audio: Reference audio for voice cloning (CosyVoice only)

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.backend == "system":
                return self._synthesize_system(text, output_path)
            elif self.backend == "pyttsx3":
                return self._synthesize_pyttsx3(text, output_path)
            elif self.backend == "cosyvoice":
                return self._synthesize_cosyvoice(text, output_path, reference_audio)
            else:
                return False
        except Exception as e:
            logger.error(f"Synthesis to file failed: {e}")
            return False

    def _synthesize_system(self, text: str, output_path: str) -> bool:
        """Synthesize using system TTS"""
        try:
            subprocess.run(["say", "-o", output_path, text], check=True)
            return os.path.exists(output_path)
        except Exception as e:
            logger.error(f"System synthesis failed: {e}")
            return False

    def _synthesize_pyttsx3(self, text: str, output_path: str) -> bool:
        """Synthesize using pyttsx3"""
        try:
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            return os.path.exists(output_path)
        except Exception as e:
            logger.error(f"pyttsx3 synthesis failed: {e}")
            return False

    def _synthesize_cosyvoice(
        self,
        text: str,
        output_path: str,
        reference_audio: Optional[str] = None
    ) -> bool:
        """Synthesize using CosyVoice"""
        # CosyVoice implementation would go here
        logger.warning("CosyVoice file synthesis not implemented")
        return False


if __name__ == "__main__":
    # Test the synthesizer
    print("VoiceSynthesizer Test")
    print("-" * 50)

    synthesizer = VoiceSynthesizer(backend="system")
    print(f"Backend: {synthesizer.backend}")
    print(f"Device: {synthesizer.device}")

    # Test speak
    test_text = "Hello, this is a test of the voice synthesizer."
    print(f"\nSpeaking: {test_text}")
    success = synthesizer.speak(test_text)
    print(f"Success: {success}")
