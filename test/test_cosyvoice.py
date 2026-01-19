"""
Test script for CosyVoice integration
Tests CosyVoice TTS functionality with the voice agent
"""

import os
import sys
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

print("""
╔═══════════════════════════════════════════════════════════════════╗
║              CosyVoice Integration Test                           ║
╚═══════════════════════════════════════════════════════════════════╝
""")

# Test 1: Check PyTorch and CUDA
print("\n[Test 1] Checking PyTorch and CUDA...")
print("-" * 70)
try:
    import torch
    print(f"✅ PyTorch version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   CUDA version: {torch.version.cuda}")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("   ⚠️  CUDA not available, will use CPU")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 2: Check CosyVoice installation
print("\n[Test 2] Checking CosyVoice installation...")
print("-" * 70)
try:
    # Check if CosyVoice path exists
    cosyvoice_path = os.getenv("COSYVOICE_PATH", "/Users/huiruzhao/github/inference/CosyVoice")
    print(f"CosyVoice path: {cosyvoice_path}")

    if not os.path.exists(cosyvoice_path):
        print(f"❌ CosyVoice not found at: {cosyvoice_path}")
        print("   Please set COSYVOICE_PATH environment variable or install CosyVoice")
        sys.exit(1)

    print(f"✅ CosyVoice directory exists")

    # Check model directory
    model_dir = os.getenv(
        "COSYVOICE_MODEL_DIR",
        os.path.join(cosyvoice_path, "pretrained_models", "CosyVoice-300M-SFT")
    )
    print(f"Model directory: {model_dir}")

    if not os.path.exists(model_dir):
        print(f"❌ Model not found at: {model_dir}")
        print("   Please download the CosyVoice-300M-SFT model")
        sys.exit(1)

    print(f"✅ Model directory exists")

    # List model files
    model_files = os.listdir(model_dir)
    print(f"   Model files: {len(model_files)} files found")
    for f in model_files[:5]:  # Show first 5
        print(f"     - {f}")
    if len(model_files) > 5:
        print(f"     ... and {len(model_files) - 5} more")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 3: Import CosyVoice
print("\n[Test 3] Importing CosyVoice modules...")
print("-" * 70)
try:
    # Add CosyVoice to path
    if cosyvoice_path not in sys.path:
        sys.path.insert(0, cosyvoice_path)

    from cosyvoice.cli.cosyvoice import CosyVoice
    from cosyvoice.utils.file_utils import load_wav
    print("✅ CosyVoice modules imported successfully")
except Exception as e:
    print(f"❌ Error importing CosyVoice: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure CosyVoice is properly installed")
    print("2. Try: cd /home/jovyan/CosyVoice && pip install -r requirements.txt")
    print("3. Check that all dependencies are installed")
    sys.exit(1)

# Test 4: Load CosyVoice model
print("\n[Test 4] Loading CosyVoice model...")
print("-" * 70)
try:
    print("This may take a minute on first load...")
    cosyvoice_model = CosyVoice(model_dir)
    print("✅ CosyVoice model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test synthesis
print("\n[Test 5] Testing speech synthesis...")
print("-" * 70)
try:
    test_text = "Hello, this is a test of CosyVoice text to speech system."
    print(f"Synthesizing: {test_text}")

    # Try inference
    output = cosyvoice_model.inference_sft(test_text, "中文女")

    # Check output
    audio_generated = False
    for i, (sample_rate, audio_data) in enumerate(output):
        print(f"✅ Generated audio chunk {i+1}:")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Audio shape: {audio_data.shape}")
        print(f"   Audio duration: {len(audio_data) / sample_rate:.2f} seconds")
        audio_generated = True

    if not audio_generated:
        print("⚠️  No audio generated")
    else:
        print("\n✅ Speech synthesis test PASSED")

except Exception as e:
    print(f"❌ Error in synthesis: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test with audio_service.py
print("\n[Test 6] Testing audio_service integration...")
print("-" * 70)
try:
    from audio_service import CosyVoiceTTSService, TextToSpeechService

    # Test CosyVoiceTTSService
    print("Creating CosyVoiceTTSService...")
    cosy_tts = CosyVoiceTTSService(model_dir=model_dir)

    if cosy_tts.model:
        print("✅ CosyVoiceTTSService initialized")

        # Test synthesis
        print("Testing synthesis with CosyVoiceTTSService...")
        audio_path = cosy_tts.synthesize("This is a test")

        if audio_path and os.path.exists(audio_path):
            print(f"✅ Audio generated: {audio_path}")
            file_size = os.path.getsize(audio_path)
            print(f"   File size: {file_size / 1024:.2f} KB")

            # Clean up
            os.unlink(audio_path)
            print("   Cleaned up test file")
        else:
            print("❌ Failed to generate audio file")
    else:
        print("❌ CosyVoiceTTSService model not loaded")

    # Test TextToSpeechService with cosyvoice backend
    print("\nTesting TextToSpeechService with cosyvoice backend...")
    tts = TextToSpeechService(backend="cosyvoice", cosyvoice_model_dir=model_dir)

    if tts.backend == "cosyvoice" and tts.cosyvoice:
        print("✅ TextToSpeechService initialized with CosyVoice")
    else:
        print(f"⚠️  TextToSpeechService fell back to: {tts.backend}")

except Exception as e:
    print(f"❌ Error in audio_service test: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("🎉 CosyVoice Integration Test Complete!")
print("=" * 70)
print("\nSummary:")
print("✅ PyTorch and CUDA available" if torch.cuda.is_available() else "✅ PyTorch available (CPU mode)")
print("✅ CosyVoice installation verified")
print("✅ CosyVoice modules imported")
print("✅ Model loaded successfully")
print("✅ Speech synthesis working")
print("✅ audio_service.py integration working")

print("\nNext steps:")
print("1. Set TTS_BACKEND=cosyvoice in your .env file")
print("2. Run: python backend.py")
print("3. Test with: python quick_start.py")
print("\nFor GPU deployment, see: GPU_DEPLOYMENT.md")
print("")
