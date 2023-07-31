from elevenlabs import clone, generate, play, set_api_key, voices
from elevenlabs.api import History
import os
set_api_key("f7497c486bd3da39ec2c29f31dcf7d05")

def get_voices():
    names = []

    v_list = voices()

    for v in v_list:
        names.append(v.name)

    return names

def clone_voice(scene_list, spkr_id, spkr_gender, srt_scene_audio_dir="clip_audio_seg", clip_name="hindi_movie_clip_1"):
    
    scene_files = [ f'{srt_scene_audio_dir}/{clip_name}/audio_{scene_num}.wav' for scene_num in scene_list]
    voice = clone(
        name=f"{clip_name}_{spkr_gender}_{spkr_id}",
        description=f"Clone {clip_name}_{spkr_gender}_{spkr_id}",
        files=scene_files,
    )
    return voice

def fetch_history():
    history = History.from_api()
    print(history)
    return history

def save_audio(audio, output_file):
    try:
        with open(output_file, 'wb') as f:
            f.write(audio)
    
    except Exception as e:
        print(e)
        return ""

def generate_voice(text, voice, output_file, dump=True, srt_scene_audio_dir="clone_clip_audio_seg", clip_name="hindi_movie_clip_1"):
    audio = generate(text=text, voice=voice)
    if dump:
        output_loc = f"{srt_scene_audio_dir}/{clip_name}/{output_file}"
        os.makedirs(os.path.dirname(output_loc), exist_ok=True)
        save_audio(audio, output_loc)
    return