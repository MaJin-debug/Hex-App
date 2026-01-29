"""
calling.py
Dynamic data and one-time functions for HEX app
Version: 1.300X
"""

from datetime import datetime
from utility import *


class DataCaller:
    """Provides dynamic data to the app"""
    
    @staticmethod
    def get_current_year():
        return str(datetime.now().year)

    @staticmethod
    def get_current_month():
        return datetime.now().strftime("%B")

    @staticmethod
    def get_current_day():
        return str(datetime.now().day)

    @staticmethod
    def get_day_of_week():
        return datetime.now().strftime("%A")

    @staticmethod
    def get_current_datetime():
        return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
    @staticmethod
    def get_current_date():
        return datetime.now().strftime("%A, %B %d, %Y")
    
    @staticmethod
    def get_current_time():
        return datetime.now().strftime("%I:%M %p")
    
    @staticmethod
    def get_user_name(user):
        if user:
            return user.get('name', 'User')
        return 'User'
    
    @staticmethod
    def get_greeting():
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "Hello"
    
    @staticmethod
    def replace_placeholders(text, user=None):
        replacements = {
            '{current_date}': DataCaller.get_current_date(),
            '{current_time}': DataCaller.get_current_time(),
            '{user_name}': DataCaller.get_user_name(user),
            '{greeting}': DataCaller.get_greeting()
        }
        
        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)
        
        return text


class TutorialManager:
    """Manages tutorial and first-time user experience"""
    
    @staticmethod
    def is_first_time(user_id):
        prefs = load_json(USER_PREFS_FILE, {})
        return not prefs.get(user_id, {}).get('tutorial_shown', False)
    
    @staticmethod
    def mark_tutorial_complete(user_id):
        prefs = load_json(USER_PREFS_FILE, {})
        if user_id not in prefs:
            prefs[user_id] = {}
        prefs[user_id]['tutorial_shown'] = True
        save_json(USER_PREFS_FILE, prefs)
    
    @staticmethod
    def get_tutorial_bubbles(user_name):
        return [
            {
                'message': f"Welcome to HEX, {user_name}! I'm your Second Brain.",
                'is_user': False,
                'animate': True
            },
            {
                'message': "I can help you store and recall information. Just ask me questions or teach me new things.",
                'is_user': False,
                'animate': True
            },
            {
                'message': "Here are some commands:\n\n/teach - Store knowledge\n/overview <topic> - View related knowledge\n/add_note - Quick notes\n/remind - Set reminders\n/memory <topic> - View memories\n/bye - Exit",
                'is_user': False,
                'animate': True
            },
            {
                'message': "Try asking me something or use /teach to get started!",
                'is_user': False,
                'animate': True
            }
        ]


class TaskChecker:
    """Manages task checking and notifications"""
    
    @staticmethod
    def get_pending_tasks(user_id):
        tasks = load_json(TASKS_FILE, {})
        user_tasks = tasks.get(user_id, [])
        
        pending = []
        current_time = datetime.now()
        
        for task in user_tasks:
            if not task.get('completed', False) and not task.get('notified', False):
                try:
                    task_time = datetime.fromisoformat(task['time'])
                    if task_time <= current_time:
                        pending.append(task)
                except:
                    continue
        
        return pending
    
    @staticmethod
    def mark_task_notified(user_id, task_id):
        tasks = load_json(TASKS_FILE, {})
        user_tasks = tasks.get(user_id, [])
        
        for task in user_tasks:
            if task.get('id') == task_id:
                task['notified'] = True
                break
        
        tasks[user_id] = user_tasks
        save_json(TASKS_FILE, tasks)
    
    @staticmethod
    def mark_task_completed(user_id, task_id):
        tasks = load_json(TASKS_FILE, {})
        user_tasks = tasks.get(user_id, [])
        
        for task in user_tasks:
            if task.get('id') == task_id:
                task['completed'] = True
                break
        
        tasks[user_id] = user_tasks
        save_json(TASKS_FILE, tasks)
    
    @staticmethod
    def create_task(user_id, reason, time_str):
        import uuid
        
        target_time = parse_time_input(time_str)
        if not target_time:
            return False, "Could not understand the time format. Try '5pm', '17:30', or 'in 2 hours'"
        
        tasks = load_json(TASKS_FILE, {})
        if user_id not in tasks:
            tasks[user_id] = []
        
        new_task = {
            'id': str(uuid.uuid4()),
            'reason': reason,
            'time': target_time.isoformat(),
            'created': datetime.now().isoformat(),
            'completed': False,
            'notified': False
        }
        
        tasks[user_id].append(new_task)
        save_json(TASKS_FILE, tasks)
        
        time_display = target_time.strftime("%I:%M %p on %B %d")
        return True, f"Reminder set for {time_display}: {reason}"


class NoteManager:
    """Manages quick notes"""
    
    @staticmethod
    def add_note(user_id, title, content):
        import uuid
        
        notes = load_json(NOTES_FILE, {})
        if user_id not in notes:
            notes[user_id] = []
        
        new_note = {
            'id': str(uuid.uuid4()),
            'title': title,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'date_display': datetime.now().strftime("%B %d, %Y at %I:%M %p")
        }
        
        notes[user_id].append(new_note)
        save_json(NOTES_FILE, notes)
        return True
    
    @staticmethod
    def get_notes(user_id):
        notes = load_json(NOTES_FILE, {})
        return notes.get(user_id, [])
    
    @staticmethod
    def delete_note(user_id, note_id):
        notes = load_json(NOTES_FILE, {})
        user_notes = notes.get(user_id, [])
        
        notes[user_id] = [n for n in user_notes if n['id'] != note_id]
        save_json(NOTES_FILE, notes)
        return True
    
    @staticmethod
    def update_note(user_id, note_id, title, content):
        notes = load_json(NOTES_FILE, {})
        user_notes = notes.get(user_id, [])
        
        for note in user_notes:
            if note['id'] == note_id:
                note['title'] = title
                note['content'] = content
                note['timestamp'] = datetime.now().isoformat()
                note['date_display'] = datetime.now().strftime("%B %d, %Y at %I:%M %p")
                break
        
        notes[user_id] = user_notes
        save_json(NOTES_FILE, notes)
        return True
