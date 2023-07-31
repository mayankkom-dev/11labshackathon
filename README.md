Magic Dub + 11Labs 

Solution is as part of Hackathon hosted on lablab.ai by 11Labs.

The solution is a POC uitlity of TTS for translating a movie into English using provided subtitles and voice analytics, cloning and TTS. 

The raw_file should contains 2 files - hindi_movie.mp4 and hindi_movie_eng_srt.srt. The movie is a Bollywood Romcom movie and is freely available on youtube, and still will be taken down if requested. The files are included in the gdrive link.
'''https://tinyurl.com/5zuc79b5'''

The project is built using conda-python3.10 and the enviroment is exported for reproducibility using ``conda env export > environment.yml``

You can use the project by installing anaconda/miniconda and then using terminal
    - ``` conda env create -f environment.yml```

Once environment is set. You can launch the streamlit app locally using the command 
    ``` streamlit run app.py ```

Next on the screen, currently, the tool is configured just for the movie in raw_files with the acurate subtitles in english. Provided these, next the image below shows the Magic Dub Control. To prove the POC, the tool allow to select any scene_num as starting scene with selected scene window (num of next scene to include), Clip ID(Unique Number), Num of Speaker(Currently we need to specify :/)
![Magic Dub Control](img/MagicDubControl.png)

And post this just hit Process and voilla!! Magic Dub

![Magic Dub Result](img/MagicDubResult.png)

