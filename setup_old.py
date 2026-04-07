#!/usr/bin/env python3

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from config import ConfigManager


# Dutch translations
TEXTS = {
    "title": "HappyFrame Configuratie",
    "word_label": "Woord/opdracht:",
    "add_word": "Woord Toevoegen",
    "add_images": "➕ Afbeeldingen Toevoegen",
    "add_sounds": "➕ Geluiden Toevoegen",
    "remove_selected": "Verwijder Geselecteerd",
    "save_close": "Opslaan & Sluiten",
    "cancel": "Annuleren",
    "image_label": "Afbeeldingen",
    "sound_label": "Geluiden",
    "configured_words": "Geconfigureerde woorden:",
    "error_word": "Fout: Voer eerst een woord in",
    "error_images": "Fout: Voeg minstens één afbeelding toe",
    "error_sounds": "Fout: Voeg minstens één geluid toe",
    "success": "Succes",
    "success_saved": "Configuratie opgeslagen!",
    "warning": "Waarschuwing",
    "warning_no_config": "Geen woorden geconfigureerd. Setup opnieuw starten.",
    "confirm_delete": "Bevestiging",
    "delete_confirm": "Woord verwijderen: '{}'?",
    "image_types": "Afbeeldingen",
    "audio_types": "Audio",
}


