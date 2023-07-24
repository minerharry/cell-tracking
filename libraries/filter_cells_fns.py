from typing import Literal, Tuple, Union
from typing import overload
import numpy as np
from skimage.io import imread
import os
from scipy import ndimage
from skimage import measure
import pandas as pd
from libraries.centers import get_centers

from typing import Any

class CellFilters:
    touching_edge = -1
    too_small = -2
    too_large = -3
    two_nuclei = -4
    
@overload
def getcells(filecell:Union[Union[str, bytes, os.PathLike],np.ndarray],filenuc:Union[Union[str, bytes, os.PathLike],np.ndarray],parameters:dict[str,Any],return_metrics:Literal[False]=...,centertype="approximate-medoid",all_centers=False,
    )->tuple[np.ndarray,np.ndarray]: ...

@overload
def getcells(filecell:Union[Union[str, bytes, os.PathLike],np.ndarray],filenuc:Union[Union[str, bytes, os.PathLike],np.ndarray],parameters:dict[str,Any],return_metrics:Literal[True]=...,centertype="approximate-medoid",all_centers=False,
    )->tuple[pd.DataFrame,np.ndarray,np.ndarray]: ...

def getcells(filecell:Union[Union[str, bytes, os.PathLike],np.ndarray],filenuc:Union[Union[str, bytes, os.PathLike],np.ndarray],parameters:dict[str,Any],return_metrics=False,centertype="approximate-medoid",all_centers=False):
    #membrane
    maskMem:np.ndarray=imread(filecell) if not isinstance(filecell,np.ndarray) else filecell;
    maskMem[maskMem>0]=1
    maskMem = ndimage.binary_fill_holes(maskMem).astype(np.int16);

    #nuclei
    maskNuc:np.ndarray = imread(filenuc) if not isinstance(filenuc,np.ndarray) else filenuc;
    maskNuc[maskNuc>0]=1
    maskNuc = ndimage.binary_fill_holes(maskNuc).astype(np.int16);

    #label different objectes in masks
    maskMem,numMem = measure.label(maskMem,return_num=True)
    maskNuc,numNuc = measure.label(maskNuc,return_num=True);

    if numMem < 128 and numNuc < 128:
        maskMem = maskMem.astype('int8');
        maskNuc = maskNuc.astype('int8');
    else:
        maskMem = maskMem.astype('int16');
        maskNuc = maskNuc.astype('int16');
  
    #FILTERS
    if parameters['remove_cells_touching_edge'] == True:
        maskMem=remove_touching_edge(maskMem,mark_removed=CellFilters.touching_edge)
  
    if parameters['filter_cell_size'] == True:
        maskMem = remove_extreme_objects(maskMem, parameters['minareacell'], parameters['maxareacell'], mark_removed = (CellFilters.too_small,CellFilters.too_large))
    
    if parameters['filter_nuc_size'] == True:
        maskNuc = remove_small_objects(maskNuc, parameters['minareanuc'],mark_removed=CellFilters.too_large)
  
    if parameters['remove_multi_nuclei_cells'] == True:
        maskMem = remove_multiple_nuclei_cells(maskMem,maskNuc,mark_removed=CellFilters.two_nuclei)

    if (return_metrics):
        #if there are cells get metrics
        ids=list(range(1,numMem+1));
        #remove 0 (background) from ids
        # ids.remove(0)
        if len(ids) > 0:
            to_measure = maskMem.copy()
            to_measure[to_measure < 0] = 0
            cellsmetrics = measure.regionprops_table(to_measure, properties=('label','area'))
            cellsmetrics=pd.DataFrame(cellsmetrics)
            if (len(cellsmetrics['label']) > 0 and len(cellsmetrics['area']) > 0):
                #GET CENTERS
                #get labels
                labels=cellsmetrics['label']    
                #Because 'label' was copied from the table, after computing the centers 
                #and concatenating them to the table they should be in the right order
                if not all_centers:
                    centers=get_centers(to_measure,centertype,labels, False)
                    #add centers to cell properties
                    cntr=pd.DataFrame(data=np.asarray(centers),columns=[centertype+'x',centertype+'y'])
                    cellsmetrics=pd.concat([cellsmetrics,cntr],axis=1)
                else:
                    for ctype in get_centers.valid_centers: 
                        ## to save on import complexity, I (H) just set get_centers.valid_centers to the list of valid center inputs. 
                        ## It's still a function, it just has the attribute now. source is libraries.centers
                        centers=get_centers(to_measure,ctype,labels,False)
                        #add centers to cell properties
                        cntr=pd.DataFrame(data=np.asarray(centers),columns=[centertype+'x',centertype+'y'])
                        cellsmetrics=pd.concat([cellsmetrics,cntr],axis=1)
        else:
            cellsmetrics=pd.DataFrame();
        return cellsmetrics, maskMem, maskNuc 
    else:
        return maskMem,maskNuc
 

