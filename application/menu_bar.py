import wx


class MenuBar(wx.MenuBar):

    def __init__(self, *args, **kw):
        super(MenuBar, self).__init__(*args, **kw)

        for eachLabel, eachStatus, eachHandler in self.menuData():
            if not eachLabel:
                self.AppendSeparator()
                continue
            menuItem = self.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)

        for eachMenuData in self.menu_data():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.create_menu(menuItems), menuLabel)

    # TODO: Refactor this into its own panel file
    def menu_data(self):
        return (("&File",
                 ("&Switch Mode", "Switch operation mode", self.on_panel_switch),
                 ("&Quit", "Quit", self.close_window)),
                ("&Options",
                 ("&Upload Model", "Upload a ML model", self.upload_model),
                 ("", "", ""),
                 ("&Documentation", "Show documentation", self.documentation)))


    def create_menu(self, menuData):
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menuData:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            menuItem = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu

    def on_panel_switch(self, event):
        if self.auv_panel.IsShown():
            self.SetTitle("ROV Controls Showing")
            self.auv_panel.Hide()
            self.rov_panel.Show()
        else:
            self.SetTitle("AUV Controls Showing")
            self.auv_panel.Show()
            self.rov_panel.Hide()
        self.Layout()

    # Empty event handlers needs to compile
    def upload_model(self, event):
        pass

    def options(self, event):
        pass

    def close_window(self, event):
        self.Destroy()

    def documentation(self, event):
        try:
            browser = os.environ.get('BROWSER')
            doc_url = 'https://vdoster.com'
            process = Popen([browser, doc_url], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            print(stdout)
        except KeyError as e:
            print("No browser env var set, creating popup\n\n{}".format(e))