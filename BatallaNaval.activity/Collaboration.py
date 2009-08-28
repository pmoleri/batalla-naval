# -*- coding: UTF-8 -*-
# Copyright 2007-2008 One Laptop Per Child
# Copyright 2007 Gerard J. Cerchio <www.circlesoft.com>
# Copyright 2008 Andrés Ambrois <andresambrois@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging

from sugar.presence import presenceservice
import telepathy
from dbus.service import method, signal
# In build 656 Sugar lacks sugartubeconn
try:
  from sugar.presence.sugartubeconn import SugarTubeConnection
except:
  from sugar.presence.tubeconn import TubeConnection as SugarTubeConnection
from dbus.gobject_service import ExportedGObject

''' En todas las actividades colaborativas Sugar nos matiene al tanto cuando entra o sale un Jugador
    Para que todos conozcan el estado de la Actividad se maneja la técnica Hello World,
    donde cuando un participante entra se emite una señal Hello que llega a todos los participantes
    y los participantes responden directamente al nuevo el método "World", mediante la cual
    se le pasa el estado actual de la actividad.
    Luego las actualizaciones se dan con señal Play, mediante la cual cada participante comunica al
    resto su jugada.

    En resumen en este módulo se encapsula la lógica de la "colaboración" con el siguiente funcionamiento:
        - Cuando alguien entra a la colaboración se emite la señal Hello
        - Quien recibe la señal automáticamente responde con la señal World
        - Cada vez que alguien juega emite la señal Play
'''

SERVICE = "org.ceibaljam.BatallaNaval"
IFACE = SERVICE
PATH = "/org/ceibaljam/BatallaNaval"

logger = logging.getLogger('BatallaNaval')
logger.setLevel(logging.DEBUG)

