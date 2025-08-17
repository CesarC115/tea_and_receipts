import os
import base64
import pprint as pprint
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video import fx as vfx, tools as videotools
from pathlib import Path

# Load API keys
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("Set ELEVENLABS_API_KEY in .venv file")

# Elevenlabs client
client_elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Paths
CWD = Path.cwd()
# STORIES_PATH:Path = CWD
STORY1_PATH:Path = CWD / "story1.txt"
AUDIO_PATH:Path = CWD / "audio_development.mp3"
VIDEO_PATH:Path = CWD / "minecraft_parkour_1_30-p1.mp4"
OUTPUT_VIDEO:Path = CWD / "video_subtitled.mp4"

    
def get_story() -> str:
    """Read the story text from a file."""
    story: str = ""
    
    # Read from a text file the story
    try:
        with open(STORY1_PATH, "r", encoding="utf-8") as file_text:
            story = file_text.read()
    except FileNotFoundError:
        print("story1.txt not found.")
    except Exception as e:
        print(f"Error reading story1.txt: {e}")
    
    return story

def synthesize_audio(text: str, output_path: Path) -> list:
    """
    Use ElevenLabs TTS to synthesize `text` into an MP3 file.
    Returns the duration of the generated audio in seconds.
    """
        
    # Generate audio stream
    response = client_elevenlabs.text_to_speech.convert_with_timestamps(
        text=text,
        voice_id='cgSgspJ2msm6clMCkdW9', # Jessica (Default voices)
        model_id="eleven_turbo_v2_5",
        output_format="mp3_22050_32",
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
    )    
    # Check for errors on API response
    if isinstance(response, dict) and "detail" in response:
        print("Error from ElevenLabs API:", response["detail"]["message"])
        raise RuntimeError("Failed to synthesize audio: " + response["detail"]["message"])
    
    # Save audio
    audio_bytes = base64.b64decode(response.audio_base_64)
    try:
        with open(output_path, "wb") as file:
            file.write(audio_bytes)
    except Exception as e:
        print(f"Failed to write to file as audio:{e}")
    print(f"Audio file saved:{output_path}")

    # Extract timestamps
    timestamps = []
    if hasattr(response, "alignment") and response.alignment:
        timestamps = [
            {"char": c, "start": s, "end": e}
            for c, s, e in zip(
                response.alignment.characters,
                response.alignment.character_start_times_seconds,
                response.alignment.character_end_times_seconds
            )
        ]
    else:
        print("Warning: No alignment data returned from ElevenLabs API.")
    return timestamps
    
def get_words_timestamps(char_timestamps: list[dict]) -> list[dict]:
    '''
    Function that adds all characters to words and attaches
    start time and end time of words.
    '''
    words_timestamps: list[dict] = []
    word_buffer:str = ""
    start_time_buffer:float = 0
    first_word:bool = True
    
    # Traverse the list
    for it in char_timestamps:
                
        # Check space
        if it['char'] == ' ':
            if word_buffer: # Only append if word_buffer is not empty
                word:dict = {
                    'word': word_buffer,
                    'start': start_time_buffer,
                    'end': it['end']
                }
                words_timestamps.append(word) # Word processed
                word_buffer = "" # Reset the word buffer
                first_word = True # Reset flag
        else:    
            # Save time start time
            if first_word == True:
                start_time_buffer = it['start']
                first_word = False
                
            # Save char to a buffer
            word_buffer += it['char']
            
    # Append the last word if any
    if word_buffer:
        word = {
            'word': word_buffer,
            'start': start_time_buffer,
            'end': char_timestamps[-1]['end']
        }
        words_timestamps.append(word)
            
    print("Words and timestamps succesfully stamped")

    return words_timestamps

def add_audio_and_subtitles(video_path: Path, audio_path: Path, word_timestamps:list, output_path: Path):
    """
    Overlay audio and word-by-word subtitles onto the video.
    """
    # Load media
    video = VideoFileClip(str(video_path), target_resolution=(1080, 1920))
    audio = AudioFileClip(str(audio_path))
    
    # Trim or extend video to match audio duration
    video = video.subclipped(0, audio.duration)
    video = video.with_audio(audio)
    
    # Adjust video aspect ratio 9:16 1080x1920p
    video.with_effects([vfx.Resize((1080,1920))]) 
    
    # Create TextClip objects from strings
    font_size:float = 200
    remove_punct = str.maketrans('', '', ",.'")
    subtitle_clips = []
    for word_info in word_timestamps:
        # Time word to be displayed
        time_displayed:float = word_info['end'] - word_info['start']
        
        # Lower case string and Eliminate Punctuations . , - '
        clean_word = word_info['word'].lower().translate(remove_punct)
        
        # Create text
        txt = TextClip(
            text=clean_word,
            font_size=font_size,
            color='white',
            stroke_color='black',
            stroke_width=2,
            size=(video.w, font_size+150),
            method='caption',
            text_align='center',
            vertical_align='center',
            horizontal_align='center'
        ).with_start(word_info['start']).with_duration(time_displayed).with_position(('center', 'center'))
        subtitle_clips.append(txt)
        
    # Composite video + subtitles
    final = CompositeVideoClip([video, *subtitle_clips], size=video.size)
    final.write_videofile(str(output_path))
    

def main():
    print("Starting app...")
    print("CWD:", CWD)
  
    # Story in Text  
    print("Getting story...")
    story:str = get_story()
    # print("Story:", story)
    
    # Text to Speech
    print("Synthetizing audio...") 
    audio_char_timestamps = synthesize_audio(story, AUDIO_PATH)
    print(f"Audio generated at: {AUDIO_PATH}")
    
    # Calculate word duration
    words_timestamps = get_words_timestamps(audio_char_timestamps)
    
    print("Adding audio and subtitles to video...")
    OUTPUT_VIDEO = CWD / "final_video.mp4"
    add_audio_and_subtitles(VIDEO_PATH, AUDIO_PATH, words_timestamps, OUTPUT_VIDEO)
    print("Video saved to ", OUTPUT_VIDEO)
    
if __name__ == "__main__":
    main()