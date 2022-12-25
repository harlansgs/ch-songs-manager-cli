## Clone Hero Songs Manager (CLI)
### A minimalist CLI application for querying and batch deleting Clone Hero songs.

<hr>

This program requires the path of your Clone Hero songs directory or a pre-created csv representing its contents (these can be generated with the "-gen-df" flag). At the moment, the script only stores song directories, artist name, song name, genre, and charter. 

The user can then query their Clone Hero library for any particular artist or genre with the "-query-genre" and "-query-artist" flags respectively. Results will be matched if the given artist/genres appear anywhere inside the matched song's data. Results can be removed from this match set using the "-ignore-artist" flag.

Matched songs can also be deleted using the "-delete-matches" flag. Removed songs will first be copied to a local ./backups directory prior to removal from the user's songs directory. Duplicate song directories are backed up as {original_song_name}_alt, but if there are already two duplicates backed up the song will simply be skipped (ie. neither backed up nor deleted). An error message is printed whenever this may occur.

Please keep in mind that the song's data fields are specified by the charter, and they are likewise wildly inaccurate in some cases. It is reccomended that you check the matched songs list before running a delete command. For artist or genre queries including spaces, please surround the name in quotes, ie. "cool artist name"

<hr>

```
usage: A simple CLI parser for local clonehero library queries. [-h] [-gen-df]
                                                                [-query-genre QUERY_GENRE [QUERY_GENRE ...]]
                                                                [-query-artist QUERY_ARTIST [QUERY_ARTIST ...]]
                                                                [-ignore-artist IGNORE_ARTIST [IGNORE_ARTIST ...]]
                                                                [-delete-matches]
                                                                path

positional arguments:
  path                  absolute path of songs directory or songs dataframe

optional arguments:
  -h, --help            show this help message and exit
  -gen-df, -df          generates a pandas dataframe from library data
  -query-genre QUERY_GENRE [QUERY_GENRE ...], -qg QUERY_GENRE [QUERY_GENRE ...]
                        searches for songs matching genre substring
  -query-artist QUERY_ARTIST [QUERY_ARTIST ...], -qa QUERY_ARTIST [QUERY_ARTIST ...]
                        searches for songs matching artist substring
  -ignore-artist IGNORE_ARTIST [IGNORE_ARTIST ...], -ia IGNORE_ARTIST [IGNORE_ARTIST ...]
                        removes search results matching artist substring
  -delete-matches, -rm  deletes all matching songs from library (makes backups first)
```

<hr>

Example: delete all \*metal\* and \*death\* songs except for the specified artists...

```
python3 libraryManager.py songs.csv -qg death metal -ia Galneryus Metallica "Five Finger" "rob zombie" Dragonforce Masahiro "System of a Down" nickelback  "Black Sabbath" "Disturbed" "Limp Bizkit" Deftones "O'Donnell" "Ozzy" "Miku" "Def Leppard" "Linkin Park" "Slayer" Evanescence "bullet for my valentine" alestorm trapt -rm
```