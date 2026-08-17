"""
Settings Window for Audio Dictionary
Handles voice selection, dark mode, and about information
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class SettingsWindow:
    """Professional settings interface with voice, theme, and about sections"""
    
    def __init__(self, parent: tk.Tk, settings_manager, speech_engine, apply_callback: Optional[Callable] = None):
        self.parent = parent
        self.settings_manager = settings_manager
        self.speech_engine = speech_engine
        self.apply_callback = apply_callback
        self.window = None
        self.current_voice = settings_manager.get("voice", "female")
        self.dark_mode = settings_manager.get("dark_mode", False)
    
    def open(self):
        """Open the settings window"""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("⚙️ Settings")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Set initial theme
        self._apply_theme()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_voice_tab()
        self._create_theme_tab()
        self._create_about_tab()
        
        # Button frame
        button_frame = tk.Frame(self.window, bg=self._get_bg_color())
        button_frame.pack(fill="x", padx=10, pady=10)
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Save & Close",
            bg="#1E4A73",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._save_and_close
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="✕ Close",
            bg="#7A2E3B",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.window.destroy
        )
        cancel_btn.pack(side="left", padx=5)
    
    def _create_voice_tab(self):
        """Create voice selection tab"""
        voice_frame = tk.Frame(self.notebook, bg=self._get_bg_color())
        self.notebook.add(voice_frame, text="🔊 Voice")
        
        # Title
        title = tk.Label(
            voice_frame,
            text="Text-to-Speech Voice Selection",
            font=("Arial", 14, "bold"),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        title.pack(pady=15, padx=20)
        
        # Description
        description = tk.Label(
            voice_frame,
            text="Choose the voice type for text-to-speech features:",
            font=("Arial", 10),
            bg=self._get_bg_color(),
            fg=self._get_fg_color(),
            wraplength=400,
            justify="left"
        )
        description.pack(padx=20, pady=(0, 20))
        
        # Voice options
        self.voice_var = tk.StringVar(value=self.current_voice)
        
        voices = [
            ("👩 Female Voice", "female", "Default female voice for speech synthesis"),
            ("👨 Male Voice", "male", "Deep male voice for speech synthesis"),
            ("👧 Child Voice", "child", "Younger voice for speech synthesis"),
        ]
        
        for voice_label, voice_value, description_text in voices:
            frame = tk.Frame(voice_frame, bg=self._get_bg_color())
            frame.pack(fill="x", padx=30, pady=10)
            
            radio = tk.Radiobutton(
                frame,
                text=voice_label,
                variable=self.voice_var,
                value=voice_value,
                bg=self._get_bg_color(),
                fg=self._get_fg_color(),
                selectcolor=self._get_accent_color(),
                font=("Arial", 11),
                command=lambda v=voice_value: self._preview_voice(v)
            )
            radio.pack(anchor="w")
            
            desc_label = tk.Label(
                frame,
                text=description_text,
                bg=self._get_bg_color(),
                fg=self._get_secondary_fg_color(),
                font=("Arial", 9),
                justify="left"
            )
            desc_label.pack(anchor="w", padx=(25, 0), pady=(0, 5))
        
        # Preview button
        preview_btn = tk.Button(
            voice_frame,
            text="🔊 Test Voice",
            bg="#2E6B43",
            fg="white",
            font=("Arial", 10),
            relief="flat",
            cursor="hand2",
            command=self._test_voice
        )
        preview_btn.pack(pady=20)
    
    def _create_theme_tab(self):
        """Create theme/appearance tab"""
        theme_frame = tk.Frame(self.notebook, bg=self._get_bg_color())
        self.notebook.add(theme_frame, text="🎨 Appearance")
        
        # Title
        title = tk.Label(
            theme_frame,
            text="Application Theme",
            font=("Arial", 14, "bold"),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        title.pack(pady=15, padx=20)
        
        # Dark mode toggle
        toggle_frame = tk.Frame(theme_frame, bg=self._get_bg_color())
        toggle_frame.pack(fill="x", padx=30, pady=20)
        
        toggle_label = tk.Label(
            toggle_frame,
            text="🌙 Dark Mode",
            font=("Arial", 12, "bold"),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        toggle_label.pack(side="left", padx=(0, 20))
        
        self.dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        toggle_switch = tk.Checkbutton(
            toggle_frame,
            variable=self.dark_mode_var,
            bg=self._get_bg_color(),
            activebackground=self._get_bg_color(),
            cursor="hand2",
            font=("Arial", 10),
            command=self._toggle_dark_mode
        )
        toggle_switch.pack(side="left")
        
        # Info text
        info_text = tk.Label(
            theme_frame,
            text="Dark mode provides a comfortable viewing experience in low-light environments.",
            font=("Arial", 9),
            bg=self._get_bg_color(),
            fg=self._get_secondary_fg_color(),
            wraplength=400,
            justify="left"
        )
        info_text.pack(padx=30, pady=(10, 0))
        
        # Theme preview
        preview_label = tk.Label(
            theme_frame,
            text="Theme Preview",
            font=("Arial", 12, "bold"),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        preview_label.pack(pady=(30, 10), padx=20)
        
        preview_box = tk.Frame(
            theme_frame,
            bg=self._get_preview_bg(),
            relief="solid",
            bd=1,
            height=150
        )
        preview_box.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        preview_text = tk.Label(
            preview_box,
            text="This is how your interface will look",
            bg=self._get_preview_bg(),
            fg=self._get_preview_fg(),
            font=("Arial", 11)
        )
        preview_text.pack(pady=30)
    
    def _create_about_tab(self):
        """Create about section"""
        about_frame = tk.Frame(self.notebook, bg=self._get_bg_color())
        self.notebook.add(about_frame, text="ℹ️ About")
        
        # Scroll frame for content
        canvas = tk.Canvas(about_frame, bg=self._get_bg_color(), highlightthickness=0)
        scrollbar = ttk.Scrollbar(about_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self._get_bg_color())
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # App title
        app_title = tk.Label(
            scrollable_frame,
            text="🎵 Audio Dictionary",
            font=("Arial", 16, "bold"),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        app_title.pack(pady=15)
        
        version = tk.Label(
            scrollable_frame,
            text="Version 1.0.0",
            font=("Arial", 10),
            bg=self._get_bg_color(),
            fg=self._get_secondary_fg_color()
        )
        version.pack()
        
        # Separator
        sep1 = tk.Frame(scrollable_frame, height=2, bg=self._get_accent_color())
        sep1.pack(fill="x", padx=20, pady=15)
        
        # Author section
        author_title = tk.Label(
            scrollable_frame,
            text="👨‍💻 Author",
            font=("Arial", 12, "bold"),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        author_title.pack(anchor="w", padx=20, pady=(10, 5))
        
        author_name = tk.Label(
            scrollable_frame,
            text="GBEMU JOSEPH ANANI",
            font=("Arial", 11),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        author_name.pack(anchor="w", padx=40, pady=2)
        
        # Separator
        sep2 = tk.Frame(scrollable_frame, height=2, bg=self._get_accent_color())
        sep2.pack(fill="x", padx=20, pady=15)
        
        # Inspiration section
        inspiration_title = tk.Label(
            scrollable_frame,
            text="💡 Inspiration & Purpose",
            font=("Arial", 12, "bold"),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        inspiration_title.pack(anchor="w", padx=20, pady=(10, 5))
        
        inspiration_text = tk.Label(
            scrollable_frame,
            text=(
                "Audio Dictionary was created to bridge the gap between traditional "
                "text-based dictionaries and modern audio learning methods. "
                "The inspiration came from the recognition that many language learners "
                "benefit greatly from hearing pronunciations and definitions read aloud.\n\n"
                "Key motivations behind this project:\n"
                "• Enhance pronunciation learning through audio feedback\n"
                "• Make dictionary exploration engaging with visual references\n"
                "• Support multiple learning styles (visual, auditory, reading)\n"
                "• Provide accessibility features for users with visual impairments\n"
                "• Create a clean, intuitive interface for all user levels\n\n"
                "Whether you're learning English, teaching pronunciation, or simply "
                "curious about word meanings, Audio Dictionary aims to make the "
                "learning experience enjoyable and effective."
            ),
            font=("Arial", 10),
            bg=self._get_bg_color(),
            fg=self._get_fg_color(),
            wraplength=420,
            justify="left"
        )
        inspiration_text.pack(padx=20, pady=10)
        
        # Separator
        sep3 = tk.Frame(scrollable_frame, height=2, bg=self._get_accent_color())
        sep3.pack(fill="x", padx=20, pady=15)
        
        # Features section
        features_title = tk.Label(
            scrollable_frame,
            text="✨ Key Features",
            font=("Arial", 12, "bold"),
            bg=self._get_bg_color(),
            fg=self._get_fg_color()
        )
        features_title.pack(anchor="w", padx=20, pady=(10, 5))
        
        features_text = tk.Label(
            scrollable_frame,
            text=(
                "🔍 Comprehensive word search\n"
                "🔊 Professional pronunciation guides\n"
                "📖 Text-to-speech with voice selection\n"
                "🖼️ Visual references from Wikimedia\n"
                "📜 Search history tracking\n"
                "⭐ Favorites management\n"
                "🎨 Dark mode support\n"
                "🌐 Works without internet dependencies"
            ),
            font=("Arial", 10),
            bg=self._get_bg_color(),
            fg=self._get_fg_color(),
            justify="left"
        )
        features_text.pack(padx=20, pady=10)
        
        # Separator
        sep4 = tk.Frame(scrollable_frame, height=2, bg=self._get_accent_color())
        sep4.pack(fill="x", padx=20, pady=15)
        
        # Footer
        footer = tk.Label(
            scrollable_frame,
            text="Made with ❤️ for language learners worldwide",
            font=("Arial", 9, "italic"),
            bg=self._get_bg_color(),
            fg=self._get_secondary_fg_color()
        )
        footer.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def _preview_voice(self, voice):
        """Preview selected voice"""
        self.speech_engine.set_voice(voice)
    
    def _test_voice(self):
        """Test the selected voice"""
        voice = self.voice_var.get()
        self.speech_engine.set_voice(voice)
        test_text = f"This is the {voice} voice."
        self.speech_engine.speak(test_text)
    
    def _toggle_dark_mode(self):
        """Toggle dark mode preview"""
        self.dark_mode = self.dark_mode_var.get()
        # Refresh colors in all tabs
        self._refresh_colors()
    
    def _refresh_colors(self):
        """Refresh all colors based on current theme"""
        # Re-create frames with new colors
        for tab in self.notebook.winfo_children():
            tab.configure(bg=self._get_bg_color())
            self._update_widget_colors(tab)
    
    def _update_widget_colors(self, widget):
        """Recursively update widget colors"""
        try:
            if isinstance(widget, tk.Label):
                widget.configure(bg=self._get_bg_color(), fg=self._get_fg_color())
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=self._get_bg_color())
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(bg=self._get_bg_color(), fg=self._get_fg_color(),
                               activebackground=self._get_bg_color())
            
            for child in widget.winfo_children():
                self._update_widget_colors(child)
        except:
            pass
    
    def _apply_theme(self):
        """Apply theme to window"""
        bg = self._get_bg_color()
        self.window.configure(bg=bg)
    
    def _get_bg_color(self) -> str:
        """Get background color based on theme"""
        return "#1e1e1e" if self.dark_mode else "#BFEAF5"
    
    def _get_fg_color(self) -> str:
        """Get foreground color based on theme"""
        return "#e0e0e0" if self.dark_mode else "#0F2E3D"
    
    def _get_secondary_fg_color(self) -> str:
        """Get secondary foreground color"""
        return "#a0a0a0" if self.dark_mode else "#123B4A"
    
    def _get_accent_color(self) -> str:
        """Get accent color based on theme"""
        return "#1E4A73" if self.dark_mode else "#1E4A73"
    
    def _get_preview_bg(self) -> str:
        """Get preview box background"""
        return "#2d2d2d" if self.dark_mode else "#D7F3FF"
    
    def _get_preview_fg(self) -> str:
        """Get preview text foreground"""
        return "#e0e0e0" if self.dark_mode else "#123B4A"
    
    def _save_and_close(self):
        """Save settings and close window"""
        # Save voice setting
        voice = self.voice_var.get()
        self.settings_manager.set("voice", voice)
        self.speech_engine.set_voice(voice)
        
        # Save dark mode setting
        dark_mode = self.dark_mode_var.get()
        self.settings_manager.set("dark_mode", dark_mode)
        
        # Call the apply callback if provided
        if self.apply_callback:
            self.apply_callback({"voice": voice, "dark_mode": dark_mode})
        
        self.window.destroy()
