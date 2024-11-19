import guicontroller
import numpy as np
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Define a global variable to track the current plot state
current_plot_state = 0

def plot_waveform(file_path):
    #verifies the file path
    if not file_path or file_path is None:
        return

    if not os.path.exists(file_path):
        return


    with guicontroller.wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        n_channels, sampwidth, framerate, n_frames, comptype, compname = params[:6]

        #calculations needed
        duration = n_frames / float(framerate)
        frames = wav_file.readframes(n_frames)
        waveform = np.frombuffer(frames, dtype=np.int16)
        rt60 = 0.161 * (n_frames / float(framerate))

        #creates the time axis
        time_axis = np.linspace(0, n_frames / framerate, num=n_frames)

        #changes the size of the graph/figure
        fig = Figure(figsize=(6, 4))  # Adjusted size to fit canvas

        #all the axis / the way the graph looks
        ax = fig.add_subplot(111)
        ax.plot(time_axis, waveform)
        ax.set_title("Waveform")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.margins(x=0.05, y=0.05)  # Margins to avoid cutting off values
        ax.set_xlim([0, np.max(time_axis)])  # Set fixed x-axis limits
        ax.set_ylim([np.min(waveform), np.max(waveform)])  # Set fixed y-axis limits
        fig.tight_layout(pad=2)  # Ensure tight layout to fit canvas

        #creates the spectrums needed
        fft_spectrum = np.fft.fft(waveform)
        freq = np.fft.fftfreq(len(fft_spectrum), d=1 / framerate)
        amplitude_spectrum = np.abs(fft_spectrum)
        max_amplitude_idx = np.argmax(amplitude_spectrum)
        highest_resonance_frequency = freq[max_amplitude_idx]

        #creates the resonance frequency based upon the ranges
        def find_resonance_frequency(freq_range):
            range_mask = (freq >= freq_range[0]) & (freq <= freq_range[1])
            range_amplitudes = amplitude_spectrum[range_mask]
            range_frequencies = freq[range_mask]
            if len(range_amplitudes) == 0:
                return None
            max_amplitude_idx = np.argmax(range_amplitudes) #max amplitude
            return range_frequencies[max_amplitude_idx]

        #creates the resonance frequencies for low, med and high, numbers are basically bin values
        low_resonance_frequency = find_resonance_frequency((20, 300))
        mid_resonance_frequency = find_resonance_frequency((300, 2000))
        high_resonance_frequency = find_resonance_frequency((2000, np.max(freq)))

        #creates the text for the frequencies
        resonance_texts = [
            f"Highest Resonance Frequency: {highest_resonance_frequency:.2f} Hz",
            f"Low Resonance Frequency: {low_resonance_frequency:.2f} Hz" if low_resonance_frequency else "No low resonance frequency",
            f"Mid Resonance Frequency: {mid_resonance_frequency:.2f} Hz" if mid_resonance_frequency else "No mid resonance frequency",
            f"High Resonance Frequency: {high_resonance_frequency:.2f} Hz" if high_resonance_frequency else "No high resonance frequency"
        ]

        #updates the controller info
        guicontroller.frequency_label.config(text="\n".join(resonance_texts), padx=20)
        guicontroller.duration_label.config(text=f"Duration: {duration:.2f} seconds\nRT60: {rt60:.2f} seconds")

        # Store the original duration and RT60 values
        guicontroller.original_duration_text = guicontroller.duration_label.cget("text")

        # Clear the canvas
        for child in guicontroller.plot_canvas.winfo_children():
            child.destroy()

        # Attach the plot to the canvas
        canvas = FigureCanvasTkAgg(fig, master=guicontroller.plot_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()

#creates a scatter plot if requirements are met
def plot_scatter(file_path, plot_type):
    if not file_path or file_path is None:
        return

    if not os.path.exists(file_path):
        return

    with guicontroller.wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        n_channels, sampwidth, framerate, n_frames, comptype, compname = params[:6]
        frames = wav_file.readframes(n_frames)
        waveform = np.frombuffer(frames, dtype=np.int16)
        fft_spectrum = np.fft.fft(waveform)
        freq = np.fft.fftfreq(len(fft_spectrum), d=1 / framerate)
        amplitude_spectrum = np.abs(fft_spectrum)

        #creates/manipulates values put on the graph depending on which it is
        if plot_type == 'low':
            mask = (freq >= 20) & (freq <= 300)
            filtered_waveform = waveform[mask]
            title = "RT60 for Low Frequency"
        elif plot_type == 'mid':
            mask = (freq >= 300) & (freq <= 2000)
            filtered_waveform = waveform[mask]
            title = "RT60 for Mid Frequency"
        elif plot_type == 'high':
            mask = (freq >= 2000) & (freq <= np.max(freq))
            filtered_waveform = waveform[mask]
            title = "RT60 for High Frequency"

        #rt60 values calculation
        rt60_values = 0.161 * (len(filtered_waveform) / float(framerate))
        #time axis updated depending on length
        time_axis = np.linspace(0, len(filtered_waveform) / framerate, num=len(filtered_waveform))

        #the graph visual aspects
        fig = Figure(figsize=(6, 4))  # Adjusted size to fit canvas
        ax = fig.add_subplot(111)
        ax.plot(time_axis, filtered_waveform)
        ax.set_title(title)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("RT60")
        ax.margins(x=0.05, y=0.05)  # Margins to avoid cutting off values
        ax.set_xlim([0, np.max(time_axis)])  # Set fixed x-axis limits
        ax.set_ylim([np.min(filtered_waveform), np.max(filtered_waveform)])  # Set fixed y-axis limits
        fig.tight_layout(pad=2)  # Ensure tight layout to fit canvas

        # Update RT60 value for the specific frequency range
        new_duration_text = f"{guicontroller.original_duration_text}\nRT60 for {plot_type.capitalize()} Freq: {rt60_values:.2f} seconds"

        guicontroller.duration_label.config(text=new_duration_text)

        # Clear the canvas so the new plots can be put in that place
        for child in guicontroller.plot_canvas.winfo_children():
            child.destroy()

        # Attach the plot to the canvas
        canvas = FigureCanvasTkAgg(fig, master=guicontroller.plot_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()

#allows the plots to be in the same location as the previous one
def swap_frequency_plot():
    global current_plot_state
    file_path = guicontroller.selected_file_path
    if current_plot_state == 0:
        plot_scatter(file_path, 'low')
    elif current_plot_state == 1:
        plot_scatter(file_path, 'mid')
    elif current_plot_state == 2:
        plot_scatter(file_path, 'high')

    current_plot_state = (current_plot_state + 1) % 3  # Cycle through 0, 1, 2 for the low, medium and high freq

#updates the plot button
def update_plot_button():
    guicontroller.plot_button.config(command=lambda: plot_waveform(guicontroller.selected_file_path))

#updates the swap button
def update_swap_button():
    guicontroller.three_plot_button.config(command=swap_frequency_plot)

#delays the update slightly
guicontroller.root.after(100, update_plot_button)
guicontroller.root.after(100, update_swap_button)

#this is added so it reads all the code before starting the controller code
guicontroller.root.mainloop()
