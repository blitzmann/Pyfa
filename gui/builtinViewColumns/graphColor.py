# noinspection PyPackageRequirements
import wx
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
