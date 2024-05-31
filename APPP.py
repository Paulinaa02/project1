from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from datetime import date
from kivymd.uix.behaviors import FakeCircularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.properties import StringProperty
import datetime
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDIconButton, MDFloatingActionButton, MDRaisedButton, \
    MDFillRoundFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.theming import ThemeManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.pickers import MDDatePicker, MDTimePicker, MDColorPicker
from kivy.core.window import Window
from plyer import notification
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import BaseListItem, IRightBodyTouch, OneLineRightIconListItem, TwoLineRightIconListItem
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.toolbar import MDTopAppBar
from database import Database

Window.size = (350, 650)


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class ToDoCard(FakeCircularElevationBehavior, MDFloatLayout):
    title = StringProperty()
    description = StringProperty()
    date_text = StringProperty()
    time_text = StringProperty()


class ToDoApp(MDApp):
    theme_cls = ThemeManager()
    theme_cls.theme_style = 'Light'

    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("mainnn.kv"))
        screen_manager.add_widget(Builder.load_file("addtodoo.kv"))

        self.db = Database()

        todayy = date.today()
        todayy_str = todayy.strftime('%A %d %B %Y')
        screen_manager.get_screen("add_todo").date_text.text = todayy_str
        Clock.schedule_interval(self.check_time, 50)

        return screen_manager

    def on_start(self):
        today = date.today()
        wd = date.weekday(today)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        year = str(datetime.datetime.now().year)
        month = str(datetime.datetime.now().strftime("%b"))
        day = str(datetime.datetime.now().strftime("%d"))

        screen_manager.get_screen("main").ids.date.text = f"{days[wd]}, {day} {month} {year}"

        self.load_todos()

    def load_todos(self):
        mainn = screen_manager.get_screen("main")
        container = mainn.ids.todo_list
        containerv2 = mainn.ids.second_todo

        # Usuń istniejące widgety ToDoCard
        for child in list(container.children):
            if isinstance(child, ToDoCard):
                container.remove_widget(child)
        for child in list(containerv2.children):
            if isinstance(child, ToDoCard):
                containerv2.remove_widget(child)

        today = date.today().strftime('%A %d %B %Y')
        todos = self.db.get_todos_for_date(today)

        for todo in todos:
            todo_card = ToDoCard(title=todo[1], description=todo[2], date_text=todo[3], time_text=todo[4])
            if todo[3] == today:
                container.add_widget(todo_card)
            else:
                containerv2.add_widget(todo_card)

    def on_complete(self, checkbox, value, description, bar, date_text, time_text):

        if value:
            description.text = f"[s]{description.text}[/s]"
            date_text.text = f"[s]{date_text.text}[/s]"
            time_text.text = f"[s]{time_text.text}[/s]"
            bar.md_bg_color = 0.2235, 1, 0.0784, 1
        else:
            remove = ["[s]", "[/s]"]
            for i in remove:
                description.text = description.text.replace(i, "")
                time_text.text = time_text.text.replace(i, "")
                date_text.text = date_text.text.replace(i, "")
                bar.md_bg_color = 0.678, 0.847, 0.933, 1.0

    def add_todo(self, title, description, date_text, time_text):
        todayy = date.today()
        todayy_str = todayy.strftime('%A %d %B %Y')
        screen_manager.current = 'main'
        screen_manager.transition.direction = 'right'

        if title != "" and date_text != "Set due date" and len(title) < 21:
            self.db.add_todo(title, description, date_text, time_text)  # Dodanie do bazy danych
            self.load_todos()  # Załaduj zadania z bazy danych

        screen_manager.get_screen("add_todo").date_text.text = todayy_str
        screen_manager.get_screen("add_todo").time_text.text = "Set reminder"

    def check_time(self, dt):
        current_time = datetime.datetime.now().strftime('%H:%M')
        todos = screen_manager.get_screen("main").second_todo.children + screen_manager.get_screen(
            "main").todo_list.children
        for todo in todos:
            if hasattr(todo, 'time_text') and todo.time_text == current_time:
                self.show_notification(todo.title, todo.description)

    def show_notification(self, title, description):
        notification.notify(
            title="REMAINDER",
            message=f"Task: {title}\n{description}",
            app_icon=None,
            timeout=4,
        )

    def change_screen(self, screen_name):
        screen_manager.current = screen_name

    def delete_data(self):
        main_screen = screen_manager.get_screen("main")

        # Remove all ToDoCard widgets from todo_list
        todo_list_container = main_screen.ids.todo_list
        for child in list(todo_list_container.children):
            if isinstance(child, ToDoCard):
                todo_list_container.remove_widget(child)

        # Remove all ToDoCard widgets from second_todo
        second_todo_container = main_screen.ids.second_todo
        for child in list(second_todo_container.children):
            if isinstance(child, ToDoCard):
                second_todo_container.remove_widget(child)

    def show_confirmation_dialog(self):
        self.dialog = MDDialog(
            text="Delete all tasks?",
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=self.close_dialog
                ),
                MDFlatButton(
                    text="OK",
                    on_release=self.confirm_delete
                ),
            ],
        )
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def confirm_delete(self, instance):
        self.dialog.dismiss()
        self.delete_data()

    def show_todo_details(self):
        main_screen = screen_manager.get_screen("main")
        print("ToDo Cards in todo_list:")
        for child in main_screen.ids.todo_list.children:
            if isinstance(child, ToDoCard):
                print(f"Title: {child.title}, Description: {child.description}")

        print("\nToDo Cards in second_todo:")
        for child in main_screen.ids.second_todo.children:
            if isinstance(child, ToDoCard):
                print(f"Title: {child.title}, Date: {child.date_text}")

    def open_menu(self, caller, card):
        d_items = ['Edit', 'Delete']
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": [
                    ("pencil-outline", lambda x, y='Edit': self.callback_for_menu_items(y, card)),
                    ("delete-outline", lambda x, y='Delete': self.callback_for_menu_items(y, card)),
                ][idx][0],
                "height": dp(40),
                "text": i,
                "on_release": lambda x=i: self.callback_for_menu_items(x, card),
                "bg_color": (0.678, 0.847, 0.933, 1.0),
            } for idx, i in enumerate(d_items)
        ]

        self.menu = MDDropdownMenu(
            elevation=4,
            caller=caller,
            items=menu_items,
            width=0.4,
            position="center",
            radius=[8, 8, 8, 8],
        )
        self.menu.open()

    def callback_for_menu_items(self, text, card):
        if text == "Edit":
            self.menu.dismiss()
            screen_manager.transition.direction = 'left'
            screen_manager.current = 'add_todo'
            screen_manager.get_screen('main').ids.todo_list.remove_widget(card)
            screen_manager.get_screen('main').ids.second_todo.remove_widget(card)

        elif text == "Delete":
            # Usuń z bazy danych
            todo_id = card.todo_id
            self.db.delete_todo_by_id(todo_id)
            screen_manager.get_screen('main').ids.todo_list.remove_widget(card)
            screen_manager.get_screen('main').ids.second_todo.remove_widget(card)
            self.menu.dismiss()

    def show_datepicker(self):
        date_dialog = MDDatePicker(radius=[8, 8, 8, 8], primary_color=(0.678, 0.847, 0.933, 1.0),
                                   selector_color=(0.678, 0.847, 0.933, 1.0),
                                   text_button_color=(0.678, 0.847, 0.933, 1.0))
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def checkk(self, checkbox, value):
        if value:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    def on_save(self, instance, value, date_range):
        date2 = value.strftime('%A %d %B %Y')

        add_todo_screen = screen_manager.get_screen("add_todo")
        add_todo_screen.date_text.text = str(date2)

    def show_timepicker(self):
        picker = MDTimePicker(
            primary_color=(0.85, 0.925, 0.975, 1.0) if self.theme_cls.theme_style == 'Light' else (0.1, 0.1, 0.1, 1),
            text_button_color=(0.678, 0.847, 0.933, 1.0), accent_color=(0.678, 0.847, 0.933, 1.0))
        picker.bind(time=self.get_time)
        picker.open()

    def get_time(self, instance, time):
        time2 = time.strftime('%H:%M')
        add_todo_screen = screen_manager.get_screen("add_todo")
        add_todo_screen.time_text.text = str(time2)

    def show_colorpicker(self):
        pickerr = MDColorPicker()
        pickerr.open()

    def on_theme_color_select(self, instance, color):
        # konwersja koloru z postaci krotki (r, g, b, a) do postaci szesnastkowej
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))

        self.theme_cls.primary_palette = hex_color


if __name__ == "__main__":
    ToDoApp().run()
