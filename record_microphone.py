import argparse
import pyaudio
import wave
import numpy as np
import time
import os

def find_kinect_device_index(audio):
    device_count = audio.get_device_count()
    for i in range(device_count):
        device_info = audio.get_device_info_by_index(i)
        device_name = device_info.get('name')
        if 'kinect' in device_name.lower():
            return i
    return None

def save_channel_to_wav(channel_data, channel_index, sample_width, sample_rate):
    output_filename = f"kinect_audio_channel_{channel_index}.wav"
    with wave.open(output_filename, 'wb') as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(sample_width)
        wave_file.setframerate(sample_rate)
        wave_file.writeframes(channel_data)
    return output_filename

def main(record_separate_channels):
    FORMAT = pyaudio.paInt16
    CHANNELS = 7  # Azure Kinect has 7 microphones
    RATE = 48000
    CHUNK = 4096
    RECORD_SECONDS = 15
    WAVE_OUTPUT_FILENAME = "kinect_audio.wav"
    GAIN_FACTOR = 50.0  # Adjust this value to increase or decrease the gain

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    kinect_device_index = find_kinect_device_index(audio)

    if kinect_device_index is None:
        print("Kinect microphone array not found.")
    else:
        # Open a streaming stream
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=kinect_device_index,
                            frames_per_buffer=CHUNK)

        print("Recording...")

        frames = []

        # Record audio with countdown timer
        start_time = time.time()
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            elapsed_time = time.time() - start_time
            remaining_time = int(RECORD_SECONDS - elapsed_time)
            print(f"Time remaining: {remaining_time}s", end="\r")

            data = stream.read(CHUNK)
            np_data = np.frombuffer(data, dtype=np.int16)
            np_data = np_data * GAIN_FACTOR
            np_data = np.clip(np_data, -32768, 32767).astype(np.int16)
            frames.append(np_data.tobytes())

        print("\nFinished recording")

        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Terminate the PortAudio interface
        audio.terminate()

        if not record_separate_channels:
            # Save the recorded data to a WAV file
            wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wave_file.setnchannels(CHANNELS)
            wave_file.setsampwidth(audio.get_sample_size(FORMAT))
            wave_file.setframerate(RATE)
            wave_file.writeframes(b''.join(frames))
            wave_file.close()

            print(f"Audio saved to {WAVE_OUTPUT_FILENAME}")
        else:
            # Combine all frames into a single NumPy array
            combined_frames = np.frombuffer(b''.join(frames), dtype=np.int16)

            # Reshape the combined_frames array to separate channels
            channel_data = combined_frames.reshape(-1, CHANNELS)

            # Save each channel to a separate WAV file
            sample_width = audio.get_sample_size(FORMAT)
            for channel_index in range(CHANNELS):
                channel_audio_data = channel_data[:, channel_index].tobytes()
                output_filename = save_channel_to_wav(channel_audio_data, channel_index, sample_width, RATE)
                print(f"Channel {channel_index} audio saved to {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record audio from Azure Kinect microphone array")
    parser.add_argument("--separate_channels", action="store_true", help="Save each channel to a separate WAV file")
    args = parser.parse_args()
    main(args.separate_channels)


    