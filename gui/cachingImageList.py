# =============================================================================
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
# =============================================================================


# noinspection PyPackageRequirements
import wx
from gui.bitmapLoader import BitmapLoader


class CachingImageList(wx.ImageList):
    def __init__(self, width, height):
        wx.ImageList.__init__(self, width, height)
        self.width = width
        self.height = height
        self.map = {}

    def GetImageIndex(self, *loaderArgs):
        id_ = self.map.get(loaderArgs)
        if id_ is None:
            bitmap = BitmapLoader.getBitmap(*loaderArgs)
            if bitmap is None:
                return -1
            id_ = self.map[loaderArgs] = wx.ImageList.Add(self, bitmap)
        return id_

    def GenerateColorBitmap(self, color):
        id_ = self.map.get(color)
        if id_ is None:
            bitmap = wx.EmptyBitmapRGBA(self.width, self.height, red=color.red, green=color.green, blue=color.blue, alpha=color.alpha)
            if bitmap is None:
                return -1
            id_ = self.map[color] = wx.ImageList.Add(self, bitmap)
        return id_


