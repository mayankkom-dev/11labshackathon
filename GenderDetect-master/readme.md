## Gender Detection

Python wrapper around LIUM's gender detection toolkit.

Gender detection is the process of finding gender of speaker(s) from the 
audio file.
* This wraps LIUM's  gender detection tool.
* LIUM uses pre-trained `gmm` models for detection which were trained with French voice
corpus. So it is possible that gender output might be inaccurate.
* This creates two files: `.seg` and `.g.seg` (learn more about them [here](http://www-lium.univ-lemans.fr/diarization/doku.php/quick_start))
* You can delete these files after detection

* Use when there is only one speaker in the audio file.


<br>

Note
----
```
The code(Python) is taken from the project voiceid.
Changes/improvements are made in order to work with minimum requirments.

Also, I modified the source code (java) of the SpeakerDiarization toolkit.
Source code is in the src folder.
See src/CHANGES.txt .
```

install
------- 
```bash
$ python setup.py install --user
```

Code
----
```python
>> from gdetect import genderdetect as gd
>> gender = gd.identify_gender('./test.wav')
>> print gender
>> # will print 'F' or 'M'
```

Credits
-------
[VoiceId project](https://code.google.com/archive/p/voiceid/)
