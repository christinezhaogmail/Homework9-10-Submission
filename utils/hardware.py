"""
Hardware Detection Utility
Detects available compute devices (CUDA, MPS, CPU) for model loading
"""

import torch
from loguru import logger


def get_device():
    """
    Detect and return the best available device for model inference.

    Priority: CUDA (NVIDIA GPU) > MPS (Apple Silicon) > CPU

    Returns:
        str: Device identifier ("cuda", "mps", or "cpu")
    """
    if torch.cuda.is_available():
        device = "cuda"
        logger.info(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
    elif torch.backends.mps.is_available():
        device = "mps"
        logger.info("✓ MPS (Apple Silicon) available")
    else:
        device = "cpu"
        logger.info("Using CPU (no GPU acceleration)")

    return device


def get_device_info():
    """
    Get detailed information about available compute devices.

    Returns:
        dict: Dictionary containing device information
    """
    info = {
        "device": get_device(),
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "cpu_count": torch.get_num_threads()
    }

    if torch.cuda.is_available():
        info["cuda_device_name"] = torch.cuda.get_device_name(0)
        info["cuda_device_count"] = torch.cuda.device_count()

    return info


if __name__ == "__main__":
    print("Hardware Detection Results:")
    print("-" * 50)
    device = get_device()
    print(f"Selected device: {device}")
    print("\nDetailed info:")
    for key, value in get_device_info().items():
        print(f"  {key}: {value}")
