"""
This file is part of GenderDetect which is released under GNU GPL V3.
See file LICENSE.txt or go to <http://www.gnu.org/licenses/> for full license details.
Copyright (C) 2011-2012, Sardegna Ricerche.
Authors: Michela Fancello, Mauro Mereu


Copyright (C) 2016 Aditya Khandkar

"""

import os
import shlex
import subprocess

import config

debug = False

def start_subprocess(commandline):
    """
    Start a subprocess using the given commandline and wait for
    termination.

    :returns string: process output

    """
    args = shlex.split(commandline)
    procs = subprocess.Popen(args, stderr=subprocess.PIPE)
    procs.wait()
    if debug:
        print(''.join(procs.stderr.readlines()))


def _segmentation(filename):
    name = os.path.splitext(os.path.basename(filename))[0]
    start_subprocess('java -cp ' + config.LIUM_JAR +
                     ' fr.lium.spkDiarization.programs.MSegInit ' +
                     ' --fInputMemoryOccupationRate=400' +
                     ' --cMinimumOfCluster=1' +
                     ' --fInputMask=' + filename + ' ' +
                     ' --fInputDesc=audio2sphinx,1:1:0:0:0:0,13,0:0:0' +
                     ' --sInputMask= --sOutputMask=' + name + '.seg ' + ' seg')


def _scoring_segments(filename):
    name = os.path.splitext(os.path.basename(filename))[0]

    # silence seg file
    seg = name + '.seg'

    # gender seg  file
    oseg = name + '.g.seg'

    start_subprocess('java -cp ' + config.LIUM_JAR + ' ' +
                     'fr.lium.spkDiarization.programs.MDecode ' +
                     '--fInputMask=' + filename + ' ' +
                     '--fInputDesc=audio2sphinx,1:3:2:0:0:0,13,1:1:0:0 ' +
                     '--dPenality=10,10,50 ' + ' ' +
                     '--sInputMask=' + seg + ' ' +
                     '--sOutputMask=' + oseg + ' ' +
                     '--tInputMask=' + config.SMS_GMMS +
                     ' ' + name)

    start_subprocess('java -cp ' + config.LIUM_JAR + ' ' +
                     'fr.lium.spkDiarization.programs.MScore ' +
                     '--sGender ' +
                     '--fInputDesc=audio2sphinx,1:3:2:0:0:0,13,1:1:0:0 ' +
                     '--fInputMask=' + filename + ' ' +
                     '--sInputMask=' + oseg + ' ' +
                     '--sOutputMask=' + seg + ' ' +
                     '--tInputMask=' + config.GENDER_GMM +
                     ' ' + name)



def extract_gender(segfile):
    """
    Identify gender from seg file
    """
    gen = {'M': 0, 'F': 0, 'U': 0}
    with open(segfile, 'r+') as seg:
        for line in seg:
            if ';;' not in line:
                gen[(line.split(' ')[4])] += 1

    if gen['M'] > gen['F']:
        return 'M'
    elif gen['M'] < gen['F']:
        return 'F'
    else:
        return 'U'


def identify_gender(filename,block = True):
    filename = os.path.abspath(filename)
    _segmentation(filename)
    _scoring_segments(filename)
    name = os.path.splitext(os.path.basename(filename))[0]
    gender = extract_gender(name + '.seg')
    return gender
















