from sugar.activity.activity import Activity, ActivityToolbox
import BatallaNaval
from Collaboration import CollaborationWrapper

class BatallaNavalActivity(Activity):
    def __init__(self, handle):
        Activity.__init__(self, handle)
        self.connect('destroy', self._cleanup_cb)
    
        self.gamename = 'BatallaNaval'
        self.set_title("Batalla Naval")
    
        # connect to the in/out events
        self.connect('focus_in_event', self._focus_in)
        self.connect('focus_out_event', self._focus_out)
        
        self.colaboracion = CollaborationWrapper(self)
        
        # The activity is a subclass of Window, so it passses itself to the init function
        BatallaNaval.init(False, self)
        # It never returns, gtk.main()
    
    def _cleanup_cb(self, data=None):
        return
    
    # We could use these methods to conserve power by having the activity stop processing when it is in the background.
    def _focus_in(self, event, data=None):
        return
    
    def _focus_out(self, event, data=None):
        return
