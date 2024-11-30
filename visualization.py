from pydub import AudioSegment
import AnalyticsModel as am
import guicontroller
import numpy as np
import os
from scipy.io import wavfile
import matplotlib.pyplot as plt
from pydub.utils import make_chunks
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# This is a general plot for all three time series plots
def plot_timeseries_general(file_path, plot_type):
    if not file_path or file_path is None:
        return

    if not os.path.exists(file_path):
        return

    with guicontroller.wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        n_channels, sampwidth, framerate, n_frames, comptype, compname = params[:6]
        frames = wav_file.readframes(n_frames)
        waveform = np.frombuffer(frames, dtype=np.int16)

        # Create the time axis for time-domain plot
        time_axis = np.linspace(0, n_frames / framerate, num=n_frames)

        if plot_type == 'low' or plot_type == 'mid' or plot_type == 'high' or plot_type == 'all':
            # This is the frequency-domain plot
            # Perform FFT to get the frequency spectrum
            fft_spectrum = np.fft.fft(waveform)
            freq = np.fft.fftfreq(len(fft_spectrum), d=1 / framerate)
            amplitude_spectrum = np.abs(fft_spectrum)
            amplitude_spectrum_db = am.amplitude_to_db(amplitude_spectrum)

            # Define frequency range for all plots
            if plot_type == 'all':
                freq_range = (5, np.max(freq))
                title = "Combined Frequency"
                color = 'blue'

            # Mask the spectrum to the chosen frequency range
            mask = (freq >= freq_range[0]) & (freq <= freq_range[1])
            filtered_freq = freq[mask]
            filtered_amplitude_db = amplitude_spectrum_db[mask]

            # Convert frequency to time: Time (t) = 1 / Frequency (f)
            # We will plot the frequency axis as time-related data
            time_related_axis = 1 / filtered_freq  # Convert frequency to time axis

            # Create the frequency-domain plot (FFT) with time on the x-axis
            fig = Figure(figsize=(6, 4))
            ax = fig.add_subplot(111)
            ax.plot(time_related_axis, filtered_amplitude_db, color='blue')  # Frequency spectrum line
            ax.set_title(title)
            ax.set_xlabel("Time (s)")  # Time on x-axis (converted from frequency)
            ax.set_ylabel("Power (dB)")  # Power in dB on y-axis
            ax.grid(True)

            # Find the peak values for each frequency range and plot them
            peak_low_index = np.argmax(amplitude_spectrum_db[(freq >= 5) & (freq <= 300)])
            peak_low_freq = filtered_freq[peak_low_index]
            peak_low_value = filtered_amplitude_db[peak_low_index]
            print(peak_low_freq) # Temporary display
            print(peak_low_value)

            peak_mid_index = np.argmax(amplitude_spectrum_db[(freq >= 300) & (freq <= 2000)])
            peak_mid_freq = filtered_freq[peak_mid_index]
            peak_mid_value = filtered_amplitude_db[peak_mid_index]
            print(peak_mid_freq)
            print(peak_mid_value)

            peak_high_index = np.argmax(amplitude_spectrum_db[(freq >= 2000) & (freq <= np.max(freq))])
            peak_high_freq = filtered_freq[peak_high_index]
            peak_high_value = filtered_amplitude_db[peak_high_index]
            print(peak_high_freq)
            print(peak_high_value)

            # Plot a dot at the highest value within each frequency range
            ax.scatter(1 / peak_low_freq, peak_low_value, color='green', s=100, label=f"Peak {plot_type}")
            ax.scatter(1 / peak_mid_freq, peak_mid_value, color='yellow', s=100, label=f"Peak {plot_type}")
            ax.scatter(1 / peak_high_freq, peak_high_value, color='red', s=100, label=f"Peak {plot_type}")


            fig.tight_layout(pad=2)

        else:
            # This is the time-domain plot (original waveform)
            fig = Figure(figsize=(6, 4))
            ax = fig.add_subplot(111)
            ax.plot(time_axis, waveform, color='black')  # Time-domain plot
            ax.set_title("Waveform")
            ax.set_xlabel("Time (s)")  # Time on x-axis in seconds
            ax.set_ylabel("Amplitude")  # Amplitude on y-axis
            ax.grid(True)
            fig.tight_layout(pad=2)

        # Clear the canvas and attach the plot
        for child in guicontroller.plot_canvas.winfo_children():
            child.destroy()

        canvas = FigureCanvasTkAgg(fig, master=guicontroller.plot_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()

def combine_plots():
    new_file_path = guicontroller.selected_file_path
    plot_timeseries_general(new_file_path, 'all')


# Plots Heatmap showing the frequency intensity
def plot_specgram(file_path):
    if not file_path or file_path is None:
        return

    if not os.path.exists(file_path):
        return

    with guicontroller.wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        n_channels, sampwidth, framerate, n_frames, comptype, compname = params[:6]
        frames = wav_file.readframes(n_frames)
        waveform = np.frombuffer(frames, dtype=np.int16)

        # Processes audio to prepare it for heatmap
        audio_file = AudioSegment.from_file(file_path)
        audio_file = audio_file.set_channels(1)
        sample_data = np.array(audio_file.get_array_of_samples())
        frame_rate = audio_file.frame_rate
        window_size = 1024
        hop_size = 512
        num_frames = (len(sample_data) - window_size) // hop_size
        freq = np.fft.fftfreq(window_size, d=1 / frame_rate)
        freq = np.fft.fftshift(freq[:window_size // 2])
        time = np.arange(num_frames) * hop_size / frame_rate

        # Computes the FFT & magnitude and stores it in the heatmap
        heatmap = np.zeros((len(freq), len(time)))
        for i in range (num_frames):
            start_idx = i * hop_size
            end_idx = start_idx + window_size
            windowed_samples = sample_data[start_idx:end_idx] * np.hanning(window_size)
            spectrum = np.fft.fft(windowed_samples)
            spectrum = np.fft.fftshift(spectrum)[:window_size // 2]
            heatmap[:, i] = np.abs(spectrum)

        # Converts the amplitude heatmap to decibels
        heatmap_db = 20 * np.log10(heatmap + np.finfo(float).eps)

        # Creates figure & displays heatmap
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        im = ax.imshow(
            heatmap_db, aspect='auto', cmap='autumn_r',
            extent=[0, time[-1], freq[0], freq[-1]],
            vmin=0, vmax=100
        )
        cbar = fig.colorbar(im, ax=ax)

        ax.set_title("Frequency Heatmap")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Frequency (Hz)")
        cbar.set_label("Intensity (dB)")
        ax.set_ylim([freq[0], freq[-1]])
        fig.tight_layout(pad=2)

        # Clear the canvas
        for child in guicontroller.plot_canvas.winfo_children():
            child.destroy()

        # Attach the plot to the canvas
        canvas = FigureCanvasTkAgg(fig, master=guicontroller.plot_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()


# Updates the Combine Plots button
def update_combine_button():
    guicontroller.combine_plot_button.config(command=combine_plots)

# Updates the other action button
def update_other_button():
    guicontroller.other_button.config(command=lambda: plot_specgram(guicontroller.selected_file_path))


# Delays the updates slightly
guicontroller.root.after(100, update_combine_button)
guicontroller.root.after(100, update_other_button)

# This is removed from the guicontroller and put here so it reads the visualization & AnalyticsModel modules before
# trying to run the guicontroller file
guicontroller.root.mainloop()