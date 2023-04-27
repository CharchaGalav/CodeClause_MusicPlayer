import os
import pickle
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from pygame import mixer
from googleapiclient.discovery import build
import webbrowser
import requests


class Player(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        mixer.init()

        if os.path.exists('songs.pickle'):
            with open('songs.pickle', 'rb') as f:
                self.playlist = pickle.load(f)
        else:
            self.playlist = []
        
        self.current = 0
        self.paused = True
        self.played = False
        
        self.create_frames()
        self.track_widgets()
        self.control_widgets()
        self.tracklist_widgets()
        self.search_widgets()
    
    def create_frames(self):
        self.track = tk.LabelFrame(self, text='Song Track', font=("times new roman", 15, "bold"), bg="#9784a6", fg="white", bd=2, relief=tk.RIDGE)
        self.track.configure(width=360, height=260)
        self.track.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        self.searchbox = tk.LabelFrame(self, text='Search', font=("times new roman", 15, "bold"), bg="#9784a6", fg="white", bd=2, relief=tk.RIDGE)
        self.searchbox.configure(width=180)
        self.searchbox.grid(row=1, column=1, padx=5, pady=5, sticky="n")

        self.tracklist = tk.LabelFrame(self, text= f'Playlist - {str(len(self.playlist))}', font=("times new roman", 15, "bold"), bg="#9784a6", fg="white", bd=2, relief=tk.RIDGE)
        self.tracklist.configure(width=220, height=150)
        self.tracklist.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.controls = tk.LabelFrame(self, text='Controls', font=("times new roman", 15, "bold"), bg="#9784a6", fg="white", bd=2, relief=tk.RIDGE)
        self.controls.configure(width=360, height=150)
        self.controls.grid(row=1, column=0, padx=5, pady=5, sticky="n")

    def track_widgets(self):
        self.canvas = tk.Label(self.track, image=img)
        self.canvas.configure(width=340, height=230)
        self.canvas.grid(row=0, column=0)

        self.songtrack = tk.Label(self.track, font=("times new roman", 13, "bold"), bg="#410468", fg="white")
        self.songtrack['text'] = "Music Player"
        self.songtrack.config(width=30, height=1)
        self.songtrack.grid(row=1, column=0)

    def search_widgets(self):
        self.song_entry = tk.Entry(self.searchbox, width=21, font=("times new roman", 12, "bold"), bg="white", fg="black", bd=0, relief=tk.RIDGE)
        self.song_entry.grid(row=0, column=0, padx=10, pady=1)

        self.search_button = tk.Button(self.searchbox, text="Search", font=("times new roman", 10, "bold"), bg="white", fg="black", bd=0, relief=tk.RIDGE, command=self.search_song)
        self.search_button.grid(row=1, column=0, pady=1)

    def control_widgets(self):
        self.loadsongs = tk.Button(self.controls, bg="white", fg="black", font=1)
        self.loadsongs['text'] = "Load Songs"
        self.loadsongs['command'] = self.browsesong
        self.loadsongs.grid(row=0, column=0, padx=1)

        self.previous = tk.Button(self.controls, image=previous)
        self.previous['command'] = self.prevsong
        self.previous.grid(row=0, column=1, padx=2)

        self.pause = tk.Button(self.controls, image=pause)
        self.pause['command'] = self.pausesong
        self.pause.grid(row=0, column=2, padx=2)

        self.next = tk.Button(self.controls, image=next)
        self.next['command'] = self.nextsong
        self.next.grid(row=0, column=3, padx=2)

        self.volume = tk.DoubleVar(self)
        self.slider = tk.Scale(self.controls, from_=0, to=10, orient=tk.HORIZONTAL)
        self.slider['variable'] = self.volume
        self.slider.set(5)
        mixer.music.set_volume(0.5)
        self.slider['command'] = self.changevolume
        self.slider.grid(row=0, column=4, pady=3, padx=3)
    
    def tracklist_widgets(self):
        self.scrollbar = tk.Scrollbar(self.tracklist, orient=tk.VERTICAL)
        self.scrollbar.grid(row=0, column=1, rowspan=5, sticky='ns')

        self.list = tk.Listbox(self.tracklist, selectmode=tk.SINGLE, yscrollcommand=self.scrollbar.set, selectbackground="skyblue", selectforeground="black", font=("times new roman", 12, "bold"), bg="silver", fg="black", bd=3, relief=tk.RIDGE)
        self.enumerate_songs()
        self.list.configure(height=12)
        self.list.bind('<Double-1>', self.play_song)

        self.scrollbar.config(command=self.list.yview)
        self.list.grid(row=0, column=0)

    def enumerate_songs(self):
        for index, song in enumerate(self.playlist):
            self.list.insert(index, os.path.basename(song))
    

    def browsesong(self):
        self.songlist = []
        directory = filedialog.askdirectory()
        for root_, dirs, files in os.walk(directory):
            for file in files:
                if os.path.splitext(file)[1] == '.mp3':
                    path = (root_ + '/' + file).replace('\\', '/')
                    self.songlist.append(path)
        
        with open('songs.pickle', 'wb') as f:
            pickle.dump(self.songlist, f)

        self.playlist = self.songlist
        self.tracklist['text'] = f'Playlist - {str(len(self.playlist))}'
        self.list.delete(0, tk.END)
        self.enumerate_songs()

    def play_song(self, event=None):
        if event is not None:
            self.current = self.list.curselection()[0]
            for i in range(len(self.playlist)):
                self.list.itemconfigure(i, bg="white") 

        mixer.music.load(self.playlist[self.current])
        self.pause['image'] = play
        self.paused = False
        self.songtrack['anchor'] = 'w'
        self.songtrack['text'] = os.path.basename(self.playlist[self.current])
        self.list.activate(self.current)
        self.list.itemconfigure(self.current, bg="skyblue")
        mixer.music.play()

    def search_song(self):
        query = self.song_entry.get()
        if query:
            youtube = build('youtube', 'v3', developerKey='AIzaSyB_ToZMxsaClKbldhxST1t1ob7Z96C_6fo')
            request = youtube.search().list(q=query, part='id', type='video', maxResults=1)
            response = request.execute()
            video_id = response['items'][0]['id']['videoId']
            url = f'https://www.youtube.com/watch?v={video_id}'
            webbrowser.open(url)
            self.played = True
            self.paused = False



    def pausesong(self):
        if not self.paused:
            self.paused = True
            mixer.music.pause()
            self.pause['image'] = pause
        else:
            if self.played == False:
                self.play_song()
            self.paused = False
            mixer.music.unpause()
            self.pause['image'] = play

    def changevolume(self, event=None):
        self.v = self.volume.get()
        mixer.music.set_volume(self.v / 10)

    def prevsong(self):
        if self.current > 0:
            self.current -= 1
        else:
            self.current = 0
        self.list.itemconfigure(self.current+1, bg="white")
        self.play_song()

    def nextsong(self):
        if self.current < len(self.playlist) - 1:
            self.current += 1
         
        else:
            self.current = 0
        self.list.itemconfigure(self.current-1, bg="white")
        self.play_song()


root = tk.Tk()
root.geometry("600x400+400+200")
root.minsize('600', '400')
root.title("Music Player")


img = PhotoImage(file="D:\AllMyProjects\Code_Clause\MusicPlayer\images\music.png")
next = PhotoImage(file="D:\AllMyProjects\Code_Clause\MusicPlayer\images/next.png").subsample(12,12)
previous = PhotoImage(file="D:\AllMyProjects\Code_Clause\MusicPlayer\images\previous.png").subsample(12,12)
pause = PhotoImage(file="D:\AllMyProjects\Code_Clause\MusicPlayer\images\pause.png").subsample(12,12)
play = PhotoImage(file="D:\AllMyProjects\Code_Clause\MusicPlayer\images\play.png").subsample(12,12)


app = Player(master=root)
app.mainloop()





