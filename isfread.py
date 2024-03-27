#!/usr/bin/env python
#coding: utf-8

"""Python 3 script for read data from a Tektronix ".ISF" files

AS SCRIPT:
=======

    usage: isfread_py3.py [-h] [-v] [-d] [-o OUTPUT_FILE] INPUT_FILE

    positional arguments:
      INPUT_FILE
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Show verbose message (default: False)
      -d, --debug           Debug mode if this flag is set (default: False)
      -o OUTPUT_FILE, --out OUTPUT_FILE
                            Output as CSV file with the name:


AS PYTHON MODULE:
==============

    >>> from isfread_py3 import isfread
    >>> data, header = isfread("hoge.isf")
    # Option "verbose": show verbose message if True (default: False)
    #        "debug":   show debug message if True (default: False)
    >>> 
    
    INPUT: 
        string of the ISF-filename

    OUTPUT:
        returns these objects
            if pointformat == 'Y'
                ndarrayValue (2*N) : [[Time...], [Value...]]                    
                tupleHeader        : (header information with dictionary,)

            elif pointformat == 'ENV'
                ndarrayValue (3*N) : [[Time...], [MinValue...], [MaxValue...]]
                tupleHeader        : (header information with dictionary,)

----------------------------------------------------------------------------
About ISF files and this code
=============================
This code is base on the similar code for Matlab isfread.m from John 
Lipp [Lipp]. Information on ISF-file is detailed in the Tektronix "Programmer 
Manual" [TekMan].
Then rewritten by Gustavo Pasquevich as python 2 code.
Modified by Dai Onishi as python 3 code and edited by Haruki Ejiri.
Last updated on August 21 2018. 

References:
[Lipp] John Lipp - isfread.m matlab code.
            www.mathworks.com/matlabcentral/fileexchange/6247
[TekMan] Tektronix Manuals, "Programmer Manual. TDS3000, TDS3000B, and  
            TDS3000C Series Digital Phosphor Oscilloscopes", 071-0381-03.
            www.tektronix.com
---------------------------------------------------------------------------

Contact: Gustavo Pasquevich, Universidad Nacional de La Plata - Argentina
         gpasquev@fisica.unlp.edu.ar
"""

import struct
import sys
import numpy as np
import argparse


