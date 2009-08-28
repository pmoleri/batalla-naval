# -*- coding: cp1252 -*-

from sugar.activity.activity import Activity, ActivityToolbox
import BatallaNaval
from Collaboration import CollaborationWrapper

class BatallaNavalActivity(Activity):
    ''' Clase llamada por sugar cuando se ejecuta la actividad.
        El nombre de esta clase está señalada en el archivo activity/activity.info '''
        
    def __init__(self, handle):
        Activity.__init__(self, handle)
    
        self.gamename = 'BatallaNaval'
        
        # Crea la barra de herramientas básica de Sugar
        toolbox = ActivityToolbox(self)
        self.set_toolbox(toolbox)
        toolbox.show()
        
        # Crea una instancia de Colaboración por si se quiere compartir la actividad
        self.colaboracion = CollaborationWrapper(self)
        
        # The activity is a subclass of Window, so it passses itself to the init function
        BatallaNaval.init(False, self)
