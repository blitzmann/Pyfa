import wx
import copy
from gui import bitmapLoader
import gui.mainFrame
import gui.globalEvents as GE
import time
from gui.PFListPane import PFListPane
import service
import eos.db
from eos.types import Tag

from wx.lib.buttons import GenBitmapButton

import gui.utils.colorUtils as colorUtils
import gui.utils.drawUtils as drawUtils
import gui.utils.animUtils as animUtils
import gui.utils.animEffects as animEffects

import gui.sfBrowserItem as SFItem
import gui.shipBrowser as SBrowser
from gui.contextMenu import ContextMenu

import service

Stage1Selected, EVT_TB_STAGE1_SEL = wx.lib.newevent.NewEvent() # Tag List
Stage2Selected, EVT_TB_STAGE2_SEL = wx.lib.newevent.NewEvent() # Fit List

class PFWidgetsContainer(PFListPane):
    def __init__(self,parent):
        PFListPane.__init__(self,parent)

        self.anim = animUtils.LoadAnimation(self,label = "", size=(100,12))
        self.anim.Stop()
        self.anim.Show(False)

    def ShowLoading(self, mode = True):
        if mode:
            aweight,aheight = self.anim.GetSize()
            cweight,cheight = self.GetSize()
            ax = (cweight - aweight)/2
            ay = (cheight - aheight)/2
            self.anim.SetPosition((ax,ay))
            self.anim.Show()
            self.anim.Play()
        else:
            self.anim.Stop()
            self.anim.Show(False)

class NavigationPanel(SFItem.SFBrowserItem):
    def __init__(self,parent, size = (-1,24)):
        SFItem.SFBrowserItem.__init__(self,parent,size = size)

        self.newBmpH = bitmapLoader.getBitmap("fit_add_small","icons")
        self.resetBmpH = bitmapLoader.getBitmap("freset_small","icons")

        self.resetBmp = self.AdjustChannels(self.resetBmpH)
        self.newBmp = self.AdjustChannels(self.newBmpH)

        self.toolbar.AddButton(self.resetBmp, "Tags", clickCallback = self.OnHistoryReset, hoverBitmap = self.resetBmpH)
        self.btnNew = self.toolbar.AddButton(self.newBmp, "New Tag", clickCallback = self.ToggleNewTagBox, hoverBitmap = self.newBmpH)

        self.padding = 4
        self.lastSearch = ""
        self.recentSearches = []
        self.inSearch = False

        self.fontSmall = wx.FontFromPixelSize((0,12),wx.SWISS, wx.NORMAL, wx.NORMAL, False)
        w,h = size
        self.NewTagBox = wx.TextCtrl(self, wx.ID_ANY, "", wx.DefaultPosition, (-1, h - 2 if 'wxGTK' in wx.PlatformInfo else -1 ), wx.TE_PROCESS_ENTER | (wx.BORDER_NONE if 'wxGTK' in wx.PlatformInfo else 0))
        self.NewTagBox.Show(False)

        self.NewTagBox.Bind(wx.EVT_TEXT_ENTER, self.OnNewTagBoxEnter)
        self.NewTagBox.Bind(wx.EVT_KILL_FOCUS, self.OnNewTagBoxLostFocus)
        self.NewTagBox.Bind(wx.EVT_KEY_DOWN, self.OnNewTagBoxEsc)

        self.SetMinSize(size)
        self.tagBrowser = self.Parent
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

        self.Bind(wx.EVT_SIZE, self.OnResize)

    def ToggleNewTagBox(self):
        if self.NewTagBox.IsShown():
            self.NewTagBox.Show(False)
        else:
            self.NewTagBox.Show(True)
            self.NewTagBox.ChangeValue("")
            self.NewTagBox.SetFocus()

    def OnNewTagBoxEnter(self, event):
        tag = eos.types.Tag()
        tag.name = self.NewTagBox.GetValue()
        eos.db.save(tag)
        self.OnNewTagBoxLostFocus(None)
        wx.PostEvent(self.tagBrowser,Stage1Selected(back = False))

    def OnNewTagBoxLostFocus(self, event):
        self.NewTagBox.ChangeValue("")
        self.NewTagBox.Show(False)

    def OnNewTagBoxEsc(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.NewTagBox.Show(False)
        else:
            event.Skip()

    def OnResize(self, event):
        self.Refresh()

    def ShowNewTagButton(self, show):
        self.btnNew.Show(show)
        self.Refresh()

    def OnHistoryReset(self):
        wx.PostEvent(self.tagBrowser,Stage1Selected(back = False))

    def AdjustChannels(self, bitmap):
        img = wx.ImageFromBitmap(bitmap)
        img = img.AdjustChannels(1.05,1.05,1.05,1)
        return wx.BitmapFromImage(img)

    def UpdateElementsPos(self, mdc):
        rect = self.GetRect()

        self.toolbarx = self.padding
        self.toolbary = (rect.height - self.toolbar.GetHeight()) / 2

        mdc.SetFont(self.fontSmall)

        wlabel,hlabel = mdc.GetTextExtent(self.toolbar.hoverLabel)

        self.thoverx = self.toolbar.GetWidth() + self.padding
        self.thovery = (rect.height - hlabel)/2
        self.thoverw = wlabel

        self.browserBoxX = self.thoverx
        bEditBoxWidth, bEditBoxHeight = self.NewTagBox.GetSize()
        self.browserBoxY = (rect.height - bEditBoxHeight) / 2

        self.bEditBoxWidth = rect.width - self.browserBoxX - self.padding

    def DrawItem(self, mdc):
        rect = self.GetRect()

        windowColor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
        textColor = colorUtils.GetSuitableColor(windowColor, 1)
        sepColor = colorUtils.GetSuitableColor(windowColor, 0.2)

        mdc.SetTextForeground(textColor)

        self.UpdateElementsPos(mdc)
        self.NewTagBox.SetPosition((self.browserBoxX, self.browserBoxY))
        self.NewTagBox.SetSize(wx.Size(self.bEditBoxWidth, -1))

        self.toolbar.SetPosition((self.toolbarx, self.toolbary))
        mdc.SetFont(self.fontSmall)
        mdc.DrawText(self.toolbar.hoverLabel, self.thoverx, self.thovery)
        mdc.SetPen(wx.Pen(sepColor,1))
        mdc.DrawLine(0,rect.height - 1, rect.width, rect.height - 1)

    def RenderBackground(self):
        rect = self.GetRect()

        windowColor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)

        sFactor = 0.1

        shipGroupsFilter = getattr(self.tagBrowser,"filterShipsWithNoFits", None)
        if shipGroupsFilter:
            sFactor = 0.15
            mFactor = 0.25
        else:
            mFactor = 0.2

        eFactor = 0.1

        if self.bkBitmap:
            if self.bkBitmap.eFactor == eFactor and self.bkBitmap.sFactor == sFactor and self.bkBitmap.mFactor == mFactor \
             and rect.width == self.bkBitmap.GetWidth() and rect.height == self.bkBitmap.GetHeight() :
                return
            else:
                del self.bkBitmap

        self.bkBitmap = drawUtils.RenderGradientBar(windowColor, rect.width, rect.height, sFactor, eFactor, mFactor, 2)

        self.bkBitmap.sFactor = sFactor
        self.bkBitmap.eFactor = eFactor
        self.bkBitmap.mFactor = mFactor

