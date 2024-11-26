import numpy as np
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import guicontroller  # Assuming this is defined elsewhere in your code

# Define a global variable to track the current plot state
current_plot_state = 0

# Function to convert amplitude to decibels (dB)
def amplitude_to_db(amplitude):
    return 20 * np.log10(np.abs(amplitude) + 1e-6)  # Small offset to avoid log(0)

def calculate_highest_resonant_frequency(waveform, framerate):
    # Perform the Fourier Transform
    spectrum = np.fft.fft(waveform)

    # Generate frequencies associated with the FFT result
    freq = np.fft.fftfreq(len(spectrum), d=1 / framerate)

    # Keep only the positive frequencies
    positive_freqs = freq[:len(freq)//2]

    # Calculate magnitude (absolute value) of the spectrum
    magnitude = np.abs(spectrum[:len(spectrum)//2])

    # Set the DC component (zero frequency) magnitude to zero to avoid the peak at 0 Hz
    magnitude[0] = 0

    # Debugging: Check for the maximum magnitude value and its corresponding frequency
    max_magnitude = np.max(magnitude)
    peak_index = np.argmax(magnitude)
    highest_resonant_frequency = positive_freqs[peak_index]

    # Ensure the resonant frequency is within the Nyquist limit
    nyquist_limit = framerate / 2
    if highest_resonant_frequency > nyquist_limit:
        print(f"Warning: Calculated resonant frequency {highest_resonant_frequency} Hz is above the Nyquist limit of {nyquist_limit} Hz.")
        highest_resonant_frequency = nyquist_limit  # Clamp to Nyquist limit

    # Clamp if the frequency is too close to Nyquist
    if highest_resonant_frequency > nyquist_limit - 100:
        print(f"Warning: Resonant frequency is too close to Nyquist limit. Clamping to {nyquist_limit - 100} Hz.")
        highest_resonant_frequency = nyquist_limit - 100  # Force it to be 100 Hz below Nyquist

    # Debugging: print frequency limits, calculated resonant frequency, and max magnitude
    print(f"Sampling rate: {framerate} Hz")
    print(f"Max Magnitude: {max_magnitude}")
    print(f"Calculated highest resonant frequency: {highest_resonant_frequency} Hz")
    print(f"Nyquist frequency: {nyquist_limit} Hz")

    return highest_resonant_frequency


def plot_waveform(file_path):
    # Verifies the file path
    if not file_path or file_path is None:
        return

    if not os.path.exists(file_path):
        return

    with guicontroller.wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        n_channels, sampwidth, framerate, n_frames, comptype, compname = params[:6]

        # Calculations needed
        duration = n_frames / float(framerate)
        frames = wav_file.readframes(n_frames)
        waveform = np.frombuffer(frames, dtype=np.int16)
        highest_resonant_frequency = calculate_highest_resonant_frequency(waveform, framerate)

        # Creates the time axis
        time_axis = np.linspace(0, n_frames / framerate, num=n_frames)

        # Changes the size of the graph/figure
        fig = Figure(figsize=(6, 4))  # Adjusted size to fit canvas

        # All the axis / the way the graph looks
        ax = fig.add_subplot(111)
        ax.plot(time_axis, waveform)
        ax.set_title("Waveform")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.margins(x=0.05, y=0.05)  # Margins to avoid cutting off values
        ax.set_xlim([0, np.max(time_axis)])  # Set fixed x-axis limits
        ax.set_ylim([np.min(waveform), np.max(waveform)])  # Set fixed y-axis limits
        fig.tight_layout(pad=2)  # Ensure tight layout to fit canvas

        # Updates the controller info
        guicontroller.duration_label.config(
            text=f"Duration: {duration:.2f} seconds\nHighest Resonant Frequency: {highest_resonant_frequency:.2f} Hz"
        )

        # Store the original duration and Highest Resonant Frequency values
        guicontroller.original_duration_text = guicontroller.duration_label.cget("text")

        # Clear the canvas
        for child in guicontroller.plot_canvas.winfo_children():
            child.destroy()

        # Attach the plot to the canvas
        canvas = FigureCanvasTkAgg(fig, master=guicontroller.plot_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()


# The time series Graph Data/Instructions
# Each dot is the dominant/peak of frequency on each of them
def plot_timeseries(file_path, plot_type):
    if not file_path or file_path is None:
        return

    if not os.path.exists(file_path):
        return

    with guicontroller.wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        n_channels, sampwidth, framerate, n_frames, comptype, compname = params[:6]
        frames = wav_file.readframes(n_frames)
        waveform = np.frombuffer(frames, dtype=np.int16)

        # Create the time axis
        time_axis = np.linspace(0, n_frames / framerate, num=n_frames)

        # Perform FFT to get the frequency spectrum
        fft_spectrum = np.fft.fft(waveform)
        freq = np.fft.fftfreq(len(fft_spectrum), d=1 / framerate)
        amplitude_spectrum = np.abs(fft_spectrum)
        amplitude_spectrum_db = amplitude_to_db(amplitude_spectrum)

        if plot_type == 'low':
            freq_range = (0, 300)  # Low frequency range
            title = "Low Frequency"
            color = 'green'  # Green for low
        elif plot_type == 'mid':
            freq_range = (300, 2000)  # Mid frequency range
            title = "Mid Frequency"
            color = 'yellow'  # Yellow for mid
        elif plot_type == 'high':
            freq_range = (2000, np.max(freq))  # High frequency range
            title = "High Frequency"
            color = 'red'  # Red for high

        # Mask the spectrum to the chosen frequency range
        mask = (freq >= freq_range[0]) & (freq <= freq_range[1])
        filtered_freq = freq[mask]
        filtered_amplitude_db = amplitude_spectrum_db[mask]

        # Create time series plot
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.plot(filtered_freq, filtered_amplitude_db, color='blue')  # Frequency spectrum line
        ax.set_title(title)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Power (dB)")
        ax.grid(True)

        # Find the peak values for each frequency range and plot them
        peak_index = np.argmax(filtered_amplitude_db)
        peak_freq = filtered_freq[peak_index]
        peak_value = filtered_amplitude_db[peak_index]

        # Plot a dot at the highest value within the frequency range
        ax.scatter(peak_freq, peak_value, color=color, s=100, label=f"Peak {plot_type}")

        fig.tight_layout(pad=2)

        # Clear the canvas and attach the plot
        for child in guicontroller.plot_canvas.winfo_children():
            child.destroy()

        canvas = FigureCanvasTkAgg(fig, master=guicontroller.plot_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()


# Allows the plots to be in the same location as the previous one
def swap_frequency_plot():
    global current_plot_state
    file_path = guicontroller.selected_file_path
    if current_plot_state == 0:
        plot_timeseries(file_path, 'low')
    elif current_plot_state == 1:
        plot_timeseries(file_path, 'mid')
    elif current_plot_state == 2:
        plot_timeseries(file_path, 'high')

    current_plot_state = (current_plot_state + 1) % 3  # Cycle through 0, 1, 2 for the low, medium, and high freq


# Updates the plot button
def update_plot_button():
    guicontroller.plot_button.config(command=lambda: plot_waveform(guicontroller.selected_file_path))


# Updates the swap button
def update_swap_button():
    guicontroller.three_plot_button.config(command=swap_frequency_plot)


# Delays the update slightly
guicontroller.root.after(100, update_plot_button)
guicontroller.root.after(100, update_swap_button)

# This is removed from the guicontroller and put here so it reads the analyticsModel file before trying to run the guicontroller file
guicontroller.root.mainloop()
