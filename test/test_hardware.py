"""
Test script for Hardware Detection Utility
Tests device detection and hardware information
"""

import sys
from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

from utils.hardware import get_device, get_device_info


def test_device_detection():
    """Test device detection"""
    print("\n" + "=" * 70)
    print("TEST 1: Device Detection")
    print("=" * 70)

    print("\n[Test 1.1] Get device")
    device = get_device()
    print(f"Detected device: {device}")
    assert device in ["cuda", "mps", "cpu"], "Invalid device detected"
    print(f"✅ Device detected: {device}")

    print("\n[Test 1.2] Get device info")
    info = get_device_info()
    print(f"Device info:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    assert "device" in info, "Device info missing 'device' key"
    assert "cuda_available" in info, "Device info missing 'cuda_available' key"
    assert "mps_available" in info, "Device info missing 'mps_available' key"
    print("✅ Device info retrieved successfully")

    print("\n[Test 1.3] Verify device consistency")
    assert info["device"] == device, "Device info inconsistent with get_device()"
    print("✅ Device information is consistent")


def test_device_priorities():
    """Test device priority logic"""
    print("\n" + "=" * 70)
    print("TEST 2: Device Priority Logic")
    print("=" * 70)

    info = get_device_info()
    device = info["device"]

    print(f"\n[Test 2.1] Verify priority: CUDA > MPS > CPU")
    if info["cuda_available"]:
        assert device == "cuda", "CUDA available but not selected"
        print("✅ CUDA has highest priority (correctly selected)")
    elif info["mps_available"]:
        assert device == "mps", "MPS available but not selected"
        print("✅ MPS has second priority (correctly selected)")
    else:
        assert device == "cpu", "CPU should be fallback"
        print("✅ CPU is fallback (correctly selected)")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("HARDWARE DETECTION - TEST SUITE")
    print("=" * 70)

    try:
        test_device_detection()
        test_device_priorities()

        print("\n" + "=" * 70)
        print("🎉 ALL HARDWARE TESTS PASSED!")
        print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
