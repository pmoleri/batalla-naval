#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#
# Copyright 2009 ceibalJAM!
# This file is part of Batalla Naval.
#
# Batalla Naval is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Batalla Naval is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Batalla Naval.  If not, see <http://www.gnu.org/licenses/>.

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
