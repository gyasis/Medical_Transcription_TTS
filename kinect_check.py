# %% 
import pyaudio
import wave
import numpy as np

p = pyaudio.PyAudio()

# Find out the index of Azure Kinect Microphone Array
azure_kinect_device_name = "Azure Kinect Microphone Array"
index = -1
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))
    if azure_kinect_device_name in p.get_device_info_by_index(i)["name"]:
        index = i
        break
if index == -1:
    print("Could not find Azure Kinect Microphone Array. Make sure it is properly connected.")
    exit()

# Open the stream for reading audio
input_format = pyaudio.paInt32
input_sample_width = 4
input_channels = 7 #choose your channel count among 2,4,7
input_sample_rate = 48000

stream = p.open(format=input_format, channels=input_channels, rate=input_sample_rate, input=True, input_device_index=index)

# Read frames from microphone and write to wav file
with wave.open("output.wav", "wb") as outfile:
    outfile.setnchannels(1) # We want to write only first channel from each frame
    outfile.setsampwidth(input_sample_width)
    outfile.setframerate(input_sample_rate)

    time_to_read_in_seconds = 5
    frames_to_read = time_to_read_in_seconds * input_sample_rate
    total_frames_read = 0
    while total_frames_read < frames_to_read:
        available_frames = stream.get_read_available()
        read_frames = stream.read(available_frames)
        first_channel_data = np.fromstring(read_frames, dtype=np.int32)[0::7].tobytes()
        outfile.writeframesraw(first_channel_data)
        total_frames_read += available_frames

stream.stop_stream()
stream.close()

p.terminate()
# %%
import pyaudio
import wave
import numpy as np

p = pyaudio.PyAudio()

# Find out the index of Azure Kinect Microphone Array
azure_kinect_device_name = "Azure Kinect Microphone Array"
index = -1
for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    print(device_info)
    if azure_kinect_device_name in device_info["name"]:
        index = i
        break

if index == -1:
    print("Could not find Azure Kinect Microphone Array. Make sure it is properly connected.")
    exit()

# Open the stream for reading audio
input_format = pyaudio.paInt32
input_sample_width = 4
input_channels = 7  # choose your channel count among 2,4,7
input_sample_rate = 48000

stream = p.open(format=input_format, channels=input_channels, rate=input_sample_rate, input=True, input_device_index=index)

# Read frames from microphone and write to wav file
with wave.open("output.wav", "wb") as outfile:
    outfile.setnchannels(1)  # We want to write only first channel from each frame
    outfile.setsampwidth(input_sample_width)
    outfile.setframerate(input_sample_rate)

    time_to_read_in_seconds = 5
    frames_to_read = time_to_read_in_seconds * input_sample_rate
    total_frames_read = 0
    while total_frames_read < frames_to_read:
        available_frames = stream.get_read_available()
        read_frames = stream.read(available_frames)
        first_channel_data = np.frombuffer(read_frames, dtype=np.int32)[0::7].tobytes()
        outfile.writeframesraw(first_channel_data)
        total_frames_read += available_frames

stream.stop_stream()
stream.close()

p.terminate()

# %%
