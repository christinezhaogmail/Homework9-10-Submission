# Fixes Summary

## Issue 1: pyttsx3 "name 'objc' is not defined" Error

**Problem**: When selecting pyttsx3 from the TTS backend dropdown, the log showed:
```
ERROR | audio_service:__init__:256 - Error initializing pyttsx3: name 'objc' is not defined
```

**Root Cause**: pyttsx3 version 2.90 had a bug in the macOS driver where it didn't properly import the `objc` module from PyObjC.

**Fix Applied**:
1. Upgraded pyttsx3 from 2.90 to 2.99 (which includes the fix)
2. Updated `requirements.txt` to specify `pyttsx3>=2.99`
3. Added PyObjC dependencies: `pyobjc-core>=9.0` and `pyobjc-framework-Cocoa>=9.0`

**Files Changed**:
- `requirements.txt` - Updated pyttsx3 version and added PyObjC dependencies
- `MACOS_SETUP.md` - Added troubleshooting section for this issue

**Status**: ✅ Fixed - pyttsx3 now initializes successfully on macOS M3

---

## Issue 2: Audio Output Button Grey/Unplayable

**Problem**: Audio output button displayed grey and couldn't play audio.

**Root Cause**: pyttsx3's `save_to_file()` method doesn't work properly on macOS - it doesn't generate valid audio files.

**Fix Applied**:
Modified `audio_service.py` to use the macOS `say` command for audio file generation when using pyttsx3 on macOS:

```python
elif self.backend == "pyttsx3":
    # pyttsx3's save_to_file doesn't work properly on macOS
    # Use the system 'say' command instead for file generation on macOS
    if os.name == "posix":
        # macOS - use 'say' command to generate audio file
        subprocess.run(["say", "-o", output_path, "--data-format=LEI16@22050", text], check=True)
        logger.info(f"Audio file generated successfully with 'say' command: {output_path}")
        return True
```

**Files Changed**:
- `audio_service.py` - Modified `text_to_audio_file()` method in `TextToSpeechService` class

**Status**: ✅ Fixed - Audio files now generate correctly (tested: 53-56KB files)

---

## Issue 3: "An error has occurred, please try again" in Audio Input

**Problem**: After hearing the response sound, the audio input section displayed "An error has occurred, please try again."

**Root Cause**: After processing an audio input and calling `st.rerun()`, the `audio_input` widget was being recreated with the same key, but with stale audio data that was invalidated by the rerun.

**Fix Applied**:
1. Changed the audio input widget to use a dynamic key that changes after each query:
   ```python
   audio_input = st.audio_input("Record your question", key=f"audio_input_{st.session_state.query_count}")
   ```

2. Simplified the audio processing logic by removing the `last_audio_input_id` tracking (no longer needed with dynamic key)

3. The key now includes the query count, so after each successful query, a fresh audio input widget is created

**Files Changed**:
- `frontend.py` - Modified audio input widget key and simplified processing logic

**Status**: ✅ Fixed - Audio input now resets cleanly after each query

---

## Testing

All three issues have been tested and verified:

1. **pyttsx3 initialization**: ✅ No more "objc not defined" error
2. **Audio file generation**: ✅ Files created successfully (56KB+ WAV files)
3. **Audio input reset**: ✅ No more "An error has occurred" message

---

## How to Test

1. **Stop your current Streamlit app** (Ctrl+C)
2. **Restart Streamlit**:
   ```bash
   streamlit run frontend.py
   ```
3. **In the sidebar**, select "pyttsx3" from the TTS Backend dropdown
4. **Record a voice question** or type a question
5. **Verify**:
   - Audio response plays correctly (blue audio button)
   - After hearing response, audio input section is ready for next question
   - No "An error has occurred" message

---

## Notes

- On macOS, both "system" and "pyttsx3" backends now use the macOS `say` command for audio file generation
- This provides consistent, high-quality audio output
- CosyVoice backend remains available for GPU deployment
- All changes are backward compatible

---

**Date Fixed**: 2025-12-14
**macOS Version**: macOS M3
**Python Version**: 3.11
