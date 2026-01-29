"""
utility.py
Utility functions and classes for HEX app
Version: 1.300X
"""

import os
import json
import hashlib
import re
from difflib import SequenceMatcher
from datetime import datetime, timedelta

from kivy.core.audio import SoundLoader

# ========== DATA PATHS ==========

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
HEX_KNOWLEDGE_FILE = os.path.join(DATA_DIR, 'knowledge_hex.json')
SPELLING_MAP_FILE = os.path.join(DATA_DIR, 'spelling_map.json')
SPELLING_REJECTED_FILE = os.path.join(DATA_DIR, 'spelling_rejected.json')
NOTES_FILE = os.path.join(DATA_DIR, 'notes.json')
TASKS_FILE = os.path.join(DATA_DIR, 'tasks.json')
USER_PREFS_FILE = os.path.join(DATA_DIR, 'user_prefs.json')
GALLERY_FILE = os.path.join(DATA_DIR, 'gallery.json')

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

GALLERY_IMAGES_DIR = os.path.join(DATA_DIR, 'gallery_images')
if not os.path.exists(GALLERY_IMAGES_DIR):
    os.makedirs(GALLERY_IMAGES_DIR)

LOGO_PATH = os.path.join(ASSETS_DIR, 'logo.png')
CLICK_SOUND = os.path.join(ASSETS_DIR, 'click.wav')
BUBBLE_SOUND = os.path.join(ASSETS_DIR, 'bubble.wav')
SUCCESS_SOUND = os.path.join(ASSETS_DIR, 'success.wav')
ERROR_SOUND = os.path.join(ASSETS_DIR, 'error.wav')


# ========== ERROR TOAST DISPLAY ==========

def show_error_toast(message):
    """Show error message as toast notification"""
    try:
        from kivymd.toast import toast
        toast(message)
    except:
        print(f"ERROR: {message}")


# ========== GLOBAL CACHE FOR JSON DATA ==========

class DataCache:
    """Cache for loaded JSON data to improve performance"""
    def __init__(self):
        self.cache = {}
        self.last_modified = {}
    
    def get(self, filepath):
        """Get cached data if file hasn't been modified"""
        if not os.path.exists(filepath):
            return None
        
        try:
            current_mtime = os.path.getmtime(filepath)
            
            if filepath in self.cache and self.last_modified.get(filepath) == current_mtime:
                return self.cache[filepath]
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache[filepath] = data
                self.last_modified[filepath] = current_mtime
                return data
        except Exception as e:
            show_error_toast(f"Cache load error: {os.path.basename(filepath)}")
            return None
    
    def invalidate(self, filepath):
        """Invalidate cache for a file"""
        if filepath in self.cache:
            del self.cache[filepath]
        if filepath in self.last_modified:
            del self.last_modified[filepath]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.last_modified.clear()


data_cache = DataCache()


# ========== SOUND MANAGER ==========

class SoundManager:
    """Manages all app sounds"""
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        """Load all sound files"""
        sound_files = {
            'click': CLICK_SOUND,
            'bubble': BUBBLE_SOUND,
            'success': SUCCESS_SOUND,
            'error': ERROR_SOUND
        }
        
        for name, filepath in sound_files.items():
            if os.path.exists(filepath):
                try:
                    sound = SoundLoader.load(filepath)
                    if sound:
                        self.sounds[name] = sound
                except:
                    pass
    
    def play(self, sound_name):
        """Play a sound by name"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass


sound_manager = SoundManager()


# ========== UTILITY FUNCTIONS ==========

def hash_password(password):
    """Simple SHA-256 hashing for offline use"""
    return hashlib.sha256(password.encode()).hexdigest()


def fuzzy_match(str1, str2, threshold=0.8):
    """Check if two strings are similar"""
    ratio = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return ratio >= threshold


def fuzzy_similarity(str1, str2):
    """Return similarity ratio between two strings"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def safe_load_json(filepath, default=None):
    """Load JSON file with caching and error handling"""
    try:
        data = data_cache.get(filepath)
        if data is not None:
            return data
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_cache.cache[filepath] = data
                data_cache.last_modified[filepath] = os.path.getmtime(filepath)
                return data
        return default if default else {}
    except json.JSONDecodeError:
        show_error_toast(f"Invalid JSON: {os.path.basename(filepath)}")
        return default if default else {}
    except Exception as e:
        show_error_toast(f"Load failed: {os.path.basename(filepath)}")
        return default if default else {}


