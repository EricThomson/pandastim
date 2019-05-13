## Examples for pandastim package
List of examples to see how things work, or to test the code.

### Full field static stimuli
Display nonmoving stimuli using the `FullFieldStatic` class.
- static_fullfield_sin.py
- static_fullfield_2byte_sin.py
- static_fullfield_red_sin.py
- static_fullfield_circle.py
- static_fullfield_red.py

### Full field drifting stimuli
Display textures that drift across the window forever using the `FullFieldDrift` class.
- drifting_fullfield_sin.py
- drifting_fullfield_2byte_sin.py
- drifting_fullfield_red_sin.py
- drifting_fullfield_grating.py
- drifting_fullfield_circle.py

### Binocular static
Testing out `BinocularStatic` class.
- static_binocular_grating.py
- static_binocular_sin.py
- static_binocular_2byte_sin.py
- static_binocular_sin_red.py
For when I have independent textures (under construction)
- static_binocular_red_green.py
- static_binocular_circles.py (half attempt in working)

### Binocular stimuli
Test out `BinocularDrift` class.
- drifting_binocular_grating.py
- drifting_binocular_green_sin.py

### Experiments (under construction)
Note experiments are more complex than other classes as they require a path for saving data, setting up what texture functions to use, what parameters
to use for each texture you will show, stimuli to show, etc..

- drifting_fullfield_grating_experiment.py
