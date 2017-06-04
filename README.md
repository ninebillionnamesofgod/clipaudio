# Install

Install the required python libraries

    $ pip install -r requirements.txt

if installing from a virtualenv, or prefix with sudo to install system-wide

# Running

Put the audio files to be clipped in the 'input' directory. 

    $ python main.py

This runs the clipping process on all the files in the input directory. Clipped output files are placed in 'output'

    $ python main.py input/abc.flac

This runs the clipping process on a single file

