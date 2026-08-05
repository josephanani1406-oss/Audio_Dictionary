import io
import json
import os
import re
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from urllib.request import Request, urlopen

from controller import DictionaryController
from history import HistoryManager
from speech import SpeechEngine


class AudioDictionaryGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Dictionary")
        self.root.geometry("900x640")
        self.root.configure(bg="#BFEAF5")
        self.root.resizable(False, False)

        self.controller = DictionaryController()
        self.history_manager = HistoryManager()
        self.speech_engine = SpeechEngine()
        self.current_theme = "light"
        self.current_language = "en"
        self.language_label = "English"

        # Stores the pronunciation audio URL
        self.audio_url = ""
        self.word_image = None
        self.current_read_text = ""
        self.read_running = False
        self.read_schedule_id = None
        self.read_ranges = []
        self.read_index = 0
        self.fallback_image_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "word_placeholder.png"
        )

        self.create_widgets()

    def create_widgets(self):
        # Heading
        heading = tk.Label(
            self.root,
            text="Audio Dictionary",
            font=("Arial", 22, "bold"),
            bg="#BFEAF5",
            fg="#0F2E3D"
        )
        heading.pack(pady=15)

        # Search label
        search_label = tk.Label(
            self.root,
            text="Enter a word:",
            font=("Arial", 12),
            bg="#BFEAF5",
            fg="#123B4A"
        )
        search_label.pack(anchor="w", padx=35)

        search_frame = tk.Frame(self.root, bg="#BFEAF5")
        search_frame.pack(fill="x", padx=30, pady=(6, 10))

        self.word_entry = tk.Entry(
            search_frame,
            width=38,
            font=("Arial", 14),
            bg="#EAFBFF",
            fg="#123B4A",
            insertbackground="#123B4A",
            highlightbackground="#7DB9C9",
            highlightthickness=1
        )
        self.word_entry.pack(side="left", expand=True, fill="x")
        self.word_entry.bind("<Return>", lambda event: self.search_word())

        self.search_btn = tk.Button(
            search_frame,
            text="Search",
            width=12,
            bg="#1E4A73",
            fg="white",
            font=("Arial", 11),
            bd=0,
            relief="flat",
            highlightbackground="#5B5B5B",
            highlightthickness=1,
            activebackground="#163A59",
            activeforeground="white",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.search_word
        )
        self.search_btn.pack(side="left", padx=(10, 0))

        self.sidebar = tk.Frame(self.root, bg="#BFEAF5")
        self.sidebar.pack(pady=(0, 8))

        self.history_button = tk.Button(
            self.sidebar,
            text="History",
            width=14,
            bg="#8BB9D0",
            fg="#123B4A",
            font=("Arial", 10, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.toggle_history_panel
        )
        self.history_button.grid(row=0, column=0, padx=8, pady=(0, 6))

        self.favorite_button = tk.Button(
            self.sidebar,
            text="Favorites",
            width=14,
            bg="#8BB9D0",
            fg="#123B4A",
            font=("Arial", 10, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.toggle_favorites_panel
        )
        self.favorite_button.grid(row=0, column=1, padx=8, pady=(0, 6))

        self.history_panel = None
        self.favorite_panel = None

        result_frame = tk.Frame(
            self.root,
            bg="#D7F3FF",
            bd=1,
            relief="solid",
            highlightbackground="#7AB7C9",
            highlightthickness=1,
            padx=12,
            pady=12
        )
        result_frame.pack(fill="x", padx=30, pady=5)

        self.meaning_box = tk.Text(
            result_frame,
            width=60,
            height=15,
            font=("Arial", 11),
            wrap=tk.WORD,
            bg="#D7F3FF",
            fg="#123B4A",
            insertbackground="#123B4A",
            bd=0,
            relief="flat",
            padx=8,
            pady=8
        )
        self.meaning_box.tag_configure("reading", background="#D9F1FF", foreground="#123B4A")
        self.meaning_box.pack(side="left", fill="y")

        side_panel = tk.Frame(result_frame, bg="#D7F3FF")
        side_panel.pack(side="left", padx=(18, 0), fill="y")

        self.word_image_label = tk.Label(
            side_panel,
            width=24,
            height=12,
            bg="#EAFBFF",
            fg="#123B4A",
            text="Word image",
            compound="center",
            anchor="center",
            justify="center",
            relief="solid",
            bd=1,
            padx=8,
            pady=8
        )

        self.word_image_label.configure(
            highlightbackground="#5A5A5A",
            highlightthickness=1
        )
        self.word_image_label.pack(pady=(0, 10))

        button_frame = tk.Frame(side_panel, bg="#D7F3FF")
        button_frame.pack()

        self.speak_button = tk.Button(
            button_frame,
            text="Pronounce",
            width=12,
            bg="#2E6B43",
            fg="white",
            font=("Arial", 11),
            bd=0,
            relief="flat",
            highlightbackground="#5B5B5B",
            highlightthickness=1,
            activebackground="#224F34",
            activeforeground="white",
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.pronounce_word
        )
        self.speak_button.grid(row=0, column=0, padx=4, pady=4)

        self.read_button = tk.Button(
            button_frame,
            text="Read",
            width=12,
            bg="#8A5A1E",
            fg="white",
            font=("Arial", 11),
            bd=0,
            relief="flat",
            highlightbackground="#5B5B5B",
            highlightthickness=1,
            activebackground="#6D4518",
            activeforeground="white",
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.read_word
        )
        self.read_button.grid(row=0, column=1, padx=4, pady=4)

        self.favorite_button = tk.Button(
            button_frame,
            text="Favorite",
            width=12,
            bg="#4F3C74",
            fg="white",
            font=("Arial", 11),
            bd=0,
            relief="flat",
            highlightbackground="#5B5B5B",
            highlightthickness=1,
            activebackground="#3D2D5A",
            activeforeground="white",
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.favorite_current_word
        )
        self.favorite_button.grid(row=1, column=0, padx=4, pady=4)

        self.clear_button = tk.Button(
            button_frame,
            text="Clear",
            width=12,
            bg="#7A2E3B",
            fg="white",
            font=("Arial", 11),
            bd=0,
            relief="flat",
            highlightbackground="#5B5B5B",
            highlightthickness=1,
            activebackground="#5D1F2B",
            activeforeground="white",
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.clear_search
        )
        self.clear_button.grid(row=1, column=1, padx=4, pady=4)

        self.status = tk.Label(
            self.root,
            text="Ready",
            bg="#BFEAF5",
            fg="#0B5F3A",
            font=("Arial", 10)
        )
        self.status.pack(pady=(6, 0))

    def search_word(self):

        word = self.word_entry.get().strip()

        if not word:
            messagebox.showwarning(
                "Input Required",
                "Please enter a word."
            )
            return

        self.status.config(text="Searching...")

        result = self.controller.search(word)

        self.meaning_box.delete("1.0", tk.END)

        if not result["success"]:
            self.meaning_box.insert(
                tk.END,
                result["message"]
            )
            self.status.config(text="Search failed")
            return

        self.audio_url = result.get("audio", "")

        self.meaning_box.insert(
            tk.END,
            f"WORD: {result['word']}\n"
        )

        self.meaning_box.insert(
            tk.END,
            f"PHONETIC: {result.get('phonetic') or 'N/A'}\n\n"
        )

        if not result.get("meanings"):
            self.meaning_box.insert(
                tk.END,
                "No definitions available for this word."
            )
            self.status.config(text="No definitions found")
            return

        for meaning in result["meanings"]:

            self.meaning_box.insert(
                tk.END,
                f"Part of Speech: {meaning['partOfSpeech']}\n"
            )

            self.meaning_box.insert(
                tk.END,
                "-" * 45 + "\n"
            )

            for definition in meaning["definitions"]:

                self.meaning_box.insert(
                    tk.END,
                    f"• {definition['definition']}\n"
                )

                if definition["example"]:
                    self.meaning_box.insert(
                        tk.END,
                        f"Example: {definition['example']}\n"
                    )

                self.meaning_box.insert(tk.END, "\n")

            if meaning["synonyms"]:
                self.meaning_box.insert(
                    tk.END,
                    "Synonyms:\n"
                )

                self.meaning_box.insert(
                    tk.END,
                    ", ".join(meaning["synonyms"][:10])
                )

                self.meaning_box.insert(
                    tk.END,
                    "\n\n"
                )

            if meaning["antonyms"]:
                self.meaning_box.insert(
                    tk.END,
                    "Antonyms:\n"
                )

                self.meaning_box.insert(
                    tk.END,
                    ", ".join(meaning["antonyms"][:10])
                )

                self.meaning_box.insert(
                    tk.END,
                    "\n\n"
                )

        self.current_read_text = self.build_read_aloud_text(result)
        self.status.config(text="Search completed")
        self.load_word_image(result["word"])
        self.history_manager.add_search(result["word"])
        self.refresh_history()

    def pronounce_word(self):
        if not self.audio_url:
            messagebox.showinfo(
                "Pronunciation",
                "No pronunciation audio available for this word."
            )
            return

        success = self.controller.pronounce(self.audio_url)
        if not success:
            messagebox.showerror(
                "Error",
                "Unable to play pronunciation."
            )

    def build_read_aloud_text(self, result):
        word = (result.get("word") or "").strip()
        if not word:
            return ""

        sections = [f"The word is {word}."]

        for meaning in result.get("meanings", []):
            for definition in meaning.get("definitions", []):
                definition_text = (definition.get("definition") or "").strip()
                if definition_text:
                    sections.append(f"Meaning: {definition_text}.")

                example = (definition.get("example") or "").strip()
                if example:
                    sections.append(f"Example: {example}.")

            synonyms = meaning.get("synonyms") or []
            if synonyms:
                sections.append(f"Synonyms include {', '.join(synonyms[:5])}.")

            antonyms = meaning.get("antonyms") or []
            if antonyms:
                sections.append(f"Antonyms include {', '.join(antonyms[:5])}.")

        return " ".join(sections)

    def read_word(self):
        word = self.word_entry.get().strip()
        if not word:
            messagebox.showinfo(
                "Read",
                "Enter a word before using the read feature."
            )
            return

        if self.read_running:
            return

        self.read_running = True
        self.meaning_box.tag_remove("reading", "1.0", tk.END)

        text_to_read = self.current_read_text or self.build_read_aloud_text(self.controller.search(word))
        if not text_to_read:
            self.status.config(text="No text to read")
            self.read_running = False
            return

        self.status.config(text="Reading naturally")

        if self.speech_engine.speak(text_to_read):
            self.status.config(text="Read complete")
        else:
            self.status.config(text="Speech unavailable")

        self.read_running = False

    def favorite_current_word(self):
        word = self.word_entry.get().strip()
        if not word:
            messagebox.showinfo(
                "Favorite",
                "Enter a word before saving it as a favorite."
            )
            return

        self.history_manager.add_favorite(word)
        self.refresh_favorites()
        self.status.config(text=f"Saved '{word}' to favorites")

    def clear_search(self):
        self.word_entry.delete(0, tk.END)
        self.meaning_box.delete("1.0", tk.END)
        self.audio_url = ""
        self.word_image = None
        self.current_read_text = ""
        self.word_image_label.configure(image="", text="Word image")
        self.status.config(text="Cleared")

    def load_word_image(self, word):
        self.word_image_label.configure(text="Loading image...")
        try:
            from PIL import Image, ImageTk
        except ImportError:
            self.set_local_image(self.fallback_image_path)
            return

        try:
            query = word.strip()
            if not query:
                raise ValueError("Empty word")

            search_url = (
                "https://commons.wikimedia.org/w/api.php?"
                "action=query&generator=search&gsrsearch=" + query +
                "&gsrnamespace=6&gsrlimit=1&prop=imageinfo&"
                "iiprop=url&iiurlwidth=300&format=json&origin=*"
            )
            request = Request(search_url, headers={"User-Agent": "AudioDictionary/1.0"})
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))

            pages = payload.get("query", {}).get("pages", {})
            image_info = None
            for page in pages.values():
                image_info = page.get("imageinfo", [{}])[0]
                if image_info:
                    break

            if not image_info:
                raise ValueError("No Wikimedia image found")

            image_url = image_info.get("thumburl") or image_info.get("url")
            if not image_url:
                raise ValueError("No Wikimedia image URL")

            with urlopen(Request(image_url, headers={"User-Agent": "AudioDictionary/1.0"}), timeout=10) as response:
                image_data = response.read()

            if not image_data:
                raise ValueError("No image data returned")

            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            image = image.resize(
                (220, 150),
                Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
            )
            self.word_image = ImageTk.PhotoImage(image)
            self.word_image_label.configure(image=self.word_image, text="")
        except Exception:
            self.set_local_image(self.fallback_image_path)

    def set_local_image(self, image_path):
        try:
            from PIL import Image, ImageTk

            if not os.path.exists(image_path):
                self.word_image_label.configure(image="", text="Image unavailable")
                return

            image = Image.open(image_path).convert("RGB")
            image = image.resize((220, 150), Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS)
            self.word_image = ImageTk.PhotoImage(image)
            self.word_image_label.configure(image=self.word_image, text="")
        except Exception:
            self.word_image_label.configure(image="", text="Image unavailable")

    def refresh_history(self):
        if self.history_panel is not None:
            history_listbox = self.history_panel.winfo_children()[0].winfo_children()[0]
            history_listbox.delete(0, tk.END)
            for word in self.history_manager.get_history():
                history_listbox.insert(tk.END, word)

    def refresh_favorites(self):
        if self.favorite_panel is not None:
            favorite_listbox = self.favorite_panel.winfo_children()[0].winfo_children()[0]
            favorite_listbox.delete(0, tk.END)
            for word in self.history_manager.get_favorites():
                favorite_listbox.insert(tk.END, word)

    def create_word_list_panel(self, title, data_source):
        panel = tk.Toplevel(self.root)
        panel.title(title)
        panel.geometry("260x260")
        panel.configure(bg="#D7F3FF")
        panel.transient(self.root)
        panel.grab_set()

        container = tk.Frame(panel, bg="#D7F3FF", padx=12, pady=12)
        container.pack(fill="both", expand=True)

        listbox = tk.Listbox(
            container,
            width=28,
            height=12,
            bg="#EAFBFF",
            fg="#123B4A",
            selectbackground="#B8E6F4",
            bd=1,
            relief="solid",
            highlightthickness=0,
            font=("Arial", 10)
        )
        listbox.pack(fill="both", expand=True, pady=(0, 8))

        for word in data_source():
            listbox.insert(tk.END, word)

        close_button = tk.Button(
            container,
            text="Close",
            width=12,
            bg="#7A2E3B",
            fg="white",
            font=("Arial", 10),
            bd=0,
            relief="flat",
            command=panel.destroy
        )
        close_button.pack()

        def on_select(event):
            selection = listbox.curselection()
            if not selection:
                return
            selected_word = listbox.get(selection[0])
            self.word_entry.delete(0, tk.END)
            self.word_entry.insert(0, selected_word)
            self.search_word()
            panel.destroy()

        listbox.bind("<<ListboxSelect>>", on_select)
        return panel

    def toggle_history_panel(self):
        if self.history_panel is None or not self.history_panel.winfo_exists():
            self.history_panel = self.create_word_list_panel("History", self.history_manager.get_history)
        else:
            self.history_panel.destroy()
            self.history_panel = None

    def toggle_favorites_panel(self):
        if self.favorite_panel is None or not self.favorite_panel.winfo_exists():
            self.favorite_panel = self.create_word_list_panel("Favorites", self.history_manager.get_favorites)
        else:
            self.favorite_panel.destroy()
            self.favorite_panel = None

    def load_history_selection(self, event):
        return

    def load_favorite_selection(self, event):
        return

    def run(self):
        self.root.mainloop()


