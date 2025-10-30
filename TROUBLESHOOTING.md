# Troubleshooting Real-Time Audio Pause Features

## Issues Fixed

### Issue #1: Audio Format Incompatibility
**Problem**: The audio threshold detection wasn't working because different meeting platforms use different audio formats (32-bit float vs 16-bit PCM), but the RMS calculation assumed a single format.

**Solution**: 
- Updated `check_audio_level_and_pause_if_needed()` to accept a `sample_width` parameter
- Bot controller now detects the audio format and passes the correct sample width (4 for float, 2 for PCM)
- Added error handling to prevent crashes if audio format is incompatible

### Audio Format by Platform
- **Google Meet**: 32-bit float (F32LE) - use sample_width=4
- **Microsoft Teams**: 32-bit float (F32LE) - use sample_width=4  
- **Zoom Web**: 32-bit float (F32LE) - use sample_width=4
- **Zoom SDK**: 16-bit PCM (S16LE) - use sample_width=2

## Testing the Features

### 1. Test Automatic Pause on Audio Threshold

**Setup**:
```json
{
  "websocket_settings": {
    "audio": {
      "url": "wss://your-server.com/audio",
      "sample_rate": 16000,
      "threshold": 300
    }
  }
}
```

**What to Check**:
1. Monitor bot logs for: `"RealtimeAudioOutputManager: Audio threshold set to X"`
2. When participants speak, look for: `"Audio level X exceeds threshold Y, pausing playback"`
3. Verify the bot stops speaking when someone talks
4. Verify the bot resumes after 800ms

**If it's not working**:
- Check logs for error messages about audio level checking
- Verify the threshold is appropriate for your platform (see recommendations below)
- Try adjusting the threshold value up or down

**Recommended Thresholds**:
- **Google Meet/Teams/Zoom Web**: Start with 300, adjust between 100-500
- **Zoom SDK**: Start with 1500, adjust between 500-3000

### 2. Test Manual Pause via WebSocket

**Send this message from your WebSocket server**:
```json
{
  "trigger": "pause_current_lecture",
  "data": {
    "duration": 2000
  }
}
```

**What to Check**:
1. Monitor bot logs for: `"Received pause_current_lecture event with duration Xms"`
2. Monitor for: `"RealtimeAudioOutputManager: Pausing playback for Xms"`
3. Verify the bot stops speaking
4. Verify the bot resumes after the specified duration

**If it's not working**:
- Check that your WebSocket connection is established
- Verify the message format matches exactly (JSON with "trigger" and "data" fields)
- Check bot logs for any error messages about unknown triggers
- Ensure the duration value is greater than 0

### 3. Debug Logging

Add these log searches to your monitoring:

**For threshold detection**:
```
"Audio threshold set to"
"Audio level"
"exceeds threshold"
"pausing playback"
```

**For WebSocket pause events**:
```
"Received pause_current_lecture"
"Pausing playback for"
"Pause duration expired"
```

**For errors**:
```
"Error checking audio level"
"Error in audio level check callback"
"Received pause_current_lecture event with invalid duration"
```

## Common Issues

### Bot Never Pauses
**Possible causes**:
1. Threshold not configured in bot settings
2. Threshold value too high for the audio format
3. Audio level calculation errors (check logs)
4. No WebSocket audio client configured

**Solutions**:
- Verify `websocket_settings.audio.threshold` is set
- Lower the threshold value
- Check logs for errors
- Ensure WebSocket audio streaming is enabled

### Bot Pauses Too Often
**Possible causes**:
1. Threshold value too low
2. Background noise triggering threshold

**Solutions**:
- Increase threshold value
- Test in quieter environment
- Try values 50-100 higher than current

### WebSocket Pause Not Working
**Possible causes**:
1. WebSocket not connected
2. Wrong message format
3. Duration = 0 or negative

**Solutions**:
- Check WebSocket connection status in logs
- Verify JSON format exactly matches documentation
- Ensure duration > 0

### Bot Crashes or Audio Stops Completely
**Possible causes**:
1. Audio format mismatch causing exceptions
2. Thread deadlock (rare)

**Solutions**:
- Check logs for exception stack traces
- Verify error handling is catching exceptions (should be in place)
- Restart bot if necessary

## Validation Checklist

Before deploying, verify:

- [ ] Bot logs show "Audio threshold set to X" on startup (if threshold configured)
- [ ] Audio level detection doesn't cause errors in logs
- [ ] Bot pauses when participants speak (if threshold is set)
- [ ] Bot resumes automatically after 800ms
- [ ] WebSocket pause_current_lecture events are received and processed
- [ ] Bot resumes after manual pause duration expires
- [ ] No crashes or exceptions in error logs
- [ ] Threshold value is appropriate for the meeting platform

## Getting More Help

If issues persist:

1. **Collect logs**: Gather 5-10 minutes of bot logs showing the issue
2. **Identify pattern**: Does it happen always, sometimes, or never?
3. **Check configuration**: Verify bot settings JSON
4. **Test isolation**: Try with just threshold, then just WebSocket pause
5. **Platform specific**: Note which meeting platform (Zoom/Meet/Teams)

Include this information when seeking support.
