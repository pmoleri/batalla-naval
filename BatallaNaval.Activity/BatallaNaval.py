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
        self.board1 = Board()
        
        self.board2 = Board()
        
        global standalone_mode
        if not standalone_mode:
            toolbox = ActivityToolbox(toplevel_window)
            toplevel_window.set_toolbox(toolbox)
            toolbox.show()
            toplevel_window.set_canvas(self)
        else:
            toplevel_window.add(self)
      
        print "Barcos Propios"
        self.ships = ShipsContainer()
        for ship in self.ships.ships:
            self.board1.add_ship(ship)
            print "%s: %s" % (ship.nombre, ship.pos)

        print "Barcos Enemigos"
        self.enemigos = ShipsContainer()
        for ship in self.enemigos.ships:
            self.board2.add_ship(ship)
            print "%s: %s" % (ship.nombre, ship.pos)

        self.pane = gtk.HBox()
        self.pane.add(self.ships)
        self.pane.add(self.board1)
        self.pane.add(self.board2)
        self.pane.show()
        
        self.add(self.pane)
        self.show()
        toplevel_window.width, toplevel_window.height = (800,600)
        toplevel_window.show_all()

class ShipsContainer(gtk.VBox):
    
    def __init__(self):
        gtk.VBox.__init__(self)
        
        self.ships = [
            Ship("Portaaviones", 5, None),
            Ship("Acorazado", 4, None),
            Ship("Crucero", 3, None),
            Ship("Submarino", 3, None),
            Ship("Destructor", 2, None)]
        
        celdas_ocupadas = []
        
        for ship in self.ships:
            ok = False
            while not ok:
                # Calculo coordenadas random, asumo orientacion horizontal
                posx = random.randint(1, 10)
                posy = random.randint(1, 10-ship.largo)
                
                ship.pos = (posx, posy)
                ok = True
                for celda in ship.get_celdas():
                    if celda in celdas_ocupadas:
                        ok = False
                if ok:
                    celdas_ocupadas.extend(ship.get_celdas())

#        self.add(Ship("Portaaviones", 5, None)) #Portaaviones
#        self.add(Ship("Acorazado", 4, None))  #Acorazado
#        self.add(Ship("Crucero", 3, None))    #Crucero
#        self.add(Ship("Submarino", 3, None))  #Submarino
#        self.add(Ship("Destructor", 2, None)) #Destructor
        
        self.show()

class Celda(gtk.Frame):
    
    def __init__(self, pos):
        gtk.Frame.__init__(self)
        self.pos = pos
    
    def ocultar(self):
        self.set_no_show_all(True)
        self.hide()
        
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
        
        self.rows = []
        
        # El tablero es otra tabla
        self.cells_table = gtk.Table(10, 10, True)
        self.table.attach(self.cells_table, 1, 2, 1, 2)
        self.cells_table.show()
        for i in range(1, 11):
            row = []
            for j in range(1, 11):
                left = j - 1
                top = i - 1
                #label = gtk.Label("(%s,%s)"%(i,j))
                celda = Celda((i, j))
                row.append(celda)
                self.cells_table.attach(celda, left, j, top, i)
                #print label.get_text()
            self.rows.append(row)
        
        self.show()
    
    def add_ship(self, ship):
        for i in ship.get_filas():
            for j in ship.get_cols():
                self.ocultar_celda(i, j)
        izq = ship.get_inicio()[1]-1
        der = ship.get_fin()[1]
        arr = ship.get_inicio()[0]-1
        aba = ship.get_fin()[0]
        print "%s, %s, %s, %s, %s" % (ship.nombre, izq, der, arr, aba)
        self.cells_table.attach(ship, izq, der, arr, aba)
        
    def ocultar_celda(self, i, j):
        self.rows[i-1][j-1].ocultar()

class Ship(gtk.Frame):
    
    horizontal = 'H'
    vertical = 'V'
    
    def __init__(self, nombre, largo, pos, orientacion = horizontal):
        #gtk.Label.__init__(self, nombre)
        gtk.Frame.__init__(self)
        self.nombre = nombre
        self.largo = largo
        self.orientacion = orientacion
        self.pos = pos
        
        self.add(gtk.Label(nombre))
        self.show()
    
    def get_inicio(self):
        return self.pos
    
    def get_fin(self):
        if self.orientacion == Ship.horizontal:
            return self.pos[0], self.pos[1] + self.largo
        else:
            return self.pos[0] + self.largo, self.pos[1]

        
    def get_filas(self):
        return range(self.get_inicio()[0], self.get_fin()[0]+1)
    
    def get_cols(self):
        return range(self.get_inicio()[1], self.get_fin()[1]+1)
    
    def get_celdas(self):
        return [(f, c) for f in self.get_filas() for c in self.get_cols()]
    
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
