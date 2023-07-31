import re, os
from moviepy.editor import VideoFileClip
from datetime import datetime, timedelta, time
from elevenlabs import set_api_key
set_api_key("f7497c486bd3da39ec2c29f31dcf7d05")

def convert_to_sec(srt_time_str):
    """Converts a srt format time string into seconds for moviepy."""
    h, m, s = srt_time_str.split(':')
    return float(h) * 3600 + float(m) * 60 + float(s.replace(',', '.'))

def find_nearest_time(start_time):
    return start_time

def generate_clips(input_file, output_file, start_time, end_time):
    try:
        video_clip = VideoFileClip(input_file).subclip(start_time-1, end_time)
        video_clip.write_videofile(output_file)
        video_clip.close()
        print("Video clip successfully created!")
    except Exception as e:
        print("Error:", e)

def read_srt_content(input_srt):
    with open(input_srt, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    return srt_content

def extract_srt_info_with_dialogues(srt_content):
    # Use regex to find all subtitle blocks in the SRT content
    subtitle_blocks = re.findall(r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n([\s\S]*?)(?=\n\n\d+\n|$)', srt_content)

    # Extract and store the scenenum, start_time, end_time, and dialogues for each block
    srt_info_list = []
    for block in subtitle_blocks:
        scenenum = block[0]
        start_time = block[1]
        end_time = block[2]
        dialogues = block[3].strip()
        srt_info_list.append((scenenum, start_time, end_time, dialogues))

    return srt_info_list

def convert_time_to_timedelta(time_obj, clip_offset=1):
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second, microseconds=time_obj.microsecond)

def convert_timedelta_to_time(timedelta_obj):
    total_seconds = timedelta_obj.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = int((seconds % 1) * 1e6)
    return time(int(hours), int(minutes), int(seconds), microsecond=microseconds)

def offset_clip_srt(srt_tuples, clip_offset=1):

    # Extract the start time from the first tuple
    start_time = datetime.strptime(srt_tuples[0][1], '%H:%M:%S,%f').time()

    # Calculate the offset time in datetime.timedelta format
    offset_time = convert_time_to_timedelta(start_time)

    # Adjust all the time tuples in the list
    adjusted_time_tuples = []
    for idx, time_tuple in enumerate(srt_tuples):
        subtitle_id, start, end, text = time_tuple
        start_time = datetime.strptime(start, '%H:%M:%S,%f').time()
        end_time = datetime.strptime(end, '%H:%M:%S,%f').time()
        
        # Apply the offset to adjust the times
        adjusted_start_time = convert_timedelta_to_time(convert_time_to_timedelta(start_time) - offset_time + timedelta(seconds=clip_offset))
        adjusted_end_time = convert_timedelta_to_time(convert_time_to_timedelta(end_time) - offset_time + timedelta(seconds=clip_offset))
        
        # Convert adjusted times back to string format
        adjusted_start_str = adjusted_start_time.strftime('%H:%M:%S,%f')[:-3]  # Remove the last 3 digits for millisecond precision
        adjusted_end_str = adjusted_end_time.strftime('%H:%M:%S,%f')[:-3]      # Remove the last 3 digits for millisecond precision
        
        # Append the adjusted tuple to the new list
        adjusted_time_tuples.append((subtitle_id, adjusted_start_str, adjusted_end_str, text))

    # Print the adjusted time tuples
    # for adjusted_tuple in adjusted_time_tuples:
    #     print(adjusted_tuple)
    return adjusted_time_tuples

def format_time(time_str):
    # Get the time and milliseconds parts
    time_part, milliseconds_part = time_str[:-4], time_str[-3:]

    # Add leading zeros to the milliseconds part to ensure 3 digits
    formatted_milliseconds = milliseconds_part.zfill(3)

    # Combine the time and formatted milliseconds
    return f"{time_part},{formatted_milliseconds}"

def convert_date(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M:%S,%f').time()
    return time_obj

def write_srt_content(adjusted_srt_tuples, output_srt=None):
    # Create an empty string to store the formatted SRT content
    srt_content = ""

    # Loop through the adjusted_time_tuples list and format each tuple
    for idx, time_tuple in enumerate(adjusted_srt_tuples):
        subtitle_id, start, end, text = time_tuple

        # Format the subtitle time
        formatted_time = f"{format_time(start)} --> {format_time(end)}"

        # Concatenate the formatted SRT content
        srt_content += f"{idx+1}\n{formatted_time}\n{text}\n"

        # Add an extra line break after each subtitle, except for the last one
        if idx < len(adjusted_srt_tuples) - 1:
            srt_content += "\n"

    # Print the complete formatted SRT content
    print(srt_content)

    # Write the formatted SRT content to a new file
    with open(output_srt, "w") as f:
        f.write(srt_content)
    return srt_content

def dump_offset_srt_clip(input_srt, output_srt, start_time, end_time):
    srt_content = read_srt_content(input_srt)
    srt_info_list = extract_srt_info_with_dialogues(srt_content)
    start_idx = [i for i, srt_info in enumerate(srt_info_list) if convert_date(srt_info[1]) <= convert_date(start_time) and   convert_date(start_time) <= convert_date(srt_info[2])][0]
    end_idx = [i for i, srt_info in enumerate(srt_info_list) if convert_date(srt_info[1]) <= convert_date(end_time) and   convert_date(end_time) <= convert_date(srt_info[2])][0]
    clip_srt_tuple = srt_info_list[start_idx:end_idx+1]
    adjusted_srt_tuples = offset_clip_srt(clip_srt_tuple)
    adjusted_srt_str = write_srt_content(adjusted_srt_tuples, output_srt)
    return clip_srt_tuple, adjusted_srt_str


def convert_mp4_to_audio(input_file, output_file, audio_codec='mp3'):
    # Load the video clip
    video_clip = VideoFileClip(input_file)

    # Extract the audio from the video
    audio_clip = video_clip.audio
    # audio_clip = audio_clip.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    # Set the audio codec for the output audio file (default: mp3)
    audio_codec = audio_codec.lower()

    # Choose the output file extension based on the audio codec
    if audio_codec == 'wav':
        output_file = output_file.replace('.mp3', '.wav')
    ffmpeg_params = ["-ac", "1", "-ar", "16000"]
    
    # Write the audio to the output file
    audio_clip.write_audiofile(output_file, codec=audio_codec, ffmpeg_params=ffmpeg_params)

    # Close the video and audio clips
    video_clip.close()
    audio_clip.close()

def generate_audo_clip(input_file, output_clip, clip_srt_tuple):
    base_name = os.path.basename(output_clip).split(".")[0]
    outfolder = f'clip_audio_seg/{base_name}'
    os.makedirs(outfolder, exist_ok=True)
    video_clip = VideoFileClip(input_file)
    all_sub_scene = []
    # start_time, end_time = convert_to_sec(clip_srt_tuple[0][1])-0.2, convert_to_sec(clip_srt_tuple[-1][2])+0.2
    for scene_num, clip_info in enumerate(clip_srt_tuple):
        clip = video_clip.subclip(convert_to_sec(clip_info[1])-0.2, convert_to_sec(clip_info[2])+0.2)
        sence_sub = clip_info[3]
        clip_duration = clip.duration - 0.4
        all_sub_scene.append((sence_sub, clip_duration))
        ffmpeg_params = ["-ac", "1", "-ar", "16000"]
        try:
            clip.audio.write_audiofile(f"{outfolder}/audio_{scene_num+1}.wav", ffmpeg_params=ffmpeg_params)
        except:
            print(f"Error in writing audio file for {scene_num+1}")

    # dump all_sub_scene
    with open(f"clip_srt/{base_name}.txt", "w") as fp:
        fp.write("\n\n".join([sub_scene for sub_scene, _ in all_sub_scene]))
    return all_sub_scene

def generate_clips_srt(input_file, input_srt, output_file, output_srt, start_time_srt, end_time_srt):   
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    start_time_srt_sec = convert_to_sec(start_time_srt)
    end_time_srt_sec = convert_to_sec(end_time_srt)
    generate_clips(input_file, output_file, start_time_srt_sec, end_time_srt_sec)
    print(output_file)
    clip_srt_tuple, adjusted_srt_str = dump_offset_srt_clip(input_srt, output_srt, start_time_srt, end_time_srt)
    output_file_mp3 = os.path.join(f'clip_srt/{os.path.basename(output_file).split(".")[0]}.wav')
    print(output_file_mp3)
    # convert_mp4_to_audio(input_file, output_file_mp3)
    convert_mp4_to_audio(output_file, output_file_mp3)
    return clip_srt_tuple


import sys
sys.path.append('GenderDetect-master/gdetect/')
import genderdetect as gd
from simple_diarizer.diarizer import Diarizer
from simple_diarizer.utils import (check_wav_16khz_mono, convert_wavfile,
                                   waveplot, combined_waveplot, waveplot_perspeaker)
from elevenlabs_utils import clone_voice, fetch_history, generate_voice, save_audio, get_voices
import os
import tempfile
from pprint import pprint
from collections import defaultdict
import matplotlib.pyplot as plt
import soundfile as sf
from moviepy.editor import AudioFileClip
import subprocess
from IPython.display import Audio, display, HTML
from tqdm.autonotebook import tqdm
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
from elevenlabs import voices

def generate_diarize_segments(num_speaker=2, srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1"):
    yt_file = f"{srt_scene_audio_dir}/{clip_name}.wav"
    wav_file = convert_wavfile(yt_file, f"{yt_file.split('.')[0]}_converted.wav")
    
    signal, fs = sf.read(wav_file)
    os.makedirs('temp_segments', exist_ok=True)
    # print(f"wav file: {wav_file}")
    try:
        diar = Diarizer(
            embed_model='ecapa', # supported types: ['xvec', 'ecapa']
            cluster_method='ahc', # supported types: ['ahc', 'sc']
            window=1.0, # size of window to extract embeddings (in seconds)
            period=0.5, # hop of window (in seconds)
        )
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

    segments = diar.diarize(wav_file, 
                            num_speakers=num_speaker, # None
                            threshold=1e-1,
                            outfile=f"{wav_file.split('.')[0]}.rttm")
    return segments, signal, fs

def convert_timestamp_to_seconds(timestamp):
    # Split the timestamp into components: hours, minutes, seconds, and milliseconds
    hours, minutes, seconds = map(float, timestamp.replace(',', '.').split(':'))
    # Calculate the total time in seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

def extract_dialogues(dialogue_text, start_time, end_time):
    extracted_dialogues = []
    lines = dialogue_text.split('\n\n')
    
    for line in lines:
        # Split the line into individual components: dialogue number, timestamps, and dialogue text
        parts = line.split('\n')
        dialogue_number = parts[0]
        timestamps = parts[1]
        dialogue_text = '\n'.join(parts[2:])
        
        # Extract start and end times in seconds
        start_timestamp = convert_timestamp_to_seconds(timestamps.split(' --> ')[0])
        end_timestamp = convert_timestamp_to_seconds(timestamps.split(' --> ')[1])

        # Check if the dialogue falls within the specified time range
        if start_timestamp <=  start_time <= end_timestamp or start_timestamp <= end_time <= end_timestamp:
            extracted_dialogues.append((dialogue_number, timestamps, dialogue_text))
    return extracted_dialogues

def extract_diar_seg_scene_dialogue(segments, srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1"):
    # Sample dialogue text
    with open(f'{srt_scene_audio_dir}/{clip_name}.srt', 'r') as f:
        dialogue_text = f.read()

    all_seg_extracted_dialogues = []
    
    for seg in segments:
        start_time = seg['start']
        end_time = seg['end']
        extracted_dialogues = extract_dialogues(dialogue_text, start_time, end_time)
        # print(extracted_dialogues)
        all_seg_extracted_dialogues.append(extracted_dialogues)
    return all_seg_extracted_dialogues

def generate_scene_segment_map(segments, segment_scene_map):
    reverse_scene_segment_map = defaultdict(list)
    for seg, srt_scene in segment_scene_map.items():
        if srt_scene is not None:
            reverse_scene_segment_map[srt_scene].append(seg)
            
    reverse_scene_segment_map['special'] = [segments[seg] for seg, srt_scene in segment_scene_map.items() if srt_scene is None]
    return reverse_scene_segment_map

def identify_speaker_num(segments, segment_list):
    speaker_label = [segments[seg_id]['label'] for seg_id in segment_list]
    num_speaker = len(set(speaker_label))
    return num_speaker, speaker_label 

def generate_diar_seg_audio(segments, segment_scence_num, scene_num, srt_scene_audio_dir="clip_srt",
                                 clip_name='hindi_movie_clip_1', outfolder = "diar_audio_seg"):
    
    segment_scence_info = segments[segment_scence_num]
    input_file = os.path.join(srt_scene_audio_dir, f'{clip_name}.wav')
    audio_clip = AudioFileClip(input_file)
    start = segment_scence_info['start']
    end = segment_scence_info['end']
    
    out_path = f'{outfolder}/{clip_name}/audio_diar_seg_{segment_scence_num}_{scene_num}_scene.wav'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    clip = audio_clip.subclip(start, end)
    ffmpeg_params = ["-ac", "1", "-ar", "16000"]
    clip.write_audiofile(out_path, ffmpeg_params=ffmpeg_params)
    return out_path

def fetch_gender_srt_scene(scene_num, srt_scene_audio_dir="clip_audio_seg", clip_name="hindi_movie_clip_1"):
    srt_scene_audio_file = os.path.join(srt_scene_audio_dir, clip_name, f"audio_{scene_num}.wav")
    gender = gd.identify_gender(srt_scene_audio_file)
    return gender

def fetch_gender_diar(segments, segment_scence_num, scene_num, srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1"):
    # segment_scence_info is segments_dict
    diar_scene_audio_file = generate_diar_seg_audio(segments, segment_scence_num, scene_num, srt_scene_audio_dir, clip_name)
    gender = gd.identify_gender(diar_scene_audio_file)
    return gender

def convert_to_sec(srt_time_str):
    """Converts a srt format time string into seconds for moviepy."""
    h, m, s = srt_time_str.split(':')
    return float(h) * 3600 + float(m) * 60 + float(s.replace(',', '.'))

def fetch_scence_duration(scene_num, srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1"):
    with open(os.path.join(srt_scene_audio_dir, f"{clip_name}.srt"), "r") as fp:
        lines = fp.read()

    scene_list = lines.split("\n\n")
    try:
        duration = scene_list[scene_num-1].split("\n")[1]
        start, end = duration.split(" --> ")
        duration_time = convert_to_sec(end) - convert_to_sec(start)
    except:
        duration_time = 0
        start = 0
        end = 0
    return convert_to_sec(start), convert_to_sec(end), round(duration_time, 2)


def fetch_total_scene(srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1"):
    with open(os.path.join(srt_scene_audio_dir, f"{clip_name}.srt"), "r") as fp:
        lines = fp.read()

    scene_list = lines.split("\n\n")
    return len(scene_list)

def fetch_text_srt_scene(scene_num, srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1"):
    with open(os.path.join(srt_scene_audio_dir, f"{clip_name}.srt"), "r") as fp:
        lines = fp.read()

    scene_list = lines.split("\n\n")
    scene_dialogue = scene_list[scene_num-1].split("\n")[2:]
    scene_dialogue = " ".join(scene_dialogue)
    start, end, scene_duration = fetch_scence_duration(scene_num, clip_name=clip_name)
    return scene_dialogue, scene_duration, start, end

def fetch_text_diar_srt_scene(segments, segment_scence_num, scene_num, 
                              reverse_scene_segment_map, srt_scene_audio_dir="clip_srt",
                               clip_name="hindi_movie_clip_1"):
    # segment_scence_info is segments_dict
    scene_text, scene_duration, start_, end_ = fetch_text_srt_scene(scene_num, clip_name=clip_name)
    num_of_diar_seg = len(reverse_scene_segment_map[scene_num])
    
    diar_segment_duration = segments[segment_scence_num]['end'] - segments[segment_scence_num]['start']
    all_diag = scene_text.split('-')
    print(len(all_diag), all_diag)
    if len(all_diag) == num_of_diar_seg:
        # find index of segment_scence_num in reverse_scene_segment_map[scene_num]
        diar_seg_idx = reverse_scene_segment_map[scene_num].index(segment_scence_num)
        diar_seg_text = all_diag[diar_seg_idx]
    elif len(all_diag) == 2:
        # sort all_diag by length
        all_diag.sort(key=len)
        if diar_segment_duration >= scene_duration/2:
            diar_seg_text = all_diag[0]
        else:
            diar_seg_text = all_diag[1]
    else:
        if diar_segment_duration >= scene_duration/2:
            diar_seg_text = all_diag[0]
        else:
            diar_seg_text = ""

        
    return diar_seg_text, diar_segment_duration, segments[segment_scence_num]['start'], segments[segment_scence_num]['end']


def fetch_sentiment_diar_srt_scene(segments, seg, scene_num, srt_scene_audio_dir="diar_audio_seg", clip_name="hindi_movie_clip_1"):
    
    # run as subprocess # python3 examples/OpenVokaWavMean.py path_to_sound_file.wav

    scene_audio_file = os.path.join(srt_scene_audio_dir, clip_name, f"audio_diar_seg_{seg}_{scene_num}_scene.wav")
    print(scene_audio_file)

    # subprocess run and capture print output change workind directory
    output = subprocess.run(["python3", "examples/OpenVokaWavMean.py", f"../../{scene_audio_file}"], capture_output=True, cwd="OpenVokaturi-4-0/OpenVokaturi-4-0")
    output_str = output.stdout.decode()
    sentiment_debug = output_str.strip().split('\n')[-5:]
    # print(output_str)
    sentiment_dict = {sent_score.split(':')[0]: float(sent_score.split(':')[1].strip()) for sent_score in sentiment_debug }  
    sentiment_max = max(sentiment_dict, key=sentiment_dict.get)
    return sentiment_dict, sentiment_max

def fetch_sentiment_srt_scene(scene_num, srt_scene_audio_dir="clip_audio_seg", clip_name="hindi_movie_clip_1"):
    
    # run as subprocess # python3 examples/OpenVokaWavMean.py path_to_sound_file.wav

    scene_audio_file = os.path.join(srt_scene_audio_dir, clip_name, f"audio_{scene_num}.wav")
    print(scene_audio_file)

    # subprocess run and capture print output change workind directory
    output = subprocess.run(["python3", "examples/OpenVokaWavMean.py", f"../../{scene_audio_file}"], capture_output=True, cwd="OpenVokaturi-4-0/OpenVokaturi-4-0")
    output_str = output.stdout.decode()
    # print(output_str)
    sentiment_debug = output_str.strip().split('\n')[-5:]
    sentiment_dict = {sent_score.split(':')[0]: float(sent_score.split(':')[1].strip()) for sent_score in sentiment_debug }  
    sentiment_max = max(sentiment_dict, key=sentiment_dict.get)
    return sentiment_dict, sentiment_max

# iterate on reverse_scene_segment_map
# know overall clip global : num_speaker
# and generate each scene required stats 
# (combined/avg) : senitment/emtotion, identify_gender, identify_speaker, 
# end goal tts for srt dial
def generate_tts_ready_dict(segments, reverse_scene_segment_map, clip_name):
    final_tts_rady_scene_li_dict = []
    speaker_label_to_gender = defaultdict(list)
    total_scene = fetch_total_scene(clip_name=clip_name)
    for scene_num, segment_list in reverse_scene_segment_map.items():
        if scene_num == "special":
            continue
        final_tts_rady_scene_dict = {}
        final_tts_rady_scene_dict['scene_num'] = scene_num
        print("scene_num: ", scene_num)
        print("segment_list: ", segment_list)
        num_speaker, speaker_label = identify_speaker_num(segments, segment_list)
        print("num_speaker: ", num_speaker)
        print("speaker_label: ", speaker_label)
        if num_speaker > 1:
            for _, speaker_label_, seg in zip(range(num_speaker), speaker_label, segment_list):
                final_tts_rady_sub_scene_dict = {}
                final_tts_rady_sub_scene_dict['scene_num'] = scene_num
                gender = fetch_gender_diar(segments, seg, scene_num, clip_name=clip_name)
                # final_tts_rady_sub_scene_dict['gender'] = gender
                final_tts_rady_sub_scene_dict['speaker_label'] = f'{speaker_label_}'
                # _, sentiment_max = fetch_sentiment_diar_srt_scene(segments, seg, scene_num)
                final_tts_rady_sub_scene_dict['sentiment'] = 'none'
                speaker_label_to_gender[speaker_label_].append(gender)
                text, duration, start_, end_ = fetch_text_diar_srt_scene(segments, seg, scene_num, 
                                                                         reverse_scene_segment_map,
                                                                         clip_name=clip_name)
                final_tts_rady_sub_scene_dict['text'] = text
                final_tts_rady_sub_scene_dict['duration'] = duration
                final_tts_rady_sub_scene_dict['start'] = start_
                final_tts_rady_sub_scene_dict['end'] = end_
                final_tts_rady_scene_li_dict.append(final_tts_rady_sub_scene_dict)

        else:
            gender = fetch_gender_srt_scene(scene_num, clip_name=clip_name)
            # final_tts_rady_scene_dict['gender'] = gender
            final_tts_rady_scene_dict['speaker_label'] = f'{speaker_label[0]}'
            speaker_label_to_gender[speaker_label[0]].append(gender)
            text, duration, start_, end_ = fetch_text_srt_scene(scene_num, clip_name=clip_name)
            final_tts_rady_scene_dict['text'] = text
            final_tts_rady_scene_dict['duration'] = duration
            final_tts_rady_scene_dict['start'] = start_
            final_tts_rady_scene_dict['end'] = end_
            # _, sentiment_max = fetch_sentiment_srt_scene(scene_num)
            final_tts_rady_scene_dict['sentiment'] = 'none'
            final_tts_rady_scene_li_dict.append(final_tts_rady_scene_dict)

    last_scene_num = list(reverse_scene_segment_map.keys())[-2] if 'special' in reverse_scene_segment_map.keys() else list(reverse_scene_segment_map.keys())[-1]
    if int(last_scene_num) < total_scene:
        for scene_ in range(last_scene_num+1, total_scene+1):
            final_tts_rady_scene_dict = {}
            final_tts_rady_scene_dict['scene_num'] = scene_
            final_tts_rady_scene_dict['speaker_label'] = f'{speaker_label[0]}'
            # speaker_label_to_gender[speaker_label[0]].append(gender)
            text, duration, start_, end_ = fetch_text_srt_scene(scene_, clip_name=clip_name)
            final_tts_rady_scene_dict['text'] = text
            final_tts_rady_scene_dict['duration'] = duration
            final_tts_rady_scene_dict['start'] = start_
            final_tts_rady_scene_dict['end'] = end_
            # _, sentiment_max = fetch_sentiment_srt_scene(scene_)
            final_tts_rady_scene_dict['sentiment'] = 'none'
            final_tts_rady_scene_li_dict.append(final_tts_rady_scene_dict)
    
    speaker_label_to_gender_map = {speaker_id: max(gender_list) for speaker_id, gender_list in speaker_label_to_gender.items()}
    
    for tts_info_dict in final_tts_rady_scene_li_dict:
        tts_info_dict['gender'] = speaker_label_to_gender_map[int(tts_info_dict['speaker_label'])]
    
    return final_tts_rady_scene_li_dict, speaker_label_to_gender_map

def generate_speaker_scene_map(final_tts_rady_scene_li_dict):
    # generate speaker_label to scene_list mapping
    speaker_label_to_scene_list = defaultdict(list)
    for tts_info_dict in final_tts_rady_scene_li_dict:
        speaker_label_to_scene_list[tts_info_dict['speaker_label']].append(tts_info_dict['scene_num'])
    return speaker_label_to_scene_list

def convert_to_suffix_array(arr):
    frequency_dict = {}
    result = []

    for num in arr:
        if num not in frequency_dict:
            frequency_dict[num] = 1
            result.append(num)
        else:
            frequency_dict[num] += 1
            result.append(f"{num}_{frequency_dict[num]}")

    return result

def read_audio_file(file_path):
    with open(file_path, 'rb') as f:
        audio_data = f.read()

    # Use pydub to create an AudioSegment from the audio data
    audio_segment = AudioSegment.from_file(file_path)

    return audio_segment

def stretch_audio(audio_segment, new_duration):
    current_duration = len(audio_segment)
    stretch_factor = new_duration / current_duration

    # Speed up or slow down the audio segment to match the desired duration
    if stretch_factor > 1.0:
        stretched_audio = audio_segment.speedup(playback_speed=stretch_factor)
    else:
        stretched_audio = audio_segment.speedup(playback_speed=1/stretch_factor)


    return stretched_audio

def extend_audio_with_filler(audio_segment, desired_duration):
    current_duration = len(audio_segment)

    # Calculate the duration difference
    duration_difference = desired_duration - current_duration

    # Calculate the number of silent segments to insert
    num_silent_segments = int(duration_difference / 1000)  # Convert to seconds

    # Create the silent segment to be inserted
    if num_silent_segments > 0:
        silence_segment = AudioSegment.silent(duration=duration_difference // num_silent_segments)

        # Insert the silent segments between original audio segments
        extended_audio = audio_segment
        for _ in range(num_silent_segments):
            extended_audio += silence_segment + audio_segment

        return extended_audio
    else:
        return audio_segment
    
    
clone_audio_time_seg_per_scene = lambda scene_num, clone_audio_time_seg : [fnm_tup for fnm_tup in clone_audio_time_seg if int(fnm_tup[0].split('.')[0].split('_')[1])==scene_num]

def generate_merge_clone_audio(clone_audio_time_seg, srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1", clone_scene_audio_dir="clone_clip_audio_seg"):
    # Load the actual audio file
    actual_audio = AudioSegment.from_wav(f"{srt_scene_audio_dir}/{clip_name}.wav")
    actual_audio = actual_audio - 20
    for scene_num in range(1, len(clone_audio_time_seg)): # wrong loop but extra seg will not harm
        clone_audio_list = clone_audio_time_seg_per_scene(scene_num, clone_audio_time_seg)
        start_time, end_time, scene_dur = fetch_scence_duration(scene_num, clip_name=clip_name)
        if scene_dur==0:
            continue
        all_clone_audio = []
        for clone_fnm, time_seg in clone_audio_list:
            clone_audio = read_audio_file(f"{clone_scene_audio_dir}/{clip_name}/{clone_fnm}")
            all_clone_audio.append(clone_audio)
        
        if all_clone_audio:
            if len(all_clone_audio)>1:
                clone_audio = all_clone_audio[0]
                for i in range(1, len(all_clone_audio)):
                    # add silence in between
                    silence = AudioSegment.silent(duration=1000)
                    clone_audio = clone_audio + silence + all_clone_audio[i]
            else:
                clone_audio = all_clone_audio[0]
        


            # Split the actual audio into two segments at the insertion point
            # actual_audio_before = actual_audio[:int(start_time * 1000)]  # Convert start_time to milliseconds
            # actual_audio_after = actual_audio[int(end_time * 1000):]  # Convert end_time to milliseconds
            # clone_audio_streched = stretch_audio(clone_audio, int(scene_dur * 1000) )
            # # Mix the overlapping parts together
            # overlapped_segment = actual_audio_before + clone_audio_streched + actual_audio_after
            # actual_audio = overlapped_segment
            clone_audio_extended = extend_audio_with_filler(clone_audio, scene_dur+1)
            actual_audio = actual_audio.overlay(clone_audio_extended, position=int(start_time * 1000))

        
    actual_audio.export(f"{srt_scene_audio_dir}/{clip_name}_clone.wav", format="wav")
    return actual_audio


def generate_dub_video(srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1"):
    clip_mp4 = f"{srt_scene_audio_dir}/{clip_name}.mp4"
    dub_audio = f"{srt_scene_audio_dir}/{clip_name}_clone.wav"
    video_clip = VideoFileClip(clip_mp4)
    dub_audio_clip = AudioFileClip(dub_audio)
    video_clip.audio = dub_audio_clip
    video_clip.write_videofile(f"{srt_scene_audio_dir}/{clip_name}_clone.mp4")
    

def translate_clip(input_file, input_srt, output_file, output_srt, start_time_srt, end_time_srt, 
                   num_speaker=2, srt_scene_audio_dir="clip_srt", clip_name="hindi_movie_clip_1", clone_new=False):
    # genreate clip and srt
    clip_srt_tuple = generate_clips_srt(input_file, input_srt, output_file, output_srt, start_time_srt, end_time_srt)
    # preprocessing to generate required sub_scene_audios
    all_sub_scene = generate_audo_clip(input_file, output_file, clip_srt_tuple)
    
    segments, signal, fs = generate_diarize_segments(num_speaker=num_speaker, srt_scene_audio_dir=srt_scene_audio_dir, clip_name=clip_name)

    all_seg_extracted_dialogues = extract_diar_seg_scene_dialogue(segments, srt_scene_audio_dir=srt_scene_audio_dir, clip_name=clip_name)
    
    segment_scene_map =  { diag_seg_idx: int(srt_scene_info[0][0]) if srt_scene_info else None for diag_seg_idx, srt_scene_info in enumerate(all_seg_extracted_dialogues)}
    reverse_scene_segment_map = generate_scene_segment_map(segments, segment_scene_map)
    
    final_tts_rady_scene_li_dict, speaker_label_to_gender_map = generate_tts_ready_dict(segments, reverse_scene_segment_map, clip_name=clip_name)
    
    speaker_label_to_scene_list = generate_speaker_scene_map(final_tts_rady_scene_li_dict)
    if clone_new:
        speaker_label_to_voice = {}
        for spkr_label, scene_num_list in speaker_label_to_scene_list.items():
            try:
                temp =  clone_voice(scene_num_list, spkr_label, 
                                    speaker_label_to_gender_map[int(spkr_label)], 
                                    srt_scene_audio_dir='clip_audio_seg', 
                                    clip_name=clip_name) 
            except Exception as e:
                print(f"Exception in cloning voice for speaker label {spkr_label}")
                print(e)
                temp =  voices()[-1]

            speaker_label_to_voice[spkr_label] = temp
    # generate cloned audio
    scene_seg_num = convert_to_suffix_array([info_dict['scene_num'] for info_dict in final_tts_rady_scene_li_dict])
    for tts_info_dict, scene_seg_ in zip(final_tts_rady_scene_li_dict, scene_seg_num):
        gender = tts_info_dict['gender']
        spkr_label = tts_info_dict['speaker_label']
        scene_num = tts_info_dict['scene_num']

        clone_voice_name = f'{clip_name}_{gender}_{spkr_label}'
        outfile_name = f"audio_{scene_seg_}_{gender}_{spkr_label}.wav"
        print(str(tts_info_dict['text']))
        try:
            generate_voice(str(tts_info_dict['text']), clone_voice_name, 
                        outfile_name, dump=True, srt_scene_audio_dir="clone_clip_audio_seg",
                            clip_name=clip_name)
        except Exception as e:
            clone_voice_name = 'hindi_movie_clip_1_M_0'
            generate_voice(str(tts_info_dict['text']), clone_voice_name, 
                        outfile_name, dump=True, srt_scene_audio_dir="clone_clip_audio_seg",
                            clip_name=clip_name)
    
    clone_audio_time_seg = [(f"audio_{scene_seg_}_{tts_info['gender']}_{tts_info['speaker_label']}.wav" , (tts_info['start'], tts_info['end'])) for tts_info, scene_seg_ in zip(final_tts_rady_scene_li_dict, scene_seg_num)]
    generate_merge_clone_audio(clone_audio_time_seg, clip_name=clip_name)
    generate_dub_video(clip_name=clip_name)

def fetch_scene_time(scene_num, window, srt_file_path='raw_file/hindi_movie_eng_srt.srt'):
    with open(srt_file_path, 'r') as f:
        dialogue_text = f.read()

    lines = dialogue_text.split('\n\n')
    
    start_timestamp, end_timestamp = None, None
    
    for line in lines:
        # Split the line into individual components: dialogue number, timestamps, and dialogue text
        parts = line.split('\n')
        dialogue_number = parts[0]
        if dialogue_number == str(scene_num):    
            timestamps = parts[1]
            # Extract start and end times in seconds
            start_timestamp = timestamps.split(' --> ')[0]
        if dialogue_number == str(scene_num + window):
            timestamps = parts[1]
            end_timestamp = timestamps.split(' --> ')[1]
        if start_timestamp and end_timestamp:
            break
    return start_timestamp, end_timestamp
            
def get_total_num_scenes(srt_file_path='raw_file/hindi_movie_eng_srt.srt'):
    with open(srt_file_path, 'r') as f:
        dialogue_text = f.read()

    lines = dialogue_text.split('\n\n')

    return len(lines)

def streamlit_wrap_run(scene_num_st, scene_window, id, num_speaker):
    
    start_time_srt, end_time_srt = fetch_scene_time(scene_num_st, scene_window, 
                                        "raw_file/hindi_movie_eng_srt.srt")
    
    start_time_srt_sec = convert_to_sec(start_time_srt)
    end_time_srt_sec = convert_to_sec(end_time_srt)

    print("Start time: ", start_time_srt, start_time_srt_sec)
    print("End time: ", end_time_srt, end_time_srt_sec)

    input_file = "raw_file/hindi_movie.mp4"
    input_srt = "raw_file/hindi_movie_eng_srt.srt"

    output_file = f"clip_srt/hindi_movie_clip_{id}.mp4"
    output_srt = f"clip_srt/hindi_movie_clip_{id}.srt"


    translate_clip(input_file, input_srt, output_file, output_srt, 
                start_time_srt, end_time_srt, num_speaker=num_speaker, 
                srt_scene_audio_dir="clip_srt", 
                clip_name=f"hindi_movie_clip_{id}", 
                clone_new=True)
    return True