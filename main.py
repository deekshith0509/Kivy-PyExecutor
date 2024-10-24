import os
import logging
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.codeinput import CodeInput
from kivy.metrics import dp
from kivy.utils import platform
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock

# Configure logging
logger = logging.getLogger("KivyDebugger")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

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
            size_hint_y: None
            height: "50dp"
            padding: "10dp"
            
            MDRaisedButton:
                text: 'Run Code'
                on_release: app.run_code()
                
            MDRaisedButton:
                text: 'Clear All'
                on_release: app.clear_all()
                theme_text_color: "Error"
                
            MDRaisedButton:
                text: 'View Preview'
                on_release: app.view_preview()

            MDRaisedButton:
                text: 'Debug'
                on_release: app.show_debug()

        MDCard:
            size_hint_y: 0.6
            padding: "10dp"
            MDBoxLayout:
                orientation: 'vertical'
                
                MDLabel:
                    text: "Python Code"
                    size_hint_y: None
                    height: "30dp"
                    bold: True
                
                ScrollView:
                    CodeInput:
                        id: python_editor
                        size_hint_y: None
                        height: "300dp"
                        font_size: '14sp'
                        text: app.get_initial_python_code()

        MDCard:
            size_hint_y: 0.4
            padding: "10dp"
            MDBoxLayout:
                orientation: 'vertical'
                
                MDLabel:
                    text: "KV Language"
                    size_hint_y: None
                    height: "30dp"
                    bold: True
                
                ScrollView:
                    CodeInput:
                        id: kv_editor
                        size_hint_y: None
                        height: "300dp"
                        font_size: '14sp'
                        text: app.get_initial_kv_code()

<PreviewScreen>:
    name: 'preview'
    MDBoxLayout:
        orientation: 'vertical'
        pos_hint: {"x": 0, "y": 0.6}  # Position at the top-left corner
            
        MDRaisedButton:
            text: 'Back'
            on_release: app.go_back()
            pos_hint: {"x": 0.01, "y": 1}  # Position at the top-left corner
            size_hint_x: None
            width: "100dp"  # Fixed width for the button
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "10dp"
            spacing: "10dp"  # Optional spacing
            


        BoxLayout:
            id: gui_display
            orientation: 'vertical'
            halign: 'center'
            pos_hint: {"x": 0, "y": 0.2}  # Position at the top-left corner
            valign: 'center'
            size_hint_y: None
            height: self.minimum_height
            padding: [10, 50, 10, 10]  # [left, top, right, bottom] padding

        MDLabel:
            id: preview_message
            text: "Run a GUI code of Kivy and it will be displayed here."
            pos_hint: {"x": 0, "y": 1}  # Position at the top-left corner
            font_style: 'H5'
            size_hint_y: None
            height: self.texture_size[1] + dp(10)

