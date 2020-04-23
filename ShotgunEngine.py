#Resolved only when deployed (via Toonkit_Module_Shotgun)
from Toonkit_Core.tkProjects.dbEngines import dbEngine

class shotgunEngine(dbEngine):
    def __init__(self):
        self.name="shotgunEngine"