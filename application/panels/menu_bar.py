import os
from subprocess import Popen, PIPE

import wx


class MenuBar(wx.MenuBar):
    def __init__(self, *args, **kw):
        super(MenuBar, self).__init__(*args, **kw)

        for eachMenuData in self.menu_data():
            menu_label = eachMenuData[0]
            menu_items = eachMenuData[1:]
            self.Append(self.create_menu(menu_data=menu_items), menu_label)

    def menu_data(self):
        return (
            ("&File", ("&Quit", "Quit", self.close_window)),
            (
                "&Options",
                ("&Upload Model", "Upload a ML model", self.upload_model),
                ("&Documentation", "Show documentation", self.documentation),
            ),
        )

    def create_menu(self, menu_data):
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menu_data:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            menu_item = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menu_item)
        return menu

    # Empty event handlers needs to compile
    def close_window(self, event):
        print("Closing app...")
        self.Destroy()

    @staticmethod
    def documentation(event):
        try:
            browser = os.environ.get("BROWSER")
            doc_url = "https://vdoster.com"
            process = Popen([browser, doc_url], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            print(stdout)
        except KeyError as e:
            print("No browser env var set, creating popup\n\n{}".format(e))

    @staticmethod
    def options(event):
        print("Not implemented yet")

    @staticmethod
    def upload_model(event):
        print("Not implemented yet")
