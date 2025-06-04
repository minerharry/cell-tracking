# cell-tracking
Automatic cell tracking, filtering, and analysis using segmented masks of experimental time-lapses

# Tracking Pipeline Guide
## Setup
### Downloading this repository
If you know how to use git, you can clone the repository anywhere on your system; otherwise, download the zip file from github and unzip anywhere on your system.

### First-time setup
To run this notebook you need a python installation with the proper packages added via `pip`. The easiest way to do this is to download conda, an environment manager that can create self-contained python installations. The conda distributor is Anaconda, but you really only need **miniconda**... what a headache. First, go to https://www.anaconda.com/download/success. Don't make an account - just click the button underneath **Miniconda Installers** and run it. When you get to the screen with checkboxes, add miniconda3 to PATH (which allows you to use conda from any terminal, not just the terminal it adds to your system) but DO NOT register it as your default python installation (to prevent it from mucking with other pythons on your system). Continue with the installation as it instructs.

Now that you have conda on your system, you'll want to make a python installation. To do this, you will create a conda environment. You have the choice of python version here; the notebook has been most tested with python versions 3.10 through 3.12, and personally I'd recommend 3.12 for performance and longevity reasons. To create the environment, open a terminal by searching commant prompt in the start menu (on windows). First, type the command `conda` and press enter to make sure it's on your PATH (e.g. that command prompt knows where to find it) - you should see a long help menu. If not, you'll need to use the anaconda terminal (again, through start menu - I think there are two, both work). Once you're in a terminal with conda, run the following command:
    `conda create -n tracking python=3.12 ffmpeg`
This command creates a conda environment named "tracking" with python version 3.12 and the ffmpeg package installed (important for the ability to write .mp4 video). If you want a different environment name or python version, just use a (no-spaces) word other than tracking or use a different version, e.g. python=3.10 instead of python=3.12.

Now, you'll need a terminal open in the place you downloaded this repository. You'll need to repeat this step again every time you run this notebook, so make sure you know how. You can either navigate the currently open terminal to it (which you'll need to do if you're in the anaconda terminal) using the `cd` command; typing `cd {directory}` will change the terminal's current folder to that directory. {directory} can be either relative (e.g. if you're in your home directory C:\users\{username}, `cd Documents` will open your documents folder) or absolute (starting with C:\). Alternatively, you can navigate to inside the folder in explorer, right click on the background, and there should be an "open in terminal" button.

Once you've opened your terminal there, activate your new conda environment by running `conda activate tracking` or your environment name in place of tracking. Finally, run `pip install -r requirements.txt`, which will install all of the packages listed in this repository's "requirements.txt" file to your python install. Your environment should now be fully set up!

