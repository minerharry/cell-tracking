import math
from typing import DefaultDict, Dict, List, Tuple, Union
import numpy as np
import matplotlib
import sys
import copy

from pandas import DataFrame

def distance(p1:Tuple[int,int],p2:Tuple[int,int]):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2);

def apply_qc(in_tracks:Dict[int,Dict[int,DataFrame]],
        keep:Dict[int,List[int]],
        trim:Dict[Tuple[int,int],Tuple[int,int]],
        removemov:List[int],
        exclude:List[Tuple[int,int]],
        minTrackLength:Union[None,int]=None,
        minTrackDisplacement:Union[None,float]=None,
        initialTrackDelay:Union[int,None]=None,
        )->Tuple[Dict[int,Dict[int,int]],Dict[int,Dict[int,DataFrame]]]:

    initialTrackDelay = initialTrackDelay or None
    if initialTrackDelay is not None and initialTrackDelay < 0:
        raise ValueError("argument initialTrackDelay must be nonnegative")

    if initialTrackDelay is not None:
        if minTrackLength is not None:
            if minTrackLength < initialTrackDelay:
                print("Warning: initial track delay larger than minimum track length; short tracks would get swallowed by the delay. Setting mintracklength to the delay");
                minTrackLength = initialTrackDelay
        else:
            minTrackLength = initialTrackDelay;

    
    out_tracks=copy.deepcopy(in_tracks)
    #a sample containes movies, each movie contains tracks
    
    #initialize the status of all tracks in the sample as 1 (active)
    sampTrStatus:Dict[int,Dict[int,int]]={};
    for movie in in_tracks:
        sampTrStatus[movie] = {};
        for id in in_tracks[movie]:
            sampTrStatus[movie][id] = 1


    
    ###CONDITIONS ON TRACKS
    if minTrackLength:
        for imov in out_tracks:
            for itr in out_tracks[imov]:        
                #if track length less than min length deactivate track
                if len(out_tracks[imov][itr]) < minTrackLength:
                    sampTrStatus[imov][itr]=0
                    print(f"removing track {itr} from movie {imov}: track length too short")

    if minTrackDisplacement is not None:
        for imov in out_tracks:
            for itr in out_tracks[imov]:
                #if track length less than min length deactivate track
                # framec = sample[imov][itr]["frame"];
                # firstframe = framec.iloc[0]
                # lastframe = framec.iloc[-1]
                # ifirstframe = framec[framec==start].index[0]
                if distance(out_tracks[imov][itr].iloc[0],out_tracks[imov][itr].iloc[-1]) < minTrackDisplacement:
                    sampTrStatus[imov][itr]=0
                    print(f"removing track {itr} from movie {imov}: track displacement too short")
    

    #exclude tracks after visual inspection
    #exclude=[[2,3],[2,4]]
    #exclude=[[1,7]]                
    for mov,track in exclude:
        sampTrStatus[mov][track]=0
    

    #only keep certain tracks
    #input: dict of elements of the form {movie:[track1,track2,...]}
    for mov,tracks in keep.items():
        #for all the tracks in movie i[0]-1 turn off all the tracks
        for itracks in sampTrStatus[mov]:
            sampTrStatus[mov][itracks]=0
        #turn on the desired tracks
        for itracks in tracks:
            sampTrStatus[mov][itracks]=1

    #remove movies
    for mov in removemov:
        for itr in sampTrStatus[mov]: 
            sampTrStatus[mov][itr]=0;
            
            
    ###CONDITIONS ON TRACK LENGTHS
    #trim tracks
    #input: dict (trim) of elements with the form {(movie, track):(begginning frame, end frame)]
    #trim={(7,1):(1,53)}
    trims:Dict[int,Dict[int,Tuple[int,int]]] = DefaultDict(lambda: {});
    for (mov,track),(start,end) in trim.items():
        if track == -1:
            trims[mov] = DefaultDict(lambda: (start,end));
        else:
            trims[mov][track] = (start,end);

    for mov,t in trims.items():
        for (track,(start,end)) in t.items():
            #print(i)
            
            #get 'frame' column
            framec=out_tracks[mov][track]['frame']
            
            ##check bounds of input frames:

            #get first and last frames of track
            firstframe = framec.iloc[0]
            lastframe = framec.iloc[-1]

            if initialTrackDelay is not None:
                firstframe = firstframe+initialTrackDelay;


            #check that input frames are in bounds
            if start < firstframe or start > lastframe:
                raise Exception(f'in movie {mov} track {track} beggining of trimming {start} is out of range {(firstframe,lastframe)}');
            if end < firstframe or end > lastframe:
                raise Exception(f'in movie {mov} track {end} end of trimming {end} is out of range {(firstframe,lastframe)}');

            if start >= end :
                raise Exception(f'in movie {mov} track {track} end of trimming {end} is smaller or equal than beggining of trimming {start}')
                
            ifirstframe = framec[framec==start].index[0]
            #get index of desired last frame
            ilastframe = framec[framec==end].index[0]

            

            #trim track
            out_tracks[mov][track]=out_tracks[mov][track].loc[ifirstframe:ilastframe+1]    
    

    return sampTrStatus, out_tracks
