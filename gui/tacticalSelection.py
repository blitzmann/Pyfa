#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import wx
import service
import gui.globalEvents as GE
import gui.mainFrame

class TacticalSelection(wx.Panel):
    def __init__(self, parent):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

        wx.Panel.__init__(self, parent)
        self.parent = parent
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(mainSizer)

        self.mode1 = wx.ToggleButton(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
        self.mode2 = wx.ToggleButton(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
        self.mode3 = wx.ToggleButton(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)

        mainSizer.Add(self.mode1, 1, wx.EXPAND, 0)
        mainSizer.Add(self.mode2, 1, wx.EXPAND, 0)
        mainSizer.Add(self.mode3, 1, wx.EXPAND, 0)

        self.mainFrame.Bind(GE.FIT_CHANGED, self.fitChanged)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.toggleMode)

    def toggleMode(self, event):
        sFit = service.Fit.getInstance()
        fitID = self.mainFrame.getActiveFit()
        sFit.setMode(fitID, event.EventObject.mode)
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))

    def fitChanged(self, event):
        sFit = service.Fit.getInstance()
        fit = sFit.getFit(event.fitID)
        modes = fit.ship.getModes() if fit else None
        if fit and modes:
            self.Show(True)
            self.parent.Layout()

            for i, mode in enumerate(modes):
                btn = getattr(self, "mode%d"%(i+1))
                btn.SetLabel(mode.item.name.rsplit()[-2])
                btn.mode = mode
                if fit.mode.item == mode.item:
                    btn.SetValue(True)
                else:
                    btn.SetValue(False)
        else:
            self.Show(False)
            self.parent.Layout()
            self.Layout()
