
from typing import TYPE_CHECKING, Dict, List, Literal, Sequence, Tuple, Union, overload
# import ultraimport

# if TYPE_CHECKING:
from libraries.movie_reading import ImageMapMovie
# else:
#     ImageMapMovie = ultraimport.ultraimport("libraries/movie_reading.py","ImageMapMovie")
import os
import re
filename_regex = r'(p[0-9]*)_s([0-9]+)_t([0-9]+).*(\.TIF|\.TIFF|\.tif|\.tiff)';
filename_regex_alphanumeric = r'(p[0-9]*)_s([^_]+)_t([0-9]+).*(\.TIF|\.TIFF|\.tif|\.tiff)';
filename_format = "{}_s{}_t{}{}"

@overload
def get_movie_params(folder:str,regex:Union[str,re.Pattern,None]=None,alphanumeric_movie:Literal[False]=...)->Tuple[str,Sequence[int],Dict[int,Sequence[int]],str]: ...
@overload
def get_movie_params(folder:str,regex:Union[str,re.Pattern,None]=None,alphanumeric_movie:Literal[True]=...)->Tuple[str,Sequence[str],Dict[str,Sequence[int]],str]: ...

def get_movie_params(folder:str,regex:Union[str,re.Pattern,None]=None,alphanumeric_movie:bool=False):
    if regex is None:
        regex = filename_regex_alphanumeric if alphanumeric_movie else filename_regex
    imagematches = [m for m in (re.match(regex,s) for s in os.listdir(folder)) if m is not None]
    movies = list(set([m.group(0) for m in imagematches if m is not None]))
    
    base = None
    ext = None

    #Get frame numbers and show the largest number
    frames:Union[Dict[int,List[int]],Dict[str,List[int]]] = dict();
    for match in imagematches:
        basename,movie,frame,exten = match.groups()
        if base is None:
            base = basename
        else:
            assert base == basename
        key = movie if alphanumeric_movie else int(movie)
        if key not in frames:
            frames[key] = []
        frames[key].append(int(frame));
        if ext is None:
            ext = exten
        else:
            assert ext == exten
    movies:Union[list[int],list[str]] = sorted(frames.keys())
    for m in movies:
        frames[m].sort();
    
    return base,movies,frames,ext

def get_movie(folder:str,alphanumeric_movie:bool=False):
    if alphanumeric_movie:
        bname,movies,frames,ext = get_movie_params(folder,alphanumeric_movie=True)
        framePaths = {m:{f:f"{bname}_s{m}_t{f}{ext}" for f in frames[m]} for m in movies}
        return ImageMapMovie[str](movies,frames,folder,framePaths)
    else:
        bname,movies,frames,ext = get_movie_params(folder,alphanumeric_movie=False)
        framePaths = {m:{f:f"{bname}_s{m}_t{f}{ext}" for f in frames[m]} for m in movies}
        return ImageMapMovie[int](movies,frames,folder,framePaths)

if __name__ == "__main__":
    from utils.filegetter import adir
    import IPython
    p = adir()
    m = get_movie(p)
    IPython.embed()