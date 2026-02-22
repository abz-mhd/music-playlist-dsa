import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import os
import random
import pickle
import pygame
from pygame import mixer
import time

# ===================== Initialize pygame =====================
pygame.init()
mixer.init()

# ===================== Song, PlaylistNode, Playlist Classes =====================
class Song:
    """Represents a song with metadata"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.title = os.path.splitext(self.filename)[0]
        self.artist = "Unknown Artist"
        self.duration = self._get_duration()
        self.album = "Unknown Album"

    def _get_duration(self):
        """Get song duration using pygame (fallback 180s)"""
        try:
            sound = pygame.mixer.Sound(self.filepath)
            duration = sound.get_length()
            del sound
            return duration if duration and duration > 0 else 180
        except Exception:
            return 180

class PlaylistNode:
    """Node for doubly-linked list implementation"""
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None

class Playlist:
    """Playlist ADT using doubly-linked list"""
    def __init__(self, name):
        self.name = name
        self.head = None
        self.tail = None
        self.current = None
        self.length = 0
        self.is_shuffled = False
        self.original_order = []
        self.shuffle_session = None  # Track played songs in shuffle mode

    def add_song(self, song):
        """Add song to end of playlist"""
        new_node = PlaylistNode(song)
        if not self.head:
            self.head = self.tail = self.current = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1
        self.original_order.append(new_node)

    def remove_song(self, song_title):
        """Remove song by title"""
        current = self.head
        while current:
            if current.song.title == song_title:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                if self.current == current:
                    self.current = current.next if current.next else self.head
                if current in self.original_order:
                    self.original_order.remove(current)
                self.length -= 1
                return True
            current = current.next
        return False

    def move_song(self, song_title, direction):
        """Move song up or down in playlist (only when not shuffled)"""
        if self.is_shuffled or self.length <= 1:
            return False
        for i, node in enumerate(self.original_order):
            if node.song.title == song_title:
                if direction == "up" and i > 0:
                    self.original_order[i], self.original_order[i-1] = self.original_order[i-1], self.original_order[i]
                    self._rebuild_linked_list()
                    return True
                if direction == "down" and i < len(self.original_order) - 1:
                    self.original_order[i], self.original_order[i+1] = self.original_order[i+1], self.original_order[i]
                    self._rebuild_linked_list()
                    return True
        return False

    def _rebuild_linked_list(self):
        """Rebuild the linked list from original_order"""
        if not self.original_order:
            self.head = self.tail = self.current = None
            return
        current_song = self.current.song if self.current else None
        for i, node in enumerate(self.original_order):
            node.prev = self.original_order[i-1] if i > 0 else None
            node.next = self.original_order[i+1] if i < len(self.original_order)-1 else None
        self.head = self.original_order[0]
        self.tail = self.original_order[-1]
        if current_song:
            for node in self.original_order:
                if node.song.title == current_song.title:
                    self.current = node
                    break
        else:
            self.current = self.head

    def shuffle(self):
        """Shuffle the playlist order (visual + pointer shuffle)"""
        if self.length <= 1:
            return
        current_song = self.current.song if self.current else None
        shuffled = self.original_order.copy()
        random.shuffle(shuffled)
        for i, node in enumerate(shuffled):
            node.prev = shuffled[i-1] if i > 0 else None
            node.next = shuffled[i+1] if i < len(shuffled)-1 else None
        self.head = shuffled[0]
        self.tail = shuffled[-1]
        self.current = self.head
        if current_song:
            for node in shuffled:
                if node.song.title == current_song.title:
                    self.current = node
                    break
        self.is_shuffled = True

    def unshuffle(self):
        """Restore original order"""
        if not self.is_shuffled:
            return
        self._rebuild_linked_list()
        self.is_shuffled = False

    def get_song_list(self):
        """Get list of song titles in current linked-list order"""
        songs = []
        current = self.head
        while current:
            songs.append(current.song.title)
            current = current.next
        return songs

    def play_next(self):
        """Move to next song (or random unplayed when shuffled)"""
        if not self.current:
            return None
        if self.is_shuffled:
            if self.shuffle_session is None or len(self.shuffle_session) == self.length:
                self.shuffle_session = []
            unplayed = [node for node in self.original_order if node not in self.shuffle_session]
            if not unplayed:
                self.shuffle_session = []
                unplayed = self.original_order.copy()
            next_node = random.choice(unplayed)
            self.shuffle_session.append(next_node)
            self.current = next_node
        else:
            self.current = self.current.next if self.current.next else self.head
        return self.current.song

    def play_previous(self):
        """Move to previous song (queue mode only)"""
        if not self.current:
            return None
        if self.is_shuffled:
            return self.play_next()
        else:
            self.current = self.current.prev if self.current.prev else self.tail
        return self.current.song

# ===================== Music Player App (Colorful UI + Full Functionality) =====================
class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Music Playlist Management System")
        self.root.geometry("900x680")
        self.root.minsize(820, 600)

        # --- Color Palette ---
        self.COL_BG = "#111827"      # very dark
        self.COL_CARD = "#1F2937"    # dark card
        self.COL_ACCENT = "#22D3EE"  # cyan
        self.COL_ACCENT_2 = "#F59E0B" # amber
        self.COL_ACCENT_3 = "#EF4444" # red
        self.COL_TEXT = "#E5E7EB"    # light text
        self.COL_MUTED = "#9CA3AF"   # muted text

        self.root.configure(bg=self.COL_BG)

        # Playlist manager
        self.playlists = {}
        self.current_playlist = None

        # Playback state
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.song_length = 0
        self.start_time = 0
        self.pause_time = 0

        # Button refs
        self.move_up_btn = None
        self.move_down_btn = None
        self.shuffle_btn = None
        self.order_btn = None

        # Styles + Data + UI
        self._configure_styles()
        self._load_playlists()
        self._create_widgets()

        # Progress updater
        self._update_progress()

        # Close handling
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- Styles ----------
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Card.TFrame', background=self.COL_CARD)
        style.configure('TLabel', background=self.COL_CARD, foreground=self.COL_TEXT, font=('Helvetica', 10))

        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'), padding=8,
                        foreground='#0B1220', background=self.COL_ACCENT)
        style.map('Accent.TButton', background=[('active', '#67E8F9')])

        style.configure('Warn.TButton', font=('Helvetica', 10, 'bold'), padding=8,
                        foreground='#0B1220', background=self.COL_ACCENT_2)
        style.map('Warn.TButton', background=[('active', '#FCD34D')])

        style.configure('Danger.TButton', font=('Helvetica', 10, 'bold'), padding=8,
                        foreground='#0B1220', background=self.COL_ACCENT_3)
        style.map('Danger.TButton', background=[('active', '#F87171')])

        style.configure('Custom.TCombobox', fieldbackground=self.COL_CARD, background=self.COL_CARD,
                        foreground=self.COL_TEXT)

        style.configure('custom.Horizontal.TProgressbar',
                        troughcolor=self.COL_BG, background=self.COL_ACCENT_2, thickness=12)

    # ---------- UI ----------
    def _create_widgets(self):
        # --- Top: Title ---
        title = tk.Label(self.root, text="🎶 Music Player", fg=self.COL_ACCENT, bg=self.COL_BG,
                         font=('Helvetica', 20, 'bold'))
        title.pack(pady=(10, 6))

        # --- Playlist Controls Card ---
        playlist_controls = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        playlist_controls.pack(fill=tk.X, padx=12, pady=6)

        t1 = tk.Label(playlist_controls, text="Playlist:", bg=self.COL_CARD, fg=self.COL_TEXT,
                      font=('Helvetica', 10, 'bold'))
        t1.pack(side=tk.LEFT)

        self.playlist_var = tk.StringVar()
        self.playlist_dropdown = ttk.Combobox(playlist_controls, textvariable=self.playlist_var,
                                              state='readonly', style='Custom.TCombobox')
        self.playlist_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.playlist_dropdown.bind("<<ComboboxSelected>>", self._select_playlist)

        ttk.Button(playlist_controls, text="New", style='Accent.TButton', command=self._create_playlist)\
            .pack(side=tk.LEFT, padx=4)
        ttk.Button(playlist_controls, text="Delete", style='Danger.TButton', command=self._delete_playlist)\
            .pack(side=tk.LEFT, padx=4)

        # --- Middle: Song list + controls ---
        middle_card = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        middle_card.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # Song list
        list_frame = tk.Frame(middle_card, bg=self.COL_CARD)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.song_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=('Helvetica', 10),
                                       activestyle='none', bg=self.COL_BG, fg=self.COL_TEXT,
                                       selectbackground=self.COL_ACCENT, selectforeground='#0B1220')
        self.song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.song_listbox.bind("<Double-Button-1>", lambda e: self._play_song())

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.song_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.song_listbox.config(yscrollcommand=scrollbar.set)

        # Song management buttons
        song_controls = tk.Frame(middle_card, bg=self.COL_CARD)
        song_controls.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(song_controls, text="Add Songs", style='Accent.TButton', command=self._add_songs)\
            .pack(side=tk.LEFT, padx=4)
        ttk.Button(song_controls, text="Remove", style='Danger.TButton', command=self._remove_song)\
            .pack(side=tk.LEFT, padx=4)

        self.order_btn = ttk.Button(song_controls, text="Order: ON", style='Accent.TButton',
                                    command=self._toggle_order)
        self.order_btn.pack(side=tk.LEFT, padx=4)

        self.shuffle_btn = ttk.Button(song_controls, text="Shuffle: OFF", style='Accent.TButton',
                                      command=self._toggle_shuffle)
        self.shuffle_btn.pack(side=tk.LEFT, padx=4)

        # --- Playback Controls ---
        controls_card = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        controls_card.pack(fill=tk.X, padx=12, pady=6)

        ttk.Button(controls_card, text="⏮", style='Accent.TButton', command=self._previous_song)\
            .pack(side=tk.LEFT, padx=4)
        self.play_pause_btn = ttk.Button(controls_card, text="⏯", style='Accent.TButton', command=self._play_pause)
        self.play_pause_btn.pack(side=tk.LEFT, padx=4)
        ttk.Button(controls_card, text="⏹", style='Danger.TButton', command=self._stop_song)\
            .pack(side=tk.LEFT, padx=4)
        ttk.Button(controls_card, text="⏭", style='Accent.TButton', command=self._next_song)\
            .pack(side=tk.LEFT, padx=4)

        # --- Progress Bar + Times ---
        progress_card = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        progress_card.pack(fill=tk.X, padx=12, pady=6)

        self.time_elapsed = tk.Label(progress_card, text="0:00", width=6, bg=self.COL_CARD, fg=self.COL_MUTED,
                                     font=('Helvetica', 10, 'bold'))
        self.time_elapsed.pack(side=tk.LEFT)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_card, variable=self.progress_var, maximum=100,
                                            style='custom.Horizontal.TProgressbar', mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=8)

        self.time_total = tk.Label(progress_card, text="0:00", width=6, bg=self.COL_CARD, fg=self.COL_MUTED,
                                   font=('Helvetica', 10, 'bold'))
        self.time_total.pack(side=tk.RIGHT)

        # --- Volume ---
        volume_card = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        volume_card.pack(fill=tk.X, padx=12, pady=6)

        tk.Label(volume_card, text="🔈", bg=self.COL_CARD, fg=self.COL_TEXT, font=('Helvetica', 12))\
            .pack(side=tk.LEFT)
        self.volume_var = tk.DoubleVar(value=0.7)
        mixer.music.set_volume(self.volume_var.get())
        ttk.Scale(volume_card, from_=0, to=1, variable=self.volume_var, command=self._set_volume, length=180)\
            .pack(side=tk.LEFT, padx=8)

        # --- Now Playing ---
        now_card = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        now_card.pack(fill=tk.X, padx=12, pady=6)

        self.now_playing_label = tk.Label(now_card, text="Now Playing:", bg=self.COL_CARD, fg=self.COL_ACCENT,
                                          font=('Helvetica', 12, 'bold'), anchor='w')
        self.now_playing_label.pack(fill=tk.X)

        self.song_info_label = tk.Label(now_card, text="No song selected", bg=self.COL_CARD, fg=self.COL_TEXT,
                                        font=('Helvetica', 10), anchor='w')
        self.song_info_label.pack(fill=tk.X)

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
                              font=('Helvetica', 9), bg=self.COL_BG, fg=self.COL_MUTED)
        status_bar.pack(fill=tk.X, padx=12, pady=(0, 8))

        # Populate playlists
        self._update_playlist_dropdown()
        self._update_move_buttons_state()
        self._update_shuffle_button_state()

    # ---------- Playlist Management ----------
    def _create_playlist(self):
        name = simpledialog.askstring("New Playlist", "Enter playlist name:")
        if name and name.strip():
            name = name.strip()
            if name in self.playlists:
                messagebox.showwarning("Duplicate Name", "Playlist with this name already exists")
                return
            self.playlists[name] = Playlist(name)
            self.current_playlist = name
            self._update_playlist_dropdown()
            self._update_song_list()
            self._save_playlists()
            self.status_var.set(f"Created playlist: {name}")

    def _delete_playlist(self):
        if not self.current_playlist:
            messagebox.showwarning("No Playlist", "No playlist selected")
            return
        if messagebox.askyesno("Delete Playlist", f"Delete playlist '{self.current_playlist}'?"):
            if self.is_playing:
                self._stop_song()
            del self.playlists[self.current_playlist]
            self.current_playlist = None
            self._update_playlist_dropdown()
            self._update_song_list()
            self._update_move_buttons_state()
            self._save_playlists()
            self.status_var.set("Playlist deleted")

    def _select_playlist(self, event=None):
        selected = self.playlist_var.get()
        if selected in self.playlists:
            self.current_playlist = selected
            self._update_song_list()
            self._update_move_buttons_state()
            self._update_shuffle_button_state()
            self.status_var.set(f"Selected playlist: {selected}")

    def _update_playlist_dropdown(self):
        self.playlist_dropdown['values'] = list(self.playlists.keys())
        if self.current_playlist and self.current_playlist in self.playlists:
            self.playlist_var.set(self.current_playlist)
        elif self.playlists:
            first = next(iter(self.playlists))
            self.playlist_var.set(first)
            self.current_playlist = first
        else:
            self.playlist_var.set("")
            self.current_playlist = None

    def _add_songs(self):
        if not self.current_playlist:
            messagebox.showwarning("No Playlist", "Please create or select a playlist first")
            return
        filepaths = filedialog.askopenfilenames(
            title="Select Songs",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )
        if filepaths:
            added = 0
            for path in filepaths:
                try:
                    if os.path.exists(path):
                        song = Song(path)
                        self.playlists[self.current_playlist].add_song(song)
                        added += 1
                    else:
                        messagebox.showwarning("File Not Found", f"File not found: {path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not add {path}:\n{str(e)}")
            if added > 0:
                self._update_song_list()
                self._save_playlists()
                self.status_var.set(f"Added {added} song(s) to {self.current_playlist}")

    def _remove_song(self):
        if not self.current_playlist:
            messagebox.showwarning("No Playlist", "No playlist selected")
            return
        selected = self.song_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a song to remove")
            return
        song_title = self.song_listbox.get(selected[0])
        if self.playlists[self.current_playlist].remove_song(song_title):
            if self.current_song and self.current_song.title == song_title:
                self._stop_song()
            self._update_song_list()
            self._save_playlists()
            self.status_var.set(f"Removed: {song_title}")
        else:
            messagebox.showerror("Error", f"Could not remove {song_title}")

    def _move_song(self, direction):
        if not self.current_playlist:
            messagebox.showwarning("No Playlist", "No playlist selected")
            return
        playlist = self.playlists[self.current_playlist]
        if playlist.is_shuffled:
            messagebox.showwarning("Shuffle Active", "Cannot move songs while shuffle is active")
            return
        selected = self.song_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a song to move")
            return
        song_title = self.song_listbox.get(selected[0])
        if playlist.move_song(song_title, direction):
            self._update_song_list()
            self._save_playlists()
            new_pos = selected[0] - 1 if direction == 'up' else selected[0] + 1
            new_pos = max(0, min(new_pos, playlist.length - 1))
            self.song_listbox.selection_clear(0, tk.END)
            self.song_listbox.selection_set(new_pos)
            self.song_listbox.see(new_pos)
            self.status_var.set(f"Moved {song_title} {direction}")

    def _toggle_order(self):
        if not self.current_playlist:
            messagebox.showwarning("No Playlist", "No playlist selected")
            return
        playlist = self.playlists[self.current_playlist]
        playlist.unshuffle()
        playlist.is_shuffled = False
        playlist.shuffle_session = None
        self.order_btn.config(text="Order: ON")
        self.shuffle_btn.config(text="Shuffle: OFF")
        self._update_song_list()
        self._update_move_buttons_state()
        self.status_var.set(f"{playlist.name} set to queue order")

    def _toggle_shuffle(self):
        if not self.current_playlist:
            messagebox.showwarning("No Playlist", "No playlist selected")
            return
        playlist = self.playlists[self.current_playlist]
        playlist.shuffle()
        playlist.is_shuffled = True
        playlist.shuffle_session = []
        self.shuffle_btn.config(text="Shuffle: ON")
        self.order_btn.config(text="Order: OFF")
        self._update_song_list()
        self._update_move_buttons_state()
        self.status_var.set(f"{playlist.name} set to shuffle mode")

    def _update_move_buttons_state(self):
        if not self.current_playlist or not self.move_up_btn or not self.move_down_btn:
            return
        playlist = self.playlists[self.current_playlist]
        state = 'disabled' if playlist.is_shuffled else 'normal'
        self.move_up_btn.config(state=state)
        self.move_down_btn.config(state=state)

    def _update_shuffle_button_state(self):
        if not self.current_playlist or not self.shuffle_btn:
            return
        playlist = self.playlists[self.current_playlist]
        self.shuffle_btn.config(text=("Shuffle: ON" if playlist.is_shuffled else "Shuffle: OFF"))

    def _update_song_list(self):
        self.song_listbox.delete(0, tk.END)
        if not self.current_playlist:
            return
        playlist = self.playlists[self.current_playlist]
        for title in playlist.get_song_list():
            self.song_listbox.insert(tk.END, title)
        if playlist.current and self.current_song:
            try:
                songs = playlist.get_song_list()
                if self.current_song.title in songs:
                    idx = songs.index(self.current_song.title)
                    self.song_listbox.selection_clear(0, tk.END)
                    self.song_listbox.selection_set(idx)
                    self.song_listbox.see(idx)
            except (ValueError, AttributeError):
                pass

    # ---------- Playback ----------
    def _play_pause(self):
        if self.is_paused:
            mixer.music.unpause()
            self.is_paused = False
            self.start_time += time.time() - self.pause_time
            self.play_pause_btn.config(text="⏸")
            self.status_var.set(f"Resumed: {self.current_song.title if self.current_song else 'Unknown'}")
        elif self.is_playing:
            self._pause_song()
        else:
            self._play_song()

    def _play_song(self):
        if not self.current_playlist or not self.playlists[self.current_playlist].length:
            messagebox.showwarning("No Songs", "No songs in current playlist")
            return
        playlist = self.playlists[self.current_playlist]
        selected = self.song_listbox.curselection()
        if selected:
            song_title = self.song_listbox.get(selected[0])
            current = playlist.head
            while current:
                if current.song.title == song_title:
                    playlist.current = current
                    break
                current = current.next
        if not playlist.current:
            playlist.current = playlist.head
        if playlist.current:
            self._play_audio(playlist.current.song)

    def _play_audio(self, song):
        try:
            if not os.path.exists(song.filepath):
                messagebox.showerror("File Not Found", f"Audio file not found:\n{song.filepath}")
                return
            mixer.music.load(song.filepath)
            mixer.music.play()
            self.current_song = song
            self.song_length = song.duration if song.duration and song.duration > 0 else 180
            self.is_playing = True
            self.is_paused = False
            self.start_time = time.time()
            self.time_total.config(text=self._format_time(self.song_length))
            self.progress_var.set(0)
            self.play_pause_btn.config(text="⏸")
            self._update_now_playing(song)
            self._update_song_list()
            self.status_var.set(f"Now playing: {song.title}")
        except pygame.error as e:
            messagebox.showerror("Playback Error", f"Could not play file:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An error occurred:\n{str(e)}")

    def _update_now_playing(self, song):
        self.now_playing_label.config(text=f"Now Playing: {song.title}")
        duration_str = self._format_time(song.duration)
        info_text = f"Artist: {song.artist} | Album: {song.album} | Duration: {duration_str}"
        self.song_info_label.config(text=info_text)

    def _pause_song(self):
        if self.is_playing and not self.is_paused:
            mixer.music.pause()
            self.is_paused = True
            self.pause_time = time.time()
            self.play_pause_btn.config(text="⏯")
            self.status_var.set(f"Paused: {self.current_song.title if self.current_song else 'Unknown'}")

    def _stop_song(self):
        mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.progress_var.set(0)
        self.time_elapsed.config(text="0:00")
        self.time_total.config(text="0:00")
        self.play_pause_btn.config(text="⏯")
        self.status_var.set("Playback stopped")
        self.now_playing_label.config(text="Now Playing:")
        self.song_info_label.config(text="No song selected")

    def _next_song(self):
        if not self.current_playlist:
            return
        playlist = self.playlists[self.current_playlist]
        if not playlist.length:
            return
        next_song = playlist.play_next()
        if next_song:
            self._play_audio(next_song)
        else:
            self._stop_song()

    def _previous_song(self):
        if not self.current_playlist:
            return
        playlist = self.playlists[self.current_playlist]
        if not playlist.length:
            return
        prev_song = playlist.play_previous()
        if prev_song:
            self._play_audio(prev_song)
        else:
            self._stop_song()

    def _set_volume(self, val):
        try:
            volume = float(val)
            mixer.music.set_volume(volume)
        except (ValueError, pygame.error):
            pass

    def _update_progress(self):
        try:
            if self.is_playing and not self.is_paused and self.current_song:
                if not mixer.music.get_busy():
                    self._next_song()
                    self.root.after(200, self._update_progress)
                    return
                elapsed = time.time() - self.start_time
                if elapsed >= self.song_length:
                    self.progress_var.set(100)
                    self.time_elapsed.config(text=self._format_time(self.song_length))
                    self._next_song()
                    self.root.after(200, self._update_progress)
                    return
                progress_percent = (elapsed / self.song_length) * 100 if self.song_length > 0 else 0
                progress_percent = min(100, max(0, progress_percent))
                self.progress_var.set(progress_percent)
                self.time_elapsed.config(text=self._format_time(elapsed))
        except Exception:
            pass
        self.root.after(200, self._update_progress)

    def _format_time(self, seconds):
        try:
            seconds = max(0, seconds)
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes}:{seconds:02d}"
        except (ValueError, TypeError):
            return "0:00"

    # ---------- Persistence ----------
    def _save_playlists(self):
        try:
            save_data = {}
            for name, playlist in self.playlists.items():
                songs = []
                for node in playlist.original_order:
                    if node and node.song and os.path.exists(node.song.filepath):
                        songs.append(node.song.filepath)
                save_data[name] = {
                    'songs': songs,
                    'is_shuffled': playlist.is_shuffled
                }
            with open('playlists.pkl', 'wb') as f:
                pickle.dump(save_data, f)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save playlists:\n{str(e)}")

    def _load_playlists(self):
        try:
            with open('playlists.pkl', 'rb') as f:
                save_data = pickle.load(f)
            for name, data in save_data.items():
                if isinstance(data, list):
                    songs = data
                    is_shuffled = False
                else:
                    songs = data.get('songs', [])
                    is_shuffled = data.get('is_shuffled', False)
                self.playlists[name] = Playlist(name)
                for path in songs:
                    if os.path.exists(path):
                        try:
                            self.playlists[name].add_song(Song(path))
                        except Exception:
                            continue
                if is_shuffled and self.playlists[name].length > 1:
                    self.playlists[name].shuffle()
            if self.playlists:
                self.current_playlist = next(iter(self.playlists))
        except (FileNotFoundError, EOFError):
            pass
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load playlists:\n{str(e)}")

    def _on_close(self):
        try:
            self._save_playlists()
            mixer.music.stop()
            mixer.quit()
            pygame.quit()
        except Exception:
            pass
        finally:
            self.root.destroy()

# ===================== Run App =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayerApp(root)
    root.mainloop()
