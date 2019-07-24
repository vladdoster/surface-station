import wx

class MenuBar(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self, parent=parent)
        fileMenu = wx.Menu()
        switch_panels_menu_item = fileMenu.Append(wx.ID_ANY,
                                                  "Switch modes")
        parent.Bind(wx.EVT_MENU, self.onSwitchPanels,
                    switch_panels_menu_item)
        self.Append(fileMenu, '&File')