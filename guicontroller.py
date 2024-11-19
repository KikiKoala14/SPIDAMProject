### This file holds the programming to design and create the GUI
### as well as import the audio file into the GUI and convert
### it to the correct format before cleaning it.

#Import packages
import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
import wave
from mutagen.mp3 import MP3
# Define a global variable to store the file path
selected_file_path = ""

# Define function for user to select file from their system
def select_file():
    global selected_file_path
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
    if file_path:
        selected_file_path = file_path
        file_name = file_path.split("/")[-1]
        nameLabel.config(text=f"Selected file: {file_name}")
        process_audio(file_path)

# Define function to process the audio file and convert to .wav if necessary
def process_audio(file_path):
    # Convert to .wav if not already
    if file_path.endswith(".mp3"):
        # Save audio from selected file in audio variable
        audio = AudioSegment.from_file(file_path)

        # Remove metadata from audio file if file is mp3
        mp3 = MP3(file_path)
        mp3.delete()
        mp3.save()

        # Continue .wav conversion
        file_path = file_path.rsplit(".", 1)[0] + ".wav"
        audio.export(file_path, format="wav")

    # Open the .wav file
    with wave.open(file_path, 'rb') as wav_file:
        #Get parameters for current and future calculations
        params = wav_file.getparams()
        n_channels, sampwidth, framerate, n_frames, comptype, compname = params[:6]

        # Convert to single channel if not already
        if n_channels > 1:
            audio = AudioSegment.from_wav(file_path)
            audio = audio.set_channels(1)
            audio.export(file_path, format="wav")

        # Calculate duration of file in seconds
        duration = n_frames / float(framerate)

        # Display duration
        duration_label.config(text=f"Duration: {duration:.2f} seconds")

# Create the main window
root = tk.Tk()
root.title("Audio Wave Analyzer")
root.geometry("800x600")  # Adjusted window size
root.configure(bg='#f0f0f0')

# Create a label to display the selected file name
nameLabel = tk.Label(root, text="No file selected", bg='#f0f0f0', font=("Arial", 12))
nameLabel.grid(pady=10, padx=10, column=0, row=0, columnspan=2)

# Create a button to open the file dialog
select_button = tk.Button(root, text="Select Audio File", command=select_file, font=("Arial", 12))
select_button.grid(pady=10, padx=10, column=0, row=1, columnspan=2)

# Create a label to display the duration of the audio file
duration_label = tk.Label(root, text="", bg='#f0f0f0', font=("Arial", 12))
duration_label.grid(pady=10, padx=10, column=0, row=2, columnspan=2)

# Create a canvas for plotting
plot_canvas = tk.Canvas(root, width=600, height=400, bg='white', highlightthickness=1, highlightbackground="black")
plot_canvas.grid(pady=10, padx=10, column=0, row=3, columnspan=2)

# Create a label to display the resonance frequencies below the plot
frequency_label = tk.Label(root, text="", bg='#f0f0f0', font=("Arial", 12))
frequency_label.grid(pady=10, padx=10, column=0, row=4, columnspan=2, sticky="w")

# Create a button to plot wav file
plot_button = tk.Button(root, text="Plot Waveform", font=("Arial", 12))
plot_button.grid(pady=10, padx=10, column=0, row=5)

# Create a button to swap between plots
three_plot_button = tk.Button(root, text="Swap Between Low, Mid, High Freq.", font=("Arial", 12))
three_plot_button.grid(pady=10, padx=10, column=1, row=5)

# Create a button to combine plots
combine_plot_button = tk.Button(root, text="Combine Plots", font=("Arial", 12))
combine_plot_button.grid(pady=10, padx=10, column=0, row=6)

# Add the 'Other Action' button
other_button = tk.Button(root, text="Other Action", font=("Arial", 12))
other_button.grid(pady=10, padx=10, column=1, row=6)

# Remove the root.mainloop() call from here, assuming it's handled elsewhere in your application
#Comment made to ensure proper files are sent over