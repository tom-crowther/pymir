# PyMIR - A Python wrapper for MIRIAD focused on allowing fast development

The goal of this repo is to allow for faster development of python scripts that utilise the Radio Astronomy software MIRIAD as the underlying engine.
With MIRIAD natively being a CLI, building and executing a series of subprocess.run() commands can cause significant code repetition and slow down the development process.
To prevent this, I've gone with a lightweight wrapper that allows quick setting of parameters and execution of tasks in minimal lines of code.

I've also written it to allow interactive use within a python interpreter

## General Info
The `Task()` class is used to build the input parameters and store the output results (stdout, stderr) of a command, and the values are assigned directly by creating Object attributes matching the MIRIAD input names.
For example `fits.op = 'xyout'` assigns the value 'xyout' to the attribute op for the Object named fits 

*** NOTE ***
One of the unfortunate workarounds I've had to make is due to the *in* keyword in python
Many MIRIAD tasks use this keyword, but in this package they are instead stored as the attribute name `in_` to avoid this conflict
The value can be assigned:
1) directly:           `fits.in_ = 'file_name.uvfits'`
2) via special method: `fits.set_in('file_name.uvfits')`

All other attributes can be set as normal.
This is handled silently and in the background when running Task.interactive() in the interpreter.

## Usage
The standard MIRIAD commands have been kept wherever possible to minimise friction in learning a new set of names for commands. The below 5 lines are all that's required to execute the *fits* task and parse the output to check for errors.

```python
from pymir.pymir import Task # need to make this an actual package

task = Task('fits') # enter the MIRIAD name of the task here
task.set_in('input_file.uvfits')
task.op = 'uvin'
task.out = 'output_dir.mir'
task.go()
```

## In Live Interpreter
The task can also be run live in an interpreter such as ipython:
```python
from pymir.pymir.pymir import Task

fits = Task('fits')
fits.inp() # as with MIRIAD CLI this prints the available parameters
fits.op = 'xyout' # example of setting a parameter value
fits.inp() # this will also print the current param values once they've been set
fits.unset('op') # deletes the value stored in the specified param
fits.clear() # deletes ALL param values previously assigned

fits.interactive()
# This will run through the params one by one
# Allows for quick commands if you know what you need to put in already
# Also saves having to type quotation marks for every field as they're implicit 
# with python's input() function
# If a parameter is left blank and had a value previously it will not be overwritten

fits.help() # Prints the MIRIAD help text for the task
fits.help(param) # Prints the MIRIAD help text for the specific parameter on the task


print(Task.mirdoc)    # should be equal to $MIRPDOC
print(Task.mirbin)    # should be equal to $MIRBIN
print(Task.task_list) # shows the allowed tasks to initialise an object with
```
The task list is based on the installed binaries located in `$MIRBIN` so anything that works on your computer should work here.
Similarly the input parameters for tasks are looked up via the task documentation in `$MIRPDOC` so there shouldn't be discrepancies between what you can do in MIRIAD shell and here.

## Initial setup
Nothing much required, just clone the repo and install the package with `pip install -e .` in the `src` directory. The -e is optional but I haven't tested without yet.
The package can then be used with `from pymir.pymir import Task`
The env variables should include $MIRPDOC and the $MIRBIN directory should be in your $PATH variable as the task list is looked up from here. This is part of the default setup for MIRIAD so if done normally, and running your python scripts through a terminal session, there should be no additional setup required.

## Still to do
- Allow selection of loud or silent failure of task
- Include throw errors where necessary
- Improve the help functionality to allow parameter selection specifically
- Prettier printout of task list
- Improve checking for $MIRBIN, etc. instead of relying on env values
- Improve this file for readability
- Add helper functions to build or convert values into miriad format where reasonably achievable
- Look into graphical outputs and make sure they work (not yet reviewed)
- Implement some sort of usable history like lastexit in base MIRIAD
