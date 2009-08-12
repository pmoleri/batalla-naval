#!/usr/bin/env python
# -*- coding: cp1252 -*-

import pygtk
pygtk.require('2.0')
import gtk
import pango

import random

try:
    from sugar.activity.activity import Activity, ActivityToolbox
except:
    pass

ESTADO_VACIO = 0
ESTADO_IZQ = 1
ESTADO_DER = 2

IGUAL = "="

class MainWindow(gtk.Frame):
    
    def __init__(self, toplevel_window):
        gtk.Frame.__init__(self)
        
        # Falta!! agregar otro board que es en el que se hacen las jugadas
        self.board = Board()
        
        global standalone_mode
        if not standalone_mode:
            toolbox = ActivityToolbox(toplevel_window)
            toplevel_window.set_toolbox(toolbox)
            toolbox.show()
            toplevel_window.set_canvas(self)
        else:
            toplevel_window.add(self)
      
        self.ships = ShipsContainer()
        self.ships.show()
        for ship in self.ships.ships:
            self.board.add_ship(ship)
            
        self.pane = gtk.HBox()
        self.pane.add(self.ships)
        self.pane.add(self.board)
        self.pane.show()
        
        self.add(self.pane)
        self.show()
        toplevel_window.width, toplevel_window.height = (800,600)
        toplevel_window.show()

class ShipsContainer(gtk.VBox):
    
    def __init__(self):
        gtk.VBox.__init__(self)
        
        self.ships = [
            Ship("Portaaviones", 5, None),
            Ship("Acorazado", 4, None),
            Ship("Crucero", 3, None),
            Ship("Submarino", 3, None),
            Ship("Destructor", 2, None)]
        
        for ship in self.ships:
            # Calculo coordenadas random, asumo orientacion horizontal
            # Falta!! mejorarlo para que los barcos no se choquen
            posx = random.randint(1, 11-ship.largo)
            posy = random.randint(1, 10)
            
            ship.pos = (posx, posy)
        
#        self.add(Ship("Portaaviones", 5, None)) #Portaaviones
#        self.add(Ship("Acorazado", 4, None))  #Acorazado
#        self.add(Ship("Crucero", 3, None))    #Crucero
#        self.add(Ship("Submarino", 3, None))  #Submarino
#        self.add(Ship("Destructor", 2, None)) #Destructor
        
        self.show()
        
class Board(gtk.Frame):
    
    def __init__(self):
        gtk.Frame.__init__(self)

        # Números
        self.top_table = gtk.Table(1, 10, True)
        for i in range(1, 11):
            label = gtk.Label(str(i))
            self.top_table.attach(label, i-1, i, 0, 1)
            label.show()
        self.top_table.show()
        
        # Letras
        self.left_table = gtk.Table(10, 1, True)
        for i in range(1, 11):
            char = chr( ord('A') + i - 1 )
            label = gtk.Label(char)
            self.left_table.attach(label, 0, 1, i-1, i)
            label.show()
        self.left_table.show()
        
        # Se hace una tabla para ubicar las letras, los números y el tablero
        self.table = gtk.Table(2, 2, False)
        self.add(self.table)
        self.table.show()

        label = gtk.Label("    ")
        label.show()
        self.table.attach(label, 0, 1, 0, 1)
        
        self.table.attach(self.top_table, 1, 2, 0, 1)
        self.table.attach(self.left_table, 0, 1, 1, 2)
        
        # El tablero es otra tabla
        self.cells_table = gtk.Table(10, 10, False)
        self.table.attach(self.cells_table, 1, 2, 1, 2)
        self.cells_table.show()
        for i in range(1, 11):
            for j in range(1, 11):
                left = j - 1
                top = i - 1
                label = gtk.Label("(%s,%s)"%(i,j))
                self.cells_table.attach(label, left, j, top, i)
                label.show()
                #print label.get_text()
        
        self.show()
    
    def add_ship(self, ship):
        self.cells_table.attach(ship, ship.pos[0]-1, ship.pos[0] + ship.largo, ship.pos[1]-1, ship.pos[1])

class Ship(gtk.Frame):
    
    horizontal = 'H'
    vertical = 'V'
    
    def __init__(self, nombre, largo, pos, orientacion = horizontal):
        gtk.Frame.__init__(self, nombre)
        self.nombre = nombre
        self.largo = largo
        self.orientacion = orientacion
        self.pos = pos
        
        self.show()

# This function is the common entry point for sugar and standalone mode
# standalone is a boolean indicating Standalone mode or Sugar mode.
def init(standalone, toplevel_window):
    
    # Falta!! Limpiar
    
    # Falta!! Se podría traer código del MainWindow para aca.
    
    # Sets a global variables
    global standalone_mode, SCREENSIZE, SCALE, FONT_SIZE
    standalone_mode = standalone
    if standalone:
        SCREENSIZE = (600,412)
        SCALE = (1./2, 1./2)
        FONT_SIZE = 18
        font_desc = pango.FontDescription("sans 72")
        if font_desc:
            toplevel_window.modify_font(font_desc)
    else:
        SCREENSIZE = (1200,825)
        SCALE = (1, 1)
        FONT_SIZE = 36
    MainWindow(toplevel_window)

# This is the main function in standalone mode
def main():
    toplevel_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    init(True, toplevel_window)
    gtk.main()
    return 0

if __name__ == "__main__":
   main()