def isfread(filename, verbose=False, debug=False):
    fileInput = open(filename,'rb')
    bytesHeader = fileInput.read(511); # read first 511 bytes
    
    """
    The version of the ISF file can be determined by finding ':CURV #' or ':CURVE #' in the Header.
    If Header includes ':CURV #', the ISF file is new version.
    else if Header includes ':CURVE #', the ISF file is older version.
    """
    key = ':CURV #'
    intLocationOfColon = bytesHeader.find(key.encode())
    keylength = len(key)
    older_version = False
    if intLocationOfColon == -1:
        key = ':CURVE #'
        intLocationOfColon = bytesHeader.find(key.encode())
        keylength = len(key)
        older_version = True
    if intLocationOfColon == -1:
        sys.exit('error: can`t find ":CURV #" nor ":CURVE #".')

    intNofDigits = int (chr (bytesHeader[intLocationOfColon+keylength]) )
    bytesHeader = bytesHeader[0: (intLocationOfColon+keylength+1+intNofDigits)]
    bytesHeader = bytesHeader.decode('utf-8')

    if debug:
        print ('DEBUG information ----------')
        print ('    type(bytesHeader) is ', end='')
        print (type(bytesHeader))
        print ('    bytesHeader  = %s' % bytesHeader )
        print ('------------------------ end')

    # Subroutines used to extract inrormation from the head --------------------
    def cmp(a, b):
        return (a > b) - (a < b) 
    
    def getnum(string,tag):
        """ Loock into the string for the tag and extract the concequent number"""
        n1=string.find(tag)
        n2=string.find(';',n1)
        
        s2=string[n1+len(tag):n2]    
        j=s2.find('.')
        if j==-1:
            return int(string[n1+len(tag):n2])
        else:
            return float(string[n1+len(tag):n2])

    def getstr(string,tag):
        """ Loock into the string for the tag and extract the concequent string"""
        n1=string.find(tag)
        n2=string.find(';',n1)
        return string[n1+len(tag):n2].lstrip()    

    def getquotedstr(string,tag):
        """ Loock into the string for the tag and extract the concequent quoted 
        string"""
        n1=string.find(tag)
        n2=string.find('"',n1+1)
        n3=string.find('"',n2+1)
        return string[n2+1:n3]    
    #---------------------------------------------------------------------------
    
    # tuple 'tupleHeader' contains information stored in the header of file with dictionary.
    if older_version:
        tupleHeader={'bytenum': getnum(bytesHeader,'BYT_NR'),
                'bitnum':  getnum(bytesHeader,'BIT_NR'),
                'encoding':  getstr(bytesHeader,'ENCDG'),
                'binformat': getstr(bytesHeader,'BN_FMT'),
                'byteorder': getstr(bytesHeader,'BYT_OR'),
                'wfid': getquotedstr(bytesHeader,'WFID'),
                'pointformat': getstr(bytesHeader,'PT_FMT'),
                'xunit': getquotedstr(bytesHeader,'XUNIT'),
                'yunit': getquotedstr(bytesHeader,'YUNIT'),
                'xzero': getnum(bytesHeader,'XZERO'),
                'xincr': getnum(bytesHeader,'XINCR'),
                'ptoff': getnum(bytesHeader,'PT_OFF'),
                'ymult': getnum(bytesHeader,'YMULT'),
                'yzero': getnum(bytesHeader,'YZERO'),
                'yoff': getnum(bytesHeader,'YOFF'),
                'npts': getnum(bytesHeader,'NR_PT')}
    else:
        tupleHeader={'bytenum': getnum(bytesHeader,'BYT_N'),
            'bitnum':  getnum(bytesHeader,'BIT_N'), 
            'encoding':  getstr(bytesHeader,'ENC'),
            'binformat': getstr(bytesHeader,'BN_F'),
            'byteorder': getstr(bytesHeader,'BYT_O'),
            'wfid': getquotedstr(bytesHeader,'WFI'),
            'pointformat': getstr(bytesHeader,'PT_F'),
            'xunit': getquotedstr(bytesHeader,'XUN'),
            'yunit': getquotedstr(bytesHeader,'YUN'),
            'xzero': getnum(bytesHeader,'XZE'), 
            'xincr': getnum(bytesHeader,'XIN'),
            'ptoff': getnum(bytesHeader,'PT_O'),
            'ymult': getnum(bytesHeader,'YMU'),
            'yzero': getnum(bytesHeader,'YZE'),
            'yoff': getnum(bytesHeader,'YOF'),
            'npts': getnum(bytesHeader,'NR_P')}

    # The only cases that this code (at this moment) not take into acount.
    # if older_version:
    #     print(tupleHeader['bytenum'])
    #     print(tupleHeader['bitnum'])
    #     print(tupleHeader['encoding'],'BINARY')
    #     print(tupleHeader['binformat'],'RI')
    #     exit()
    #     if ((tupleHeader['bytenum'] != 2) or (tupleHeader['bitnum'] != 16) or
    #     cmp(tupleHeader['encoding'],'BINARY') or cmp(tupleHeader['binformat'],'RI')):
    #         fileInput.close()
    #         sys.exit('Unable to process IFS file.')
    # else:
    #     print(tupleHeader['bytenum'])
    #     print(tupleHeader['bitnum'])
    #     print(tupleHeader['encoding'],'BINARY')
    #     print(tupleHeader['binformat'],'RI')
    #     exit()
    #     if ((tupleHeader['bytenum'] != 2) or (tupleHeader['bitnum'] != 16) or 
    #     cmp(tupleHeader['encoding'],'BIN') or cmp(tupleHeader['binformat'],'RI')):
    #         fileInput.close()
    #         sys.exit('Unable to process IFS file.')
         
    # Skipping the #<x><yy...y> part of the <Block> bytes
    fileInput.seek(intLocationOfColon+keylength+1)
    intNofDataBytes =  int(fileInput.read(intNofDigits))
    
    # information from the tupleHeader needed to read and to convert the data
    npts = tupleHeader['npts']
    yzero= tupleHeader['yzero']
    ymult= tupleHeader['ymult']
    xzero= tupleHeader['xzero']
    xincr= tupleHeader['xincr']
    ptoff= tupleHeader['ptoff']
    yoff = tupleHeader['yoff']

    dict_endian = {             # Dictionary to converts significant bit infor-  
               'MSB': '>',      # mation to struct module definitions.
               'LSB': '<' 
             }
    fmt = dict_endian[tupleHeader['byteorder']] + str(npts) + 'h'

    intCalculatedNofBytes=struct.calcsize(fmt)

    # "intNofDataBytes" is the number of bytes to be readed directly from Tek-ISF-file.
    # Meanwhile "intCalculatedNofBytes" is the number of bytes to be readed calculated through:
    #                    NumOfPoints x BytePerPoint 
    if intNofDataBytes != intCalculatedNofBytes:
        sys.exit('error: intNofDataBytes != intCalculatedNofBytes.')
        
    string_data=fileInput.read(intCalculatedNofBytes)
    string_data2=fileInput.read(intCalculatedNofBytes)
    data=struct.unpack(fmt, string_data)

    if debug:
        print ('DEBUG information ----------')
        print ('    intNofDataBytes = %d, intCalculatedNofBytes = %d' %(intNofDataBytes,intCalculatedNofBytes))
        print ('    type(intNofDataBytes) is ', type(intNofDataBytes))
        print ('    type(intCalculatedNofBytes) is ', type(intCalculatedNofBytes))
        print ('    type(string_data) is ', type(string_data))
        print ('    len(string_data) is ', len(string_data))
        print ('    type(data) is ', type(data))
        print ('    len(data) is ', len(data))
        print ('------------------------ end')

    # output calculated values as tuple
    if cmp(tupleHeader['pointformat'],'Y') == 0:    # pointformat == 'Y'
        listTime =[xzero + xincr*(i-ptoff) for i in range(npts)]
        listValue =[yzero + ymult*(y-yoff) for y in data]
        ndarrayValue = np.array([listTime, listValue])
        fileInput.close()

    elif cmp(tupleHeader['pointformat'],'ENV') == 0:    # pointformat == 'ENV'
        npts = int(npts / 2.)
        listTime =[xzero + xincr*(i-ptoff)*2 for i in range(npts)]
        listMinValue =[yzero + ymult*(y-yoff) for y in data[0:len(data):2]]
        listMaxValue =[yzero + ymult*(y-yoff) for y in data[1:len(data):2]]
        ndarrayValue = np.array([listTime, listMinValue, listMaxValue])
        fileInput.close()

    else:
        sys.exit('error: plotformat != "Y" or "ENV".')

    if verbose or debug:
        print ('isfread() exited successfully ---------------------------------------------------------------')
        print ('|     Information : %s' % tupleHeader['wfid'])
        print ('|     Pointformat : %s' % tupleHeader['pointformat'])
        print ('|     Time Points : %d' % ndarrayValue.shape[1])
        print ('| Horizontal Unit : [%s]' % tupleHeader['xunit'])
        print ('| Vertical   Unit : [%s]' % tupleHeader['yunit'])
        print (' --------------------------------------------------------------------------------------------')

    return ndarrayValue, tupleHeader

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT_FILE")
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose message (default: False)')
    parser.add_argument('-d', '--debug', action='store_true', help='debug mode if this flag is set (default: False)')
    parser.add_argument('-o', '--out', help='output data as OUTPUT_FILE.csv', type=str, metavar='OUTPUT_FILE')
    args = parser.parse_args()

    ndarrayValue, tupleHeader = isfread(args.INPUT_FILE,verbose=args.verbose,debug=args.debug)

    if args.out != None:
        fileOutput = open (args.out, 'w') 
        fileOutput.write (tupleHeader['wfid'] + '\n')
        for keys, items in tupleHeader.items(): # write header information
            if keys == 'wfid':
                continue
            fileOutput.write ('%s: %s,' %(keys, items))
        
        if ndarrayValue.shape[0] == 2:    # write data (pointformat = Y)
            fileOutput.write ('\nTime,Value\n')
            for i in range(ndarrayValue.shape[1]):
                fileOutput.write (str(ndarrayValue[0,i])+','
                                  +str(ndarrayValue[1,i])+'\n')
        elif ndarrayValue.shape[0] == 3:    # write data (pointformat = ENV)
            fileOutput.write ('\nTime,MinValue,MaxValue\n')
            for i in range(ndarrayValue.shape[1]):
                fileOutput.write (str(ndarrayValue[0,i])+','
                                  +str(ndarrayValue[1,i])+','
                                  +str(ndarrayValue[2,i])+'\n')
        else:
            sys.exit('error: ndarrayValue[0] != 2 or 3')
        fileOutput.close()
    else:
        for i in range(ndarrayValue.shape[1]):
            for j in range(ndarrayValue.shape[0]):
                print("%e"%ndarrayValue[j][i], end=' ')
            print()
