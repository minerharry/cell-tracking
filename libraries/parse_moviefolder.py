
from typing import TYPE_CHECKING,Union
# import ultraimport

# if TYPE_CHECKING:
from libraries.movie_reading import ImageMapMovie
# else:
#     ImageMapMovie = ultraimport.ultraimport("libraries/movie_reading.py","ImageMapMovie")
import os
import re
filename_regex = r'(p[0-9]*)_s([0-9]+)_t([0-9]+).*(\.TIF|\.TIFF|\.tif|\.tiff)';
filename_format = "{}_s{}_t{}{}"


def get_movie_params(folder:str,regex:Union[str,re.Pattern=filename_regex]):
    imagematches = [m for m in (re.match(filename_regex,s) for s in os.listdir(folder)) if m is not None]
    movies = list(set([m.group(0) for m in imagematches if m is not None]))
    
    base = None
    ext = None

    #Get frame numbers and show the largest number
    frames:dict[int,list[int]] = {};
    for match in imagematches:
        basename,movie,frame,exten = match.groups()
        if base is None:
            base = basename
        else:
            assert base == basename
        if int(movie) not in frames:
            frames[int(movie)] = []
        frames[int(movie)].append(int(frame));
        if ext is None:
            ext = exten
        else:
            assert ext == exten
    movies = sorted(frames.keys())
    for m in movies:
        frames[m].sort();
    
    return base,movies,frames,ext

def get_movie(folder:str):
    bname,movies,frames,ext = get_movie_params(folder)
    framePaths = {m:{f:f"{bname}_s{m}_t{f}{ext}" for f in frames[m]} for m in movies}
    return ImageMapMovie[int](movies,frames,folder,framePaths)

if __name__ == "__main__":
    from filegetter import adir
    import IPython
    p = adir()
    m = get_movie(p)
    IPython.embed()