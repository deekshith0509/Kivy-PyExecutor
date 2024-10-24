import os
import sys
import logging
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.codeinput import CodeInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform

# Configure logging
logger = logging.getLogger("KivyDebugger")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

if platform == 'android': ##########################experimental android has to be replaced.
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET])
KV_MAIN = '''
ScreenManager:
    MainScreen:
    PreviewScreen:
    DebugScreen:

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'

        MDBoxLayout:
            size_hint_y: 0.07
            padding: dp(3)
            spacing: dp(10)

            MDRaisedButton:
                text: 'Run Code'
                on_release: app.run_code()

            MDRaisedButton:
                text: 'Clear All'
                on_release: app.clear_all()
                theme_text_color: "Error"

            MDRaisedButton:
                text: 'Debug'
                on_release: app.show_debug()

        MDBoxLayout:
            size_hint_y: 0.07
            padding: dp(3)
            spacing: dp(10)

            MDRaisedButton:
                text: 'View Preview'
                on_release: app.view_preview()

            MDRaisedButton:
                text: 'Save Code'
                on_release: app.save_code()

            MDRaisedButton:
                text: 'Load Code'
                on_release: app.load_code()

        MDCard:
            size_hint_y: 0.55
            padding: dp(10)

            MDBoxLayout:
                orientation: 'vertical'

                MDLabel:
                    text: "Python Code"
                    size_hint_y: None
                    height: dp(30)
                    bold: True

                CodeInput:
                    id: python_editor
                    size_hint_y: 1
                    font_size: '13sp'
                    text: app.get_initial_python_code()

                MDBoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    padding: dp(10)
                    spacing: dp(10)

                    MDRaisedButton:
                        text: 'Zoom In'
                        on_release: app.zoom_in('python_editor')

                    MDRaisedButton:
                        text: 'Zoom Out'
                        on_release: app.zoom_out('python_editor')

        MDCard:
            size_hint_y: 0.30
            padding: dp(3)

            MDBoxLayout:
                orientation: 'vertical'

                MDLabel:
                    text: "KV Language"
                    size_hint_y: None
                    height: dp(30)
                    bold: True

                CodeInput:
                    id: kv_editor
                    size_hint_y: 1
                    font_size: '14sp'
                    text: app.get_initial_kv_code()

<DebugScreen>:
    name: 'debug'
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)

        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)

            MDRaisedButton:
                text: 'Back'
                on_release: app.go_back()
                size_hint_x: None
                width: dp(100)

            MDRaisedButton:
                text: 'Clear Output'
                on_release: app.clear_debug()
                size_hint_x: None
                width: dp(120)

        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                spacing: dp(10)

                MDLabel:
                    text: "Debug Output"
                    halign: 'center'
                    font_style: 'H5'
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    id: debug_text
                    text: ""
                    size_hint_y: None
                    height: self.texture_size[1]
                    halign: 'left'
                    markup: True

<PreviewScreen>:
    name: 'preview'
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        # Top button layout
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)

            MDRaisedButton:
                text: 'Back'
                on_release: app.go_back()
                size_hint_x: None
                width: dp(100)

        # ScrollView that takes the remaining height
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            size_hint_y: 1  # Fill the remaining vertical space
            MDBoxLayout:
                id: gui_display
                orientation: 'vertical'
                padding: dp(20)  # Reduced padding for better layout
                spacing: dp(10)  # Added spacing between widgets
                size_hint_y: 1.4 # Allow height to be defined by contents
                height: self.minimum_height  # Dyna
        # Label at the bottom
        MDLabel:
            id: preview_message
            text: "Run a GUI code of Kivy and it will be displayed here."
            halign: 'center'
            font_style: 'H5'
            size_hint_y: None
            height: self.texture_size[1]  # Size to fit the text

'''

class MainScreen(Screen):
    pass

class PreviewScreen(Screen):
    pass

class DebugScreen(Screen):
    pass

class KivyDualEditorApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.zoom_level = 14
        self.debug_buffer = StringIO()
        self.ensure_storage_dir()

    def build(self):
        return Builder.load_string(KV_MAIN)

    def ensure_storage_dir(self):
        """Ensure storage directory exists and is writable"""
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            # Test write permissions
            test_file = os.path.join(self.user_data_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"Storage directory ready: {self.user_data_dir}")
        except Exception as e:
            logger.error(f"Storage directory error: {str(e)}")
            self.show_error(f"Storage access error: {str(e)}")

    def get_initial_python_code(self):
        return '''# Simple test program

import platform
import psutil
import sys
from datetime import datetime

def system_info():
    print("="*30)
    print("      System Information")
    print("="*30)
    print(f"System      : {platform.system()}")
    print(f"Node Name   : {platform.node()}")
    print(f"Release     : {platform.release()}")
    print(f"Version     : {platform.version()}")
    print(f"Machine     : {platform.machine()}")
    print(f"Processor   : {platform.processor()}")
    print(f"CPU Cores   : {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
    print(f"CPU Usage   : {psutil.cpu_percent(interval=1)}%")
    print(f"Memory      : {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print(f"Available   : {psutil.virtual_memory().available / (1024**3):.2f} GB")
    print(f"Used Memory : {psutil.virtual_memory().used / (1024**3):.2f} GB ({psutil.virtual_memory().percent}%)")
    print(f"Boot Time   : {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Ver  : {sys.version.split()[0]}")
    print("="*30)
    print("     The Power of Python")
    print("="*30)
    print("Python is versatile, powerful, and easy to learn. It is used in web dev, data science, AI, scientific computing, and more. Python's extensive libraries and simple syntax make it ideal for rapid development and complex problem-solving.")
    print("="*30)

if __name__ == "__main__":
    system_info()


'''

    def get_initial_kv_code(self):
        return '''
BoxLayout:
    orientation: 'vertical'
    spacing: dp(10)
    padding: dp(10)

    MDLabel:
        text: 'Welcome to KivyMD!'
        halign: 'center'
        font_size: '24sp'
        color: 0, 0.6, 1, 1
        size_hint_y: None
        height: dp(40)

    MDTextField:
        hint_text: 'Enter your name'
        mode: 'rectangle'
        size_hint_x: None
        width: dp(300)
        pos_hint: {'center_x': 0.5}
        size_hint_y: None
        height: dp(40)

    MDRaisedButton:
        text: 'Submit'
        size_hint_x: None
        width: dp(150)
        pos_hint: {'center_x': 0.5}
        size_hint_y: None
        height: dp(40)
        on_release: app.submit_name()

    MDLabel:
        text: 'Choose your options:'
        halign: 'left'
        font_size: '20sp'
        color: 1, 0, 0, 1
        size_hint_y: None
        height: dp(30)

    MDCheckbox:
        active: False
        size_hint_x: None
        width: dp(48)
        size_hint_y: None
        height: dp(48)

    MDLabel:
        text: 'Option 1'
        size_hint_x: None
        width: dp(100)
        size_hint_y: None
        height: dp(48)

    MDCheckbox:
        active: False
        size_hint_x: None
        width: dp(48)
        size_hint_y: None
        height: dp(48)

    MDLabel:
        text: 'Option 2'
        size_hint_x: None
        width: dp(100)
        size_hint_y: None
        height: dp(48)

    MDLabel:
        text: 'Select your favorite color:'
        halign: 'left'
        font_size: '20sp'
        color: 0, 1, 0, 1
        size_hint_y: None
        height: dp(30)

    MDTextField:
        hint_text: 'Select color'
        mode: 'rectangle'
        size_hint_x: None
        width: dp(300)
        pos_hint: {'center_x': 0.5}
        size_hint_y: None
        height: dp(40)

    MDLabel:
        text: 'Your feedback:'
        halign: 'left'
        font_size: '20sp'
        color: 0, 0, 1, 1
        size_hint_y: None
        height: dp(30)

    MDTextField:
        hint_text: 'Enter feedback'
        mode: 'rectangle'
        size_hint_x: None
        width: dp(300)
        pos_hint: {'center_x': 0.5}
        size_hint_y: None
        height: dp(40)

    MDRaisedButton:
        text: 'Send Feedback'
        size_hint_x: None
        width: dp(150)
        pos_hint: {'center_x': 0.5}
        size_hint_y: None
        height: dp(40)

'''

    def run_code(self):
        """Run Python code with proper error handling"""
        try:
            # Get the code
            python_code = self.root.get_screen('main').ids.python_editor.text.strip()
            
            # Save code to a temporary file
            code_file = os.path.join(self.user_data_dir, 'temp_code.py')
            with open(code_file, 'w') as f:
                f.write(python_code)
            
            # Clear previous output
            self.debug_buffer = StringIO()
            
            # Redirect stdout and stderr
            with redirect_stdout(self.debug_buffer), redirect_stderr(self.debug_buffer):
                try:
                    # Execute the code
                    with open(code_file, 'r') as f:
                        code = compile(f.read(), code_file, 'exec')
                        exec(code, {'__name__': '__main__', 
                                  'sys': sys,
                                  'os': os,
                                  'print': print})
                except Exception as e:
                    print(f"Error executing code: {str(e)}")
                    print("\nTraceback:")
                    traceback.print_exc(file=self.debug_buffer)
            
            # Display output
            output = self.debug_buffer.getvalue()
            debug_screen = self.root.get_screen('debug')
            if output:
                debug_screen.ids.debug_text.text = output
            else:
                debug_screen.ids.debug_text.text = "Code executed successfully with no output."
            
            # Clean up
            try:
                os.remove(code_file)
            except:
                pass
                
        except Exception as e:
            self.show_error(f"Error running code: {str(e)}\n{traceback.format_exc()}")
        
        self.root.current = 'debug'

    def view_preview(self):
        """Preview KV code with error handling"""
        try:
            kv_code = self.root.get_screen('main').ids.kv_editor.text.strip()
            preview_screen = self.root.get_screen('preview')
            preview_screen.ids.gui_display.clear_widgets()

            if not kv_code:
                preview_screen.ids.preview_message.text = "Please enter some KV code to preview."
                self.root.current = 'preview'
                return

            # Save KV code to temporary file
            kv_file = os.path.join(self.user_data_dir, 'temp.kv')
            with open(kv_file, 'w') as f:
                f.write(kv_code)

            try:
                # Load and create widget
                widget = Builder.load_file(kv_file)
                preview_screen.ids.gui_display.add_widget(widget)
                preview_screen.ids.preview_message.text = ""
            except Exception as e:
                preview_screen.ids.preview_message.text = f"Error in KV code: {str(e)}"
                logger.error(f"KV preview error: {str(e)}")

            # Clean up
            try:
                os.remove(kv_file)
            except:
                pass

        except Exception as e:
            self.show_error(f"Preview error: {str(e)}")
        
        self.root.current = 'preview'

    def save_code(self):
        """Save code with error handling"""
        try:
            python_code = self.root.get_screen('main').ids.python_editor.text
            kv_code = self.root.get_screen('main').ids.kv_editor.text
            
            # Save Python code
            python_file = os.path.join(self.user_data_dir, 'saved_code.py')
            with open(python_file, 'w') as f:
                f.write(python_code)
            
            # Save KV code
            kv_file = os.path.join(self.user_data_dir, 'saved_code.kv')
            with open(kv_file, 'w') as f:
                f.write(kv_code)
            
            # self.show_message("Code saved successfully!")
            
        except Exception as e:
            self.show_error(f"Error saving code: {str(e)}")

    def load_code(self):
        """Load code with error handling"""
        try:
            # Load Python code
            python_file = os.path.join(self.user_data_dir, 'saved_code.py')
            kv_file = os.path.join(self.user_data_dir, 'saved_code.kv')
            
            if not os.path.exists(python_file) or not os.path.exists(kv_file):
                self.show_message("No saved code found.")
                return
            
            with open(python_file, 'r') as f:
                self.root.get_screen('main').ids.python_editor.text = f.read()
            
            with open(kv_file, 'r') as f:
                self.root.get_screen('main').ids.kv_editor.text = f.read()
            
            # self.show_message("Code loaded successfully!")
            
        except Exception as e:
            self.show_error(f"Error loading code: {str(e)}")

    def show_message(self, message):
        """Show a message in debug screen"""
        debug_screen = self.root.get_screen('debug')
        debug_screen.ids.debug_text.text = message
        self.root.current = 'debug'

    def show_error(self, error_message):
        """Show an error message in debug screen"""
        debug_screen = self.root.get_screen('debug')
        debug_screen.ids.debug_text.text = f"ERROR: {error_message}"
        logger.error(error_message)
        self.root.current = 'debug'

    def clear_all(self):
        """Clear all editors"""
        self.root.get_screen('main').ids.python_editor.text = ""
        self.root.get_screen('main').ids.kv_editor.text = ""

    def clear_debug(self):
        """Clear debug output"""
        debug_screen = self.root.get_screen('debug')
        debug_screen.ids.debug_text.text = ""

    def zoom_in(self, editor_id):
        """Increase font size"""
        code_input = self.root.get_screen('main').ids[editor_id]
        self.zoom_level += 2
        code_input.font_size = f'{self.zoom_level}sp'

    def zoom_out(self, editor_id):
        """Decrease font size"""
        code_input = self.root.get_screen('main').ids[editor_id]
        if self.zoom_level > 8:
            self.zoom_level -= 2
            code_input.font_size = f'{self.zoom_level}sp'

    def show_debug(self):
        """Show debug screen"""
        self.root.current = 'debug'

    def go_back(self):
        """Return to main screen"""
        self.root.current = 'main'

if __name__ == '__main__':
    try:
        KivyDualEditorApp().run()
    except Exception as e:
        logger.critical(f"Application crashed: {str(e)}\n{traceback.format_exc()}")