### [Optional] Google Cloud Setup
This notebook was written to be compatible with google cloud platform, a remote storage service that allows programmatic upload/download. Basically all of my (Harrison's) optotaxis data is stored there. Setup requires downloading a commandline app and logging in; google cloud access is handled by the elston lab, and I don't know if I can share it - honestly they've been moving to longleaf, so I'm probably going to download all the optotaxis data to the raid array (or scrap the junk cause there's a lot of it) and the google cloud code will probably be vestigial. If you ever switch to another remote provider, though, it will probably come in handy (theoretically, not much would need to be changed).

However, the notebook is fully capable of just using local folders and filepaths. It will automatically detect a gcp path via its custom prefix "gs://". If you haven't set up google cloud on your device, if you run a cell with a path like that, you might get an authentication error / filenotfound error. Just change the path to a local file and you'll be fine.

## Usage
### Running Jupyter lab
The pipeline is in the format of a "Jupyter Notebook". To interact with it, you need to run the jupyter interface from the command line. Open a terminal that can run conda in the folder of this repository, as discussed in first-time setup. Activate the conda environment with `conda activate {name}`, then run the command `jupyter lab`. Jupyter is a python utility that was installed from the requirements.txt file, so you should just be able to run it. If it works, it will print a URL to the terminal (and will attempt to automatically open it in the browser; if it doesn't, copypaste the link into your browser). 

Jupyter works by hosting a website locally and letting you interact with it via the browser. The website itself, and the python code it runs, is running in that terminal where you ran `jupyter lab`, so don't close the terminal! The jupyter lab interface has a file browser on the left, where you should be able to see all the files in this repository. Open "Cell_Tracking_Pipeline.ipynb" with a double click. If you need to stop jupyter, save all your files, close the tab, then either close the terminal or press Ctrl+C with the terminal focused to tell jupyter to stop and exit to the terminal.

\[NOTE: you can also run the notebook with visual studio code's built-in notebook manager. It and jupyter both have pros and cons. Visual studio code has a much better programming interface and doesn't require the command line, but is limited in other ways. If you use visual studio code, just make sure you select the kernel associated with the conda environment you created\]

### Using Jupyter Notebooks
A "Notebook" is a code format in which code is organized into self-contained "cells" which can be run independently. Variables are stored globally and are accessible by any cell when it is run, meaning cells can be run out of order or repeatedly and the program state will be continually updated. Note that the code in a cell has no affect until the cell is actually run; for example, changing the code from `variable = 3` to `variable = 4` will not change the actual value of the variable until it is executed again.

I've tried to make the code as hard as possible to break, though. If at any time you think the program is in a bad state, first try re-running the section from the beginning, re-run the setup section at the top of the notebook, or if that still hasn't worked, you can restart the kernel (the python instance running the thing that holds the variables) with the little circular arrow at the top of the window.

### The Cell Tracking Pipeline
The notebook is divided into a number of top-level "sections". The first section is a setup section that must be run in its entirety each time you use the notebook; it contains a large number of helper functions used throughout the notebook, and it's also where you input your parameters like the experiment name, paths to the images and masks, and tell the program where you want to save the analysis.

The other top-level sections can all be run independently of one another, and once you run the setup cells, you can start where you left off from a previous time running the notebook. The pipeline goes top-to-bottom, and aside from the sections labeled \[Optional\] (mostly visualizations), each section must be run before the following can be run (it'll give you an error if a section realizes it's missing something from a previous one). 

To navigate the notebook, I highly recommend the table of contents tab on the left side of the screen (the three horizontal lines with dots)\*. Not only does it let you navigate notebook sections, it also lets you run all cells of a section at once. You can also step through running cells one at a time by pressing Shift+Enter with a code cell selected.

Certain sections and cells will have "parameters" in the code - variables whose value can/should be changed by the user. These can be anywhere from input/output paths for file saving, algorithm parameters (max/min cell area, for example), visualization parameters (colors, framerates), and other variables with smaller or larger-ranging impacts. It's not particularly glamorous or easy to use, but I've done my best to keep them to the beginning of code cells (though not always the beginning of sections). I've tried to describe each parameter with a comment before it, and the vast majority of them are marked at the end of the line with an #@param annotation (though I'm certain there are a few I missed). Most importantly, the formatting of code sections will tell you whether they have parameters in them - *if they are italicized, there are no parameters in that section or subsection, and you can feel free to run the section without ever even opening it to see what's inside*. **If a section is bolded, that means there are parameters that can be changed inside.** Remember that you have to run a cell again if you change a parameter, and usually you should rerun the following cells in the section as well.

FYI, all parameters that affect the tracking algorithms are saved to the analysis folder in a variety of files, so you don't need to worry overmuch about keeping track of what values parameters were. However, if you run a later section of the pipeline, then run the earlier section again with different parameters, the output of the later sectoin will stay (out-of-date) in the analysis folder, so make sure you keep track of that.

\*\[VSCode also has a table of contents that works similarly, though you can run sections in the notebook itself directly. With the file browser tab open on the left, it's at the bottom of the panel\].

There are a handful of python and pipeline-specific tips and tricks that help with using the notebook and/or interpreting its code, which I've listed below.


## Tips and Tricks / Python shortcuts
### Path/string formatting
To save on endlessly changing save paths, and to attempt to avoid human error when doing so, there are many many filepaths throughout the notebook that are automatically formatted based on notebook parameters. The most obvious is that basically every output goes to the current experiment's dedicated analysis output folder, so there can be no mixing up between experiments; however, there are still cases in an experiment where you might run the analysis multiple times with different parameters (for example: with or without smoothing), where you'd like to have the analyzed files for both with different names. To enable this, I created a helper function called format_path (available throughout the whole notebook) that takes in several contextual parameters from the notebook and will format a given string/filepath. Specifically, if that string has variable names surrounded with {curly brackets}, and those names correspond to one of the parameters given, it will replace that name and brackets with the value of a variable.

The format_path function will convert certain common parameters into easier plaintext values. For example, the smoothing parameter is named "do_smoothing", and using {do_smoothing} will replace it with True/False. However, format_path also allows {smoothing}, which will be replaced with "raw" or "smoothed".

Specific parameter locations might also have other formatting possibilities available. In general, the list of special format keys should be listed in the comment above the parameter. If more functionality is added to the notebook, this is definitely a place where editing the format_path function (which is in the in Global Parameters and Setup > Auxiliary Helper Functions > Path Formatting) could be helpful. In general, any parameter passed to format_path as a keyword argument (via name=value) will allow {name} to be replaced by "value".

#### Experiment Suffixes
Another way to parameterize different versions of analyzing experiments is with "experiment suffixes". This is just a trick baked into the format_path function which makes it easy to have multiple analysis folders, mask inputs, or image inputs from the same experiment. Specifically, if you add " \$suffixname" to the end of the name of the experiment, you can pass strip_suffix=True to format_path to strip that suffix away. Currently strip_suffix is true when formatting for the image and mask paths, meaning adding a suffix will produce a new analysis folder, but use the same image and masks folder. This can also be useful for making a manually tracked version of an experiment's analysis, for example.

### The Path Class
Paths, especially joining path sections together, is famously annoying, when you have to keep track of all the slashes. Luckily, python has a Path() class - a custom object - where calling `Path(path)` will turn `path` into a `Path` object. Path objects have several convenience attributes, like `.name` (returns the last component of the path, e.g. filename or directory name), `.parent` (returns the parent path), `.suffix` (the file extension), and many others. Additionally, `Path`s can be very easily nested: `Path.home()/"Documents"/"Github"/"cell-tracking"` gives a platform-independent path from the current user's home directory to Documents/Github/cell-tracking. It plays very nicely with joining multiple paths together and it's all around a great class. Most of the time when you input a string filename, you'll notice it gets converted to a path pretty quickly.

### Python Literals
When parameters ask you to provide a value to a variable, usually you will type out the value directly, to the right of the equals sign. For example, you might say `number = 2` or `name = "steven"`. In doing so, you are describing data in the form of a "literal", as you are describing the data literally. Python has several types of data, and ways to literally describe each one.

Numbers are easy - the number `123` means 123, and `123.45` means 123.45. Text is expressed in the form of "strings", denoted by wrapping characters in double or single quotes. Python also has [escape characters](https://www.w3schools.com/python/gloss_python_escape_characters.asp) which let you input special characters like line breaks or quotation marks. Boolean variables, which hold either `True` or `False`, can be assigned using the keywords `True` and `False` (e.g. `yes = True`). 

One special python value is the keyword `None` - None is a special object which generally represents the absence of a value. Certain parameters will specify (either in their description or by their *type*, see below) that they can be set to `None` to represent they have no value.

Several parameters also ask you to enter information in a structured form, beyond just a `number` or a `"string"`. Luckily, python has a very easy syntax for manually entering structured data. There are three main data structures that can be written this way: Lists, Tuples, and Dicts.

Lists and Tuples are very similar - comma separated sequences of stuff. Syntax-wise, they are identical but for that lists use \[square brackets\] to surround the list and tuples use (parentheses) to do the same:

List:  `[1,2,3,4]`, `[1,"seventeen",4,"twelve",None]`

Tuple: `(1,2,3,4)`, `(1,"seventeen",4,"twelve",None)`

As you can see, each entry in a list or a tuple can be any object. Often, though, parameters will ask you for lists containing entries all of a particular type - a list of strings, for examples (see *types* below).

Dicts, on the other hand, represent *mappings* or *look-up tables* of data. Each entry in a dictionary has two parts: a *key*, and a *value*. Like lists and tuples, these keys and values can be anything\*. Dictionaries are also comma separated lists, surrounded by \{curly brackets\}, but each entry is expressed with the syntax `key:value`:

Dict: `{1:"one", 2:"two", 3:"three", 4:"four"}`

Dicts, lists, and tuples can also be arbitrarily nested:

`square_roots = {1:(-1,1), 4:(-2,2), 9:(-3,3)}`, `pairs = [("red","blue"),("one","two"),("me","you")]`.

\*Dicts have a restriction that the keys must be **hashable**, which is a computer science term that essentially means they can be looked up really fast via a hashtable. For built-in python types, this equates to the objects being **immutable**, where their internal value cannot change. This is true for numbers - 1 is always 1, there's no extra data there - as well as strings, booleans, None, and tuples, but not lists or dicts.

### Python Types
Every object in python has a *type* which describes what it is. In the literal section, many types were described: numbers (which can either be `int`s if they are whole numbers or `float`s if not), strings (`str`), booleans (`bool`), None (`None`), lists (either `list` or `List`), tuples (either `tuple` or `Tuple`), and dictionaries (either `dict` or `Dict`). Each object has a special keyword (in parentheses) that can be used to "annotate" the type of a particular variable. This is done by adding a colon after the name of a variable when it is first introduced, then writing the type:

`name:str = "steven"`, `proportion:float = 0.9`, `items:list = [1,2,3,4]`, `speed:float = 2`

*Note that in the fourth example there, a whole number is assigned to a variable of type float, which is totally fine.*

These annotations do nothing to affect the code itself, and are entirely there for programmers (and automatic type-checkers) to help describe what variables should be. In the pipeline, I've tried to annotate every parameter with the type of data it should have.

There are two extensions to this basic typing which makes it very powerful, and can give a lot of information to the user. The first is **Union** types - used to denote when a variable can have multiple possible types. For example,

`override_speed:Union[float,None] = None` 

denotes a variable which can either have a numeric value, maybe representing the override of some other value, or `None`, which the code can check for and interpret as the lack of value, and choose not to override. In newer python versions (3.10+), this can be written as float|None, but for backwards compatibility I've converted those to Union\[\] where I found them.

The second is **Generic/Nested** types, which is super important for the data structure literals above - lists, dicts, and tuples. You'll notice that all three types are collections of other objects, each of which have their own types. By default, the `list` type represents any list of any object, of any length. Often, though, a variable needs to hold specifically a list of names (`str`), or numbers (`int` / `float`), or maybe more complicated objects like pairs of (name, num). Luckily, python provides a way to be more specific with these more advanced types, by using extra type *parameters* after the type name, surrounded by square brackets.

List is the simplest case. In older python versions (before 3.9), this sytax could only be done with the special type `List` (as opposed to the builtin type `list`), and similarly for `Dict` and `Tuple`, so the notebook exclusively uses those older notations. To annotate a list of integers, the type is `List[int]`. A list of strings is a `List[str]`. A list of booleans or None types is `List[bool|None]`, and so on. A list is of any length, all matching the provided type.

Dict is more complicated, because there are two slots to be typed: the keys and the values. A dict that maps numbers with a string representation, for example, could be a `Dict[int,str]`:

`number_names:Dict[int,str] = {1:"one",2:"two",3:"three"}`

Finally, tuples are a very interesting case. So far, tuples and lists have seemed very similar, but one key difference is that tuples are unchangeable and always of a fixed length. This means they can be annotated in a very interesting way, by assigning types to each *position* in a tuple:

`pair:Tuple[int,str] = (1,"two")`

This makes them very handy for holding multiple tidbits of information together in one block. For example, the most complicated parameter in the notebook is

`group_dict:Dict[str,List[Tuple[str,int]]] = {}`

This means group_dict is a dictionary, mapping strings to a complex list type. Each list holds some number of tuples, with each tuple being of length two; its first element is a string, and its second is an integer.

