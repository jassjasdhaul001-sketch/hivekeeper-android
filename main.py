
import json
import os

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView

Window.clearcolor = (0.055, 0.075, 0.10, 1)

DATA_FILE = os.path.join(
    App.get_running_app().user_data_dir if App.get_running_app()
    else os.path.expanduser("~"),
    "hives.json"
)


class HiveKeeper(App):
    def build(self):
        self.title = "HiveKeeper"
        self.hives = []
        self.load_data()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12)
        )

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(82),
            spacing=dp(4)
        )
        header.add_widget(Label(
            text="[b]HiveKeeper[/b]  🐝",
            markup=True,
            font_size=sp(28),
            color=(1, 0.76, 0.20, 1),
            halign="left",
            size_hint_y=None,
            height=dp(42)
        ))
        header.add_widget(Label(
            text="Your apiary, organised.",
            font_size=sp(14),
            color=(0.72, 0.78, 0.84, 1),
            halign="left"
        ))
        root.add_widget(header)

        self.summary = Label(
            text="Your Hive Dashboard",
            font_size=sp(19),
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign="left"
        )
        root.add_widget(self.summary)

        self.hive_id = TextInput(
            hint_text="Hive ID (e.g. H-001)",
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size=sp(16),
            padding=dp(12)
        )
        root.add_widget(self.hive_id)

        self.strength = Spinner(
            text="Colony strength",
            values=("Strong", "Medium", "Weak"),
            size_hint_y=None,
            height=dp(48)
        )
        root.add_widget(self.strength)

        self.honey = TextInput(
            hint_text="Honey harvested (kg)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(48),
            font_size=sp(16),
            padding=dp(12)
        )
        root.add_widget(self.honey)

        self.notes = TextInput(
            hint_text="Notes: queen, brood, health...",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
            font_size=sp(15),
            padding=dp(12)
        )
        root.add_widget(self.notes)

        save = Button(
            text="SAVE HIVE RECORD",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=(0.96, 0.65, 0.12, 1),
            color=(0.08, 0.09, 0.10, 1),
            bold=True
        )
        save.bind(on_press=self.save_hive)
        root.add_widget(save)

        self.status = Label(
            text="Records are stored on this device.",
            size_hint_y=None,
            height=dp(28),
            font_size=sp(12),
            color=(0.65, 0.85, 0.70, 1)
        )
        root.add_widget(self.status)

        root.add_widget(Label(
            text="RECENT HIVE RECORDS",
            size_hint_y=None,
            height=dp(32),
            halign="left",
            bold=True,
            font_size=sp(15)
        ))

        scroll = ScrollView()
        self.records = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=(0, 0, 0, dp(12))
        )
        self.records.bind(
            minimum_height=self.records.setter("height")
        )
        scroll.add_widget(self.records)
        root.add_widget(scroll)

        self.refresh_records()
        return root

    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.hives = json.load(f)
        except (OSError, ValueError):
            self.hives = []

    def save_data(self):
        folder = os.path.dirname(DATA_FILE)
        os.makedirs(folder, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.hives, f, ensure_ascii=False, indent=2)

    def save_hive(self, _button):
        hive_id = self.hive_id.text.strip()

        if not hive_id:
            self.status.text = "Please enter a Hive ID."
            return

        try:
            honey_kg = float(self.honey.text or "0")
            if honey_kg < 0:
                raise ValueError
        except ValueError:
            self.status.text = "Enter a valid honey quantity."
            return

        record = {
            "id": hive_id,
            "strength": self.strength.text,
            "honey_kg": honey_kg,
            "notes": self.notes.text.strip()
        }

        self.hives.insert(0, record)

        try:
            self.save_data()
        except OSError:
            self.hives.pop(0)
            self.status.text = "Could not save. Check device storage."
            return

        self.hive_id.text = ""
        self.honey.text = ""
        self.notes.text = ""
        self.strength.text = "Colony strength"

        self.status.text = "Hive record saved successfully!"
        self.refresh_records()

    def refresh_records(self):
        self.records.clear_widgets()
        total_honey = sum(
            float(item.get("honey_kg", 0))
            for item in self.hives
        )
        self.summary.text = (
            f"Dashboard  |  {len(self.hives)} records"
            f"  |  {total_honey:g} kg honey"
        )

        if not self.hives:
            self.records.add_widget(Label(
                text="No records yet. Add your first hive above.",
                size_hint_y=None,
                height=dp(55),
                color=(0.70, 0.76, 0.82, 1)
            ))
            return

        for item in self.hives:
            text = (
                f"[b]{item['id']}[/b]   |   "
                f"{item['strength']}\n"
                f"Honey: {item['honey_kg']} kg\n"
                f"{item['notes'] or 'No notes'}"
            )
            card = Label(
                text=text,
                markup=True,
                size_hint_y=None,
                height=dp(90),
                halign="left",
                valign="middle",
                padding=(dp(12), dp(8)),
                color=(0.91, 0.94, 0.97, 1)
            )
            card.bind(
                size=lambda widget, size:
                setattr(widget, "text_size",
                        (size[0] - dp(24), None))
            )
            self.records.add_widget(card)


if __name__ == "__main__":
    HiveKeeper().run()

