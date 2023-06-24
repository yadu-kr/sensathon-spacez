import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from scipy import signal
import math
import pandas as pd

sample_freq = 4000
time_duration = 5
down_sample = 1
input_gain_db = 12
device = 'snd_rpi_i2s_card' 
sound_speed = 343  
microphone_distance = 0.04  

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def set_gain_db(audiodata, gain_db):
    audiodata *= np.power(10, gain_db/10)
    return np.array([1 if s > 1 else -1 if s < -1 else s for s in audiodata], dtype=np.float32)

def similarity(audio_1, audio_2):
	correlation = np.correlate(audio_1, audio_2, mode='full')
	index = np.argmax(correlation) 
	time_delay = (index) / sample_freq
	print("Matching Index : ", index) 
	print("Time Delay: ", time_delay)
	cos_theta = time_delay * sound_speed / microphone_distance
	return cos_theta
	
def processing(audiodata):
	audio_1 = np.array(audiodata[::down_sample, 0], dtype=np.float32) 
	audio_2 = np.array(audiodata[::down_sample, 1], dtype=np.float32) 
	print("Difference: ", np.sum(np.absolute(audio_1 - audio_2)))
	print("Similarity Angle: ", similarity(audio_1, audio_2))

	audio_1 = butter_highpass_filter(audio_1, 10, sample_freq)
	audio_1 = set_gain_db(audio_1, input_gain_db)
	
	audio_2 = butter_highpass_filter(audio_2, 10, sample_freq)
	audio_2 = set_gain_db(audio_2, input_gain_db)
	
	write('left.wav', int(sample_freq/down_sample), 50*audio_1)
	write('right.wav', int(sample_freq/down_sample), 50*audio_2)
	write('diff.wav', int(sample_freq/down_sample), 50*np.abs(audio_1-audio_2))
	np.savetxt("file-1.csv", audio_1, delimiter=",")
	np.savetxt("file-2.csv", audio_2, delimiter=",")
	
	# Output the data in the same format as it came in.
	return np.array([[audio_1[i], audio_2[i]] for i in range(len(audio_1))], dtype=np.float32)
    

rec = sd.rec(int(time_duration * sample_freq), samplerate=sample_freq, channels=2)
sd.wait()
processed = processing(rec)
write('out.wav', int(sample_freq/down_sample), processed)

	
	
