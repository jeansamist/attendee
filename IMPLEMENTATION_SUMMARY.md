# Real-Time Audio Playback Management Implementation

## Overview

This implementation adds two key features to the Attendee bot system for managing real-time audio playback:

1. **Automatic Pause on Call Audio Threshold**: The bot automatically pauses its audio playback when participants speak (audio level exceeds a configurable threshold)
2. **WebSocket Pause Control**: A new WebSocket event that allows external systems to pause the bot's audio playback for a specific duration

## Changes Made

### 1. RealtimeAudioOutputManager Enhancements

**File**: `bots/bot_controller/realtime_audio_output_manager.py`

#### New Features:
- **Pause State Management**: Added `is_paused`, `pause_until_time`, and `pause_lock` to manage paused state
- **Audio Threshold Detection**: Added `audio_threshold` and `auto_pause_duration_seconds` (default 800ms)
- **New Methods**:
  - `set_audio_threshold(threshold: int)`: Configure the RMS audio level threshold
  - `check_audio_level_and_pause_if_needed(audio_chunk: bytes)`: Automatically pause when call audio exceeds threshold
  - `pause_playback(duration_ms: int)`: Pause audio playback for a specified duration
  - `resume_playback()`: Manually resume audio playback

#### Key Implementation Details:
- The `_process_audio_queue()` method now checks pause state before playing audio chunks
- When paused, the thread sleeps for 100ms intervals and checks if the pause duration has expired
- Audio level is calculated using `audioop.rms()` which computes the Root Mean Square of the audio signal

### 2. WebSocket Event Type

**File**: `bots/models.py`

#### New Event Type:
- **PAUSE_CURRENT_LECTURE** (code: 103, API code: "pause_current_lecture")
- Added `api_code_to_type()` class method for reverse mapping

### 3. Bot Controller Integration

**File**: `bots/bot_controller/bot_controller.py`

#### Changes:
1. **Mixed Audio Callback**: Modified `add_mixed_audio_chunk_callback()` to check audio levels and auto-pause when threshold is exceeded
2. **WebSocket Message Handler**: Updated `on_message_from_websocket_audio()` to handle the new `pause_current_lecture` event
3. **Threshold Configuration**: Added code to set audio threshold from bot settings during initialization

### 4. Bot Model Extension

**File**: `bots/models.py`

#### New Method:
- `websocket_audio_threshold()`: Retrieves the audio threshold from bot's websocket settings

### 5. Documentation

**File**: `docs/realtime_audio.md`

Updated documentation to include:
- Configuration instructions for the `threshold` parameter
- Usage guide for the new `pause_current_lecture` WebSocket event
- Explanation of the automatic pause feature and recommended threshold values

## Usage

### Configuring Automatic Pause on Audio Threshold

When creating a bot, include the `threshold` parameter in the websocket settings:

```json
{
  "meeting_url": "https://meet.google.com/abc-def-ghi",
  "bot_name": "Audio Bot",
  "websocket_settings": {
    "audio": {
      "url": "wss://your-server.com/attendee-websocket",
      "sample_rate": 16000,
      "threshold": 500
    }
  }
}
```

**Threshold Guidelines**:
- 100-300: Very sensitive, pauses on any audio
- 300-800: Moderate sensitivity, pauses on normal speech
- 800-2000: Less sensitive, only pauses on loud speech
- Higher values: Only pauses on very loud audio

### Using the pause_current_lecture WebSocket Event

Send this message from your WebSocket server to pause the bot's audio:

```json
{
  "trigger": "pause_current_lecture",
  "data": {
    "duration": 2000
  }
}
```

The `duration` field is in milliseconds. After this duration, playback automatically resumes.

## How It Works

### Automatic Pause Flow

1. Bot receives mixed audio from the call via `add_mixed_audio_chunk_callback()`
2. If audio threshold is configured, `check_audio_level_and_pause_if_needed()` is called
3. Audio level (RMS) is calculated using `audioop.rms()`
4. If RMS exceeds threshold, `pause_playback()` is called with 800ms duration
5. Audio playback thread checks pause state and waits until pause expires
6. Playback automatically resumes after 800ms

### Manual Pause Flow

1. External system sends `pause_current_lecture` WebSocket message
2. `on_message_from_websocket_audio()` receives and parses the message
3. Calls `pause_playback(duration_ms)` with the specified duration
4. Audio playback thread pauses for the specified duration
5. Playback automatically resumes after duration expires

## Benefits

1. **Natural Conversation Flow**: Bot doesn't talk over participants
2. **Flexible Control**: External systems can pause the bot as needed
3. **Configurable Sensitivity**: Threshold can be tuned per use case
4. **Automatic Recovery**: Playback always resumes automatically
5. **Thread-Safe**: All pause operations use proper locking mechanisms

## Testing Recommendations

1. Test with different threshold values to find optimal sensitivity
2. Test manual pause with various duration values
3. Verify that audio resumes correctly after pause
4. Test concurrent pause requests (manual + automatic)
5. Verify behavior when bot receives audio chunks while paused (they should queue up)

## Technical Notes

- The pause mechanism uses `threading.Lock()` for thread safety
- Paused audio chunks are queued, not dropped
- The 800ms auto-pause duration is hardcoded but can be made configurable if needed
- Audio level calculation uses 16-bit PCM mono audio (SAMPLE_WIDTH = 2, CHANNELS = 1)
