from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.filechooser import FileChooserIconView
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFlatButton
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from access_token_storage import TokenStorage
from kivy.clock import Clock
from kivy.metrics import dp
import requests
import os


Window.size = (300, 500)

class HomeScreen(Screen):
    pass

class ItemScreen(Screen):
    pass

class SignupScreen(Screen):
    pass

class Nav(Widget):
    pass
class LoginScreen(Screen):
    pass

class OrderScreen(Screen):
    pass

class AdminScreen(Screen):
    pass

class CategoriesScreen(Screen):
    pass

class ProfileScreen(Screen):
    pass

class Card(Widget):
    pass

class Window(ScreenManager):
    pass

class ShopkeeperApp(MDApp):
    def __init__(self, **kwargs):
        super(ShopkeeperApp, self).__init__(**kwargs)
        self.token_storage = TokenStorage()
        self.vals = ()
        self.login_credentials = {
            "username" : None,
            "password" : None
        }

        self.item = {'name': '', 'price': '',
            'bp': '', 'barcode': '', 'image': ''
        }
        self.path = None

    def build(self):
        self.theme_cls.primary_palette = "Lime"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )

        self.window = Window()
        return self.window

    def open_file_manager(self):
        self.file_manager.show(os.path.expanduser("~"))

    def select_path(self, path):
        toast(f"Selected file: {path}")
        self.path = path
        self.exit_manager()

    def exit_manager(self, *args):
        self.file_manager.close()

    def create_ac(self, widget):
        for key in self.login_credentials:
            if self.login_credentials[key] == None:
                widget.add_widget(MDLabel(text="Incomplete credentials given!"))
                return

        response = requests.post("http://127.0.0.1:5000/create_ac", data=self.login_credentials)
        if response.status_code == 200:
            self.window.current = "loginScreen"
        else:
            widget.add_widget(MDLabel(text=f"{response.json()}"))

    def set_credential(self, key, value):
        if key in self.login_credentials:
            self.login_credentials[key] = value
            print(self.login_credentials[key])

    def load_credentials(self):
        self.access_token = self.token_storage.retrieve_token("access")
        self.refresh_token = self.token_storage.retrieve_token("refresh")
        return (self.access_token, self.refresh_token)


    def on_start(self):
        vals = self.load_credentials()
        print(vals)

        if not vals[0]:
            self.window.current = 'loginScreen'
        else:
            self.window.current = 'homeScreen'
            self.headers = { "Authorization": f"Bearer {vals[0]}" }
            response = requests.get("http://127.0.0.1:5000/products", headers=self.headers)
            self.resp = response.json()
            if type(self.resp) != list:
                self.headers = { "Authorization": f"Bearer {vals[1]}" }
                response = requests.post("http://127.0.0.1:5000/refresh", headers=self.headers)
                resp = response.json()
                print(resp)
                self.access_token = resp['access_token']
                self.token_storage.store_token("access", resp["access_token"])
                self.headers = { "Authorization" : f"Bearer {resp['access_token']}"}
                response = requests.get("http://127.0.0.1:5000/products", headers=self.headers)
                self.resp = response.json()
                if not self.resp:
                    self.window.current = 'loginScreen'
                    return
                stack_layout = self.window.get_screen('homeScreen')
                #for item in new_resp:
                    #stack_layout.ids.item_display.add_widget(card)
                    #print(response.json())
                return
            stack_layout = self.window.get_screen('homeScreen')
            for item in self.resp:
                card = MDCard(
                    size_hint=(None, None),
                    size=(dp(100), dp(150)),
                    radius=[1,1,1,1],
                    orientation='vertical',
                )
                card.add_widget(
                    Image(
                        source=f"{item[5]}",
                        size_hint_y=None,
                        height="70dp",
                    )
                )

                card.add_widget(
                    MDLabel(
                        text=f"{item[1]}",
                        theme_text_color="Secondary",
                        halign="center",
                        size_hint_x=None,
                        text_size=(None, None)
                    )
                )

                card.add_widget(
                    MDLabel(
                        text=f"{item[2]}",
                        theme_text_color="Secondary",
                        halign="center"
                    )
                )

                stack_layout.ids.item_display.add_widget(card)
            if len(stack_layout.ids.item_display.children) == 0:
                stack_layout.ids.item_display.add_widget(MDLabel(text="Nothing found"))

    def login(self, widget):
        for key in self.login_credentials:
            if self.login_credentials[key] == None:
                widget.add_widget(MDLabel(text="Incomplete credentials given!"))
                return

        response = requests.post("http://127.0.0.1:5000/login", data=self.login_credentials)

        if response.status_code == 200:
            resp = response.json()
            self.access_token = resp['access_token']
            self.refresh_token = resp['refresh_token']
            self.token_storage.store_token("access", self.access_token)
            self.token_storage.store_token("refresh", self.refresh_token)
            self.on_start()
        else:
            widget.add_widget(
                MDLabel(
                    id='warn',
                    text="Invalid details",
                    pos_hint= {"center_x": .5, "center_y": .93},
                    theme_text_color='Custom',
                    halign="center",
                    text_color=[1, .2, .5, 1]
                )
            )

    def logout(self):
        self.token_storage.delete()

    def screen_switch(self, screen_name):
        self.window.get_screen('homeScreen').ids.nav_drawer.set_state("close")
        self.window.current = screen_name

    def card(self, item):
        print(item)

    def do_search(self, search):
        import re
        pattern = re.compile(search.lower())

        stack_layout = self.window.get_screen('homeScreen').ids.item_display
        stack_layout.clear_widgets()

        for item in self.resp:
            if pattern.search(item[1].lower()):
                card = MDCard(
                    size_hint=(None, None),
                    size=(dp(100), dp(150)),
                    radius=[1,1,1,1],
                    orientation='vertical',
                )

                card.add_widget(
                    Image(
                        source=f"{item[5]}",
                        size_hint_y=None,
                        height="70dp"
                    )
                )

                card.add_widget(
                    MDLabel(
                        text=f"{item[1]}",
                        theme_text_color="Secondary",
                        halign="center",
                        size_hint_x=None,
                        text_size=(None, None)
                    )
                )

                card.add_widget(
                    MDLabel(
                        text=f"{item[2]}",
                        theme_text_color="Secondary",
                        halign="center"
                    )
                )

                stack_layout.add_widget(card)


    def set_item(self, key, value):
        self.item[key] = value
        print(self.item[key])
        print(self.item)

    def create_item(self, widget):
        for key in self.item:
            if key != "image":
                if self.item[key] == "":
                    widget.add_widget(MDLabel(text="Incomplete credentials given!"))
                    return

        if self.path:
            with open(self.path, 'rb') as image:
                files = {'file': image}
                response = requests.post(
                    "http://127.0.0.1:5000/create_item",
                    data=self.item,
                    headers=self.headers,
                    files=files)
                if response.status_code == 200:
                    print('created')
        else:
            response = requests.post(
                "http://127.0.0.1:5000/create_item",
                data=self.item,
                headers=self.headers
            )

            if response.status_code == 200:
                print('created')
        self.path = None

    def nav_draw(self):
        print("MEME")

    def on_card_click(self):
        print('do something')

ShopkeeperApp().run()
