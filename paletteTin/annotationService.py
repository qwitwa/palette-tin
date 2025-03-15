from json import dumps, loads
from os import path
from krita import * # type: ignore
from PyQt5.QtCore import QByteArray

class AnnotationService():
    # wait until document is open to use service
    # https://scripting.krita.org/lessons/notifiers
    def __init__(self) -> None:
        self._doc = None
        self._palette = None
        self._settings = None
        self.annotationTag = 'PaletteTin'
        self.annotationDescription = "Stores Palettin Tin docker palette color data"

    def startup(self):
        if (self._doc and not self._palette):
            data = self._doc.annotation(self.annotationTag).data().decode('utf8')
            if data:
                self._palette = loads(data)
    
    def loadSettings(self):
        if (self._doc):
            data = self._doc.annotation(self.annotationTag).data().decode('utf8')
            if data:
                self._palette = loads(data)

    def savePalette(self, palette):
        if (self._doc):
            self._doc.setAnnotation(
                self.annotationTag,
                self.annotationDescription,
                QByteArray(dumps(palette).encode())
            )
    
    def printAnnotation(self):
        self.loadSettings()
        print(self.palette)
    
    @property
    def palette(self):
        return self._palette

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value
    
    @property
    def document(self):
        return self._doc
    
    @document.setter
    def document(self, value):
        if value != self._doc:
            self._doc = value
            self._palette = None
    
    def saveSettings(self, defaultMode: str, customSettings: dict):
        self.defaultMode = defaultMode
        self.customSettings = customSettings
        jsonSetting = dumps(self.settings, indent=4)
        with open(path.dirname(path.realpath(__file__)) + '/userData/settings/settings.json', "w") as outfile:
            outfile.write(jsonSetting)
    
    def toString(self):
        pass