class CollaborationWrapper(ExportedGObject):
    ''' A wrapper for the collaboration bureaucracy
        Recibe la actividad y los callbacks necesarios '''
    
    def __init__(self, activity):
        self.activity = activity
        self.presence_service = presenceservice.get_instance()
        self.owner = self.presence_service.get_owner()
    
    def set_up(self, buddy_joined_cb, buddy_left_cb, World_cb, Play_cb, mis_barcos):
        self.activity.connect('shared', self._shared_cb)
        if self.activity._shared_activity:
            # We are joining the activity
            self.activity.connect('joined', self._joined_cb)
            if self.activity.get_shared():
                # We've already joined
                self._joined_cb()
        
        self.buddy_joined = buddy_joined_cb
        self.buddy_left = buddy_left_cb
        self.World_cb = World_cb        # Llamado cuando alguien me pasa el estado del tablero
        self.Play_cb = Play_cb          # Llamado cuando alguien me informa de una jugada
        
        # Enviado al hacer World sobre un nuevo compañero
        self.mis_barcos = [(b.nombre, b.orientacion, b.largo, b.pos[0], b.pos[1]) for b in mis_barcos]
        self.world = False
        self.entered = False

    def _shared_cb(self, activity):
        #self.activity.gameToolbar.grey_out_size_change()
        #self.activity.gameToolbar.grey_out_restart()
        #self.activity.gameToolbar.grey_out_ai()
        self._sharing_setup()
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            SERVICE, {})
        self.is_initiator = True
        #self.activity.undo_button.hide()
            
    def _joined_cb(self, activity):
        #self.activity.gameToolbar.grey_out_size_change()
        #self.activity.gameToolbar.grey_out_restart()
        #self.activity.gameToolbar.grey_out_ai()
        self._sharing_setup()
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb, 
            error_handler=self._list_tubes_error_cb)
        self.is_initiator = False
        #self.activity.undo_button.hide()
    
    def _sharing_setup(self):
        if self.activity._shared_activity is None:
            logger.error('Failed to share or join activity')
            return

        self.conn = self.activity._shared_activity.telepathy_conn
        self.tubes_chan = self.activity._shared_activity.telepathy_tubes_chan
        self.text_chan = self.activity._shared_activity.telepathy_text_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal(
            'NewTube', self._new_tube_cb)

        self.activity._shared_activity.connect('buddy-joined', self._buddy_joined_cb)
        self.activity._shared_activity.connect('buddy-left', self._buddy_left_cb)

        # Optional - included for example:
        # Find out who's already in the shared activity:
        for buddy in self.activity._shared_activity.get_joined_buddies():
            logger.debug('Buddy %s is already in the activity',
                               buddy.props.nick)
   
    def participant_change_cb(self, added, removed):
        logger.debug('Tube: Added participants: %r', added)
        logger.debug('Tube: Removed participants: %r', removed)
        for handle, bus_name in added:
            buddy = self._get_buddy(handle)
            if buddy is not None:
                logger.debug('Tube: Handle %u (Buddy %s) was added',
                                   handle, buddy.props.nick)
        for handle in removed:
            buddy = self._get_buddy(handle)
            if buddy is not None:
                logger.debug('Buddy %s was removed' % buddy.props.nick)
        if not self.entered:
            if self.is_initiator:
                logger.debug("I'm initiating the tube, will watch for hellos.")
                self.add_hello_handler()
            else:
                logger.debug('Hello, everyone! What did I miss?')
                self.Hello()
        self.entered = True
        
        
    # This is sent to all participants whenever we join an activity
    @signal(dbus_interface=IFACE, signature='')
    def Hello(self):
        """Say Hello to whoever else is in the tube."""
        logger.debug('I said Hello.')
    
    # This is called by whoever receives our Hello signal
    # This method receives the current game state and puts us in sync
    # with the rest of the participants. 
    # The current game state is represented by the game object
    @method(dbus_interface=IFACE, in_signature='a(ssiii)', out_signature='a(ssiii)')
    def World(self, barcos):
        """To be called on the incoming XO after they Hello."""
        if not self.world:
            logger.debug('Somebody called World on me')
            #self.activity.board_size_change(None, size)
            self.world = True   # En vez de cargar el mundo, lo voy recibiendo jugada a jugada.
            self.World_cb(barcos)
            #self.activity.set_player_color(self.activity.invert_color(taken_color))
            #self.players = players
            # now I can World others
            self.add_hello_handler()
        else:
            self.world = True
            logger.debug("I've already been welcomed, doing nothing")
        return self.mis_barcos
    
    @signal(dbus_interface=IFACE, signature='ii')
    def Play(self, x, y):
        """Say Hello to whoever else is in the tube."""
        logger.debug('Ejecutando jugada remota:%s x %s.', x, y)
    
    def add_hello_handler(self):
        logger.debug('Adding hello handler.')
        self.tube.add_signal_receiver(self.hello_signal_cb, 'Hello', IFACE,
            path=PATH, sender_keyword='sender')
        self.tube.add_signal_receiver(self.play_signal_cb, 'Play', IFACE,
            path=PATH, sender_keyword='sender')
            
    def hello_signal_cb(self, sender=None):
        """Somebody Helloed me. World them."""
        if sender == self.tube.get_unique_name():
            # sender is my bus name, so ignore my own signal
            return
        logger.debug('Newcomer %s has joined', sender)
        logger.debug('Welcoming newcomer and sending them the game state')
        
        self.other = sender     # Sería práctico cuando juego contra uno solo y quiero ejecutar métodos sobre él
        
        # Le mando mis barcos y me devuelve los suyos
        barcos_enemigos = self.tube.get_object(self.other, PATH).World(self.mis_barcos, dbus_interface=IFACE)
        
        # Llamo al callback de World, para que cargue los barcos enemigos
        self.World_cb(barcos_enemigos)
        
    def play_signal_cb(self, x, y, sender=None):
        """Somebody placed a stone. """
        if sender == self.tube.get_unique_name():
            return  # sender is my bus name, so ignore my own signal
        logger.debug('Buddy %s placed a stone at %s x %s', sender, x, y)
        # Call our Play callback
        #self.Play_cb(x, y, sender)
        self.Play_cb(x, y)  # En principio no importa quien lo mandó

    def _list_tubes_error_cb(self, e):
        logger.error('ListTubes() failed: %s', e)
            
    def _list_tubes_reply_cb(self, tubes):
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)
            
    def _new_tube_cb(self, id, initiator, type, service, params, state):
        logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
                     'params=%r state=%d', id, initiator, type, service,
                     params, state)
        if (type == telepathy.TUBE_TYPE_DBUS and
            service == SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)
            self.tube = SugarTubeConnection(self.conn,
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES],
                id, group_iface=self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP])
            super(CollaborationWrapper, self).__init__(self.tube, PATH)
            self.tube.watch_participants(self.participant_change_cb)

    def _buddy_joined_cb (self, activity, buddy):
        """Called when a buddy joins the shared activity. """
        logger.debug('Buddy %s joined', buddy.props.nick)
        if self.buddy_joined:
            self.buddy_joined(buddy)

    def _buddy_left_cb (self, activity, buddy):
        """Called when a buddy leaves the shared activity. """
        if self.buddy_left:
            self.buddy_left(buddy)

    def _get_buddy(self, cs_handle):
        """Get a Buddy from a channel specific handle."""
        logger.debug('Trying to find owner of handle %u...', cs_handle)
        group = self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP]
        my_csh = group.GetSelfHandle()
        logger.debug('My handle in that group is %u', my_csh)
        if my_csh == cs_handle:
            handle = self.conn.GetSelfHandle()
            logger.debug('CS handle %u belongs to me, %u', cs_handle, handle)
        elif group.GetGroupFlags() & telepathy.CHANNEL_GROUP_FLAG_CHANNEL_SPECIFIC_HANDLES:
            handle = group.GetHandleOwners([cs_handle])[0]
            logger.debug('CS handle %u belongs to %u', cs_handle, handle)
        else:
            handle = cs_handle
            logger.debug('non-CS handle %u belongs to itself', handle)
            # XXX: deal with failure to get the handle owner
            assert handle != 0
        return self.presence_service.get_buddy_by_telepathy_handle(
            self.conn.service_name, self.conn.object_path, handle)
