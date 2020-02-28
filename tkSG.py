import sys
import os

sgPath = os.path.join(os.path.dirname(__file__),"pythonApi")

if not sgPath in sys.path:
	sys.path.append(sgPath)

import shotgun_api3 as shotgun