def remove_multiple_nuclei_cells(labeledcellsmask:np.ndarray,labelednucsmask:np.ndarray,mark_removed:int=0)->np.ndarray:
    out = np.copy(labeledcellsmask)
    labels=set(out.ravel())
    for i in labels:
        if i > 0: #ignore background           
            #get obect i coordinates 
            icoord=np.where(out==i)
            #get values of nuclear mask for those coordinates
            nucvalues=labelednucsmask[icoord]
            #get labels list (get individual elements)
            nuclabels=set(nucvalues)
            #if there is more than one nuclei (2 objects counting backround)
            if len(nuclabels) > 2: 
                #remove cell object:
                out[out==i]=mark_removed
    return out


#essentially identical procedure to morphology's version, but with less input validation and custom mark_removed value
def remove_large_objects(labeledmask:np.ndarray,maxarea:float,mark_removed:int=0)->np.ndarray:
    out = np.copy(labeledmask)
    pos = np.copy(out)
    pos[pos<0] = 0
    component_sizes = np.bincount(pos.ravel()) #label-indexed array of sizes (starting from zero)
    too_large = component_sizes > maxarea #label-indexed bool array
    too_large[0] = False #don't affect the zero object
    too_large_mask = too_large[pos] #use labels as indexes into the array
    out[too_large_mask] = mark_removed #mask: array with each label replaced by its corresponding element in too_large
    return out

def remove_small_objects(labeledmask:np.ndarray,minarea:float,mark_removed:int=0)->np.ndarray:
    out = np.copy(labeledmask)
    pos = np.copy(out)
    pos[pos<0] = 0
    component_sizes = np.bincount(pos.ravel()) #label-indexed array of sizes (starting from zero)
    too_small = component_sizes < minarea #label-indexed bool array
    too_small[0] = False #don't affect the zero object
    too_small_mask = too_small[pos] #mask: array with each label replaced by its corresponding element in too_small
    out[too_small_mask] = mark_removed
    return out

def remove_extreme_objects(labeledmask:np.ndarray,minarea:float,maxarea:float,mark_removed:int|tuple[int,int]=0):
    if isinstance(mark_removed,int):
        mark_removed = (mark_removed,mark_removed)
    out = np.copy(labeledmask)
    pos = np.copy(out)
    pos[pos<0] = 0
    component_sizes = np.bincount(pos.ravel())

    too_large = component_sizes > maxarea
    too_large[0] = False
    too_large_mask = too_large[pos]

    too_small = component_sizes < minarea
    too_small[0] = False
    too_small_mask = too_small[pos]

    out[too_small_mask] = mark_removed[0]
    out[too_large_mask] = mark_removed[1]
    return out


def remove_touching_edge(labeledmask:np.ndarray,margins:Union[int,Tuple[int,int],Tuple[int,int,int,int]]=1,mark_removed:int=0)->np.ndarray:
    '''remove regions that touch the edge of the image.

    margins param can be:
    - int - will remove regions that have pixels within distance margins from each edge; will not remove if margins=0
    - tuple[int,int] - filter regions within margins[0] of the first axis, within margins[1] of the second axis
    - tuple[int,int,int,int] - filter regions by: [-first axis, +first axis, -second axis, +second axis]
    '''
    if isinstance(margins,tuple) and len(margins) == 2:
        margins = (margins[0],margins[0],margins[1],margins[1]);
    elif isinstance(margins,int):
        margins = (margins,margins,margins,margins);
    

    out = np.copy(labeledmask)

    #scan each edge of the image
    first=out.shape[0]
    second=out.shape[1]

    def rm_idx(a,b):
        if out[a,b] > 0:
            out[out==out[a,b]] = mark_removed;
    
    #i = first axis, j = second axis

    #negative first axis
    for i in range(margins[0]): 
        for j in range(second):
            rm_idx(i,j);            
    
    #positive first axis
    for i in range(first-margins[1],first):
        for j in range(second):
            rm_idx(i,j);

        
    #negative second axis
    for i in range(first):
        for j in range(margins[2]):
            rm_idx(i,j);
    
    
    #positive second axis
    for i in range(first):
        for j in range(second-margins[3],second):
            rm_idx(i,j);
    
    return out