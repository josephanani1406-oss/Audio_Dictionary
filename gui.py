"""
Audio Dictionary - Main Graphical User Interface

Multi-page interface for:
    - Home
    - Dictionary
    - Pronunciation
    - Learn
    - Favorites
    - History
    - Progress
    - Settings

Designed to work with the existing application services:
    DictionaryController
    HistoryManager
    SpeechEngine
    SettingsManager
    SettingsWindow
"""

import io
import json
import os
import random
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from urllib.request import Request, urlopen

from controller import DictionaryController
from history import HistoryManager
from speech import SpeechEngine
from settings import SettingsManager
from settings_window import SettingsWindow


# ============================================================
# TOOLTIP
# ============================================================

class Tooltip:
    """Displays a small tooltip when the mouse hovers over a widget."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

        self.widget.bind(
            "<Enter>",
            self.on_enter,
            add="+"
        )

        self.widget.bind(
            "<Leave>",
            self.on_leave,
            add="+"
        )

    def on_enter(self, event):
        if self.tooltip is not None:
            return

        try:
            x = (
                event.widget.winfo_rootx()
                + event.widget.winfo_width() // 2
            )

            y = (
                event.widget.winfo_rooty()
                + event.widget.winfo_height()
                + 5
            )

            self.tooltip = tk.Toplevel(
                event.widget
            )

            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(
                f"+{x}+{y}"
            )

            label = tk.Label(
                self.tooltip,
                text=self.text,
                bg="#1F2937",
                fg="#F1F5F9",
                font=("Arial", 9),
                padx=7,
                pady=4,
                relief="solid",
                bd=1
            )

            label.pack()

        except tk.TclError:
            self.tooltip = None

    def on_leave(self, event):
        if self.tooltip is not None:

            try:
                self.tooltip.destroy()
            except tk.TclError:
                pass

            self.tooltip = None


# ============================================================
# MAIN APPLICATION
# ============================================================

class AudioDictionaryGUI:

    def __init__(self):

        # ----------------------------------------------------
        # ROOT WINDOW
        # ----------------------------------------------------

        self.root = tk.Tk()

        self.settings_manager = SettingsManager()

        # ----------------------------------------------------
        # APPLICATION ICON
        # ----------------------------------------------------

        icon_path = os.path.join(
            os.path.dirname(__file__),
            "audio_dictionary_icon.ico"
        )

        if os.path.exists(icon_path):

            try:
                self.root.iconbitmap(icon_path)

            except Exception as error:
                print(
                    f"Icon Error: {error}"
                )

        # ----------------------------------------------------
        # WINDOW SETTINGS
        # ----------------------------------------------------

        self.root.title(
            "Audio Dictionary"
        )

        saved_geometry = self.settings_manager.get(
            "window_geometry",
            "1100x720"
        )

        self.root.geometry(
            saved_geometry
        )

        self.root.minsize(
            1000,
            650
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        # ----------------------------------------------------
        # CORE SERVICES
        # ----------------------------------------------------

        self.controller = DictionaryController()
        self.history_manager = self.controller.history_manager
        self.speech_engine = SpeechEngine()

        # ----------------------------------------------------
        # SETTINGS
        # ----------------------------------------------------

        self.saved_voice = (
            self.settings_manager.get(
                "voice",
                "female"
            )
        )

        self.dark_mode = bool(
            self.settings_manager.get(
                "dark_mode",
                False
            )
        )

        self.current_language = (
            self.settings_manager.get(
                "language",
                "en"
            )
        )

        self.current_theme = (
            "dark"
            if self.dark_mode
            else "light"
        )

        self.language_label = (
            self.get_language_name(
                self.current_language
            )
        )

        self.speech_engine.set_voice(
            self.saved_voice
        )

        self.controller.set_language(
            self.current_language
        )

        self.settings_window = None

        # ----------------------------------------------------
        # APPLICATION STATE
        # ----------------------------------------------------

        self.current_page = "home"

        self.audio_url = ""
        self.word_image = None
        self.current_read_text = ""
        self.current_result = None
        self.current_word = ""

        self.read_running = False
        self.search_running = False
        self.image_loading = False

        self.status_text = "Ready"

        # ----------------------------------------------------
        # LEARNING STATE
        # ----------------------------------------------------

        self.quiz_word = None
        self.quiz_answer = None
        self.quiz_options = []

        # ----------------------------------------------------
        # UI REFERENCES
        # ----------------------------------------------------

        self.pages = {}

        self.nav_buttons = {}

        self.history_listbox = None
        self.favorite_listbox = None

        self.progress_labels = {}

        self.word_image_label = None

        # ----------------------------------------------------
        # FALLBACK IMAGE
        # ----------------------------------------------------

        self.fallback_image_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "word_placeholder.png"
        )

        # ----------------------------------------------------
        # BUILD UI
        # ----------------------------------------------------

        self.create_application_layout()

        self.apply_theme()

        self.show_page(
            "home"
        )

    # ========================================================
    # THEME COLORS
    # ========================================================

    def get_theme_colors(self):

        if self.dark_mode:

            return {
                "background": "#121212",
                "sidebar": "#181818",
                "surface": "#1E1E1E",
                "surface_alt": "#252525",
                "input": "#2A2A2A",
                "border": "#3A3F45",

                "text": "#F1F5F9",
                "secondary_text": "#B8C1CC",
                "muted_text": "#8B95A1",

                "accent": "#60A5FA",
                "accent_hover": "#3B82F6",

                "button": "#30353B",
                "button_hover": "#3B424A",

                "success": "#7DD3A8",

                "search": "#2563EB",
                "search_hover": "#1D4ED8",

                "speak": "#15803D",
                "speak_hover": "#166534",

                "read": "#B45309",
                "read_hover": "#92400E",

                "favorite": "#7C3AED",
                "favorite_hover": "#6D28D9",

                "learned": "#047857",
                "learned_hover": "#065F46",

                "note": "#0369A1",
                "note_hover": "#075985",

                "review": "#C2410C",
                "review_hover": "#9A3412",

                "clear": "#BE123C",
                "clear_hover": "#9F1239"
            }

        return {
            "background": "#BFEAF5",
            "sidebar": "#A9DDEA",
            "surface": "#D7F3FF",
            "surface_alt": "#E6F9FF",
            "input": "#EAFBFF",
            "border": "#7AB7C9",

            "text": "#123B4A",
            "secondary_text": "#42616D",
            "muted_text": "#667F89",

            "accent": "#1E4A73",
            "accent_hover": "#163A59",

            "button": "#8BB9D0",
            "button_hover": "#72A8BF",

            "success": "#0B5F3A",

            "search": "#1E4A73",
            "search_hover": "#163A59",

            "speak": "#2E6B43",
            "speak_hover": "#224F34",

            "read": "#8A5A1E",
            "read_hover": "#6D4518",

            "favorite": "#4F3C74",
            "favorite_hover": "#3D2D5A",

            "learned": "#2E7D5B",
            "learned_hover": "#236346",

            "note": "#2B6F8F",
            "note_hover": "#20566F",

            "review": "#A85D2A",
            "review_hover": "#874820",

            "clear": "#7A2E3B",
            "clear_hover": "#5D1F2B"
        }

    # ========================================================
    # LANGUAGE HELPERS
    # ========================================================

    def get_language_name(self, language_code):

        languages = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "tr": "Turkish",
            "ja": "Japanese",
            "zh": "Chinese",
            "ko": "Korean",
            "ar": "Arabic"
        }

        return languages.get(
            language_code,
            "English"
        )

    # ========================================================
    # APPLICATION LAYOUT
    # ========================================================

    def create_application_layout(self):

        colors = self.get_theme_colors()

        self.root.configure(
            bg=colors["background"]
        )

        # ----------------------------------------------------
        # MAIN CONTAINER
        # ----------------------------------------------------

        self.main_container = tk.Frame(
            self.root,
            bg=colors["background"]
        )

        self.main_container.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        self.sidebar = tk.Frame(
            self.main_container,
            width=210,
            bg=colors["sidebar"]
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(
            False
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        self.logo_frame = tk.Frame(
            self.sidebar,
            bg=colors["sidebar"]
        )

        self.logo_frame.pack(
            fill="x",
            pady=(25, 20),
            padx=15
        )

        self.logo_icon = tk.Label(
            self.logo_frame,
            text="🔊",
            font=("Arial", 25),
            bg=colors["sidebar"],
            fg=colors["accent"]
        )

        self.logo_icon.pack(
            side="left"
        )

        self.logo_label = tk.Label(
            self.logo_frame,
            text="Audio\nDictionary",
            font=("Arial", 13, "bold"),
            justify="left",
            bg=colors["sidebar"],
            fg=colors["text"]
        )

        self.logo_label.pack(
            side="left",
            padx=8
        )

        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        self.navigation_frame = tk.Frame(
            self.sidebar,
            bg=colors["sidebar"]
        )

        self.navigation_frame.pack(
            fill="both",
            expand=True,
            padx=10
        )

        navigation = [
            ("home", "🏠", "Home"),
            ("dictionary", "📖", "Dictionary"),
            ("pronunciation", "🎧", "Pronunciation"),
            ("learn", "🧠", "Learn"),
            ("favorites", "★", "Favorites"),
            ("history", "☷", "History"),
            ("progress", "📊", "Progress"),
            ("settings", "⚙", "Settings")
        ]

        for page_name, icon, title in navigation:

            button = tk.Button(
                self.navigation_frame,
                text=f"  {icon}   {title}",
                anchor="w",
                font=("Arial", 11),
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=12,
                pady=10,
                command=lambda p=page_name:
                    self.show_page(p)
            )

            button.pack(
                fill="x",
                pady=2
            )

            self.nav_buttons[
                page_name
            ] = button

        # ----------------------------------------------------
        # SIDEBAR FOOTER
        # ----------------------------------------------------

        self.sidebar_footer = tk.Label(
            self.sidebar,
            text="Audio Dictionary\nVersion 2.0",
            font=("Arial", 8),
            justify="center",
            bg=colors["sidebar"],
            fg=colors["muted_text"]
        )

        self.sidebar_footer.pack(
            side="bottom",
            pady=15
        )

        # ----------------------------------------------------
        # CONTENT AREA
        # ----------------------------------------------------

        self.content_container = tk.Frame(
            self.main_container,
            bg=colors["background"]
        )

        self.content_container.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------

        self.top_bar = tk.Frame(
            self.content_container,
            height=65,
            bg=colors["background"]
        )

        self.top_bar.pack(
            fill="x",
            padx=25,
            pady=(15, 5)
        )

        self.top_bar.pack_propagate(
            False
        )

        self.page_title = tk.Label(
            self.top_bar,
            text="Home",
            font=("Arial", 20, "bold"),
            bg=colors["background"],
            fg=colors["text"]
        )

        self.page_title.pack(
            side="left"
        )

        self.language_display = tk.Label(
            self.top_bar,
            text=self.language_label,
            font=("Arial", 10),
            bg=colors["background"],
            fg=colors["secondary_text"]
        )

        self.language_display.pack(
            side="right",
            padx=10
        )

        # ----------------------------------------------------
        # PAGE CONTAINER
        # ----------------------------------------------------

        self.page_container = tk.Frame(
            self.content_container,
            bg=colors["background"]
        )

        self.page_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        # ----------------------------------------------------
        # STATUS BAR
        # ----------------------------------------------------

        self.status = tk.Label(
            self.content_container,
            text="Ready",
            font=("Arial", 9),
            anchor="w",
            bg=colors["background"],
            fg=colors["success"]
        )

        self.status.pack(
            fill="x",
            padx=28,
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # CREATE PAGES
        # ----------------------------------------------------

        self.create_home_page()
        self.create_dictionary_page()
        self.create_pronunciation_page()
        self.create_learn_page()
        self.create_favorites_page()
        self.create_history_page()
        self.create_progress_page()
        self.create_settings_page()

    # ========================================================
    # PAGE CREATION HELPER
    # ========================================================

    def create_page(self):

        colors = self.get_theme_colors()

        frame = tk.Frame(
            self.page_container,
            bg=colors["background"]
        )

        frame.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        return frame

    # ========================================================
    # HOME PAGE
    # ========================================================

    def create_home_page(self):

        colors = self.get_theme_colors()

        page = self.create_page()

        self.pages["home"] = page

        # ----------------------------------------------------
        # Welcome
        # ----------------------------------------------------

        welcome = tk.Label(
            page,
            text="Welcome to Audio Dictionary",
            font=("Arial", 24, "bold"),
            bg=colors["background"],
            fg=colors["text"]
        )

        welcome.pack(
            pady=(30, 5)
        )

        subtitle = tk.Label(
            page,
            text="Search, listen, learn and improve your vocabulary.",
            font=("Arial", 11),
            bg=colors["background"],
            fg=colors["secondary_text"]
        )

        subtitle.pack(
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        self.home_search_frame = tk.Frame(
            page,
            bg=colors["background"]
        )

        self.home_search_frame.pack(
            fill="x",
            padx=80
        )

        self.home_word_entry = tk.Entry(
            self.home_search_frame,
            font=("Arial", 14),
            bg=colors["input"],
            fg=colors["text"],
            insertbackground=colors["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=colors["border"],
            highlightcolor=colors["accent"]
        )

        self.home_word_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=10
        )

        self.home_word_entry.bind(
            "<Return>",
            lambda event: self.home_search()
        )

        self.home_search_button = tk.Button(
            self.home_search_frame,
            text="Search",
            font=("Arial", 11, "bold"),
            bg=colors["search"],
            fg="#FFFFFF",
            activebackground=colors["search_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.home_search
        )

        self.home_search_button.pack(
            side="left",
            padx=(10, 0)
        )

        # ----------------------------------------------------
        # Cards
        # ----------------------------------------------------

        self.home_cards = tk.Frame(
            page,
            bg=colors["background"]
        )

        self.home_cards.pack(
            fill="x",
            padx=50,
            pady=35
        )

        self.create_home_card(
            self.home_cards,
            "📖",
            "Dictionary",
            "Search words and explore their meanings.",
            lambda: self.show_page("dictionary")
        ).grid(
            row=0,
            column=0,
            padx=8,
            sticky="nsew"
        )

        self.create_home_card(
            self.home_cards,
            "🎧",
            "Pronunciation",
            "Listen to words and practice speaking.",
            lambda: self.show_page("pronunciation")
        ).grid(
            row=0,
            column=1,
            padx=8,
            sticky="nsew"
        )

        self.create_home_card(
            self.home_cards,
            "🧠",
            "Learn",
            "Use flashcards and vocabulary challenges.",
            lambda: self.show_page("learn")
        ).grid(
            row=0,
            column=2,
            padx=8,
            sticky="nsew"
        )

        for column in range(3):
            self.home_cards.columnconfigure(
                column,
                weight=1
            )

        # ----------------------------------------------------
        # Word Of The Day
        # ----------------------------------------------------

        self.home_word_card = tk.Frame(
            page,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1
        )

        self.home_word_card.pack(
            fill="x",
            padx=80,
            pady=10
        )

        self.home_word_title = tk.Label(
            self.home_word_card,
            text="📅 Word of the Day",
            font=("Arial", 13, "bold"),
            bg=colors["surface"],
            fg=colors["accent"]
        )

        self.home_word_title.pack(
            pady=(15, 5)
        )

        self.home_word_label = tk.Label(
            self.home_word_card,
            text=self.get_word_of_the_day(),
            font=("Arial", 20, "bold"),
            bg=colors["surface"],
            fg=colors["text"]
        )

        self.home_word_label.pack(
            pady=(0, 15)
        )

        self.home_word_button = tk.Button(
            self.home_word_card,
            text="Learn this word",
            font=("Arial", 10),
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["button_hover"],
            activeforeground=colors["text"],
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.open_word_of_day
        )

        self.home_word_button.pack(
            pady=(0, 15)
        )

    def create_home_card(
        self,
        parent,
        icon,
        title,
        description,
        command
    ):

        colors = self.get_theme_colors()

        card = tk.Frame(
            parent,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1,
            padx=15,
            pady=15
        )

        icon_label = tk.Label(
            card,
            text=icon,
            font=("Arial", 24),
            bg=colors["surface"],
            fg=colors["accent"]
        )

        icon_label.pack(
            pady=(5, 8)
        )

        title_label = tk.Label(
            card,
            text=title,
            font=("Arial", 12, "bold"),
            bg=colors["surface"],
            fg=colors["text"]
        )

        title_label.pack()

        description_label = tk.Label(
            card,
            text=description,
            font=("Arial", 9),
            wraplength=180,
            justify="center",
            bg=colors["surface"],
            fg=colors["secondary_text"]
        )

        description_label.pack(
            pady=8
        )

        button = tk.Button(
            card,
            text="Open",
            font=("Arial", 9),
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["button_hover"],
            activeforeground=colors["text"],
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
            command=command
        )

        button.pack()

        return card

    def home_search(self):

        word = self.home_word_entry.get().strip()

        if not word:
            messagebox.showwarning(
                "Search",
                "Please enter a word."
            )
            return

        self.word_entry.delete(
            0,
            tk.END
        )

        self.word_entry.insert(
            0,
            word
        )

        self.show_page(
            "dictionary"
        )

        self.search_word()

    # ========================================================
    # DICTIONARY PAGE
    # ========================================================

    def create_dictionary_page(self):

        colors = self.get_theme_colors()

        page = self.create_page()

        self.pages["dictionary"] = page

        # ----------------------------------------------------
        # Search bar
        # ----------------------------------------------------

        search_frame = tk.Frame(
            page,
            bg=colors["background"]
        )

        search_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        self.word_entry = tk.Entry(
            search_frame,
            font=("Arial", 14),
            bg=colors["input"],
            fg=colors["text"],
            insertbackground=colors["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=colors["border"],
            highlightcolor=colors["accent"]
        )

        self.word_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=9
        )

        self.word_entry.bind(
            "<Return>",
            lambda event: self.search_word()
        )

        self.search_btn = tk.Button(
            search_frame,
            text="🔎 Search",
            font=("Arial", 10, "bold"),
            bg=colors["search"],
            fg="#FFFFFF",
            activebackground=colors["search_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=18,
            pady=7,
            cursor="hand2",
            command=self.search_word
        )

        self.search_btn.pack(
            side="left",
            padx=(10, 0)
        )

        Tooltip(
            self.search_btn,
            "Search for a word"
        )

        # ----------------------------------------------------
        # Result frame
        # ----------------------------------------------------

        self.result_frame = tk.Frame(
            page,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1
        )

        self.result_frame.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Meaning
        # ----------------------------------------------------

        self.meaning_frame = tk.Frame(
            self.result_frame,
            bg=colors["surface"]
        )

        self.meaning_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.meaning_title = tk.Label(
            self.meaning_frame,
            text="Definition",
            font=("Arial", 13, "bold"),
            bg=colors["surface"],
            fg=colors["accent"]
        )

        self.meaning_title.pack(
            anchor="w",
            pady=(0, 5)
        )

        self.meaning_box = tk.Text(
            self.meaning_frame,
            font=("Arial", 11),
            wrap=tk.WORD,
            bg=colors["surface"],
            fg=colors["text"],
            insertbackground=colors["text"],
            selectbackground=colors["button_hover"],
            selectforeground=colors["text"],
            bd=0,
            relief="flat",
            padx=8,
            pady=8
        )

        self.meaning_box.pack(
            fill="both",
            expand=True
        )

        self.configure_meaning_tags()

        # ----------------------------------------------------
        # Right side
        # ----------------------------------------------------

        self.side_panel = tk.Frame(
            self.result_frame,
            width=300,
            bg=colors["surface"]
        )

        self.side_panel.pack(
            side="right",
            fill="y",
            padx=(5, 15),
            pady=15
        )

        self.side_panel.pack_propagate(
            False
        )

        self.image_title = tk.Label(
            self.side_panel,
            text="Visual Reference",
            font=("Arial", 12, "bold"),
            bg=colors["surface"],
            fg=colors["accent"]
        )

        self.image_title.pack(
            pady=(0, 7)
        )

        self.image_frame = tk.Frame(
            self.side_panel,
            width=280,
            height=210,
            bg=colors["input"],
            relief="solid",
            bd=1,
            highlightbackground=colors["border"],
            highlightthickness=1
        )

        self.image_frame.pack(
            pady=(0, 15)
        )

        self.image_frame.pack_propagate(
            False
        )

        self.word_image_label = tk.Label(
            self.image_frame,
            text="Search for a word\nto see an image",
            font=("Arial", 10),
            justify="center",
            bg=colors["input"],
            fg=colors["secondary_text"]
        )

        self.word_image_label.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Action buttons
        # ----------------------------------------------------

        self.action_frame = tk.Frame(
            self.side_panel,
            bg=colors["surface"]
        )

        self.action_frame.pack()

        self.speak_button = self.create_action_button(
            self.action_frame,
            "🔊",
            colors["speak"],
            colors["speak_hover"],
            self.pronounce_word
        )

        self.speak_button.grid(
            row=0,
            column=0,
            padx=4,
            pady=4
        )

        Tooltip(
            self.speak_button,
            "Pronounce word"
        )

        self.read_button = self.create_action_button(
            self.action_frame,
            "▶",
            colors["read"],
            colors["read_hover"],
            self.read_word
        )

        self.read_button.grid(
            row=0,
            column=1,
            padx=4,
            pady=4
        )

        Tooltip(
            self.read_button,
            "Read definition aloud"
        )

        self.favorite_button = self.create_action_button(
            self.action_frame,
            "★",
            colors["favorite"],
            colors["favorite_hover"],
            self.favorite_current_word
        )

        self.favorite_button.grid(
            row=0,
            column=2,
            padx=4,
            pady=4
        )

        Tooltip(
            self.favorite_button,
            "Save to favorites"
        )

        self.learned_button = self.create_action_button(
            self.action_frame,
            "✓",
            colors["learned"],
            colors["learned_hover"],
            self.mark_current_word_learned
        )

        self.learned_button.grid(
            row=1,
            column=0,
            padx=4,
            pady=4
        )

        Tooltip(
            self.learned_button,
            "Mark word as learned"
        )

        self.note_button = self.create_action_button(
            self.action_frame,
            "📝",
            colors["note"],
            colors["note_hover"],
            self.add_note_to_current_word
        )

        self.note_button.grid(
            row=1,
            column=1,
            padx=4,
            pady=4
        )

        Tooltip(
            self.note_button,
            "Add or edit personal note"
        )

        self.review_button = self.create_action_button(
            self.action_frame,
            "🔄",
            colors["review"],
            colors["review_hover"],
            self.toggle_review_current_word
        )

        self.review_button.grid(
            row=1,
            column=2,
            padx=4,
            pady=4
        )

        Tooltip(
            self.review_button,
            "Review this word later"
        )

        self.clear_button = self.create_action_button(
            self.action_frame,
            "×",
            colors["clear"],
            colors["clear_hover"],
            self.clear_search
        )

        self.clear_button.grid(
            row=2,
            column=1,
            padx=4,
            pady=4
        )

        Tooltip(
            self.clear_button,
            "Clear search"
        )

    def configure_meaning_tags(self):

        colors = self.get_theme_colors()

        self.meaning_box.tag_configure(
            "word",
            foreground=colors["accent"],
            font=("Arial", 16, "bold")
        )

        self.meaning_box.tag_configure(
            "phonetic",
            foreground=colors["secondary_text"],
            font=("Arial", 10, "italic")
        )

        self.meaning_box.tag_configure(
            "part_of_speech",
            foreground=colors["accent"],
            font=("Arial", 11, "bold")
        )

        self.meaning_box.tag_configure(
            "example",
            foreground=colors["secondary_text"],
            font=("Arial", 10, "italic")
        )

        self.meaning_box.tag_configure(
            "section",
            foreground=colors["accent"],
            font=("Arial", 10, "bold")
        )

    def create_action_button(
        self,
        parent,
        text,
        background,
        hover,
        command
    ):

        return tk.Button(
            parent,
            text=text,
            font=("Arial", 14, "bold"),
            bg=background,
            fg="#FFFFFF",
            activebackground=hover,
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2",
            command=command
        )

    # ========================================================
    # PRONUNCIATION PAGE
    # ========================================================

    def create_pronunciation_page(self):

        colors = self.get_theme_colors()

        page = self.create_page()

        self.pages["pronunciation"] = page

        title = tk.Label(
            page,
            text="🎧 Pronunciation Studio",
            font=("Arial", 22, "bold"),
            bg=colors["background"],
            fg=colors["text"]
        )

        title.pack(
            pady=(35, 8)
        )

        subtitle = tk.Label(
            page,
            text="Listen to the pronunciation of the word you searched.",
            font=("Arial", 10),
            bg=colors["background"],
            fg=colors["secondary_text"]
        )

        subtitle.pack(
            pady=(0, 25)
        )

        self.pronunciation_word_label = tk.Label(
            page,
            text="No word selected",
            font=("Arial", 28, "bold"),
            bg=colors["background"],
            fg=colors["accent"]
        )

        self.pronunciation_word_label.pack(
            pady=15
        )

        self.pronunciation_phonetic_label = tk.Label(
            page,
            text="",
            font=("Arial", 13, "italic"),
            bg=colors["background"],
            fg=colors["secondary_text"]
        )

        self.pronunciation_phonetic_label.pack(
            pady=5
        )

        button_frame = tk.Frame(
            page,
            bg=colors["background"]
        )

        button_frame.pack(
            pady=30
        )

        self.pronounce_page_button = tk.Button(
            button_frame,
            text="🔊 Play Pronunciation",
            font=("Arial", 12, "bold"),
            bg=colors["speak"],
            fg="#FFFFFF",
            activebackground=colors["speak_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.pronounce_word
        )

        self.pronounce_page_button.grid(
            row=0,
            column=0,
            padx=8
        )

        self.read_page_button = tk.Button(
            button_frame,
            text="▶ Read Aloud",
            font=("Arial", 12, "bold"),
            bg=colors["read"],
            fg="#FFFFFF",
            activebackground=colors["read_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.read_word
        )

        self.read_page_button.grid(
            row=0,
            column=1,
            padx=8
        )

        self.stop_speech_button = tk.Button(
            button_frame,
            text="⏹ Stop",
            font=("Arial", 12, "bold"),
            bg=colors["clear"],
            fg="#FFFFFF",
            activebackground=colors["clear_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.stop_speech
        )

        self.stop_speech_button.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=15
        )

        # Speed information
        self.speed_label = tk.Label(
            page,
            text="Speech speed is controlled from Settings.",
            font=("Arial", 10),
            bg=colors["background"],
            fg=colors["muted_text"]
        )

        self.speed_label.pack(
            pady=15
        )

    # ========================================================
    # LEARN PAGE
    # ========================================================

    def create_learn_page(self):

        colors = self.get_theme_colors()

        page = self.create_page()

        self.pages["learn"] = page

        title = tk.Label(
            page,
            text="🧠 Learn",
            font=("Arial", 23, "bold"),
            bg=colors["background"],
            fg=colors["text"]
        )

        title.pack(
            pady=(30, 5)
        )

        subtitle = tk.Label(
            page,
            text="Build your vocabulary one word at a time.",
            font=("Arial", 10),
            bg=colors["background"],
            fg=colors["secondary_text"]
        )

        subtitle.pack(
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # Word of the Day
        # ----------------------------------------------------

        self.learn_word_card = tk.Frame(
            page,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1,
            padx=30,
            pady=25
        )

        self.learn_word_card.pack(
            fill="x",
            padx=100
        )

        tk.Label(
            self.learn_word_card,
            text="📅 WORD OF THE DAY",
            font=("Arial", 10, "bold"),
            bg=colors["surface"],
            fg=colors["accent"]
        ).pack()

        self.learn_word_label = tk.Label(
            self.learn_word_card,
            text=self.get_word_of_the_day(),
            font=("Arial", 28, "bold"),
            bg=colors["surface"],
            fg=colors["text"]
        )

        self.learn_word_label.pack(
            pady=12
        )

        self.learn_word_search_button = tk.Button(
            self.learn_word_card,
            text="Search & Learn",
            font=("Arial", 10, "bold"),
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["button_hover"],
            activeforeground=colors["text"],
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.open_word_of_day
        )

        self.learn_word_search_button.pack()

        # ----------------------------------------------------
        # Flashcards
        # ----------------------------------------------------

        self.flashcard_frame = tk.Frame(
            page,
            bg=colors["background"]
        )

        self.flashcard_frame.pack(
            fill="x",
            padx=100,
            pady=25
        )

        self.flashcard_button = tk.Button(
            self.flashcard_frame,
            text="🃏 Review Favorites",
            font=("Arial", 12, "bold"),
            bg=colors["favorite"],
            fg="#FFFFFF",
            activebackground=colors["favorite_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.start_flashcards
        )

        self.flashcard_button.pack()

        self.flashcard_status = tk.Label(
            self.flashcard_frame,
            text="Save words to Favorites to create your flashcards.",
            font=("Arial", 9),
            bg=colors["background"],
            fg=colors["muted_text"]
        )

        self.flashcard_status.pack(
            pady=10
        )

    # ========================================================
    # FAVORITES PAGE
    # ========================================================

    def create_favorites_page(self):

        colors = self.get_theme_colors()

        page = self.create_page()

        self.pages["favorites"] = page

        title = tk.Label(
            page,
            text="⭐ Favorites",
            font=("Arial", 22, "bold"),
            bg=colors["background"],
            fg=colors["text"]
        )

        title.pack(
            pady=(20, 15)
        )

        container = tk.Frame(
            page,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1
        )

        container.pack(
            fill="both",
            expand=True,
            padx=80,
            pady=10
        )

        self.favorite_listbox = tk.Listbox(
            container,
            font=("Arial", 12),
            bg=colors["input"],
            fg=colors["text"],
            selectbackground=colors["button_hover"],
            selectforeground=colors["text"],
            bd=0,
            highlightthickness=0
        )

        self.favorite_listbox.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.favorite_listbox.bind(
            "<Double-Button-1>",
            self.favorite_selection
        )

        button_frame = tk.Frame(
            page,
            bg=colors["background"]
        )

        button_frame.pack(
            pady=10
        )

        self.favorite_search_button = tk.Button(
            button_frame,
            text="🔎 Search Selected",
            font=("Arial", 10),
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["button_hover"],
            activeforeground=colors["text"],
            bd=0,
            padx=15,
            pady=7,
            cursor="hand2",
            command=self.search_selected_favorite
        )

        self.favorite_search_button.grid(
            row=0,
            column=0,
            padx=5
        )

        self.favorite_clear_button = tk.Button(
            button_frame,
            text="Clear Favorites",
            font=("Arial", 10),
            bg=colors["clear"],
            fg="#FFFFFF",
            activebackground=colors["clear_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=15,
            pady=7,
            cursor="hand2",
            command=self.clear_favorites
        )

        self.favorite_clear_button.grid(
            row=0,
            column=1,
            padx=5
        )

    # ========================================================
    # HISTORY PAGE
    # ========================================================

    def create_history_page(self):

        colors = self.get_theme_colors()

        page = self.create_page()

        self.pages["history"] = page

        title = tk.Label(
            page,
            text="🕘 Search History",
            font=("Arial", 22, "bold"),
            bg=colors["background"],
            fg=colors["text"]
        )

        title.pack(
            pady=(20, 15)
        )

        container = tk.Frame(
            page,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1
        )

        container.pack(
            fill="both",
            expand=True,
            padx=80,
            pady=10
        )

        self.history_listbox = tk.Listbox(
            container,
            font=("Arial", 12),
            bg=colors["input"],
            fg=colors["text"],
            selectbackground=colors["button_hover"],
            selectforeground=colors["text"],
            bd=0,
            highlightthickness=0
        )

        self.history_listbox.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.history_listbox.bind(
            "<Double-Button-1>",
            self.history_selection
        )

        button_frame = tk.Frame(
            page,
            bg=colors["background"]
        )

        button_frame.pack(
            pady=10
        )

        self.history_search_button = tk.Button(
            button_frame,
            text="🔎 Search Selected",
            font=("Arial", 10),
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["button_hover"],
            activeforeground=colors["text"],
            bd=0,
            padx=15,
            pady=7,
            cursor="hand2",
            command=self.search_selected_history
        )

        self.history_search_button.grid(
            row=0,
            column=0,
            padx=5
        )

        self.history_clear_button = tk.Button(
            button_frame,
            text="Clear History",
            font=("Arial", 10),
            bg=colors["clear"],
            fg="#FFFFFF",
            activebackground=colors["clear_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=15,
            pady=7,
            cursor="hand2",
            command=self.clear_history
        )

        self.history_clear_button.grid(
            row=0,
            column=1,
            padx=5
        )

    # ========================================================
    # PROGRESS PAGE
    # ========================================================

    def create_progress_page(self):

        colors = self.get_theme_colors()

        page = self.create_page()

        self.pages["progress"] = page

        title = tk.Label(
            page,
            text="📊 Learning Progress",
            font=("Arial", 22, "bold"),
            bg=colors["background"],
            fg=colors["text"]
        )

        title.pack(
            pady=(25, 5)
        )

        subtitle = tk.Label(
            page,
            text="Track your vocabulary activity.",
            font=("Arial", 10),
            bg=colors["background"],
            fg=colors["secondary_text"]
        )

        subtitle.pack(
            pady=(0, 25)
        )

        cards = tk.Frame(
            page,
            bg=colors["background"]
        )

        cards.pack(
            fill="x",
            padx=60
        )

        self.progress_labels["history"] = (
            self.create_progress_card(
                cards,
                "🕘",
                "Words Searched",
                "0"
            )
        )

        self.progress_labels["favorites"] = (
            self.create_progress_card(
                cards,
                "⭐",
                "Favorites",
                "0"
            )
        )

        self.progress_labels["learned"] = (
            self.create_progress_card(
                cards,
                "🧠",
                "Words Learned",
                "0"
            )
        )

        self.progress_labels["streak"] = (
            self.create_progress_card(
                cards,
                "🔥",
                "Study Streak",
                "0 days"
            )
        )

        # Layout
        for index in range(4):
            cards.columnconfigure(
                index,
                weight=1
            )

        # ----------------------------------------------------
        # Information
        # ----------------------------------------------------

        self.progress_info = tk.Label(
            page,
            text=(
                "Keep searching, reviewing and learning "
                "new words to build your vocabulary."
            ),
            font=("Arial", 11),
            wraplength=600,
            justify="center",
            bg=colors["background"],
            fg=colors["secondary_text"]
        )

        self.progress_info.pack(
            pady=45
        )

    def create_progress_card(
        self,
        parent,
        icon,
        title,
        value
    ):

        colors = self.get_theme_colors()

        card = tk.Frame(
            parent,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1,
            padx=15,
            pady=20
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        tk.Label(
            card,
            text=icon,
            font=("Arial", 20),
            bg=colors["surface"],
            fg=colors["accent"]
        ).pack()

        value_label = tk.Label(
            card,
            text=value,
            font=("Arial", 20, "bold"),
            bg=colors["surface"],
            fg=colors["text"]
        )

        value_label.pack(
            pady=5
        )

        tk.Label(
            card,
            text=title,
            font=("Arial", 9),
            bg=colors["surface"],
            fg=colors["secondary_text"]
        ).pack()

        return value_label

    # ========================================================
    # SETTINGS PAGE
    # ========================================================

    def create_settings_page(self):

        colors = self.get_theme_colors()

        page = self.create_page()

        self.pages["settings"] = page

        title = tk.Label(
            page,
            text="⚙ Settings",
            font=("Arial", 22, "bold"),
            bg=colors["background"],
            fg=colors["text"]
        )

        title.pack(
            pady=(30, 10)
        )

        description = tk.Label(
            page,
            text="Manage your application preferences.",
            font=("Arial", 10),
            bg=colors["background"],
            fg=colors["secondary_text"]
        )

        description.pack(
            pady=(0, 25)
        )

        card = tk.Frame(
            page,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1,
            padx=30,
            pady=30
        )

        card.pack(
            padx=120,
            fill="x"
        )

        self.settings_theme_label = tk.Label(
            card,
            text="Appearance",
            font=("Arial", 12, "bold"),
            bg=colors["surface"],
            fg=colors["text"]
        )

        self.settings_theme_label.pack(
            anchor="w"
        )

        self.settings_theme_value = tk.Label(
            card,
            text=self.current_theme.title(),
            font=("Arial", 10),
            bg=colors["surface"],
            fg=colors["secondary_text"]
        )

        self.settings_theme_value.pack(
            anchor="w",
            pady=(3, 15)
        )

        self.settings_voice_label = tk.Label(
            card,
            text=f"Voice: {self.saved_voice.title()}",
            font=("Arial", 10),
            bg=colors["surface"],
            fg=colors["secondary_text"]
        )

        self.settings_voice_label.pack(
            anchor="w",
            pady=3
        )

        self.settings_language_label = tk.Label(
            card,
            text=f"Language: {self.language_label}",
            font=("Arial", 10),
            bg=colors["surface"],
            fg=colors["secondary_text"]
        )

        self.settings_language_label.pack(
            anchor="w",
            pady=3
        )

        self.open_settings_button = tk.Button(
            card,
            text="Open Settings",
            font=("Arial", 11, "bold"),
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["button_hover"],
            activeforeground=colors["text"],
            bd=0,
            padx=20,
            pady=9,
            cursor="hand2",
            command=self.open_settings
        )

        self.open_settings_button.pack(
            pady=(20, 0)
        )

    # ========================================================
    # NAVIGATION
    # ========================================================

    def show_page(self, page_name):

        if page_name not in self.pages:
            return

        self.current_page = page_name

        page = self.pages[page_name]

        page.lift()

        titles = {
            "home": "Home",
            "dictionary": "Dictionary",
            "pronunciation": "Pronunciation",
            "learn": "Learn",
            "favorites": "Favorites",
            "history": "History",
            "progress": "Progress",
            "settings": "Settings"
        }

        self.page_title.config(
            text=titles.get(
                page_name,
                "Audio Dictionary"
            )
        )

        # Update active navigation button
        colors = self.get_theme_colors()

        for name, button in self.nav_buttons.items():

            if name == page_name:

                button.configure(
                    bg=colors["accent"],
                    fg="#FFFFFF",
                    activebackground=colors["accent_hover"],
                    activeforeground="#FFFFFF"
                )

            else:

                button.configure(
                    bg=colors["sidebar"],
                    fg=colors["text"],
                    activebackground=colors["button_hover"],
                    activeforeground=colors["text"]
                )

        # Refresh dynamic pages
        if page_name == "favorites":
            self.refresh_favorites_page()

        elif page_name == "history":
            self.refresh_history_page()

        elif page_name == "progress":
            self.update_progress()

        elif page_name == "pronunciation":
            self.update_pronunciation_page()

        elif page_name == "learn":
            self.update_learn_page()

    # ========================================================
    # SEARCH
    # ========================================================

    def search_word(self):

        if self.search_running:
            return

        word = self.word_entry.get().strip()

        if not word:

            messagebox.showwarning(
                "Input Required",
                "Please enter a word."
            )

            return

        self.search_running = True

        self.search_btn.config(
            state="disabled"
        )

        self.status.config(
            text="Searching..."
        )

        threading.Thread(
            target=self.search_worker,
            args=(word,),
            daemon=True
        ).start()

    def search_worker(self, word):

        try:

            result = self.controller.search(
                word
            )

            self.root.after(
                0,
                lambda r=result:
                self.finish_search(r)
            )

        except Exception as error:

            print(
                f"Search Error: {error}"
            )

            self.root.after(
                0,
                lambda e=str(error):
                self.search_failed(e)
            )

    def finish_search(self, result):

        self.search_running = False

        self.search_btn.config(
            state="normal"
        )

        self.meaning_box.delete(
            "1.0",
            tk.END
        )

        if not result.get("success"):

            self.meaning_box.insert(
                tk.END,
                result.get(
                    "message",
                    "Word not found."
                )
            )

            self.status.config(
                text="Search failed"
            )

            return

        self.current_result = result

        self.audio_url = result.get(
            "audio",
            ""
        )

        word = result.get(
            "word",
            ""
        )

        self.current_word = word

        phonetic = result.get(
            "phonetic"
        ) or "N/A"

        self.meaning_box.insert(
            tk.END,
            f"WORD: {word}\n",
            "word"
        )

        self.meaning_box.insert(
            tk.END,
            f"PHONETIC: {phonetic}\n\n",
            "phonetic"
        )

        meanings = result.get(
            "meanings",
            []
        )

        if not meanings:

            self.meaning_box.insert(
                tk.END,
                "No definitions available "
                "for this word."
            )

        else:

            for meaning in meanings:

                part_of_speech = meaning.get(
                    "partOfSpeech",
                    ""
                )

                self.meaning_box.insert(
                    tk.END,
                    f"Part of Speech: "
                    f"{part_of_speech}\n",
                    "part_of_speech"
                )

                self.meaning_box.insert(
                    tk.END,
                    "─" * 45 + "\n"
                )

                for definition in meaning.get(
                    "definitions",
                    []
                ):

                    definition_text = (
                        definition.get(
                            "definition",
                            ""
                        )
                    )

                    if definition_text:

                        self.meaning_box.insert(
                            tk.END,
                            f"• {definition_text}\n"
                        )

                    example = definition.get(
                        "example",
                        ""
                    )

                    if example:

                        self.meaning_box.insert(
                            tk.END,
                            f"Example: {example}\n",
                            "example"
                        )

                    self.meaning_box.insert(
                        tk.END,
                        "\n"
                    )

                synonyms = (
                    meaning.get("synonyms")
                    or []
                )

                if synonyms:

                    self.meaning_box.insert(
                        tk.END,
                        "Synonyms:\n",
                        "section"
                    )

                    self.meaning_box.insert(
                        tk.END,
                        ", ".join(
                            synonyms[:10]
                        )
                    )

                    self.meaning_box.insert(
                        tk.END,
                        "\n\n"
                    )

                antonyms = (
                    meaning.get("antonyms")
                    or []
                )

                if antonyms:

                    self.meaning_box.insert(
                        tk.END,
                        "Antonyms:\n",
                        "section"
                    )

                    self.meaning_box.insert(
                        tk.END,
                        ", ".join(
                            antonyms[:10]
                        )
                    )

                    self.meaning_box.insert(
                        tk.END,
                        "\n\n"
                    )

        self.current_read_text = (
            self.build_read_aloud_text(
                result
            )
        )

        self.refresh_history_page()

        self.update_progress()

        self.update_pronunciation_page()
        self.update_learning_controls()

        self.status.config(
            text=f"Found '{word}'"
        )

        self.load_word_image(
            word
        )

        # Automatically update home word entry
        if hasattr(
            self,
            "home_word_entry"
        ):

            self.home_word_entry.delete(
                0,
                tk.END
            )

            self.home_word_entry.insert(
                0,
                word
            )

    def search_failed(self, error):

        self.search_running = False

        self.search_btn.config(
            state="normal"
        )

        self.status.config(
            text="Search error"
        )

        print(
            f"Search Error: {error}"
        )

    # ========================================================
    # READ ALOUD
    # ========================================================

    def build_read_aloud_text(
        self,
        result
    ):

        word = (
            result.get("word") or ""
        ).strip()

        if not word:
            return ""

        sections = [
            f"The word is {word}."
        ]

        for meaning in result.get(
            "meanings",
            []
        ):

            for definition in meaning.get(
                "definitions",
                []
            ):

                definition_text = (
                    definition.get(
                        "definition"
                    ) or ""
                ).strip()

                if definition_text:

                    sections.append(
                        f"Meaning: "
                        f"{definition_text}."
                    )

                example = (
                    definition.get(
                        "example"
                    ) or ""
                ).strip()

                if example:

                    sections.append(
                        f"Example: "
                        f"{example}."
                    )

            synonyms = (
                meaning.get("synonyms")
                or []
            )

            if synonyms:

                sections.append(
                    "Synonyms include "
                    + ", ".join(
                        synonyms[:5]
                    )
                    + "."
                )

            antonyms = (
                meaning.get("antonyms")
                or []
            )

            if antonyms:

                sections.append(
                    "Antonyms include "
                    + ", ".join(
                        antonyms[:5]
                    )
                    + "."
                )

        return " ".join(
            sections
        )

    def read_word(self):

        if not self.current_read_text:

            messagebox.showinfo(
                "Read",
                "Search for a word first."
            )

            return

        if self.read_running:

            self.status.config(
                text="Already reading..."
            )

            return

        self.read_running = True

        self.read_button.config(
            state="disabled"
        )

        if hasattr(
            self,
            "read_page_button"
        ):

            self.read_page_button.config(
                state="disabled"
            )

        self.status.config(
            text="Reading..."
        )

        threading.Thread(
            target=self.read_worker,
            args=(self.current_read_text,),
            daemon=True
        ).start()

    def read_worker(self, text):

        try:

            success = (
                self.speech_engine.speak(
                    text
                )
            )

        except Exception as error:

            print(
                f"Speech Error: {error}"
            )

            success = False

        try:

            self.root.after(
                0,
                lambda s=success:
                self.finish_read(s)
            )

        except tk.TclError:
            pass

    def finish_read(self, success):

        self.read_running = False

        self.read_button.config(
            state="normal"
        )

        if hasattr(
            self,
            "read_page_button"
        ):

            self.read_page_button.config(
                state="normal"
            )

        if success:

            self.status.config(
                text="Read complete"
            )

        else:

            self.status.config(
                text="Speech stopped"
            )

    def stop_speech(self):

        try:

            self.speech_engine.stop()

        except Exception as error:

            print(
                f"Speech stop error: {error}"
            )

        self.read_running = False

        self.read_button.config(
            state="normal"
        )

        if hasattr(
            self,
            "read_page_button"
        ):

            self.read_page_button.config(
                state="normal"
            )

        self.status.config(
            text="Speech stopped"
        )

    # ========================================================
    # PRONUNCIATION
    # ========================================================

    def pronounce_word(self):

        if not self.audio_url:

            messagebox.showinfo(
                "Pronunciation",
                "No pronunciation audio "
                "is available for this word."
            )

            return

        success = self.controller.pronounce(
            self.audio_url
        )

        if success:

            self.status.config(
                text=f"Playing pronunciation: {self.current_word}"
            )

        else:

            messagebox.showerror(
                "Audio Error",
                "Unable to play pronunciation."
            )

    def update_pronunciation_page(self):

        if not hasattr(
            self,
            "pronunciation_word_label"
        ):
            return

        if self.current_word:

            self.pronunciation_word_label.config(
                text=self.current_word
            )

            phonetic = ""

            if self.current_result:

                phonetic = (
                    self.current_result.get(
                        "phonetic"
                    )
                    or ""
                )

            self.pronunciation_phonetic_label.config(
                text=phonetic
            )

        else:

            self.pronunciation_word_label.config(
                text="No word selected"
            )

            self.pronunciation_phonetic_label.config(
                text=""
            )

    # ========================================================
    # IMAGE
    # ========================================================

    def load_word_image(self, word):

        self.word_image_label.configure(
            image="",
            text="Loading image..."
        )

        if self.image_loading:
            return

        self.image_loading = True

        threading.Thread(
            target=self.image_worker,
            args=(word,),
            daemon=True
        ).start()

    def image_worker(self, word):

        try:

            from PIL import Image

            query = word.strip()

            if not query:
                raise ValueError(
                    "Empty word"
                )

            search_url = (
                "https://commons.wikimedia.org/"
                "w/api.php?"
                "action=query&"
                "generator=search&"
                "gsrsearch=" + query +
                "&gsrnamespace=6&"
                "gsrlimit=1&"
                "prop=imageinfo&"
                "iiprop=url&"
                "iiurlwidth=600&"
                "format=json&"
                "origin=*"
            )

            request = Request(
                search_url,
                headers={
                    "User-Agent":
                    "AudioDictionary/2.0"
                }
            )

            with urlopen(
                request,
                timeout=10
            ) as response:

                payload = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            pages = (
                payload
                .get("query", {})
                .get("pages", {})
            )

            image_info = None

            for page_data in pages.values():

                image_info = (
                    page_data.get(
                        "imageinfo",
                        [{}]
                    )[0]
                )

                if image_info:
                    break

            if not image_info:
                raise ValueError(
                    "No image found"
                )

            image_url = (
                image_info.get(
                    "thumburl"
                )
                or image_info.get(
                    "url"
                )
            )

            if not image_url:
                raise ValueError(
                    "No image URL"
                )

            image_request = Request(
                image_url,
                headers={
                    "User-Agent":
                    "AudioDictionary/2.0"
                }
            )

            with urlopen(
                image_request,
                timeout=10
            ) as response:

                image_data = response.read()

            if not image_data:
                raise ValueError(
                    "No image data"
                )

            image = Image.open(
                io.BytesIO(image_data)
            ).convert("RGB")

            image.thumbnail(
                (270, 200)
            )

            self.root.after(
                0,
                lambda img=image:
                self.display_image(img)
            )

        except Exception as error:

            print(
                f"Image Error: {error}"
            )

            try:

                self.root.after(
                    0,
                    self.display_fallback_image
                )

            except tk.TclError:
                pass

    def display_image(self, image):

        try:

            from PIL import ImageTk

            self.word_image = (
                ImageTk.PhotoImage(
                    image
                )
            )

            self.word_image_label.configure(
                image=self.word_image,
                text=""
            )

        except Exception as error:

            print(
                f"Display Image Error: {error}"
            )

            self.display_fallback_image()

        finally:

            self.image_loading = False

    def display_fallback_image(self):

        self.image_loading = False

        self.set_local_image(
            self.fallback_image_path
        )

    def set_local_image(self, image_path):

        try:

            from PIL import Image, ImageTk

            if not os.path.exists(
                image_path
            ):

                self.word_image_label.configure(
                    image="",
                    text="Image unavailable"
                )

                return

            image = Image.open(
                image_path
            ).convert("RGB")

            image.thumbnail(
                (270, 200)
            )

            self.word_image = (
                ImageTk.PhotoImage(
                    image
                )
            )

            self.word_image_label.configure(
                image=self.word_image,
                text=""
            )

        except Exception as error:

            print(
                f"Fallback Image Error: {error}"
            )

            self.word_image_label.configure(
                image="",
                text="Image unavailable"
            )

    # ========================================================
    # FAVORITES
    # ========================================================

    def favorite_current_word(self):

        word = self.current_word.strip()

        if not word:

            messagebox.showinfo(
                "Favorite",
                "Search for a word before "
                "saving it as a favorite."
            )

            return

        self.history_manager.add_favorite(
            word
        )

        self.refresh_favorites_page()

        self.update_progress()

        self.status.config(
            text=f"Saved '{word}' to favorites"
        )

    def refresh_favorites_page(self):

        if self.favorite_listbox is None:
            return

        self.favorite_listbox.delete(
            0,
            tk.END
        )

        for word in (
            self.history_manager.get_favorites()
        ):

            self.favorite_listbox.insert(
                tk.END,
                word
            )

    def favorite_selection(self, event=None):

        if self.favorite_listbox is None:
            return

        selection = (
            self.favorite_listbox.curselection()
        )

        if not selection:
            return

        word = self.favorite_listbox.get(
            selection[0]
        )

        self.load_word(
            word
        )

    def search_selected_favorite(self):

        self.favorite_selection()

    def clear_favorites(self):

        if not self.history_manager.get_favorites():
            return

        answer = messagebox.askyesno(
            "Clear Favorites",
            "Are you sure you want to remove "
            "all favorite words?"
        )

        if not answer:
            return

        self.history_manager.clear_favorites()

        self.refresh_favorites_page()

        self.update_progress()

        self.status.config(
            text="Favorites cleared"
        )

    # ========================================================
    # HISTORY
    # ========================================================

    def refresh_history_page(self):

        if self.history_listbox is None:
            return

        self.history_listbox.delete(
            0,
            tk.END
        )

        for word in (
            self.history_manager.get_history()
        ):

            self.history_listbox.insert(
                tk.END,
                word
            )

    def history_selection(self, event=None):

        if self.history_listbox is None:
            return

        selection = (
            self.history_listbox.curselection()
        )

        if not selection:
            return

        word = self.history_listbox.get(
            selection[0]
        )

        self.load_word(
            word
        )

    def search_selected_history(self):

        self.history_selection()

    def clear_history(self):

        if not self.history_manager.get_history():
            return

        answer = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear "
            "your search history?"
        )

        if not answer:
            return

        self.history_manager.clear_history()

        self.refresh_history_page()

        self.update_progress()

        self.status.config(
            text="History cleared"
        )

    # ========================================================
    # LOAD WORD
    # ========================================================

    def load_word(self, word):

        self.word_entry.delete(
            0,
            tk.END
        )

        self.word_entry.insert(
            0,
            word
        )

        self.show_page(
            "dictionary"
        )

        self.search_word()

    # ========================================================
    # CLEAR SEARCH
    # ========================================================

    def clear_search(self):

        self.stop_speech()

        self.current_result = None
        self.current_word = ""
        self.current_read_text = ""
        self.audio_url = ""

        self.word_entry.delete(
            0,
            tk.END
        )

        self.meaning_box.delete(
            "1.0",
            tk.END
        )

        self.word_image = None

        self.word_image_label.configure(
            image="",
            text="Search for a word\nto see an image"
        )

        self.read_button.config(
            state="normal"
        )

        self.update_pronunciation_page()
        self.update_learning_controls()

        self.status.config(
            text="Cleared"
        )

    # ========================================================
    # LEARNING
    # ========================================================

    def get_word_of_the_day(self):

        words = [
            "serendipity",
            "resilient",
            "eloquent",
            "meticulous",
            "ambiguous",
            "benevolent",
            "curious",
            "diligent",
            "innovative",
            "perseverance",
            "vivid",
            "magnificent",
            "adaptable",
            "authentic",
            "compassion"
        ]

        # Use the day of the year so the same word
        # remains throughout the day.
        import datetime

        day_number = (
            datetime.date.today().timetuple().tm_yday
        )

        return words[
            day_number % len(words)
        ]

    def open_word_of_day(self):

        word = self.get_word_of_the_day()

        self.load_word(
            word
        )

    def mark_current_word_learned(self):

        word = self.current_word.strip()

        if not word:
            messagebox.showinfo(
                "Learned",
                "Search for a word before marking it as learned."
            )
            return

        if self.history_manager.is_learned(word):
            self.history_manager.unmark_learned(word)
            self.status.config(
                text=f"'{word}' removed from learned words"
            )
        else:
            self.history_manager.mark_learned(word)
            self.status.config(
                text=f"'{word}' marked as learned"
            )

        self.update_learning_controls()
        self.update_learn_page()
        self.update_progress()

    def add_note_to_current_word(self):

        word = self.current_word.strip()

        if not word:
            messagebox.showinfo(
                "Personal Note",
                "Search for a word before adding a note."
            )
            return

        existing_note = self.history_manager.get_note(word)

        note = simpledialog.askstring(
            "Personal Note",
            f"Add a personal note for '{word}':",
            initialvalue=existing_note,
            parent=self.root
        )

        if note is None:
            return

        self.history_manager.add_note(
            word,
            note
        )

        if note.strip():
            self.status.config(
                text=f"Personal note saved for '{word}'"
            )
        else:
            self.status.config(
                text=f"Personal note cleared for '{word}'"
            )

        self.update_learning_controls()

    def toggle_review_current_word(self):

        word = self.current_word.strip()

        if not word:
            messagebox.showinfo(
                "Review Later",
                "Search for a word before adding it to review."
            )
            return

        if self.history_manager.is_review_later(word):
            self.history_manager.remove_review_later(word)
            self.status.config(
                text=f"'{word}' removed from Review Later"
            )
        else:
            self.history_manager.mark_review_later(word)
            self.status.config(
                text=f"'{word}' added to Review Later"
            )

        self.update_learning_controls()
        self.update_learn_page()
        self.update_progress()

    def update_learning_controls(self):
        """Update learning button labels and tooltips for the current word."""

        if not self.current_word:
            if hasattr(self, "learned_button"):
                self.learned_button.config(text="✓")
            if hasattr(self, "note_button"):
                self.note_button.config(text="📝")
            if hasattr(self, "review_button"):
                self.review_button.config(text="🔄")
            return

        word = self.current_word

        if self.history_manager.is_learned(word):
            self.learned_button.config(text="✓")
        else:
            self.learned_button.config(text="✓")

        if self.history_manager.get_note(word):
            self.note_button.config(text="📝")
        else:
            self.note_button.config(text="📝")

        if self.history_manager.is_review_later(word):
            self.review_button.config(text="✓")
        else:
            self.review_button.config(text="🔄")

    def update_learn_page(self):

        if hasattr(
            self,
            "learn_word_label"
        ):

            self.learn_word_label.config(
                text=self.get_word_of_the_day()
            )

        if hasattr(
            self,
            "flashcard_status"
        ):

            favorite_count = len(
                self.history_manager.get_favorites()
            )

            learned_count = self.history_manager.get_learned_count()
            review_count = self.history_manager.get_review_count()
            streak = self.history_manager.get_learning_streak()

            if favorite_count:
                favorite_text = (
                    f"You have {favorite_count} favorite "
                    f"word{'s' if favorite_count != 1 else ''} "
                    f"available for review."
                )
            else:
                favorite_text = (
                    "Save words to Favorites to "
                    "create your flashcards."
                )

            self.flashcard_status.config(
                text=(
                    f"{favorite_text}\n"
                    f"Learned: {learned_count}   •   "
                    f"Review Later: {review_count}   •   "
                    f"Streak: {streak} day{'s' if streak != 1 else ''}"
                )
            )

    # ========================================================
    # FLASHCARDS
    # ========================================================

    def start_flashcards(self):

        favorites = (
            self.history_manager.get_favorites()
        )

        if not favorites:

            messagebox.showinfo(
                "Flashcards",
                "You do not have any favorite words yet.\n\n"
                "Search for words and save them as favorites "
                "to create flashcards."
            )

            return

        self.show_flashcard_window(
            favorites
        )

    def show_flashcard_window(self, words):

        colors = self.get_theme_colors()

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Vocabulary Flashcards"
        )

        window.geometry(
            "520x420"
        )

        window.configure(
            bg=colors["background"]
        )

        card = tk.Frame(
            window,
            bg=colors["surface"],
            bd=1,
            relief="solid",
            highlightbackground=colors["border"],
            highlightthickness=1
        )

        card.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        state = {
            "index": 0,
            "show_answer": False
        }

        word_label = tk.Label(
            card,
            text="",
            font=("Arial", 28, "bold"),
            bg=colors["surface"],
            fg=colors["accent"]
        )

        word_label.pack(
            pady=(50, 20)
        )

        answer_label = tk.Label(
            card,
            text="Click 'Show Answer'",
            font=("Arial", 13),
            wraplength=400,
            justify="center",
            bg=colors["surface"],
            fg=colors["secondary_text"]
        )

        answer_label.pack(
            pady=20
        )

        def update_card():

            word = words[
                state["index"]
            ]

            word_label.config(
                text=word
            )

            state["show_answer"] = False

            answer_label.config(
                text="Click 'Show Answer'"
            )

        def show_answer():

            word = words[
                state["index"]
            ]

            answer_label.config(
                text=(
                    f"Remember the definition "
                    f"of '{word}'.\n\n"
                    "Use the Dictionary screen to "
                    "review the complete definition."
                )
            )

            state["show_answer"] = True

            self.word_entry.delete(
                0,
                tk.END
            )

            self.word_entry.insert(
                0,
                word
            )

            self.current_word = word

        def next_card():

            state["index"] = (
                state["index"] + 1
            ) % len(words)

            update_card()

        buttons = tk.Frame(
            card,
            bg=colors["surface"]
        )

        buttons.pack(
            pady=20
        )

        tk.Button(
            buttons,
            text="Show Answer",
            font=("Arial", 10, "bold"),
            bg=colors["button"],
            fg=colors["text"],
            activebackground=colors["button_hover"],
            activeforeground=colors["text"],
            bd=0,
            padx=15,
            pady=7,
            cursor="hand2",
            command=show_answer
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        tk.Button(
            buttons,
            text="Next →",
            font=("Arial", 10, "bold"),
            bg=colors["accent"],
            fg="#FFFFFF",
            activebackground=colors["accent_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=15,
            pady=7,
            cursor="hand2",
            command=next_card
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        update_card()

    # ========================================================
    # PROGRESS
    # ========================================================

    def update_progress(self):

        if not self.progress_labels:
            return

        history_count = len(
            self.history_manager.get_history()
        )

        favorite_count = len(
            self.history_manager.get_favorites()
        )

        learned_count = self.history_manager.get_learned_count()
        streak = self.history_manager.get_learning_streak()

        self.progress_labels[
            "history"
        ].config(
            text=str(history_count)
        )

        self.progress_labels[
            "favorites"
        ].config(
            text=str(favorite_count)
        )

        self.progress_labels[
            "learned"
        ].config(
            text=str(learned_count)
        )

        self.progress_labels[
            "streak"
        ].config(
            text=(
                f"{streak} day{'s' if streak != 1 else ''}"
            )
        )

    # ========================================================
    # SETTINGS
    # ========================================================

    def open_settings(self):

        try:

            self.settings_window = SettingsWindow(
                self.root,
                self.settings_manager,
                self.speech_engine,
                apply_callback=self.apply_settings
            )

            self.settings_window.open()

        except Exception as error:

            print(
                f"Settings Error: {error}"
            )

            messagebox.showerror(
                "Settings Error",
                f"Unable to open settings:\n{error}"
            )

    def apply_settings(self, settings):

        if not isinstance(
            settings,
            dict
        ):
            return

        voice = settings.get(
            "voice",
            self.saved_voice
        )

        language = settings.get(
            "language",
            self.current_language
        )

        dark_mode = bool(
            settings.get(
                "dark_mode",
                self.dark_mode
            )
        )

        self.saved_voice = voice

        self.speech_engine.set_voice(
            voice
        )

        self.current_language = language

        self.language_label = (
            self.get_language_name(
                language
            )
        )

        self.controller.set_language(
            language
        )

        self.dark_mode = dark_mode

        self.current_theme = (
            "dark"
            if dark_mode
            else "light"
        )

        self.settings_manager.update({
            "voice": voice,
            "language": language,
            "dark_mode": dark_mode
        })

        self.apply_theme()

        self.status.config(
            text="Settings applied"
        )

    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(self):

        colors = self.get_theme_colors()

        self.root.configure(
            bg=colors["background"]
        )

        self.main_container.configure(
            bg=colors["background"]
        )

        self.sidebar.configure(
            bg=colors["sidebar"]
        )

        self.logo_frame.configure(
            bg=colors["sidebar"]
        )

        self.logo_icon.configure(
            bg=colors["sidebar"],
            fg=colors["accent"]
        )

        self.logo_label.configure(
            bg=colors["sidebar"],
            fg=colors["text"]
        )

        self.navigation_frame.configure(
            bg=colors["sidebar"]
        )

        self.sidebar_footer.configure(
            bg=colors["sidebar"],
            fg=colors["muted_text"]
        )

        self.content_container.configure(
            bg=colors["background"]
        )

        self.top_bar.configure(
            bg=colors["background"]
        )

        self.page_title.configure(
            bg=colors["background"],
            fg=colors["text"]
        )

        self.language_display.configure(
            bg=colors["background"],
            fg=colors["secondary_text"],
            text=self.language_label
        )

        self.page_container.configure(
            bg=colors["background"]
        )

        self.status.configure(
            bg=colors["background"],
            fg=colors["success"]
        )

        # Navigation
        for name, button in self.nav_buttons.items():

            if name == self.current_page:

                button.configure(
                    bg=colors["accent"],
                    fg="#FFFFFF",
                    activebackground=colors["accent_hover"],
                    activeforeground="#FFFFFF"
                )

            else:

                button.configure(
                    bg=colors["sidebar"],
                    fg=colors["text"],
                    activebackground=colors["button_hover"],
                    activeforeground=colors["text"]
                )

        # Dictionary
        if hasattr(
            self,
            "word_entry"
        ):

            self.word_entry.configure(
                bg=colors["input"],
                fg=colors["text"],
                insertbackground=colors["text"],
                highlightbackground=colors["border"],
                highlightcolor=colors["accent"]
            )

        if hasattr(
            self,
            "search_btn"
        ):

            self.search_btn.configure(
                bg=colors["search"],
                activebackground=colors["search_hover"]
            )

        if hasattr(
            self,
            "result_frame"
        ):

            self.result_frame.configure(
                bg=colors["surface"],
                highlightbackground=colors["border"]
            )

            self.meaning_frame.configure(
                bg=colors["surface"]
            )

            self.meaning_title.configure(
                bg=colors["surface"],
                fg=colors["accent"]
            )

            self.meaning_box.configure(
                bg=colors["surface"],
                fg=colors["text"],
                insertbackground=colors["text"],
                selectbackground=colors["button_hover"],
                selectforeground=colors["text"]
            )

            self.configure_meaning_tags()

            self.side_panel.configure(
                bg=colors["surface"]
            )

            self.image_title.configure(
                bg=colors["surface"],
                fg=colors["accent"]
            )

            self.image_frame.configure(
                bg=colors["input"],
                highlightbackground=colors["border"]
            )

            self.word_image_label.configure(
                bg=colors["input"],
                fg=colors["secondary_text"]
            )

            self.action_frame.configure(
                bg=colors["surface"]
            )

            self.speak_button.configure(
                bg=colors["speak"],
                activebackground=colors["speak_hover"]
            )

            self.read_button.configure(
                bg=colors["read"],
                activebackground=colors["read_hover"]
            )

            self.favorite_button.configure(
                bg=colors["favorite"],
                activebackground=colors["favorite_hover"]
            )

            self.learned_button.configure(
                bg=colors["learned"],
                activebackground=colors["learned_hover"]
            )

            self.note_button.configure(
                bg=colors["note"],
                activebackground=colors["note_hover"]
            )

            self.review_button.configure(
                bg=colors["review"],
                activebackground=colors["review_hover"]
            )

            self.clear_button.configure(
                bg=colors["clear"],
                activebackground=colors["clear_hover"]
            )

        # Home
        self.apply_recursive_page_theme(
            colors
        )

        # Update settings labels
        if hasattr(
            self,
            "settings_theme_label"
        ):

            self.settings_theme_label.configure(
                bg=colors["surface"],
                fg=colors["text"]
            )

            self.settings_theme_value.configure(
                bg=colors["surface"],
                fg=colors["secondary_text"],
                text=self.current_theme.title()
            )

            self.settings_voice_label.configure(
                bg=colors["surface"],
                fg=colors["secondary_text"],
                text=f"Voice: {self.saved_voice.title()}"
            )

            self.settings_language_label.configure(
                bg=colors["surface"],
                fg=colors["secondary_text"],
                text=f"Language: {self.language_label}"
            )

        self.update_progress()

    def apply_recursive_page_theme(
        self,
        colors
    ):

        for page in self.pages.values():

            self.theme_widget_tree(
                page,
                colors
            )

    def theme_widget_tree(
        self,
        widget,
        colors
    ):

        try:

            if isinstance(
                widget,
                tk.Listbox
            ):

                widget.configure(
                    bg=colors["input"],
                    fg=colors["text"],
                    selectbackground=colors["button_hover"],
                    selectforeground=colors["text"]
                )

            elif isinstance(
                widget,
                tk.Entry
            ):

                widget.configure(
                    bg=colors["input"],
                    fg=colors["text"],
                    insertbackground=colors["text"],
                    highlightbackground=colors["border"],
                    highlightcolor=colors["accent"]
                )

            elif isinstance(
                widget,
                tk.Button
            ):

                # Don't override special action buttons.
                current_text = widget.cget(
                    "text"
                )

                if (
                    current_text
                    not in {
                        "🔎 Search",
                        "🔊",
                        "▶",
                        "★",
                        "×",
                        "✓",
                        "📝",
                        "🔄",
                        "🔊 Play Pronunciation",
                        "▶ Read Aloud",
                        "⏹ Stop"
                    }
                ):

                    widget.configure(
                        bg=colors["button"],
                        fg=colors["text"],
                        activebackground=colors["button_hover"],
                        activeforeground=colors["text"]
                    )

            elif isinstance(
                widget,
                tk.Label
            ):

                current_bg = widget.cget(
                    "bg"
                )

                # Keep image/input surfaces intact.
                if current_bg not in {
                    "#EAFBFF",
                    "#2A2A2A"
                }:

                    widget.configure(
                        bg=colors["background"],
                        fg=colors["text"]
                    )

            elif isinstance(
                widget,
                tk.Frame
            ):

                widget.configure(
                    bg=colors["background"]
                )

        except tk.TclError:
            pass

        for child in widget.winfo_children():

            self.theme_widget_tree(
                child,
                colors
            )

        # Restore important surface cards.
        self.restore_surface_widgets(
            colors
        )

    def restore_surface_widgets(
        self,
        colors
    ):

        widgets = [
            getattr(
                self,
                "result_frame",
                None
            ),
            getattr(
                self,
                "meaning_frame",
                None
            ),
            getattr(
                self,
                "side_panel",
                None
            ),
            getattr(
                self,
                "action_frame",
                None
            ),
            getattr(
                self,
                "home_word_card",
                None
            ),
            getattr(
                self,
                "learn_word_card",
                None
            )
        ]

        for widget in widgets:

            if widget is not None:

                try:
                    widget.configure(
                        bg=colors["surface"]
                    )
                except tk.TclError:
                    pass

    # ========================================================
    # CLOSE
    # ========================================================

    def on_close(self):

        try:

            self.speech_engine.stop()

        except Exception:
            pass

        try:

            geometry = self.root.geometry()

            self.settings_manager.set(
                "window_geometry",
                geometry
            )

        except Exception as error:

            print(
                f"Geometry save error: {error}"
            )

        try:

            self.root.destroy()

        except tk.TclError:
            pass

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        self.root.mainloop()
        

        