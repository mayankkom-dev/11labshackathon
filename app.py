import streamlit as st
from moviepy.editor import VideoFileClip
import base64
import time
from magic_dub import streamlit_wrap_run, get_total_num_scenes

# import subprocess

# # Execute the shell script to install FFmpeg
# try:
#     subprocess.run(["./install_ffmpeg.sh"], check=True, shell=True)
# except subprocess.CalledProcessError as e:
#     st.error(f"Error installing FFmpeg: {e}")
#     exit(1)

# Backend function for processing
def process_data(scene, window):
    # Your backend processing logic here
    # Replace this with your actual processing code
    # Simulate processing delay with time.sleep (remove in production)
    time.sleep(5)

    # For the demonstration purpose, assume the video file locations
    v1_file_loc = "clip_srt/hindi_movie_clip_2.mp4"
    v2_file_loc = "clip_srt/hindi_movie_clip_2_clone.mp4"

    return v1_file_loc, v2_file_loc

# Function to read video data as bytes
def read_video_bytes(video_file_path):
    with open(video_file_path, "rb") as f:
        video_bytes = f.read()
    return video_bytes

# Streamlit UI
def main():
    st.title("Magic Dub + 11Labs")

    
    max_value = get_total_num_scenes()
    # Slider widget to select a value for the numerical variable
    numerical_variable = st.slider("Scene Num", min_value=0, max_value=max_value, value=10)

    # Number input box to allow manual input of a value for the numerical variable
    scene_num = st.number_input("Or enter a value", min_value=0, max_value=max_value, value=numerical_variable)

    # Display the selected value
    st.write("Selected Scene Num:", scene_num)

    # Dropdowns for scene and window
    scene_window = st.selectbox("Select Scene Window", [20, 30, 40, 50, 60, 100])
    
    clip_id = st.text_input("Clip ID", "1")
    num_speakers = st.selectbox("Number of Speakers", [1, 2, 3, 4])

    # Initialize video file locations
    v1_file_loc = None
    v2_file_loc = None

    # Process button
    if st.button("Process"):
        with st.spinner("Processing in progress..."):
            # Backend processing
            streamlit_wrap_run(scene_num, scene_window, clip_id, num_speakers)
            v1_file_loc = f"clip_srt/hindi_movie_clip_{clip_id}.mp4"
            v2_file_loc = f"clip_srt/hindi_movie_clip_{clip_id}_clone.mp4"

        # Display response
        st.info("Processing completed")

    if v1_file_loc and v2_file_loc:
        try:
            # Enable the first video player
            video1_bytes = read_video_bytes(v1_file_loc)
            st.header(f"Hindi Movie Clip {clip_id}")
            st.video(video1_bytes)

            # Enable the second video player
            video2_bytes = read_video_bytes(v2_file_loc)
            st.header(f"Magic Dub Hindi Movie Clip {clip_id}")
            st.video(video2_bytes)

            # Download button for the second video
            st.markdown(get_video_download_link(v2_file_loc), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error displaying the videos: {e}")
            st.info("Please check if the videos are valid and try again.")

def get_video_download_link(file_path):
    """Generates a link allowing the video to be downloaded."""
    with open(file_path, "rb") as f:
        video_data = f.read()
    video_base64 = base64.b64encode(video_data).decode("utf-8")
    return f'<a href="data:video/mp4;base64,{video_base64}" download="video.mp4">Download Video 2</a>'

if __name__ == "__main__":
    main()
