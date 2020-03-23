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