## Description of examples
- `fixed_gray_sin.py`: unmoving gray sinusoidal texture
- `drifting_red_sin.py`: drifting red sinusoidal texture
- `fixed_binocular_sin.py` : unmoving green binocular sinosoids
- `drifting_binocular_grating.py`: two red/black gratings moving in opposite directions.
- `keyboard_switcher.py`: toggles between two drifting gratings based on keyboard press (0/1 keys). This is not something you would use in an experiment, but shows how to use the extra machinery needed to handle basic input-dependence: namely, the texture/parameter lists as well as the file saving functionality (which saves the stimuli and time of delivery).
- `input_control_simple.py`: this basically replaces the keyboard from the previous example with a random number generator. Sets up a subscriber to monitor a random input signal (1's and 0's in `publish_random2.py` which you should run separately). This monitor feeds events to the stimulus class, which toggles between two full-field sinusoidal textures.
- `input_control.py`: switches randomly among three different stimuli (controlled by the publisher `publish_random3.py` which you need to run separately). Will swap between a full field black, a drifting red full-field sinusoid, and a binocular black and white drifting grating.