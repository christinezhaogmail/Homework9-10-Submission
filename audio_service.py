"""
Audio Service: Speech-to-Text (Whisper) and Text-to-Speech (CosyVoice/alternatives)
Handles all audio processing for the voice agent
"""

import os
import tempfile
from typing import Optional
import subprocess
import numpy as np
import soundfile as sf
from loguru import logger

# Try to import whisper
try:
    import warnings
    import whisper
    WHISPER_AVAILABLE = True
    # Suppress the specific FutureWarning related to torch.load
    warnings.filterwarnings("ignore", "You are using `torch.load` with `weights_only=False`*", FutureWarning)
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available. Speech-to-text will be limited.")

# Try to import pyttsx3 as fallback TTS
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available. Using alternative TTS.")

# Try to import CosyVoice
try:
    import sys
    import torch
    # Add CosyVoice to path if it exists
    COSYVOICE_PATH = os.getenv("COSYVOICE_PATH", "/Users/huiruzhao/github/inference/CosyVoice")
    if os.path.exists(COSYVOICE_PATH) and COSYVOICE_PATH not in sys.path:
        sys.path.insert(0, COSYVOICE_PATH)

    from cosyvoice.cli.cosyvoice import CosyVoice as CosyVoiceModel
    COSYVOICE_AVAILABLE = True
    logger.info(f"CosyVoice available at: {COSYVOICE_PATH}")
except ImportError as e:
    COSYVOICE_AVAILABLE = False
    logger.warning(f"CosyVoice not available: {e}. Install from https://github.com/FunAudioLLM/CosyVoice")


class SpeechToTextService:
    """
    Speech-to-Text service using OpenAI Whisper
    """

    def __init__(self, model_name: str = "base"):
        """
        Initialize the Speech-to-Text service

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None

        if WHISPER_AVAILABLE:
            try:
                logger.info(f"Loading Whisper model: {model_name}")
                self.model = whisper.load_model(model_name)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
        else:
            logger.warning("Whisper not available. Please install: pip install openai-whisper")

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Transcribed text
        """
        try:
            if not self.model:
                return "Error: Whisper model not loaded. Please install openai-whisper."

            logger.info(f"Transcribing audio file: {audio_file_path}")

            # Transcribe the audio
            result = self.model.transcribe(audio_file_path)
            text = result["text"].strip()

            logger.info(f"Transcription: {text}")
            return text

        except Exception as e:
            error_msg = f"Error transcribing audio: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def transcribe_audio_data(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribe audio data (numpy array) to text

        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio

        Returns:
            Transcribed text
        """
        try:
            if not self.model:
                return "Error: Whisper model not loaded."

            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                sf.write(temp_path, audio_data, sample_rate)

            # Transcribe
            text = self.transcribe_audio(temp_path)

            # Clean up
            os.unlink(temp_path)

            return text

        except Exception as e:
            error_msg = f"Error transcribing audio data: {str(e)}"
            logger.error(error_msg)
            return error_msg


class CosyVoiceTTSService:
    """
    CosyVoice TTS Service for high-quality neural voice synthesis
    """

    def __init__(self, model_dir: str = None):
        """
        Initialize CosyVoice TTS service

        Args:
            model_dir: Path to CosyVoice model directory
        """
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if not COSYVOICE_AVAILABLE:
            logger.error("CosyVoice not available. Please install it first.")
            return

        try:
            # Default model path
            if model_dir is None:
                cosyvoice_base = os.getenv("COSYVOICE_PATH", "/Users/huiruzhao/github/inference/CosyVoice")
                model_dir = os.path.join(cosyvoice_base, "pretrained_models", "CosyVoice-300M-SFT")

            if not os.path.exists(model_dir):
                logger.error(f"CosyVoice model not found at: {model_dir}")
                return

            logger.info(f"Loading CosyVoice model from: {model_dir}")
            logger.info(f"Using device: {self.device}")

            # Load CosyVoice model
            self.model = CosyVoiceModel(model_dir)
            logger.info("CosyVoice model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading CosyVoice model: {e}")
            self.model = None

    def synthesize(self, text: str, speaker: str = "中文女", output_path: str = None) -> Optional[str]:
        """
        Synthesize speech from text using CosyVoice

        Args:
            text: Text to synthesize
            speaker: Speaker voice to use
            output_path: Optional path to save audio file

        Returns:
            Path to generated audio file, or None if failed
        """
        if not self.model:
            logger.error("CosyVoice model not loaded")
            return None

        try:
            logger.info(f"Synthesizing with CosyVoice: {text[:100]}...")

            # Generate speech
            output = self.model.inference_sft(text, speaker)

            # Save to file
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                output_path = temp_file.name
                temp_file.close()

            # CosyVoice returns (sample_rate, audio_data)
            for sample_rate, audio_data in output:
                sf.write(output_path, audio_data, sample_rate)
                logger.info(f"Audio saved to: {output_path}")
                return output_path

            return None

        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None


class TextToSpeechService:
    """
    Text-to-Speech service with multiple backends
    Supports: pyttsx3 (fallback), CosyVoice (advanced), system TTS
    """

    def __init__(self, backend: str = "pyttsx3", cosyvoice_model_dir: str = None):
        """
        Initialize the Text-to-Speech service

        Args:
            backend: TTS backend to use (pyttsx3, cosyvoice, system)
            cosyvoice_model_dir: Path to CosyVoice model (if using cosyvoice backend)
        """
        self.backend = backend
        self.engine = None
        self.cosyvoice = None

        if backend == "cosyvoice" and COSYVOICE_AVAILABLE:
            try:
                self.cosyvoice = CosyVoiceTTSService(model_dir=cosyvoice_model_dir)
                if self.cosyvoice.model:
                    logger.info("CosyVoice TTS initialized")
                else:
                    logger.warning("CosyVoice failed to initialize, falling back to system TTS")
                    self.backend = "system"
            except Exception as e:
                logger.error(f"Error initializing CosyVoice: {e}")
                self.backend = "system"

        elif backend == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                # Configure voice properties
                self.engine.setProperty('rate', 150)  # Speed
                self.engine.setProperty('volume', 0.9)  # Volume
                logger.info("pyttsx3 TTS initialized")
            except Exception as e:
                logger.error(f"Error initializing pyttsx3: {e}")
        elif backend == "system":
            logger.info("Using system TTS (macOS 'say' command)")
        else:
            logger.info(f"TTS backend: {backend}")

    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it

        Args:
            text: The text to speak

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Speaking: {text[:100]}...")

            if self.backend == "cosyvoice" and self.cosyvoice:
                # Generate audio with CosyVoice
                audio_path = self.cosyvoice.synthesize(text)
                if audio_path:
                    # Play the audio file
                    if os.name == "posix":  # macOS/Linux
                        subprocess.run(["afplay", audio_path], check=True)
                    else:  # Windows
                        import winsound
                        winsound.PlaySound(audio_path, winsound.SND_FILENAME)
                    # Clean up temp file
                    try:
                        os.unlink(audio_path)
                    except OSError as e:
                        logger.warning(f"Could not delete temp file: {e}")
                    return True
                return False

            elif self.backend == "pyttsx3" and self.engine:
                self.engine.say(text)
                self.engine.runAndWait()
                return True

            elif self.backend == "system":
                # Use macOS 'say' command or Windows equivalent
                if os.name == "posix":  # macOS/Linux
                    subprocess.run(["say", text], check=True)
                else:  # Windows
                    # Windows doesn't have a simple TTS command by default
                    logger.warning("System TTS not available on Windows. Install pyttsx3.")
                    return False
                return True

            else:
                logger.warning(f"TTS backend '{self.backend}' not implemented yet")
                return False

        except Exception as e:
            logger.error(f"Error in TTS: {e}")
            return False

    def text_to_audio_file(self, text: str, output_path: str) -> bool:
        """
        Convert text to speech and save to audio file

        Args:
            text: The text to convert
            output_path: Path to save the audio file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Converting text to audio file: {output_path}")

            if self.backend == "cosyvoice" and self.cosyvoice:
                # Use CosyVoice to generate audio
                result_path = self.cosyvoice.synthesize(text, output_path=output_path)
                return result_path is not None

            elif self.backend == "pyttsx3":
                # pyttsx3's save_to_file doesn't work properly on macOS
                # Use the system 'say' command instead for file generation on macOS
                if os.name == "posix":
                    # macOS - use 'say' command to generate audio file
                    subprocess.run(["say", "-o", output_path, "--data-format=LEI16@22050", text], check=True)
                    logger.info(f"Audio file generated successfully with 'say' command: {output_path}")
                    return True
                elif self.engine:
                    # Windows/Linux - use pyttsx3
                    self.engine.save_to_file(text, output_path)
                    self.engine.runAndWait()
                    return True
                else:
                    logger.warning("pyttsx3 engine not initialized")
                    return False

            elif self.backend == "system" and os.name == "posix":
                # Use macOS 'say' command with file output
                subprocess.run(["say", "-o", output_path, "--data-format=LEI16@22050", text], check=True)
                return True

            else:
                logger.warning("Audio file generation not supported for this backend")
                return False

        except Exception as e:
            logger.error(f"Error generating audio file: {e}")
            return False


