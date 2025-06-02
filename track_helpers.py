## Global helper function setup
### File Management
#### Image Files
#keyword should be unique for each type of object pulled from the cloud to avoid collisions
from pathlib import Path


def _fetch_image_files(in_path:Path,keyword:str,overwrite:bool,capture:bool)->Path: ##should not be called outside of other helper functions, will always overwrite
  if parameters_updated:
    raise Exception("experimental parameters (file paths, exp name, etc) changed without update analysis outputs. Please run Analysis Output Filenames cell!")
  ctx = contextlib.nullcontext if not capture else capture_output;
  is_file = str(in_path).lower().endswith(('.zip','.tif','.tiff'));
  is_gcp = is_gcp_path(in_path);
  destination = gcp_transfer_folder/keyword/strsuffix(experiment);
  if not(os.path.exists(destination)):
    os.makedirs(destination);
  command_output = None;
  if is_gcp and (overwrite or len(os.listdir(destination)) == 0):
    with ctx():
      if is_file:
        command_output = !gsutil -m cp -r "{gs_str(in_path)}" "{gs_str(destination)}"
      else:
        command_output = !gsutil -m rsync -r "{gs_str(in_path)}" "{gs_str(destination)}"
    if (command_output is not None and command_output[0].startswith("CommandException")):
      raise RuntimeError(f"Error while downloading {keyword} from bucket: " + '\n'.join(command_output));
    elif len(os.listdir(destination)) == 0:
      raise RuntimeError("Error: downloading failed for an unknown reason; downloading command_output:",command_output);
  if (not is_file):
    return destination if is_gcp else in_path; #we're done
  else:
    destination = destination/in_path.name;
  if (in_path.suffix == '.zip'):
    out_path = destination.with_suffix('');
    # print(copy_out);
    command_output = None;
    if (overwrite or not os.path.exists(out_path)):
      with ctx():
        command_output = cmd_unzip(destination,destination.parent,overwrite=True)
    # print(command_output);
    if (command_output is not None and command_output[0].startswith("CommandException")):
      raise RuntimeError(f"Error while unzipping {keyword}: " + '\n'.join(command_output));
    elif not os.path.exists(out_path):
      raise RuntimeError(f"Error: zip file {destination} does not contain folder {destination.with_suffix('')}");
    return out_path;
  elif (in_path.suffix.lower().startswith('.tif')):
    raise NotImplementedError("unstacking TIF files not yet supported");
  else:
    raise NameError("Invalid input suffix, input validation should have caught this >:(");


def fetch_images(force_overwrite=False,capture=False)->Path:
  global images_changed;
  out = _fetch_image_files(Path(images_source),'images',images_changed or force_overwrite,capture);
  images_changed = False;
  return out;

def fetch_cell_masks(force_overwrite=False,capture=False)->Path:
  global cell_masks_changed;
  out = _fetch_image_files(Path(cellmasks_source),'cellmasks',cell_masks_changed or force_overwrite,capture);
  cell_masks_changed = False;
  return out;

def fetch_nuc_masks(force_overwrite=False,capture=False)->Path:
  global nuc_masks_changed;
  out = _fetch_image_files(Path(nucmasks_source),'nucmasks',nuc_masks_changed or force_overwrite,capture);
  nuc_masks_changed = False;
  return out;


#### Analysis Files
def push_analysis(): #VERY IMPORTANT: THIS METHOD RELIES ON local_analysis_output_folder BEING ONE-DEPTH
  '''Push to sync the current contents of the gcp bucket's gcp_analysis_output_folder with its local counterpart'''
  if parameters_updated:
    raise Exception("experimental parameters (file paths, exp name, etc) changed without update analysis outputs. Please run Analysis Output Filenames cell!")
  if gcp_analysis_output_folder is None:
    print("Segmentation analysis is local only; skipping push");
    return;
  s = !gsutil -m rsync -r "{gs_str(local_analysis_output_folder)}" "{gs_str(gcp_analysis_output_folder)}"
  if (s[0].startswith("CommandException")):
    raise RuntimeError("error while uploading analysis folder: " + '\n'.join(s));

def fetch_analysis():
  '''Pull to sync the current contents of local_analysis_output_folder with its counterpart in the gcp bucket'''
  if parameters_updated:
    raise Exception("experimental parameters (file paths, exp name, etc) changed without update analysis outputs. Please run Analysis Output Filenames cell!")
  if gcp_analysis_output_folder is None:
    print("Segmentation analysis is local only; skipping fetch");
    return;
  if not os.path.exists(local_analysis_output_folder):
    os.makedirs(local_analysis_output_folder);
  t = !gsutil ls "{gs_str(gcp_analysis_output_folder)}"
  if (t[0].startswith("CommandException")):
    print("analysis folder not found in bucket, skipping analysis fetch:");
    print('\n'.join(t));
    return;
  s = !gsutil -m rsync -r "{gs_str(gcp_analysis_output_folder)}" "{gs_str(local_analysis_output_folder)}"
  if (s[0].startswith("CommandException")):
    raise RuntimeError("error while downloading analysis folder: " + '\n'.join(s));

def _submit_masks(source:Path,dest:Path):
  cmd_zip(source,dest,recurse=True);
  push_analysis()

def submit_labeled_cellmasks(submission:Path):
  '''Input a folder containing a list of cell masks; will zip, put into analysis, and push'''
  return _submit_masks(submission,labeled_cellmasks_path)

def submit_labeled_nucmasks(submission:Path):
  '''Input a folder containing a list of nucleus masks; will zip, put into analysis, and push'''
  return _submit_masks(submission,labeled_nucmasks_path);

def _fetch_masks(file:Path):
  fetch_analysis()
  dest = temp_folder/(file.stem)
  cmd_unzip(file,dest,overwrite=True);
  return dest

def fetch_labeled_cellmasks():
  '''Pulls and unzips labeled and filtered cell masks from segmentation analysis; returns a folder containing the masks'''
  return _fetch_masks(Path(labeled_cellmasks_path));

def fetch_labeled_nucmasks():
  '''Pulls and unzips labeled and filtered nucleus masks from segmentation analysis; returns a folder containing the masks'''
  return _fetch_masks(Path(labeled_nucmasks_path));
#### Misc
def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod( path, stat.S_IWRITE )
    # os.unlink( path )

def cleardir(dir): #clears all files in dir without deleting dir
  for f in os.scandir(dir):
    # f = os.path.join(dir,f)
    if os.path.isdir(f): shutil.rmtree(f,onerror=on_rm_error); #just in case
    else: os.remove(f);