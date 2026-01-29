"""
custom_widgets.py
Custom UI widgets for HEX app
Version: 1.300X
"""

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty
from kivy.graphics import Color, RoundedRectangle

from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard
from kivymd.uix.spinner import MDSpinner

from utility import format_text_to_markup, sound_manager


# ========== TYPEWRITER LABEL ==========

class TypeWriterLabel(MDLabel):
    """Label with typewriter animation effect"""
    full_text = StringProperty("")
    current_index = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = ""
        self._animation_event = None
    
    def start_animation(self, text, speed=0.012):
        """Start typewriter animation"""
        self.full_text = text
        self.text = ""
        self.current_index = 0
        
        if self._animation_event:
            self._animation_event.cancel()
        
        self._animation_event = Clock.schedule_interval(self._type_next_char, speed)
    
    def _type_next_char(self, dt):
        """Type next character"""
        if self.current_index < len(self.full_text):
            self.text = self.full_text[:self.current_index + 1]
            self.current_index += 1
        else:
            if self._animation_event:
                self._animation_event.cancel()
                self._animation_event = None
            return False


# ========== ENHANCED CHAT BUBBLE ==========

class ChatBubble(MDCard):
    """Enhanced chat bubble widget"""
    def __init__(self, message, is_user=True, is_sure=None, animate=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = dp(14)
        self.spacing = dp(10)
        self.radius = [dp(20), dp(20), dp(20), dp(4)] if is_user else [dp(20), dp(20), dp(4), dp(20)]
        self.elevation = 2
        self.message_text = message
        self.is_animating = animate and not is_user
        
        # Color scheme
        if is_user:
            self.md_bg_color = (0.15, 0.55, 0.95, 1)
        else:
            self.md_bg_color = (0.18, 0.18, 0.22, 1)
        
        # Calculate height
        char_per_line = 35
        estimated_lines = max(2, (len(message) // char_per_line) + 1)
        base_height = dp(14) + dp(32) + dp(10) + dp(14)
        text_height = estimated_lines * dp(24)
        self.height = base_height + text_height
        
        # Build content
        self._build_content(is_user, is_sure, animate)
        
        # Entrance animation
        if animate:
            self.opacity = 0
            self.pos_hint = {'center_x': 0.5}
            
            sound_manager.play('bubble')
            
            anim = Animation(opacity=1, duration=0.35, t='out_quad')
            anim.start(self)
    
    def _build_content(self, is_user, is_sure, animate):
        """Build bubble content"""
        # Header with icon and name
        header_box = BoxLayout(size_hint=(1, None), height=dp(32), spacing=dp(10))
        
        if is_user:
            icon = MDIcon(
                icon='account-circle',
                font_size=sp(22),
                theme_text_color='Custom',
                text_color=(1, 1, 1, 0.95),
                size_hint=(None, None),
                size=(dp(28), dp(28))
            )
            name_label = MDLabel(
                text='YOU',
                font_style='Caption',
                bold=True,
                theme_text_color='Custom',
                text_color=(1, 1, 1, 0.95),
                size_hint_y=1
            )
        else:
            icon = MDIcon(
                icon='brain',
                font_size=sp(22),
                theme_text_color='Custom',
                text_color=(0.4, 0.8, 1, 1),
                size_hint=(None, None),
                size=(dp(28), dp(28))
            )
            name_label = MDLabel(
                text='HEX',
                font_style='Caption',
                bold=True,
                theme_text_color='Custom',
                text_color=(0.4, 0.8, 1, 1),
                size_hint_y=1
            )
        
        header_box.add_widget(icon)
        header_box.add_widget(name_label)
        
        # Sureness indicator
        if not is_user and is_sure is not None:
            if is_sure:
                sure_icon = MDIcon(
                    icon='check-decagram',
                    font_size=sp(20),
                    theme_text_color='Custom',
                    text_color=(0.3, 1, 0.4, 1),
                    size_hint=(None, None),
                    size=(dp(26), dp(26))
                )
            else:
                sure_icon = MDIcon(
                    icon='alert-circle-outline',
                    font_size=sp(20),
                    theme_text_color='Custom',
                    text_color=(1, 0.75, 0, 1),
                    size_hint=(None, None),
                    size=(dp(26), dp(26))
                )
            header_box.add_widget(sure_icon)
        
        self.add_widget(header_box)
        
        # Format message
        formatted_message = format_text_to_markup(self.message_text)
        
        # Calculate text width
        available_width = Window.width - dp(60)
        
        # Create message label
        if animate and not is_user:
            self.message_label = TypeWriterLabel(
                markup=True,
                theme_text_color='Custom',
                text_color=(1, 1, 1, 0.95),
                size_hint=(1, None),
                height=dp(50),
                halign='left',
                valign='top'
            )
            self.message_label.text_size = (available_width, None)
            self.message_label.bind(texture_size=self._update_text_height)
            self.message_label.start_animation(formatted_message, speed=0.012)
        else:
            self.message_label = MDLabel(
                text=formatted_message,
                markup=True,
                theme_text_color='Custom',
                text_color=(1, 1, 1, 0.95),
                size_hint=(1, None),
                height=dp(50),
                halign='left',
                valign='top'
            )
            self.message_label.text_size = (available_width, None)
            self.message_label.bind(texture_size=self._update_text_height)
        
        self.add_widget(self.message_label)
        
        Clock.schedule_once(self._finalize_height, 0.1)
    
    def _update_text_height(self, instance, texture_size):
        """Update text label height based on texture"""
        if texture_size[1] > 0:
            instance.height = max(dp(50), texture_size[1] + dp(10))
            Clock.schedule_once(lambda dt: self._adjust_card_height(), 0.05)
    
    def _adjust_card_height(self):
        """Adjust card height based on content"""
        if self.message_label:
            header_height = dp(32)
            text_height = self.message_label.height
            padding_spacing = dp(14) + dp(10) + dp(14)
            
            total_height = header_height + text_height + padding_spacing
            self.height = max(dp(90), total_height)
    
    def _finalize_height(self, dt):
        """Final height adjustment"""
        self._adjust_card_height()


# ========== LOADING SPINNER ==========

class LoadingSpinner(BoxLayout):
    """Loading spinner widget"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.height = dp(70)
        self.padding = dp(15)
        
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': 0.5},
            active=True,
            line_width=dp(3.5),
            determinate=False
        )
        
        self.add_widget(spinner)
        
        self.opacity = 0
        anim = Animation(opacity=1, duration=0.4, t='out_cubic')
        anim.start(self)


# ========== SUGGESTION CHIP ==========

class SuggestionChip(MDCard):
    """Suggestion chip widget"""
    def __init__(self, text, on_press_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.height = dp(36)
        self.padding = [dp(16), dp(8)]
        self.radius = [dp(18)]
        self.elevation = 1
        self.md_bg_color = (0.25, 0.25, 0.28, 1)
        self.ripple_behavior = True
        
        label = MDLabel(
            text=text,
            size_hint=(None, 1),
            theme_text_color='Custom',
            text_color=(0.9, 0.9, 0.9, 1),
            font_style='Caption'
        )
        label.bind(texture_size=lambda i, s: setattr(label, 'width', s[0]))
        
        self.add_widget(label)
        self.width = label.width + dp(32)
        
        self.bind(on_release=on_press_callback)
        
        # Entrance animation
        self.opacity = 0
        self.scale_value_x = 0.8
        self.scale_value_y = 0.8
        
        anim = Animation(
            opacity=1,
            scale_value_x=1,
            scale_value_y=1,
            duration=0.25,
            t='out_back'
        )
        anim.start(self)