class VoiceAgentAudio:
    """
    Combined voice agent audio service
    Handles complete STT -> Processing -> TTS pipeline
    """

    def __init__(self, whisper_model: str = "base", tts_backend: str = "system"):
        """
        Initialize the voice agent audio service

        Args:
            whisper_model: Whisper model name
            tts_backend: TTS backend to use
        """
        self.stt = SpeechToTextService(whisper_model)
        self.tts = TextToSpeechService(tts_backend)
        logger.info("Voice Agent Audio service initialized")

    def greet_user(self) -> bool:
        """
        Greet the user with audio

        Returns:
            True if successful
        """
        return self.tts.speak("How can I help you?")

    def acknowledge_processing(self) -> bool:
        """
        Tell user we're processing their request

        Returns:
            True if successful
        """
        return self.tts.speak("I will check, give me a second.")

    def announce_result(self) -> bool:
        """
        Announce that we found the answer

        Returns:
            True if successful
        """
        return self.tts.speak("I found it.")

    def speak_response(self, text: str) -> bool:
        """
        Speak the response to the user

        Args:
            text: The response text

        Returns:
            True if successful
        """
        return self.tts.speak(text)


if __name__ == "__main__":
    # Test the audio services
    print("Testing Text-to-Speech:")
    tts = TextToSpeechService(backend="system")
    tts.speak("Hello, this is a test of the text to speech system.")

    print("\nTesting Voice Agent Audio:")
    voice_agent = VoiceAgentAudio()
    voice_agent.greet_user()
    voice_agent.acknowledge_processing()
    voice_agent.announce_result()
    voice_agent.speak_response("The answer to your question is 42.")

    # Note: Whisper testing requires an actual audio file
    # print("\nTo test Whisper, provide an audio file path")
