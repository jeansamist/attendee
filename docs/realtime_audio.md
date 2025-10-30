# Realtime Audio Input and Output

Attendee supports bidirectional realtime audio streaming through websockets. You can receive audio from meetings and have your bot output audio into meetings in real-time.

## Setup

To enable realtime audio streaming, configure the `websocket_settings.audio` parameter when creating a bot:

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

Configuration options:
- `sample_rate`: Can be `8000`, `16000`, or `24000` and defaults to `16000`. It determines the sample rate of the audio chunks you receive from Attendee.
- `threshold` (optional): RMS audio level threshold for automatic pause. When the mixed audio from the call exceeds this value, the bot will automatically pause its audio playback for 800ms. This prevents the bot from talking over participants. Typical values range from 100 (very sensitive) to 2000 (less sensitive).

## Websocket Message Format

### Outgoing Audio (Attendee → Your Websocket Server)

Your WebSocket server will receive messages in this format.

```json
{
  "bot_id": "bot_12345abcdef",
  "trigger": "realtime_audio.mixed",
  "data": {
    "chunk": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAABACAAAGRLVEE...",
    "sample_rate": 16000,
    "timestamp_ms": 1703123456789
  }
}
```

The `chunk` field is base64-encoded 16-bit single channel PCM audio data at the frequency specified in the `sample_rate` field.

### Incoming Audio (Your Websocket Server → Attendee)

When you want the bot to speak audio in the meeting, send a message in this format.

```json
{
  "trigger": "realtime_audio.bot_output",
  "data": {
    "chunk": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAABACAAAGRLVEE...",
    "sample_rate": 16000
  }
}
```

The `chunk` field is base64-encoded 16-bit single-channel PCM audio data. The sample rate can be `8000`, `16000` or `24000`.

### Pausing Audio Playback (Your Websocket Server → Attendee)

You can pause the bot's audio playback for a specified duration by sending this message:

```json
{
  "trigger": "pause_current_lecture",
  "data": {
    "duration": 2000
  }
}
```

The `duration` field is in milliseconds and specifies how long to pause the audio playback. After the duration expires, playback will automatically resume.

## Integration with Voice Agent APIs

The realtime audio streaming can be easily integrated with voice agent APIs to bring voice agents into meetings.

### Deepgram Voice Agent API
Connect directly to Deepgram's voice agent WebSocket API by forwarding audio chunks. Set an output sample rate of `16000` to be compatible with Deepgram's real-time streaming requirements. See an example app showing how to integrate with Deepgram's voice agent API [here](https://github.com/attendee-labs/voice-agent-example).

### OpenAI Realtime API
Connect directly to OpenAI's realtime API by forwarding audio chunks. Set an output sample rate of `24000` to be compatible with OpenAI's real-time streaming requirements.

## Code Samples

A simple example app showing how to integrate with Deepgram's voice agent API: https://github.com/attendee-labs/voice-agent-example

## Retries on Websocket Connections

Attendee will automatically retry to connect to your websocket server if the connection is lost or the initial connection attempt fails. We will retry up to 30 times with a 2 second delay between retries.

## Automatic Pause on Call Audio Threshold

The bot can automatically pause audio playback when the audio level from the call exceeds a certain threshold. This is useful for preventing the bot from talking over participants.

To enable this feature:

1. Set an audio threshold value (RMS audio level) in your bot configuration
2. When the mixed audio from the call exceeds this threshold, the bot will automatically pause playback for 800ms
3. This allows participants to speak without the bot interrupting them

The threshold is configurable and can be adjusted based on your use case. Higher values mean the bot will only pause when there's louder audio (e.g., someone speaking loudly), while lower values will make the bot more sensitive to any audio in the call.

## Error Messages

Currently, we don't give any feedback on errors with the websocket connection or invalid message formats. We plan to improve this in the future.


