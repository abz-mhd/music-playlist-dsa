# 🎶 Music Playlist Manager (DSA)

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
[![GitHub stars](https://img.shields.io/github/stars/abz-mhd/music-playlist-dsa?style=for-the-badge)](https://github.com/abz-mhd/music-playlist-dsa/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/abz-mhd/music-playlist-dsa?style=for-the-badge)](https://github.com/abz-mhd/music-playlist-dsa/network)
[![GitHub issues](https://img.shields.io/github/issues/abz-mhd/music-playlist-dsa?style=for-the-badge)](https://github.com/abz-mhd/music-playlist-dsa/issues)
[![GitHub license](https://img.shields.io/github/license/abz-mhd/music-playlist-dsa?style=for-the-badge)](LICENSE) <!-- TODO: Add a LICENSE file -->

**A command-line music playlist manager demonstrating core Data Structures and Algorithms.**

</div>

## 📖 Overview

This project is a Python-based command-line application designed to manage music playlists. It serves as a practical demonstration of how fundamental Data Structures and Algorithms (DSA) can be applied to build an interactive application, focusing on efficient storage, retrieval, and manipulation of song and playlist data. The application allows users to create, modify, view, and interact with their music collections directly from the terminal, with playlist data persisted across sessions using Python's `pickle` module.

## ✨ Features

-   **Playlist Management**: Create, view, select, and delete multiple music playlists.
-   **Song Management**: Add new songs (with title, artist, genre) to a selected playlist.
-   **Song Removal**: Remove specific songs from a playlist.
-   **Interactive Playback**: Simulate playing songs from a playlist.
-   **Search Functionality**: Efficiently search for songs by title or artist across all playlists.
-   **Data Persistence**: Automatically saves and loads playlist data using serialization (`.pkl` files), ensuring your data is not lost between sessions.
-   **DSA Implementation**: Built with core data structures (e.g., linked lists, hash maps, or trees, depending on internal implementation) for optimized performance in managing songs and playlists.

## 🛠️ Tech Stack

-   **Runtime**: Python
-   **Data Persistence**: Python's `pickle` module for object serialization.

## 🚀 Quick Start

### Prerequisites
-   Python 3.x (tested with Python 3.8+)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/abz-mhd/music-playlist-dsa.git
    cd music-playlist-dsa
    ```

2.  **Run the application**
    ```bash
    python Playlist.py
    ```

### First Run

Upon running `Playlist.py` for the first time, the application will either load existing `playlists.pkl` data or initialize an empty state if no such file is found. It will then present an interactive menu in your terminal.

## 📖 Usage

After starting the application with `python Playlist.py`, you will be greeted by a main menu. You can navigate through the options by entering the corresponding number.

**Example Interactive Session:**

```
Welcome to the Music Playlist Manager!

Main Menu:
1. Create New Playlist
2. Select Playlist
3. View All Playlists
4. Search for Song
5. Exit

Enter your choice: 1
Enter the name for your new playlist: My Rock Hits
Playlist 'My Rock Hits' created successfully!

Main Menu:
1. Create New Playlist
2. Select Playlist
3. View All Playlists
4. Search for Song
5. Exit

Enter your choice: 2
Available Playlists:
1. My Rock Hits

Enter the number of the playlist you want to select: 1
Selected playlist: My Rock Hits

Playlist Menu for 'My Rock Hits':
1. Add Song
2. Remove Song
3. View Songs
4. Play Songs (Simulated)
5. Go back to Main Menu

Enter your choice: 1
Enter song title: Stairway to Heaven
Enter artist: Led Zeppelin
Enter genre: Rock
'Stairway to Heaven' added to 'My Rock Hits'.

Playlist Menu for 'My Rock Hits':
1. Add Song
2. Remove Song
3. View Songs
4. Play Songs (Simulated)
5. Go back to Main Menu

Enter your choice: 3
Songs in 'My Rock Hits':
1. Stairway to Heaven - Led Zeppelin (Rock)

Playlist Menu for 'My Rock Hits':
1. Add Song
2. Remove Song
3. View Songs
4. Play Songs (Simulated)
5. Go back to Main Menu

Enter your choice: 5

Main Menu:
1. Create New Playlist
2. Select Playlist
3. View All Playlists
4. Search for Song
5. Exit

Enter your choice: 5
Exiting. Goodbye!
```

## 📁 Project Structure

```
music-playlist-dsa/
├── Playlist.py    # Main application script containing all logic
├── playlists.pkl  # Data file for persisting playlists (generated after first run)
└── README.md      # Project README file
```

## ⚙️ Configuration

The application primarily operates through its interactive menu. There are no external configuration files or environment variables to set up. Playlist data is automatically saved to and loaded from `playlists.pkl` in the root directory.

## 🔧 Development

The entire application logic resides within `Playlist.py`. Developers can explore this file to understand the underlying data structures and algorithms used for managing playlists and songs.

### Running Tests
No explicit test suite is included in this repository. You can manually test functionalities by interacting with the CLI as described in the Usage section.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for new features, improvements, or bug fixes, please open an issue or submit a pull request.

## 📄 License

This project is currently without a specific license. Please refer to the repository owner for licensing information. <!-- TODO: Add a LICENSE file with a chosen open-source license, e.g., MIT -->

## 🙏 Acknowledgments

-   This project is a demonstration of Data Structures and Algorithms concepts in a practical application.

## 📞 Support & Contact

-   🐛 Issues: [GitHub Issues](https://github.com/abz-mhd/music-playlist-dsa/issues)

---

<div align="center">

**⭐ Star this repo if you find it helpful or interesting!**

Made with ❤️ by [abz-mhd](https://github.com/abz-mhd)

</div>
```
