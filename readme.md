# pandastim
<img align = "right" width = "120" src=".\images\omr_sin_example.png ">

Cross-platform Python package for generating visual stimuli using the [Panda3d](https://www.panda3d.org/) library, a Python game-engine developed by Disney.

### Installation
This assumes you are using Anaconda and Python 3:

    conda create --name pstim
    conda activate pstim
    conda install numpy scipy matplotlib zeromq
    pip install panda3d

Once you've got your environment squared away, you can install pandastim by heading to the directory where you want it installed, and run:    

    git clone https://github.com/EricThomson/pandastim.git

To test the installation, try running one of the examples in [examples/readme.md](examples/readme.md). Since panda3d is sometimes fickle with IDEs, I always run scripts from the command line (e.g., `python -m examples.drifting_binocular_grating` if you are in the `pandastim` directory).

### Package structure
The three main modules:
- `stimuli.py`: instances of `ShowBase`, the panda3d class that is used to render scenes.  Can be as simple as showing a static grey sinusoidal grating, or showing a sequence of stimuli locked to an input signal from some external source.
- `textures.py`: texture classes used by stimuli. They are all instances of the `TextureBase` abstract base class defined therein. Creating your own textures is very easy: just create a numpy array that shows what you want!
- `utils.py`: helper code used across different classes. For instance, the interface classes for zmq sockets are here.

The `examples/` folder contains representative examples. It is probably easiest to use these examples as a starting point for building your own experiments.

### Tweaking/profiling pandastim apps
There is a well-commented config file in `panda3d\etc\Config.prc`: this includes lots of parameters you can set (such as the window location and size). To uncap the frame rate of panda3d you can add the following line:

    sync-video #f

This will *not* let you show video at frame rates faster than your monitor's maximum, but can be useful to test how fast your code could run when not encumbered by such limitations.

If your app is running more slowly than you'd like, panda3d comes with a nice graphical code profiler that will show you were the resources are being used. The stimulus classes all include a `profile_on` flag (which defaults to `False`). To activate this profiler, you have to run the standalone `pstats` program separately before starting your Python code (see below), and set that flag to `True`. Setting `profile_on` to `True` will also cause an FPS display to show on your stimulus window, and it will cause a small 'x' to appear at the center of the stimulus (when applicable). See the examples folder if curious.

On Windows, the correct `pstats.exe` file is in your conda directory in `\envs\pstim\Scripts` -- there is another instance of pstats.exe in `pstim\Lib` that will not work (not sure why). In Linux, `pstats` is in `\envs\pstim\bin` -- run it from the command line with `./pstats` -- you may need to install the module `libcanberra-gtk-module` first (`sudo apt-get install libcanberra-gtk-module`).

To learn more about optimizing/profiling in panda3d: https://docs.panda3d.org/1.10/python/optimization/index

#### Notes
- If you are just learning panda3d, consider working through their tutorial (https://www.panda3d.org/manual/). Also you might consider installing their SDK, as it comes with useful examples (https://www.panda3d.org/download/).
- panda3d doesn't listen to your OS scale settings, so 800 pixel window is an 800 pixel window, it will not be scaled by your OS.
- It often looks like textures are drifting vertically/horizontally even when they are not. This is the well-known 'aperture problem' from psychophysics. To disambiguate, increase the window size until you can see their edges.
- To get more info about what is going on in `stimuli.py` you can use the logger set up there, either change the cutoff from INFO to DEBUG, or add some messages where you want more feedback.
- Do versioning with git tag. E.g., `git tag -a "v0.1" -m "version v0.1"`
- On filtering out stimulus repeats (so you don't change the stim when you get the same input): this is currently done in `set_stimulus` (for instance in `examples/input_control_simple.py`) but it could be done by the subscriber, monitor, or sender (publisher) applications. Just do what is best for you.
- If you want to set antialiasing: https://docs.panda3d.org/1.10/python/programming/render-attributes/antialiasing .
- If you want to programatically change the camera position, you need to disable the mouse: `ShowBaseGlobal.base.disableMouse()`. pandastim don't currently use this mechanism, but it may be useful at some point for drifting around a scene.
- Consider using apitrace to look at what is going on on the back end.

#### Conventions
PEP8, largely. UpperCamelCase for classes; lower_case_underscore for vars/functions/methods. Explicit is better than implicit.

#### Acknowledgments
Thanks to rdb (developer of panda3d) who provided lots of help figuring out how to efficiently do 2d things in a 3d game engine. Also the panda3d community in general has been very helpful.

#### To do
- For InputControlParams, add checks for same inputs -- don't change transform if the inputs are the same (decide how fine-grained to make this)
- Find good example of weird rendiering differences with two angles, and ask about it @panda3d.
- Create open loop stim class.
- Create new stimulus classes
    - scaling
    - looming circle stimulus (static_fullfield_circle)
    - randomly updating stimulus (tex_random_working.py)
    - radial sine stimulus
    - radial grating stimulus:
- Add contrast to sines/gratings
- Independent color of middle band? Right now it is constrained to be the background color (black)
- Add independent velocities/textures for binocular stimuli (so left/right can have different textures).
- Consider making monitor a process, or use zmq iostream features: see `working/monitoring_notes.txt`.
- Document how to make a new texture class and stim class.
- How to close programatically? Would be useful for smoothness and also could add time/close signal code to save file.
- How to ensure there is a texture (avoid `Assertion failed: !is_empty()`) Seems you are asking for bugs. Note cards made most recently will show on top of other cards. You could make them invisible temporarily or something. Ultimately add a third stim type and test this it will be a bit messy: you will want to generate a list of stim types, and then when you have one type, delete the other types in clear_cards, not just the one we are about to switch away from.
- It seems when stimuli switch over there is some shearing/tearing of the texture for the first few ms.
- It is a known issue that pub/sub in zeromq misses the first message published. To overcome this, sync up the pub/sub first, before you start publishing: https://stackoverflow.com/a/25580646/1886357. Or you could just send a bunch of 0's initially to get them sync'd up.
- check with photodiode at different locations on window: is it identical?
- try compressing textures? (https://www.panda3d.org/manual/?title=Texture_Compression)
- Consider porting to `pixel2d` (basics are in working/)? then everything will be in pixel-based coordinates rather than normalized.
-  Consider making texture/window size x/y different.
- make conda installer for pandastim (or pip and then conda):
    - https://docs.conda.io/projects/conda-build/en/latest/user-guide/tutorials/build-pkgs-skeleton.html
    - https://medium.com/@giswqs/building-a-conda-package-and-uploading-it-to-anaconda-cloud-6a3abd1c5c52
    - https://realpython.com/pypi-publish-python-package/
