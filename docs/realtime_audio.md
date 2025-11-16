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
      "pause_threshold": 1800
    }
  }
}
```

The `sample_rate` can be `8000`, `16000`, or `24000` and defaults to `16000`. It determines the sample rate of the audio chunks you receive from Attendee. Optionally, set `pause_threshold` (RMS amplitude, `0-32767`) to have Attendee automatically pause outgoing realtime audio for 800 ms whenever the mixed meeting audio is at or above that threshold.

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

#### Temporarily pause bot audio output

To temporarily pause realtime audio playback (for example, while your agent processes an update), send a message with the `realtime_audio.pause_current_lecture` trigger. The `duration` field is specified in milliseconds.

```json
{
  "trigger": "realtime_audio.pause_current_lecture",
  "data": {
    "duration": 1500
  }
}
```

When Attendee detects loud meeting audio that crosses the configured `pause_threshold`, it will automatically pause its own realtime playback for 800 ms and forward the same `realtime_audio.pause_current_lecture` message (including the `bot_id` field) to your websocket listener so that your agent can temporarily stop sending additional audio.

During the pause window, any queued realtime audio chunks are held until playback resumes.

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

## Error Messages

Currently, we don't give any feedback on errors with the websocket connection or invalid message formats. We plan to improve this in the future.


