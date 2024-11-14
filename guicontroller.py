### This file holds the programming to design and create the GUI
### as well as import the audio file into the GUI and convert
### it to the correct format before cleaning it.

#Import packages
import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
import wave
from mutagen.mp3 import MP3

#Define function for user to select file from their system
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")]) #Open file select and limit to audio files
    if file_path:
        file_name = file_path.split("/")[-1]  #Extract the file name from the path
        nameLabel.config(text=f"Selected file: {file_name}") #Update nameLabel to show file name
        process_audio(file_path) #Run process_audio function defined below

#Define function to process the audio file and convert to .wav if necessary
def process_audio(file_path):
    #Convert to .wav if not already
    if file_path.endswith(".mp3"):
        # Save audio from selected file in audio variable
        audio = AudioSegment.from_file(file_path) #Save audio from selected file in audio variable

        #Remove metadata from audio file if file is mp3
        mp3 = MP3(file_path)
        mp3.delete()
        mp3.save()

        #Continue .wav conversion
        file_path = file_path.rsplit(".", 1)[0] + ".wav" #Change file name to .wav
        audio.export(file_path, format="wav") #Export audio as .wav

    #Open the .wav file
    with wave.open(file_path, 'rb') as wav_file: #Open .wav file
        #Get parameters for current and future calculations
        params = wav_file.getparams()
        n_channels, sampwidth, framerate, n_frames, comptype, compname = params[:6]

        #Convert to single channel if not already
        if n_channels > 1:
            audio = AudioSegment.from_wav(file_path)
            audio = audio.set_channels(1)
            audio.export(file_path, format="wav")

        #Calculate duration of file in seconds
        duration = n_frames / float(framerate)

        #Display duration
        duration_label.config(text=f"Duration: {duration:.2f} seconds")

#Create the main window
root = tk.Tk()
root.title("Audio Wave Analyzer") #Define window name
root.geometry("600x200") #Define window size

#Create a label to display the selected file name
nameLabel = tk.Label(root, text="No file selected")
nameLabel.grid(pady=20, padx=10, column=0, row=0, columnspan=1)

#Create a button to open the file dialog
select_button = tk.Button(root, text="Select Audio File", command=select_file) #Command=select_file means the select_file function will be run when the button is clicked
select_button.grid(pady=20, padx=10, column=1, row=0, columnspan=1)

#Create a label to display the duration of the audio file
duration_label = tk.Label(root, text="") #Duration is displayed when audio file is selected
duration_label.grid(pady=10, padx=100, column=0, row=2, columnspan=1)

#Create a button to plot wav file
plot_button = tk.Button(root, text="Plot Waveform", command="Method name here") #Name of method for plotting waveform here
plot_button.grid(pady=10, padx=10, column=1, row=2, columnspan=1)

#Create a label to display the frequency of greatest amplitude of the audio file
frequency_label = tk.Label(root, text="") #Print function to determine greatest frequency output here
frequency_label.grid(pady=10, padx=10, column=0, row=3, columnspan=1)

#Create a button to alternate between three plots
three_plot_button = tk.Button(root, text="Swap Between Low, Mid, High Freq.", command="Method name here") #Name of method for swapping between plots here
three_plot_button.grid(pady=10, padx=10, column=1, row=3, columnspan=1)

#Create a button to combine plots into single plot
three_plot_button = tk.Button(root, text="Combine Plots", command="Method name here") #Name of method for combining plots here
three_plot_button.grid(pady=10, padx=10, column=1, row=4, columnspan=1)

#Create a label to display the RT60 differences in seconds
difference_label = tk.Label(root, text="") #Print function to determine differences output here
difference_label.grid(pady=10, padx=10, column=0, row=4, columnspan=1)

#Run the application
root.mainloop()