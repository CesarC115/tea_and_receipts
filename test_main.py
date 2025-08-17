from main import *
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

OUTPUT_VIDEO_TEST:Path = CWD / "OUTPUT_VIDEO_TEST.mp4"

@pytest.fixture
def dummy_story():
    return "Hello world! This is a test."


def dummy_word_timestamps():
    return [
    {'word': 'Hello', 'start': 0.0, 'end': 0.5},
    {'word': 'world', 'start': 0.5, 'end': 1.0},
    {'word': 'This', 'start': 1.0, 'end': 1.5},
    {'word': 'is', 'start': 1.5, 'end': 2.0},
    {'word': 'a', 'start': 2.0, 'end': 2.2},
    {'word': 'test', 'start': 2.2, 'end': 2.7},
    
    {'word': 'Hello', 'start': 2.7, 'end': 3.2},
    {'word': 'world', 'start': 3.2, 'end': 3.7},
    {'word': 'This', 'start': 3.7, 'end': 4.2},
    {'word': 'is', 'start': 4.2, 'end': 4.7},
    {'word': 'a', 'start': 4.7, 'end': 4.9},
    {'word': 'test', 'start': 4.9, 'end': 5.4},
    
    {'word': 'Hello', 'start': 5.4, 'end': 5.9},
    {'word': 'world', 'start': 5.9, 'end': 6.4},
    {'word': 'This', 'start': 6.4, 'end': 6.9},
    {'word': 'is', 'start': 6.9, 'end': 7.4},
    {'word': 'a', 'start': 7.4, 'end': 7.6},
    {'word': 'test', 'start': 7.6, 'end': 8.1},
    
    {'word': 'Hello', 'start': 8.1, 'end': 8.6},
    {'word': 'world', 'start': 8.6, 'end': 9.1},
    {'word': 'This', 'start': 9.1, 'end': 9.6},
    {'word': 'is', 'start': 9.6, 'end': 10.1},
    {'word': 'a', 'start': 10.1, 'end': 10.3},
    {'word': 'test', 'start': 10.3, 'end': 10.8}
]

ElevenLabs_API_TEST:dict = {
  "audio_base64": "base64_encoded_audio_string",
  "alignment": {
    "characters": [
      "H",
      "e",
      "l",
      "l",
      "o",
      " ",
      "w",
      "o",
      "r",
      "l",
      "d"
    ],
    "character_start_times_seconds": [
      0,
      0.1,
      0.2,
      0.3,
      0.4,
      0.5,
      0.6,
      0.7,
      0.8,
      0.9,
      1.0
    ],
    "character_end_times_seconds": [
      0.1,
      0.2,
      0.3,
      0.4,
      0.5,
      0.6,
      0.7,
      0.8,
      0.9,
      1.0,
      1.1
    ]
  },
  "normalized_alignment": {
    "characters": [
      "H",
      "e",
      "l",
      "l",
      "o"
    ],
    "character_start_times_seconds": [
      0,
      0.1,
      0.2,
      0.3,
      0.4
    ],
    "character_end_times_seconds": [
      0.1,
      0.2,
      0.3,
      0.4,
      0.5
    ]
  }
}

def test_get_words_timestamps():
    
    test_chars:list[dict] = []
    test_chars = [
        {"char": c, "start": s, "end": e}
        for c, s, e in zip(
                ElevenLabs_API_TEST['alignment']['characters'],
                ElevenLabs_API_TEST['alignment']['character_start_times_seconds'],
                ElevenLabs_API_TEST['alignment']['character_end_times_seconds']
            )
    ]
    
    words_timestamps:list[dict] = get_words_timestamps(test_chars)
    
    FIRST_WORD:int = 0
    assert isinstance(words_timestamps, list)
    assert isinstance(words_timestamps[FIRST_WORD], dict)
    
    assert words_timestamps[FIRST_WORD]['word'] == 'Hello'
    assert words_timestamps[FIRST_WORD]['start'] == 0.0
    assert words_timestamps[FIRST_WORD]['end'] == 0.6
    
    
def test_add_audio_and_subtitles_development():
  
  
  mock_audio_file:Path = CWD / "audio_test.mp3"
  mock_word_timestamps = dummy_word_timestamps()
  
  add_audio_and_subtitles(VIDEO_PATH, mock_audio_file, mock_word_timestamps, OUTPUT_VIDEO_TEST)
  
  print(f"Test video at:{OUTPUT_VIDEO_TEST}")
    
@patch("main.VideoFileClip")
@patch("main.AudioFileClip")
@patch("main.TextClip")
@patch("main.CompositeVideoClip")
def test_add_audio_and_subtitles_success(
    mock_composite, mock_textclip, mock_audiofile, mock_videofile,
    dummy_story, dummy_word_timestamps, tmp_path
):
    # Setup mocks
    mock_video = MagicMock()
    mock_video.w = 1080
    mock_video.size = (1080, 1920)
    mock_video.subclipped.return_value = mock_video
    mock_video.with_audio.return_value = mock_video
    mock_video.with_effects.return_value = mock_video
    mock_videofile.return_value = mock_video

    mock_audio = MagicMock()
    mock_audio.duration = 3.0
    mock_audiofile.return_value = mock_audio

    mock_textclip.return_value = MagicMock()
    mock_composite.return_value = MagicMock()
    mock_composite.return_value.write_videofile = MagicMock()

    video_path = tmp_path / "input.mp4"
    audio_path = tmp_path / "input.mp3"
    output_path = tmp_path / "output.mp4"

    # Call the function
    add_audio_and_subtitles(video_path, audio_path, dummy_word_timestamps, output_path)

    # Assertions
    mock_videofile.assert_called_once_with(str(video_path), target_resolution=(1080, 1920))
    mock_audiofile.assert_called_once_with(str(audio_path))
    mock_video.subclipped.assert_called_once()
    mock_video.with_audio.assert_called_once_with(mock_audio)
    mock_video.with_effects.assert_called_once()
    assert mock_textclip.call_count == len(dummy_story.split())
    mock_composite.assert_called_once()
    mock_composite.return_value.write_videofile.assert_called_once_with(str(output_path))

@patch("main.VideoFileClip")
@patch("main.AudioFileClip")
@patch("main.TextClip")
@patch("main.CompositeVideoClip")
def test_add_audio_and_subtitles_zero_words(
    mock_composite, mock_textclip, mock_audiofile, mock_videofile, tmp_path
):
    # Setup mocks
    mock_video = MagicMock()
    mock_video.w = 1080
    mock_video.size = (1080, 1920)
    mock_video.subclipped.return_value = mock_video
    mock_video.with_audio.return_value = mock_video
    mock_video.with_effects.return_value = mock_video
    mock_videofile.return_value = mock_video

    mock_audio = MagicMock()
    mock_audio.duration = 3.0
    mock_audiofile.return_value = mock_audio

    mock_textclip.return_value = MagicMock()
    mock_composite.return_value = MagicMock()
    mock_composite.return_value.write_videofile = MagicMock()

    video_path = tmp_path / "input.mp4"
    audio_path = tmp_path / "input.mp3"
    output_path = tmp_path / "output.mp4"

    # Call the function with empty story
    add_audio_and_subtitles(video_path, audio_path, [], output_path)

    # Should not create any subtitle clips
    assert mock_textclip.call_count == 0
    mock_composite.assert_called_once()
    mock_composite.return_value.write_videofile.assert_called_once_with(str(output_path))

if __name__ == '__main__':
  print("Starting development tests...")
  # test_add_audio_and_subtitles_development()