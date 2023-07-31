"""
This file is part of GenderDetect which is released under GNU GPL V3.
See file LICENSE.txt or go to <http://www.gnu.org/licenses/> for full license details.
Copyright (C) 2016 Aditya Khandkar
"""

import os

__VERSION__ = '0.1'

LIUM_JAR = os.path.join(os.path.dirname(__file__),
                        './LIUM_SpkDiarization-8.4.jar')

GENDER_SH = os.path.join(os.path.dirname(__file__),
                         './gender.sh')
SMS_GMMS = os.path.join(os.path.dirname(__file__),
                        'sms.gmms')
GENDER_GMM = os.path.join(os.path.dirname(__file__),
                          'gender.gmms')