class TagBrowser(wx.Panel):
    RACE_ORDER = ["amarr", "caldari", "gallente", "minmatar", "sisters", "ore", "serpentis", "angel", "blood", "sansha", "guristas", "jove", None]

    def __init__(self, parent):
        wx.Panel.__init__ (self, parent,style = 0)
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

        # needed to use shipBrowsers FitItem widget
        # effectively a dummy variable that doesn't do anything in TagBrowser
        self.fitIDMustEditName = -1

        self.tagList=[]
        self.racesFilter = {}

        for race in self.RACE_ORDER:
            if race:
                self.racesFilter[race] = False

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # lpane is main container for adding widgets (category, ships, fits, etc)
        self.lpane = PFWidgetsContainer(self)

        self.navpanel = NavigationPanel(self)
        mainSizer.Add(self.navpanel, 0 , wx.EXPAND)
        container = wx.BoxSizer(wx.VERTICAL)

        container.Add(self.lpane,1,wx.EXPAND)

        mainSizer.Add(container, 1, wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Layout()
        self.Show()

        self.Bind(wx.EVT_SIZE, self.SizeRefreshList)
        self.Bind(EVT_TB_STAGE2_SEL, self.stage2)
        self.Bind(EVT_TB_STAGE1_SEL, self.stage1)

        self.mainFrame.Bind(GE.FIT_CHANGED, self.RefreshList)

        # initial stage, can be changed for debug purposes
        self.stage1(None)


    def GetBrowserContainer(self):
        return self.lpane

    def RefreshList(self, event):
        return
        stage = self.GetActiveStage()
        if stage == 3 or stage == 4:
            self.lpane.RefreshList(True)
        event.Skip()

    def SizeRefreshList(self, event):
        ewidth, eheight = event.GetSize()
        self.Layout()
        self.lpane.Layout()
        self.lpane.RefreshList(True)
        event.Skip()

    def __del__(self):
        pass

    def ToggleRacesFilter(self, race):
        if self.racesFilter[race]:
            self.racesFilter[race] = False
        else:
            self.racesFilter[race] = True

    def GetRaceFilterState(self, race):
        return self.racesFilter[race]

    def stage1(self, event):
        sMarket = service.Market.getInstance()

        self.lpane.ShowLoading(False)

        self.lpane.Freeze()
        self.lpane.RemoveAllChildren()

        self.navpanel.ShowNewTagButton(True)

        self.tagList = list(eos.db.getTagList())

        if len(self.tagList) == 0:
            self.lpane.AddWidget(SBrowser.PFStaticText(self.lpane, label = u"You have not created any tags. Click the New Tag button in the navigation bar."))
            self.lpane.Thaw()
            return

        self.tagList.sort(key=lambda tag: tag.name)

        # add category to browser
        for tag in self.tagList:
            self.lpane.AddWidget(TagItem(self.lpane, tag.tagID, (tag.name, 0)))

        self.lpane.RefreshList()
        self.lpane.Thaw()

    def raceNameKey(self, ship):
        return self.RACE_ORDER.index(ship.race), ship.name

    def stage2(self, event):
        self.lpane.ShowLoading(False)

        tagID = event.tagID
        sFit = service.Fit.getInstance()

        self.lpane.Freeze()
        self.lpane.RemoveAllChildren()
        fitList = sFit.getFitsWithTag(tagID)

        self.navpanel.ShowNewTagButton(False)

        if len(fitList) == 0:
            # show message about adding fits to this tag
            self.lpane.AddWidget(SBrowser.PFStaticText(self.lpane, label = u"No fits available for this tag. You can tag fits by using the Show Info icon."))
            self.lpane.Thaw()
            return

        fitList.sort(key=self.nameKey)

        for ID, name, shipID, booster, timestamp in fitList:
            self.lpane.AddWidget(FitItem(self.lpane, ID, ("", name, booster, timestamp), shipID))

        self.lpane.RefreshList()
        self.lpane.Thaw()

    def nameKey(self, info):
        return info[1]

class TagItem(SBrowser.CategoryItem):
    '''
    TagItem inherits from shipBrowser's CategoryItem. This allows us
    to write code specifically for the TagBrowser implementation of
    it.
    '''
    def __init__(self,parent, tagID, fittingInfo, size = (0,16)):
        SBrowser.CategoryItem.__init__(self,parent, tagID, fittingInfo, size)

        # it's not shipBmp, but we set it the same as parent to play nice
        # it would be nice to eventually abstract this and FitItem from the shipBrowser
        self.shipBmp = bitmapLoader.getBitmap("tag_small","icons")
        self.dropShadowBitmap = drawUtils.CreateDropShadowBitmap(self.shipBmp, 0.2)

        self.tagID = tagID
        self.fittingInfo = fittingInfo
        self.tagBrowser = self.Parent.Parent

        self.tagMenu = wx.Menu()
        self.deleteTag = self.tagMenu.Append(-1, "Delete Tag")
        self.renameTag = self.tagMenu.Append(-1, "Rename Tag")

        self.Bind(wx.EVT_MENU, self.OnDeleteTag, self.deleteTag)
        self.Bind(wx.EVT_MENU, self.OnRenameTag, self.renameTag)

        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_RIGHT_UP, self.OnContextMenu)

    def OnDeleteTag(self, event):
        print "Delete Tag"
        pass

    def OnRenameTag(self, event):
        print "Rename Tag"
        pass

    def OnContextMenu(self, event):
        ''' Handles context menu for tag '''
        pos = wx.GetMousePosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(self.tagMenu, pos)
        event.Skip()

    def MouseLeftUp(self, event):
        wx.PostEvent(self.tagBrowser,Stage2Selected(tagID=self.tagID, back=False))

class FitItem(SBrowser.FitItem):
    def __init__(self, parent, fitID=None, shipFittingInfo=("Test", "cnc's avatar", 0, 0 ), shipID = None, itemData=None,
                 id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(0, 40), style=0):
        SBrowser.FitItem.__init__(self, parent, fitID, shipFittingInfo, shipID, itemData)