def safe_save_json(filepath, data):
    """Save JSON file with error handling and cache invalidation"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        data_cache.invalidate(filepath)
        return True
    except PermissionError:
        show_error_toast(f"Permission denied: {os.path.basename(filepath)}")
        return False
    except Exception as e:
        show_error_toast(f"Save failed: {os.path.basename(filepath)}")
        return False


load_json = safe_load_json
save_json = safe_save_json


def format_text_to_markup(text):
    """Convert markdown-like formatting to Kivy markup"""
    # Bold
    text = re.sub(r'\*([^\*]+)\*', r'[b]\1[/b]', text)
    # Italic
    text = re.sub(r'_([^_]+)_', r'[i]\1[/i]', text)
    
    # Handle bullet points
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        # Bullet points
        if line.strip().startswith('•'):
            formatted_lines.append('  ' + line)
        # Numbered points
        elif re.match(r'^\s*\d+\.', line):
            formatted_lines.append('  ' + line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def parse_time_input(text):
    """Parse time from user input"""
    text = text.lower().strip()
    
    # Format: 5pm, 5:30pm
    match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3)
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        
        target_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time < datetime.now():
            target_time += timedelta(days=1)
        
        return target_time
    
    # Format: 17:30
    match = re.search(r'(\d{1,2}):(\d{2})', text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        target_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time < datetime.now():
            target_time += timedelta(days=1)
        return target_time
    
    # Format: in 2 hours, in 30 minutes
    match = re.search(r'in\s+(\d+)\s*(minute|hour|min|hr)s?', text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        
        if unit in ['minute', 'min']:
            return datetime.now() + timedelta(minutes=amount)
        elif unit in ['hour', 'hr']:
            return datetime.now() + timedelta(hours=amount)
    
    return None


def get_current_date():
    """Get current date formatted"""
    return datetime.now().strftime("%A, %B %d, %Y")


def get_current_time():
    """Get current time formatted"""
    return datetime.now().strftime("%I:%M %p")


def export_data_external(user_id):
    """Export all user data to external storage"""
    try:
        import shutil
        
        # Try to get external storage path
        try:
            from android.storage import primary_external_storage_path
            export_base = os.path.join(primary_external_storage_path(), 'HEX_Backups')
        except:
            # Fallback for non-Android or if import fails
            export_base = os.path.join(os.path.expanduser('~'), 'HEX_Backups')
        
        if not os.path.exists(export_base):
            os.makedirs(export_base)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_folder = os.path.join(export_base, f'hex_export_{timestamp}')
        os.makedirs(export_folder)
        
        # Export user knowledge
        user_file = os.path.join(DATA_DIR, f'knowledge_user_{user_id}.json')
        if os.path.exists(user_file):
            shutil.copy(user_file, os.path.join(export_folder, 'my_knowledge.json'))
        
        # Export notes
        notes = safe_load_json(NOTES_FILE, {})
        user_notes = notes.get(user_id, [])
        if user_notes:
            with open(os.path.join(export_folder, 'my_notes.json'), 'w', encoding='utf-8') as f:
                json.dump({'notes': user_notes}, f, indent=2, ensure_ascii=False)
        
        # Export gallery
        gallery = safe_load_json(GALLERY_FILE, {})
        user_gallery = gallery.get(user_id, [])
        if user_gallery:
            # Create gallery folder
            gallery_export = os.path.join(export_folder, 'gallery')
            os.makedirs(gallery_export)
            
            # Copy images and create index
            for item in user_gallery:
                if 'image_path' in item and os.path.exists(item['image_path']):
                    filename = os.path.basename(item['image_path'])
                    shutil.copy(item['image_path'], os.path.join(gallery_export, filename))
            
            # Save gallery metadata
            with open(os.path.join(gallery_export, 'gallery_index.json'), 'w', encoding='utf-8') as f:
                json.dump({'gallery': user_gallery}, f, indent=2, ensure_ascii=False)
        
        return True, export_folder
    except Exception as e:
        return False, str(e)
