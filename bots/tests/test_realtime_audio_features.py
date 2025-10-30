import json
import struct
import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from bots.bot_controller.bot_controller import BotController
from bots.bot_controller.realtime_audio_output_manager import RealtimeAudioOutputManager
from bots.models import RealtimeTriggerTypes


def make_pcm_chunk(sample_value: int, repeat: int = 100) -> bytes:
    """Helper to build a PCM chunk with a constant sample value."""
    return struct.pack("<" + "h" * repeat, *([sample_value] * repeat))


def test_realtime_audio_output_manager_respects_pause():
    played = []

    def play_raw_audio_callback(*, bytes, sample_rate):
        played.append((time.time(), bytes, sample_rate))

    manager = RealtimeAudioOutputManager(
        play_raw_audio_callback=play_raw_audio_callback,
        sleep_time_between_chunks_seconds=0,
        output_sample_rate=16000,
    )

    try:
        pause_seconds = 0.2
        manager.pause_for(pause_seconds)

        chunk = make_pcm_chunk(2000, repeat=160)  # chunk length (~0.01s) processed by add_chunk_inner
        manager.add_chunk_inner(chunk, 16000)

        time.sleep(pause_seconds / 4)
        assert played == []

        time.sleep(pause_seconds)
        assert len(played) == 1
    finally:
        manager.cleanup()


def test_bot_controller_auto_pause_triggers_when_threshold_met():
    controller = BotController.__new__(BotController)
    controller.bot_in_db = SimpleNamespace(settings={"websocket_settings": {"audio": {"pause_threshold": 1500}}}, object_id="bot_auto_pause")
    controller.realtime_audio_output_manager = Mock()

    loud_chunk = make_pcm_chunk(2200)
    controller.maybe_pause_realtime_audio_due_to_mixed_audio(loud_chunk)

    controller.realtime_audio_output_manager.pause_for.assert_called_once_with(
        controller.REALTIME_AUDIO_AUTOPAUSE_DURATION_SECONDS
    )

    controller.realtime_audio_output_manager.pause_for.reset_mock()

    quiet_chunk = make_pcm_chunk(800)
    controller.maybe_pause_realtime_audio_due_to_mixed_audio(quiet_chunk)

    controller.realtime_audio_output_manager.pause_for.assert_not_called()


def test_bot_controller_auto_pause_uses_env_threshold(monkeypatch):
    controller = BotController.__new__(BotController)
    controller.bot_in_db = SimpleNamespace(settings={}, object_id="bot_env_threshold")
    controller.realtime_audio_output_manager = Mock()

    monkeypatch.setenv(BotController.REALTIME_AUDIO_AUTOPAUSE_THRESHOLD_ENV_VAR, "1200")

    loud_chunk = make_pcm_chunk(2000)
    controller.maybe_pause_realtime_audio_due_to_mixed_audio(loud_chunk)

    controller.realtime_audio_output_manager.pause_for.assert_called_once_with(
        controller.REALTIME_AUDIO_AUTOPAUSE_DURATION_SECONDS
    )


def test_pause_current_lecture_message_pauses_audio():
    controller = BotController.__new__(BotController)
    controller.bot_in_db = SimpleNamespace(object_id="bot_ws_pause")
    controller.realtime_audio_output_manager = Mock()

    message = {
        "trigger": RealtimeTriggerTypes.type_to_api_code(RealtimeTriggerTypes.PAUSE_CURRENT_LECTURE),
        "data": {"duration": 1500},
    }

    controller.on_message_from_websocket_audio(json.dumps(message))

    controller.realtime_audio_output_manager.pause_for.assert_called_once_with(1.5)
