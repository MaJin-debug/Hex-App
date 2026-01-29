"""
main.py
Main entry point for HEX - Your Second Brain app
Version: 1.300X
"""

import os
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from kivymd.app import MDApp

from screens.splash_screen import SplashScreen
from screens.auth_screens import RegisterScreen, LoginScreen
from screens.chat_screen import ChatScreen
from screens.knowledge_screens import AddKnowledgeScreen, EditKnowledgeScreen
from screens.settings_screen import SettingsScreen
from screens.account_screen import AccountScreen
from screens.notes_screen import NotesScreen, NoteDetailScreen
from screens.gallery_screen import GalleryScreen, AddMemoryScreen

from utility import DATA_DIR

Window.orientation = 'portrait'
Window.softinput_mode = "below_target"

APP_VERSION = "1.300X"


class HexApp(MDApp):
    """Main HEX Application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.pending_teach_question = None
        self.pending_answer = None
        self.app_version = APP_VERSION
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M3"
    
    def build(self):
        # Ensure data directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        
        # Add all screens
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(AddKnowledgeScreen(name='add_knowledge'))
        sm.add_widget(EditKnowledgeScreen(name='edit_knowledge'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(NotesScreen(name='notes'))
        sm.add_widget(NoteDetailScreen(name='note_detail'))
        sm.add_widget(GalleryScreen(name='gallery'))
        sm.add_widget(AddMemoryScreen(name='add_memory'))
        
        return sm


if __name__ == '__main__':
    HexApp().run()
