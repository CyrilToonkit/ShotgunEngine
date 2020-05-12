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
------------------------    -------------------------------------------------------
"""
__author__ = "Cyril GIBAUD - Toonkit"

import logging
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
DEBUG = True

import tkSG

#Resolved only when deployed (via Toonkit_Module_Shotgun)
import Toonkit_Core.tkCore as tc

from Toonkit_Core.tkProjects.dbEngines.dbEngine import dbEngine
from Toonkit_Core.tkProjects.tkProjectObj import tkProjectObj

FORBIDDEN_UPDATE_KEYS = [
    "id",
    "type",
]

RESTRICTED_UPDATE_KEYS = [
    "name",
    "assetType",
]

DEFAULTTRANSLATORS = {
    "Type":{},

    "Operators":{
        "==":"is",
        "!=":"is_not",
        "<":"less_than",
        ">":"greater_than",
        },

    "Asset":{
        "name":"code",
        "status":"sg_status_list",
        "assetType":"sg_asset_type",
        },

    "Episode":{
        "name":"code",
        "status":"sg_status_list",
        "Shots":"shots",
        "Assets":"assets",
        },

    "Sequence":{
        "name":"code",
        "status":"sg_status_list",
        "Episode":"episode",
        },

    "Shot":{
        "name":"code",
        "status":"sg_status_list",
        "duration":"sg_cut_duration",
        "Sequence":"sg_sequence",
        },

    "Task":{
        "name":"content",
        "status":"sg_status_list",
        "startDate":"start_date",
        "endDate":"due_date",
        },

    "Note":{
        "name":"subject",
        "description":"content",
        "status":"sg_status_list",
        },
}

class shotgunEngine(dbEngine):
    def __init__(self, inTranslators=None, *args, **kwargs):
        inTranslators = inTranslators or DEFAULTTRANSLATORS

        super(shotgunEngine, self).__init__(inTranslators, *args, **kwargs)

        self.name="shotgunEngine"

        self._sgScriptName = kwargs.get("inScriptName")
        self._sgScritpKey = kwargs.get("inScriptKey")
        self._sgSite = kwargs.get("inSite","https://toonkit.shotgunstudio.com")

        self._sg = None

    @property
    def SG(self):
        if self._sg is None:
            self._sg = tkSG.Shotgun(self._sgSite, script_name=self._sgScriptName, api_key=self._sgScritpKey)

        return self._sg

    @tc.verbosed
    def _get(self, inEntityType, inSender, inFilters=None, inKeys=None, inOrder=None, inLimit=0, inVerbose=DEBUG, inLogger=LOGGER):

        #Filters
        if inFilters is None:
            inFilters = []
        else:
            for myFilter in inFilters:
                myFilter[0] = self.translate(myFilter[0], inType=inEntityType)
                myFilter[1] = self.translate(myFilter[1], inType="Operators")

        #Same type and no filters, retrieve "sender"
        if inSender.type == inEntityType and len(inFilters) == 0:
            inFilters.append(["id", "is", inSender.id])

        #Sender is project, add project filter 
        elif inSender.type == "Project":
            inFilters.append(["project.Project.id", "is", inSender.id])

        #Sender is entity, filter by links 
        elif inSender.type in ["Asset", "Shot", "Sequence"]:
            fieldName = inSender.type.lower() + "s"

            if inEntityType == "Task":
                fieldName = "entity"
            elif inEntityType == "Note":
                filedName = "note_links"

            inFilters.append([fieldName, "is", tkSG.getDummy(inSender.id, inType=inSender.type)])

        elif inSender.type == "Episode":
            fieldName = inSender.type.lower() + "s"

            if inEntityType == "Shot":
                fieldName = "sg_sequence.Sequence.episode"

            inFilters.append([fieldName, "is", tkSG.getDummy(inSender.id, inType=inSender.type)])

        elif inSender.type == "Task":
            fieldName = inSender.type.lower() + "s"

            inFilters.append([fieldName, "is", tkSG.getDummy(inSender.id, inType=inSender.type)])

        #Keys
        if inKeys is None:
            inKeys = []

        defaultKeys = self.getDefaultKeys(inEntityType)

        inKeys = list(set(inKeys + defaultKeys))

        #Actual call
        inLogger.debug("Shotgun.find('{0}', {1}, {2})".format(inEntityType, inFilters, inKeys))
        rawResults = self.SG.find(inEntityType, inFilters, inKeys, order=inOrder, limit=inLimit)
        inLogger.debug("Raw results : {0}".format(rawResults))
        classPointer = tkProjectObj.getClass(self.translate(inEntityType, inType="Type"))

        results = []
        for rawResult in rawResults:
            for key, value in rawResult.iteritems():
                if isinstance(value, dict):
                    subClassPointer = tkProjectObj.getClass(self.translate(value["type"], inType="Type"))
                    rawResult[key] = subClassPointer(self, **value)

            results.append(classPointer(self, **rawResult))

        return results

    @tc.verbosed
    def _set(self, inObject, inForce=False, inVerbose=DEBUG, inLogger=LOGGER):
        values = {}

        forbiddenKeys = FORBIDDEN_UPDATE_KEYS + RESTRICTED_UPDATE_KEYS

        properties = inObject._properties if inForce else inObject.modifiedProperties

        if len(properties) == 0:
            inLogger.warning("Nothing to update on {0}".format(inObject))
            return None

        for key, prop in properties.iteritems():
            if not key in forbiddenKeys and not isinstance(prop.value, tkProjectObj):
                values[self.translate(key, inType=inObject.type)] = prop.value

        entityType = self.translate(inObject.type, inType="Type")

        inLogger.debug("Shotgun.update('{0}', {1}, {2})".format(entityType, inObject.id, values))

        result = self.SG.update(
            entityType,
            inObject.id,
            values,
            )

        if not result is None:
            classPointer = tkProjectObj.getClass(self.translate(inObject.type, inType="Type"))
            return classPointer(self, **result)

        return None