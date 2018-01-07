# noinspection PyPackageRequirements
import wx
from eos.saveddata.implant import Implant
from eos.saveddata.drone import Drone
from eos.saveddata.module import Module, Slot, Rack
from eos.saveddata.fit import Fit
from eos.saveddata.targetResists import TargetResists
from gui.viewColumn import ViewColumn
from logbook import Logger

pyfalog = Logger(__name__)


class GraphColor(ViewColumn):
    name = "Graph Color"

    def __init__(self, view, params):
        ViewColumn.__init__(self, view)
        self.size = 24
        self.maxsize = self.size
        self.mask = wx.LIST_MASK_IMAGE
        self.columnText = ""

    def getImageId(self, stuff):
        return self.fittingView.imageList.GenerateColorBitmap(self.fittingView.getColor(stuff))


GraphColor.register()
