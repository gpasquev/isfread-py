Python script for read data from a Tektronix ".ISF" files
----------------------------------------------------------

Python script for ascii-converting binary ISF files from TDS series Tektronix 
Oscilloscope instruments. 

Short usage example (for Python3.x)
--------------------
In linux command line (convert .isf to .csv)::

    $ python isfread.py file.isf -o ascii.csv 

--------------------
As the python module::

    $ python 
    >>> from isfread import isfread
    >>> data, header = isfread('file.isf')
    >>> 

Short usage example (for Python2.x)
--------------------
In linux command line (convert .isf to .dat)::

    $ python isfread_py2.py file.isf > ascii.dat 

--------------------
As the python module::

    $ python 
    >>> from isfread_py2 import isfread
    >>> data, header = isfread('file.isf')
    >>> 

Author
------
Gustavo Pasquevich - 2011 
UNLP-CONICET-Argentina

keywords: ISF, TekTronix, isfread, python

Acknowledgment
--------------

Based on matab script isfread.m by Jhon Lipp. 

