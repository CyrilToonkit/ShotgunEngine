"""
------------------------- LICENCE INFORMATION -------------------------------
    This file is part of Toonkit Module Lite, Python Maya library and module.
    Author : Cyril GIBAUD - Toonkit
    Copyright (C) 2014-2017 Toonkit
    http://toonkit-studio.com/

    Toonkit Module Lite is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Toonkit Module Lite is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with Toonkit Module Lite.  If not, see <http://www.gnu.org/licenses/>
-------------------------------------------------------------------------------
"""
__author__ = "Cyril GIBAUD - Toonkit"

import sys
import os

sgPath = os.path.join(os.path.dirname(__file__),"pythonApi")
certsPath = os.path.join(sgPath, "shotgun_api3", "lib", "httplib2", "python2", "cacerts.txt")

if not sgPath in sys.path:
	sys.path.append(sgPath)

from shotgun_api3 import *
from shotgun_api3 import Shotgun as ShotgunOrig

#Implement certificates bugfix (https://developer.shotgunsoftware.com/c593f0aa/)
def Shotgun(*args, **kwargs):
	#Add ca_certs on the fly if not given
	if not "ca_certs" in kwargs:
		kwargs["ca_certs"] = certsPath

	return ShotgunOrig(*args, **kwargs)

def getDummy(inId, inType="Project"):
    return {"type": inType, "id": inId}