class SetupGUI:
    """Simplified setup wizard for HappyFrame"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.config_manager = ConfigManager(base_dir)
        self.current_word = ""
        self.current_images = []
        self.current_sounds = []
        
        self.root = tk.Tk()
        self.root.title(TEXTS["title"])
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the simplified GUI widgets"""
        
        # Title
        title = tk.Label(self.root, text=TEXTS["title"], 
                        font=("Arial", 18, "bold"), bg="#f0f0f0")
        title.pack(pady=10)
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Word management
        left_frame = tk.LabelFrame(main_frame, text=TEXTS["configured_words"], 
                                   font=("Arial", 12, "bold"),
                                   bg="#f0f0f0", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Word input
        word_frame = tk.Frame(left_frame, bg="#f0f0f0")
        word_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(word_frame, text=TEXTS["word_label"], bg="#f0f0f0").pack(side=tk.LEFT)
        self.word_entry = tk.Entry(word_frame, width=20, font=("Arial", 12))
        self.word_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(word_frame, text=TEXTS["add_word"], 
                 command=self.add_word).pack(side=tk.LEFT)
        
        # Word list
        self.word_listbox = tk.Listbox(left_frame, height=15, width=25, font=("Arial", 10))
        self.word_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.word_listbox.bind('<<ListboxSelect>>', self.on_word_select)
        
        tk.Button(left_frame, text=TEXTS["remove_selected"], 
                 command=self.delete_word).pack(fill=tk.X, pady=5)
        
        # Right panel - Content
        right_frame = tk.LabelFrame(main_frame, text="Content", 
                                    font=("Arial", 12, "bold"),
                                    bg="#f0f0f0", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Images section
        img_frame = tk.LabelFrame(right_frame, text=TEXTS["image_label"], 
                                 bg="#f0f0f0", padx=5, pady=5)
        img_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(img_frame, text=TEXTS["add_images"], 
                 command=self.add_images).pack(side=tk.TOP, padx=2, pady=2)
        
        self.images_listbox = tk.Listbox(img_frame, height=8, font=("Arial", 9))
        self.images_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(img_frame, text=TEXTS["remove_selected"], 
                 command=self.remove_image).pack(side=tk.TOP, padx=2)
        
        # Sounds section
        snd_frame = tk.LabelFrame(right_frame, text=TEXTS["sound_label"], 
                                 bg="#f0f0f0", padx=5, pady=5)
        snd_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(snd_frame, text=TEXTS["add_sounds"], 
                 command=self.add_sounds).pack(side=tk.TOP, padx=2, pady=2)
        
        self.sounds_listbox = tk.Listbox(snd_frame, height=8, font=("Arial", 9))
        self.sounds_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(snd_frame, text=TEXTS["remove_selected"], 
                 command=self.remove_sound).pack(side=tk.TOP, padx=2)
        
        # Bottom buttons
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(bottom_frame, text=TEXTS["save_close"], command=self.save_and_close,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 padx=20, pady=10).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(bottom_frame, text=TEXTS["cancel"], command=self.root.quit,
                 bg="#f44336", fg="white", font=("Arial", 12, "bold"),
                 padx=20, pady=10).pack(side=tk.RIGHT, padx=5)
        
        self.load_words()
    
    def load_words(self):
        """Load existing words into the listbox"""
        self.word_listbox.delete(0, tk.END)
        config = self.config_manager.load_config()
        if config and config.get("triggers"):
            for trigger in config["triggers"]:
                self.word_listbox.insert(tk.END, trigger["id"])
    
    def add_word(self):
        """Add a new word"""
        word = self.word_entry.get().strip().lower()
        if not word:
            messagebox.showwarning(TEXTS["error_word"], TEXTS["error_word"])
            return
        
        # Check if word already exists
        config = self.config_manager.load_config()
        if config and config.get("triggers"):
            for trigger in config["triggers"]:
                if trigger["id"] == word:
                    messagebox.showwarning("Woord bestaat al", f"Woord '{word}' bestaat al!")
                    return
        
        self.current_word = word
        self.current_images = []
        self.current_sounds = []
        self.word_entry.delete(0, tk.END)
        self.update_content_display()
        self.load_words()
    
    def on_word_select(self, event):
        """Load selected word content"""
        selection = self.word_listbox.curselection()
        if not selection:
            return
        
        word = self.word_listbox.get(selection[0])
        config = self.config_manager.load_config()
        
        if config and config.get("triggers"):
            for trigger in config["triggers"]:
                if trigger["id"] == word:
                    self.current_word = word
                    self.current_images = trigger.get("images", [])
                    self.current_sounds = trigger.get("sounds", [])
                    self.update_content_display()
                    break
    
    def update_content_display(self):
        """Update the images and sounds listboxes"""
        self.images_listbox.delete(0, tk.END)
        for img in self.current_images:
            self.images_listbox.insert(tk.END, img)
        
        self.sounds_listbox.delete(0, tk.END)
        for snd in self.current_sounds:
            self.sounds_listbox.insert(tk.END, snd)
    
    def add_images(self):
        """Add images to current word"""
        if not self.current_word:
            messagebox.showwarning(TEXTS["error_word"], TEXTS["error_word"])
            return
        
        files = filedialog.askopenfilenames(
            title=TEXTS["image_types"],
            filetypes=[(TEXTS["image_types"], "*.jpg *.jpeg *.png *.bmp *.gif"),
                      ("Alle Bestanden", "*.*")]
        )
        
        for file in files:
            filename = self.config_manager.copy_file_to_project(
                file, self.config_manager.images_dir
            )
            if filename and filename not in self.current_images:
                self.current_images.append(filename)
        
        self.update_content_display()
    
    def add_sounds(self):
        """Add sounds to current word"""
        if not self.current_word:
            messagebox.showwarning(TEXTS["error_word"], TEXTS["error_word"])
            return
        
        files = filedialog.askopenfilenames(
            title=TEXTS["audio_types"],
            filetypes=[(TEXTS["audio_types"], "*.ogg *.wav *.mp3 *.flac"),
                      ("Alle Bestanden", "*.*")]
        )
        
        for file in files:
            filename = self.config_manager.copy_file_to_project(
                file, self.config_manager.sounds_dir
            )
            if filename and filename not in self.current_sounds:
                self.current_sounds.append(filename)
        
        self.update_content_display()
    
    def remove_image(self):
        """Remove selected image"""
        selection = self.images_listbox.curselection()
        if selection:
            self.current_images.pop(selection[0])
            self.update_content_display()
    
    def remove_sound(self):
        """Remove selected sound"""
        selection = self.sounds_listbox.curselection()
        if selection:
            self.current_sounds.pop(selection[0])
            self.update_content_display()
    
    def delete_word(self):
        """Delete selected word"""
        selection = self.word_listbox.curselection()
        if not selection:
            return
        
        word = self.word_listbox.get(selection[0])
        if messagebox.askyesno(TEXTS["confirm_delete"], 
                              TEXTS["delete_confirm"].format(word)):
            config = self.config_manager.load_config() or self.config_manager.create_default_config()
            config["triggers"] = [t for t in config["triggers"] if t["id"] != word]
            self.config_manager.save_config(config)
            self.load_words()
            self.current_word = ""
            self.current_images = []
            self.current_sounds = []
            self.update_content_display()
    
    def save_and_close(self):
        """Save current word and close"""
        if self.current_word:
            if not self.current_images:
                messagebox.showwarning(TEXTS["error_images"], TEXTS["error_images"])
                return
            
            if not self.current_sounds:
                messagebox.showwarning(TEXTS["error_sounds"], TEXTS["error_sounds"])
                return
            
            # Save with the word as both ID and phrase
            self.config_manager.add_trigger(
                self.current_word,
                self.current_images,
                self.current_sounds,
                [self.current_word]  # Use the word itself as the phrase
            )
        
        config = self.config_manager.load_config()
        if config and config.get("triggers"):
            messagebox.showinfo(TEXTS["success"], TEXTS["success_saved"])
            self.root.quit()
        else:
            messagebox.showwarning(TEXTS["warning"], TEXTS["warning_no_config"])
            self.root.quit()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


def run_setup(base_dir):
    """Run the setup GUI"""
    gui = SetupGUI(base_dir)
    gui.run()


if __name__ == "__main__":
    import sys
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    run_setup(base_dir)
        
        tk.Button(img_frame, text=TEXTS["remove_selected"], 
                 command=self.remove_image).pack(side=tk.LEFT, padx=2)
        
        # Sounds section
        snd_frame = tk.LabelFrame(right_frame, text=TEXTS["sound_label"], 
                                 bg="#f0f0f0", padx=5, pady=5)
        snd_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(snd_frame, text=TEXTS["add_phrase"], 
                 command=self.add_sounds).pack(side=tk.LEFT, padx=2)
        
        self.sounds_listbox = tk.Listbox(snd_frame, height=5)
        self.sounds_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(snd_frame, text=TEXTS["remove_selected"], 
                 command=self.remove_sound).pack(side=tk.LEFT, padx=2)
        
        # Voice phrases input section
        voice_frame = tk.LabelFrame(right_frame, 
                                    text=TEXTS["phrases_label"], 
                                    bg="#f0f0f0", padx=5, pady=5)
        voice_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.phrases_text = scrolledtext.ScrolledText(voice_frame, height=5, width=40)
        self.phrases_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom buttons
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(bottom_frame, text=TEXTS["save_close"], command=self.save_and_close,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 padx=20, pady=10).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(bottom_frame, text=TEXTS["cancel"], command=self.root.quit,
                 bg="#f44336", fg="white", font=("Arial", 12, "bold"),
                 padx=20, pady=10).pack(side=tk.RIGHT, padx=5)
        
        self.load_phrases()
    
    def load_phrases(self):
        """Load existing phrases into the listbox"""
        self.phrase_listbox.delete(0, tk.END)
        config = self.config_manager.load_config()
        if config and config.get("triggers"):
            for trigger in config["triggers"]:
                # Use the first phrase as display name
                first_phrase = trigger["phrases"][0] if trigger["phrases"] else trigger["id"]
                self.phrase_listbox.insert(tk.END, first_phrase)
    
    def add_images(self):
        """Add images to current phrase set"""
        if not self.current_trigger_id:
            messagebox.showwarning(TEXTS["error_select"], TEXTS["error_select"])
            return
        
        files = filedialog.askopenfilenames(
            title=TEXTS["select_images"],
            filetypes=[(TEXTS["image_types"], "*.jpg *.jpeg *.png *.bmp *.gif"),
                      ("All Files", "*.*")]
        )
        
        for file in files:
            filename = self.config_manager.copy_file_to_project(
                file, self.config_manager.images_dir
            )
            if filename and filename not in self.current_images:
                self.current_images.append(filename)
        
        self.update_content_display()
    
    def add_sounds(self):
        """Add sounds to current phrase set"""
        if not self.current_trigger_id:
            messagebox.showwarning(TEXTS["error_select"], TEXTS["error_select"])
            return
        
        files = filedialog.askopenfilenames(
            title=TEXTS["select_sounds"],
            filetypes=[(TEXTS["audio_types"], "*.ogg *.wav *.mp3 *.flac"),
                      ("All Files", "*.*")]
        )
        
        for file in files:
            filename = self.config_manager.copy_file_to_project(
                file, self.config_manager.sounds_dir
            )
            if filename and filename not in self.current_sounds:
                self.current_sounds.append(filename)
        
        self.update_content_display()
    
    def remove_image(self):
        """Remove selected image"""
        selection = self.images_listbox.curselection()
        if selection:
            self.current_images.pop(selection[0])
            self.update_content_display()
    
    def remove_sound(self):
        """Remove selected sound"""
        selection = self.sounds_listbox.curselection()
        if selection:
            self.current_sounds.pop(selection[0])
            self.update_content_display()
    
    def update_content_display(self):
        """Update the images and sounds listboxes"""
        self.images_listbox.delete(0, tk.END)
        for img in self.current_images:
            self.images_listbox.insert(tk.END, img)
        
        self.sounds_listbox.delete(0, tk.END)
        for snd in self.current_sounds:
            self.sounds_listbox.insert(tk.END, snd)
    
    def on_phrase_select(self, event):
        """Load selected phrase set"""
        selection = self.phrase_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.phrase_listbox.get(selection[0])
        config = self.config_manager.load_config()
        
        if config and config.get("triggers"):
            for trigger in config["triggers"]:
                # Find the trigger by checking if selected text is in its phrases
                if selected_text in trigger["phrases"] or trigger["id"] == selected_text:
                    self.current_trigger_id = trigger["id"]
                    self.current_images = trigger.get("images", [])
                    self.current_sounds = trigger.get("sounds", [])
                    self.current_phrases = trigger.get("phrases", [])
                    self.update_content_display()
                    self.phrases_text.delete(1.0, tk.END)
                    self.phrases_text.insert(tk.END, "\n".join(self.current_phrases))
                    break
    
    def delete_phrase(self):
        """Delete selected phrase set"""
        selection = self.phrase_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.phrase_listbox.get(selection[0])
        config = self.config_manager.load_config()
        
        trigger_to_delete = None
        if config and config.get("triggers"):
            for trigger in config["triggers"]:
                if selected_text in trigger["phrases"] or trigger["id"] == selected_text:
                    trigger_to_delete = trigger["id"]
                    break
        
        if not trigger_to_delete:
            return
        
        if messagebox.askyesno(TEXTS["confirm_delete"], 
                              TEXTS["delete_confirm"].format(selected_text)):
            config["triggers"] = [t for t in config["triggers"] if t["id"] != trigger_to_delete]
            self.config_manager.save_config(config)
            self.load_phrases()
            self.current_trigger_id = None
            self.current_images = []
            self.current_sounds = []
            self.current_phrases = []
            self.update_content_display()
            self.phrases_text.delete(1.0, tk.END)
    
    def save_and_close(self):
        """Save current phrase set and close"""
        phrases = [p.strip() for p in self.phrases_text.get(1.0, tk.END).split('\n') 
                  if p.strip()]
        
        if not phrases:
            messagebox.showwarning(TEXTS["error_input"], TEXTS["error_input"])
            return
        
        if not self.current_images or not self.current_sounds:
            messagebox.showwarning(TEXTS["error_incomplete"], 
                                  TEXTS["error_incomplete"])
            return
        
        # Use first phrase as trigger ID
        trigger_id = phrases[0].lower()
        
        self.config_manager.add_trigger(
            trigger_id,
            self.current_images,
            self.current_sounds,
            phrases
        )
        
        config = self.config_manager.load_config()
        if config and config.get("triggers"):
            messagebox.showinfo(TEXTS["success"], TEXTS["success_saved"])
            self.root.quit()
        else:
            messagebox.showwarning(TEXTS["warning"], TEXTS["warning_no_config"])
            self.root.quit()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


def run_setup(base_dir):
    """Run the setup GUI"""
    gui = SetupGUI(base_dir)
    gui.run()


if __name__ == "__main__":
    import sys
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    run_setup(base_dir)

