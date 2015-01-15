# Installing PySISS

## Introduction

This page suggests one approach to installing pySISS and its dependencies to get started quickly. 

In the simplest case, you will already have the relevant Scientific Python distribution or configuration installed, ready for pysiss and its dependencies so that you can just type:

  pip install pysiss

from your operating system's command-line (Windows cmd shell or Linux/Mac shell).

If not, then the following sections should help.

Under Windows and Mac in particular, I have made use of the Anaconda Python distribution for this purpose. Note that I am not advocating a particular distribution of Scientific Python, merely pointing out one way in which you can get started as quickly as possible. You should feel free to install another distribution of Python, Scientific or otherwise, or just start with the one you already have, but the following levels the playing field by assuming a particular distribution. Anaconda also has the advantage of the conda package/dependency manager. This simplifies the satisfaction of one pysiss dependency in particular (GDAL). 

The following does assume at least a passing familiarity with your operating system's command-line environment.

## Windows

__1. Install Anaconda Python__

The latest version at the time of writing is 2.0.1

I have tried this under Windows 7 only

If you run into issues (e.g. re: admin privileges), select Install for: Just Me in the installer GUI

If you run into Firewall problems, you should be able to change the settings in Control Panel to allow the installer to proceed

__2. Open a command prompt window (type: cmd in Start -> Search programs and files text box) and type: python__

The first line should include the word "Anaconda"

If not, change your PATH via Control Panel so that it is before other Python installations

__3. pysiss requires the GDAL Python library that depends upon particular lib files__

The simplest approach is to type the following at a command prompt:

conda install gdal

An alternative is to try following the instructions under the Windows section of the GDAL page or follow the Quick Start steps here http://trac.osgeo.org/osgeo4w

I have not had success with either yet, whereas conda Just Works.

__4. pysiss setup requires a new setuptools than comes with Anaconda 2.0.1__ 

so type this into a command window

    easy_install -U setuptools

You may need to run the command window as administrator (right-click on command window icon for Run as Administrator option)

 I used Anaconda's but a standard cmd window should suffice

If you see an error regarding not being able to access the easy_install program, continue to the next step anyway 

__5. Now you should be able to install pysiss via:__

    pip install pysiss

Starting python and importing pysiss should give you something like this with no errors:

    Python 2.7.7 |Anaconda 2.0.1 (32-bit)| (default, Jun 11 2014, 10:41:43) [MSC v.1500 32 bit (Intel)] on win32
    ...
    >>> import pysiss
    >>> dir(pysiss)
    ['__all__', '__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__', 'borehole', 'coverage', 'metadata', 'utilities', 'vocabulary']

## Max (OSX)

__1. Install Anaconda Python__

The latest version at the time of writing is 2.0.1

You'll need Mac OS X 10.7.x or higher. I installed on 10.9.4

I would suggest installing under /usr/local if possible for easy dependency satisfaction (see GDAL below)

This is easiest to specify via the Mac OS X command-line installer vs the GUI installer

__2. Open a Terminal window and type: python__

The first line should include the word "Anaconda"

If not, change your PATH in ~/.bash_profile so that it is before other Python installations

__3. pysiss requires the GDAL Python library that depends upon particular lib files (in /usr/local/lib)__

One approach isto install this is via homebrew (thanks to Jess Robertson for suggesting this)
- Install homebrew (http://brew.sh)
- Then install the gdal libraries via the Terminal command: `brew install gdal`
- Then install the Python bindings to GDAL by typing: `sudo easy_install GDAL`
- You may see lots of warnings. If using Anaconda and not installed under /usr/local/anaconda, you may see an error regarding libgeos_c.dylib not being accessible. Creating a symbolic link to the library will fix this. For example, if Anaconda is installed under /opt/local/anaconda, type: `sudo ln -s /usr/local/lib/libgeos_c.dylib  /opt/local/lib/libgeos_c.dylib`
- TODO: Try replacing all the these steps with: `sudo conda install gdal`

__4. Now you should be able to install pysiss via:__

    sudo pip install pysiss

Starting python and importing pysiss should give you something like this with no errors:

    Python 2.7.7 |Anaconda 2.0.1 (x86_64)| (default, Jun  2 2014, 12:48:16)
    [GCC 4.0.1 (Apple Inc. build 5493)] on darwin
    ...
    >>> import pysiss
    >>> dir(pysiss)
    ['__all__', '__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__', 'borehole', 'coverage', 'metadata', 'utilities', 'vocabulary']

## Linux

On Linux things are relatively simple - first install the package dependencies via your package manager. For instance, on Debian or Ubuntu, open a terminal and type

    apt-get install python27 python-numpy python-scipy python-matplotlib libgdal1

There should be a similar process for other package managers (e.g. yum etc), although some of the packages may change

Then you should be able to install pySISS and all it's dependencies via pip:

    pip install pysiss [--user]