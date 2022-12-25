# barebones clonehero library parser
# TODO: make a GUI so other people will actually use it?
from datetime import date
from pathlib import Path
from typing import List
import pandas as pd
import traceback
import argparse
import shutil
import re
import os

# Minimal python representation of a CH song
class Song:
    ''' fields include...
     - path : location of song folder
     - charter : for paying homage to my beloved ghostybob
     - artist : musician / composer / something something vocaloids
     - genre : genre of music (assigned by charter)
     - name : title of track
    '''
    def __init__(self, path: Path, charter: bytes = None, \
     artist: bytes = None, genre: bytes = None, name: bytes = None):
        self.path = path if not path.suffix == '.ini' else path.parent

        # if given initialization values, assign them and return
        if not path.suffix == '.ini':
            self.charter = charter
            self.artist = artist
            self.genre = genre
            self.path = path
            self.name = name            
            return

        # initialize fields to none
        self.charter = b'no-charter'
        self.artist = b'no-artist'
        self.genre = b'no-genre'
        self.name = b'no-name'
        
        # note standard library doesn't support headerless ini files
        with open(path, 'rb') as f:
            for line in f.readlines():
                # split ini entries on = symbol
                entries = line.split(b'=')
                if len(entries) <= 1:
                    continue
                
                # remove leading and trailing whitespace
                keyName,value = [txt.strip() for txt in entries][:2]
                
                # if it is data we want, record!
                if keyName == b'charter':
                    self.charter = value
                elif keyName == b'artist':
                    self.artist = value
                elif keyName == b'genre':
                    self.genre = value
                elif keyName == b'name':
                    self.name = value

    # string repr for debugging
    def __repr__(self) -> str:
        return f'Song: {self.name},\nArtist: {self.artist},\nGenre: {self.genre},\n'\
            f'Charter: {self.charter},\nLocation on disk: {self.path}'

    # returns dict representation (for interfacing w/ pandas)
    def dict(self) -> dict:
        return {
            'path' : self.path,
            'charter' : self.charter,
            'artist' : self.artist,
            'genre' : self.genre,
            'name' : self.name,
        }

# Convert tracks to pythonic representation
def generate_db(path: Path):
    songs = []

    # if given a df, instantiate directly
    if path.suffix == '.csv':
        df = pd.read_csv(path)
        songs = [
            Song(Path(path), charter, artist, genre, name) for \
            _idx,(_num, path, charter, artist, genre, name) in df.iterrows()
        ]

    # otherwise load songs from clonehero storage
    else:
        for p in path.rglob('song.ini'):
            songs.append(Song(p))

    # print summary
    print(f'> Loaded {len(songs)} songs from {path}')
    return songs

# Generates a unique file prefix for .txt query summaries
def _get_query_prefix():
    # bruteforce: retry query_number until prefix is unique
    basePrefix = 'query'
    iter = 0
    while Path(f'{basePrefix}_{iter}.songs.txt').exists():
        iter += 1
    # return first unique prefix
    return f'{basePrefix}_{iter}'

# Identifies any songs matching given parameters
def query(songs: List[Song], genre: str, artist: str, ignore_artist: str) -> List[Song]:
    # do nothing if no query params given!
    if genre is None and artist is None and ignore_artist is None:
        return
    print(f'> Querying for songs matching the following search params...')
    print(f' - genre: {genre},\n - artist: {artist},\n - ignored artists: {ignore_artist}')
    queryPrefix = _get_query_prefix()

    # grab relevant songs according to query params
    relevantSongs = [
        s for s in songs if
        (genre is not None and any([g.lower() in s.genre.lower() for g in genre])) or
        (artist is not None and any([artist.lower() in s.artist.lower() for s in artist])) or
        (genre is None and artist is None)
    ]
    ignoredSongs = []

    # then filter results according to whitelisting params 
    if ignore_artist is not None:
        ignoredSongs = list(filter(
            lambda s: any([ia.lower() in s.artist.lower() for ia in ignore_artist]),
            relevantSongs
        ))
        relevantSongs = [s for s in relevantSongs if not s in ignoredSongs]
    
    # write matched song names and paths to disk
    if len(ignoredSongs) > 0:
        with open(f'{queryPrefix}_ignored.songs.txt', 'w') as f:
            f.writelines([f'{s.name[2:-1]}, [{s.genre[2:-1]}]\n-> by {s.artist[2:-1]}\n' for s in ignoredSongs])
    if len(relevantSongs) > 0:
        with open(f'{queryPrefix}.songs.txt', 'w') as f:
            f.writelines([f'{s.name[2:-1]}, [{s.genre[2:-1]}]\n-> by {s.artist[2:-1]}\n' for s in relevantSongs])
        with open(f'{queryPrefix}.song_paths.txt', 'w') as f:
            f.writelines([str(s.path) for s in relevantSongs])

    # print query results summary
    print(f'> Ignored {len(ignoredSongs)} songs, notes in ignored_{queryPrefix}.songs.txt')
    print(f'> Recorded {len(relevantSongs)} matches in {queryPrefix}.songs.txt')
    return relevantSongs

# Deletes selected songs from disk (puts backups in ./backups)
def delete(songs: List[Song]) -> None:
    # create backup directory if it doesn't exist
    if not os.path.exists('./backups'):
        print(f'> Backups directory not found, creating ./backups...')
        os.mkdir('./backups')
    deleted = 0

    # create backups and delete songs!
    for s in songs:
        backupDirName = s.path.parts[-1]
        copied = False
        attempts = 0
        
        # lazy backup solution for duplicate song files
        while not copied:
            try:
                shutil.copytree(s.path, f'./backups/{backupDirName}')
                copied = True
            except Exception:
                attempts += 1
                backupDirName += '_alt'
                if attempts > 2:
                    print(f'> Could not backup {s.name}! Reason:')
                    print(traceback.format_exc())
                    break

        # delete if backup went through
        if copied:
            shutil.rmtree(s.path, ignore_errors=True)
            deleted += 1

    print(f'> Deleted {deleted} songs from match set')

# Parses CLI args and renders/modifies song library accordingly
if __name__ == '__main__':
    p = argparse.ArgumentParser('A simple CLI parser for local clonehero library queries.')
    p.add_argument('path', help = 'absolute path of songs directory or songs dataframe')
    p.add_argument('-gen-df', '-df', help = 'generates a pandas dataframe from library data', action='store_true')
    p.add_argument('-query-genre', '-qg', help = 'searches for songs matching genre substring', default=None, nargs='+')
    p.add_argument('-query-artist', '-qa', help = 'searches for songs matching artist substring', default=None, nargs='+')
    p.add_argument('-ignore-artist', '-ia', help = 'removes search results matching artist substring', default=None, nargs='+')
    p.add_argument('-delete-matches', '-rm', help = 'deletes all matching songs from library (makes backups first)', action='store_true')
    args = p.parse_args()
    
    # parse that song library baby
    print(f'> Generating database from {args.path}...')
    songs = generate_db(Path(os.fsdecode(args.path)))

    # generate df as requested
    if args.gen_df:
        df = pd.DataFrame([s.dict() for s in songs])
        df.to_csv('songs.csv')

    # run song search and delete queries
    relevant = query(songs, args.query_genre, args.query_artist, args.ignore_artist)
    if args.delete_matches:
        delete(relevant)

    