<DebugScreen>:
    name: 'debug'
    MDBoxLayout:
        orientation: 'vertical'
        
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "10dp"
            spacing: "100dp"  # Optional spacing
            
            MDRaisedButton:
                text: 'Back'
                on_release: app.go_back()

        MDLabel:
            text: "Debug Output"
            halign: 'center'
            font_style: 'H5'
            size_hint_y: None
            height: self.texture_size[1] + dp(10)

        ScrollView:
            MDLabel:
                id: debug_text
                text: ""
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

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
        self.debug_screen = None
        self.current_preview = None
        self.setup_app_directory()
        self._default_python_code = '''# Your Python code here
print("Hello, World!")'''
        self._default_kv_code = '''# Your KV code here
MDBoxLayout:
    orientation: 'vertical'
    padding: "10dp"
    
    MDTextField:
        hint_text: "Enter text"
        helper_text: "Helper text"
        helper_text_mode: "on_focus"'''

    def view_preview(self):
        """Handle preview functionality for KV code."""
        try:
            # Clear any existing preview
            preview_screen = self.root.get_screen('preview')
            preview_screen.ids.gui_display.clear_widgets()
            
            # Get the current KV code
            kv_code = self.root.get_screen('main').ids.kv_editor.text.strip()
            
            if not kv_code:
                preview_screen.ids.preview_message.text = "No KV code to preview"
                self.root.current = 'preview'
                return
            
            # Clean up previous preview if it exists
            if self.current_preview:
                try:
                    self.current_preview.clear_widgets()
                    preview_screen.ids.gui_display.remove_widget(self.current_preview)
                except:
                    pass
            
            try:
                # Try to build the KV code
                preview_widget = Builder.load_string(kv_code)
                self.current_preview = preview_widget
                
                # Add the preview to the display area
                preview_screen.ids.gui_display.add_widget(preview_widget)
                preview_screen.ids.preview_message.text = "Preview of your KV code"
                
            except Exception as e:
                # If there's an error in the KV code, show it in the preview message
                error_msg = f"Error in KV code: {str(e)}"
                preview_screen.ids.preview_message.text = error_msg
                logger.error(error_msg)
                
            # Switch to preview screen
            self.root.current = 'preview'
            
        except Exception as e:
            logger.error(f"Error in preview: {str(e)}")
            if self.debug_screen:
                self.debug_screen.ids.debug_text.text = f"Preview error: {str(e)}"
                self.root.current = 'debug'

    def clear_all(self):
        """Clear all text fields and clean up storage."""
        self.root.get_screen('main').ids.python_editor.text = ""
        self.root.get_screen('main').ids.kv_editor.text = ""
        
        # Clear preview screen
        preview_screen = self.root.get_screen('preview')
        preview_screen.ids.gui_display.clear_widgets()
        preview_screen.ids.preview_message.text = "Run a GUI code of Kivy and it will be displayed here."
        
        # Clear debug screen
        self.root.get_screen('debug').ids.debug_text.text = ""
        
        # Clean up storage and temporary files
        self.cleanup_temp_files()
        if self.storage.exists('last_session'):
            self.storage.delete('last_session')
        
        # Reset current preview
        self.current_preview = None
        
    def setup_app_directory(self):
        """Setup the application directory structure."""
        try:
            # Get the app's user data directory
            self.app_dir = self.user_data_dir
            
            print('this is userdatadir:'+self.app_dir)
            
            # Create necessary subdirectories
            self.temp_dir = os.path.join(self.app_dir, 'temp')
            self.cache_dir = os.path.join(self.app_dir, 'cache')
            
            # Ensure directories exist
            for directory in [self.temp_dir, self.cache_dir]:
                os.makedirs(directory, exist_ok=True)
                
            # Setup storage for app data
            self.storage = JsonStore(os.path.join(self.app_dir, 'app_data.json'))
            
            logger.info(f"App directory setup complete at {self.app_dir}")
        except Exception as e:
            logger.error(f"Error setting up app directory: {e}")

    def cleanup_temp_files(self, *args):
        """Clean up temporary files."""
        try:
            temp_file = os.path.join(self.temp_dir, 'main.py')
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logger.debug(f"Cleaned up temporary file: {temp_file}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")

    def build(self):
        return Builder.load_string(KV_MAIN)

    def on_start(self):
        self.debug_screen = self.root.get_screen('debug')
        # Schedule periodic cleanup of temp files
        Clock.schedule_interval(self.cleanup_temp_files, 300)  # Clean every 5 minutes

    def on_stop(self):
        # Final cleanup when app closes
        self.cleanup_temp_files()

    def run_code(self):
        """Run the Python code with proper error handling and output capture."""
        python_code = self.root.get_screen('main').ids.python_editor.text.strip()
        
        try:
            # Save code to temporary file
            temp_file = os.path.join(self.temp_dir, 'main.py')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            # Capture output using StringIO
            from io import StringIO
            import sys
            stdout = StringIO()
            stderr = StringIO()
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            try:
                # Redirect output
                sys.stdout = stdout
                sys.stderr = stderr
                
                # Execute the code
                exec(python_code, {})
                
                # Get output
                output = stdout.getvalue()
                error = stderr.getvalue()
                
            finally:
                # Restore original stdout/stderr
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                stdout.close()
                stderr.close()
            
            # Update debug screen
            debug_text = "Output:\n{}\n\nErrors:\n{}".format(
                output if output else "No output",
                error if error else "No errors"
            )
            
            if self.debug_screen:
                self.debug_screen.ids.debug_text.text = debug_text
                self.root.current = 'debug'
            else:
                logger.error("Debug screen not initialized")
                
        except Exception as e:
            error_msg = f"Error executing code: {str(e)}"
            logger.error(error_msg)
            if self.debug_screen:
                self.debug_screen.ids.debug_text.text = error_msg
                self.root.current = 'debug'

    def save_current_code(self):
        """Save current code to persistent storage."""
        try:
            self.storage.put('last_session',
                python_code=self.root.get_screen('main').ids.python_editor.text,
                kv_code=self.root.get_screen('main').ids.kv_editor.text
            )
        except Exception as e:
            logger.error(f"Error saving code: {e}")






    def load_saved_code(self):
        """Load previously saved code if it exists."""
        try:
            if self.storage.exists('last_session'):
                data = self.storage.get('last_session')
                return data.get('python_code', self._default_python_code), data.get('kv_code', self._default_kv_code)
            return self._default_python_code, self._default_kv_code
        except Exception as e:
            logger.error(f"Error loading saved code: {e}")
            return self._default_python_code, self._default_kv_code

    def get_initial_python_code(self):
        """Get initial Python code."""
        python_code, _ = self.load_saved_code()
        return python_code

    def get_initial_kv_code(self):
        """Get initial KV code."""
        _, kv_code = self.load_saved_code()
        return kv_code


            
    def show_debug(self):
        """Navigate to the Debug screen."""
        self.root.current = 'debug'

    def go_back(self):
        """Navigate back to the previous screen."""
        self.root.current = 'main'

if __name__ == '__main__':
    KivyDualEditorApp().run()
