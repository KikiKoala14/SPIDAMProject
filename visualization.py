import AnalyticsModel as am
import guicontroller
import numpy as np
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def timeseries_general(file_path, plot_type):
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

            # Define frequency ranges for low, mid, and high plots
            if plot_type == 'low':
                freq_range = (5, 300)  # Low frequency range
                title = "Low Frequency"
                color = 'green'
            elif plot_type == 'mid':
                freq_range = (300, 2000)  # Mid frequency range
                title = "Mid Frequency"
                color = 'yellow'
            elif plot_type == 'high':
                freq_range = (2000, np.max(freq))  # High frequency range
                title = "High Frequency"
                color = 'red'
            elif plot_type == 'all':
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
            print(peak_low_freq)
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
    timeseries_general(new_file_path, 'all')

def update_combine_button():
    guicontroller.combine_plot_button.config(command=combine_plots)

guicontroller.root.after(100, update_combine_button)

guicontroller.root.mainloop()