import os
from kivy.utils import platform
from kivy.app import App
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

from kivy.utils import platform
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass, cast

    # Required Android classes
    Build = autoclass('android.os.Build')
    Environment = autoclass('android.os.Environment')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    PackageManager = autoclass('android.content.pm.PackageManager')
    
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
                    padding: dp(0)
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

                # Replace MDLabel with TextInput
                TextInput:
                    id: debug_text
                    text: ""
                    size_hint_y: None
                    height: self.minimum_height  # This allows it to expand with content
                    halign: 'left'
                    readonly: True  # Set to True to prevent editing
                    multiline: True  # Allow for multiple lines of text
                    background_color: [1, 1, 1, 1]  # Optional: Set background color if needed
                    font_size: '14sp'  # Adjust font size if desired
                    padding: dp(5)  # Add padding for a better look

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

    def check_and_request_storage_permissions(self):
        if platform =='linux':
            return
            
        if not Environment.isExternalStorageManager():
            self.show_storage_permission_dialog()
        else:
            print("Already have all files access permission")
        return True

    def show_storage_permission_dialog(self):
        """Show dialog explaining why we need storage permission"""
        dialog = MDDialog(
            title="Storage Permission Required",
            text="This app needs permission to manage files in external storage. Please enable 'Allow all files access' in the next screen.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="SETTINGS",
                    on_release=lambda x: self.open_all_files_settings()
                ),
            ],
        )
        dialog.open()

    def open_all_files_settings(self):
        """Open Android settings for all files access"""
        if platform == 'android':
            activity = PythonActivity.mActivity
            
            # Create intent for "All files access" settings page
            intent = Intent()
            intent.setAction(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            
            # Set package URI
            uri = Uri.fromParts("package", "com.kivy.debugger", None)
            intent.setData(uri)
            
            # Start the settings activity
            activity.startActivity(intent)
            
            # Schedule a check after returning from settings
            Clock.schedule_once(self.check_permission_after_return, 1)

    def check_permission_after_return(self, dt):
        """Check if permission was granted after returning from settings"""
        if platform == 'android':
            if Environment.isExternalStorageManager():
                print("All files access permission granted!")
                # Proceed with your file operations
                self.initialize_storage()
            else:
                print("All files access permission not granted")
                # Optionally show another dialog or handle denial

    def initialize_storage(self):
        """Initialize storage after getting permissions"""
        try:
            storage_path = '/sdcard/kivy'
            os.makedirs(storage_path, exist_ok=True)
            print(f"Successfully created directory: {storage_path}")
        except Exception as e:
            print(f"Error creating directory: {str(e)}")

    def on_start(self):
        """Check permissions when app starts"""
        self.check_and_request_storage_permissions()
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
import requests
def fetch_info(url):
    try:
        return requests.get(url).json()
    except requests.ConnectionError:
        print("Turn on internet for this code Snippet.")
    except Exception as e:
        print(f"Error: {e}")
def print_info(data):
    if isinstance(data, dict):
        for k, v in data.items():
            print(f"{k}:")
            print_info(v)
    elif isinstance(data, list):
        for item in data:
            print_info(item)
    else:
        print(data)
if __name__ == "__main__":
    url = 'https://gist.github.com/deekshith0509/59dde995eb386530344d7997cca2c929/raw'
    info = fetch_info(url)
    if info: print_info(info)

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
        """Run Python code with proper error handling and paginated output"""
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
            
            # Get the complete output
            output = self.debug_buffer.getvalue()
            
            # Process and display output
            debug_screen = self.root.get_screen('debug')
            if output:
                # Split output into lines
                output_lines = output.splitlines()
                total_lines = len(output_lines)
                
                if total_lines > 500:
                    # Initialize pagination attributes
                    self.current_page = 1
                    self.lines_per_page = 500
                    self.total_pages = (total_lines + self.lines_per_page - 1) // self.lines_per_page
                    
                    # Store complete output for pagination
                    self.full_output = output_lines
                    
                    # Display first page
                    self._display_current_page(debug_screen)
                    
                    # Add pagination controls if they don't exist
                    if not hasattr(debug_screen.ids, 'pagination_controls'):
                        self._create_pagination_controls(debug_screen)
                else:
                    # For smaller outputs, display everything
                    debug_screen.ids.debug_text.text = output
                    
                    # Hide pagination controls if they exist
                    if hasattr(debug_screen.ids, 'pagination_controls'):
                        debug_screen.ids.pagination_controls.opacity = 0
            else:
                debug_screen.ids.debug_text.text = "Code executed successfully with no output."
                if hasattr(debug_screen.ids, 'pagination_controls'):
                    debug_screen.ids.pagination_controls.opacity = 0
            
            # Clean up
            try:
                os.remove(code_file)
            except:
                pass
                
        except Exception as e:
            self.show_error(f"Error running code: {str(e)}\n{traceback.format_exc()}")
        
        self.root.current = 'debug'

    def _display_current_page(self, debug_screen):
        """Display the current page of output"""
        start_idx = (self.current_page - 1) * self.lines_per_page
        end_idx = min(start_idx + self.lines_per_page, len(self.full_output))
        
        current_chunk = '\n'.join(self.full_output[start_idx:end_idx])
        debug_screen.ids.debug_text.text = (
            f"Showing page {self.current_page} of {self.total_pages}\n"
            f"Lines {start_idx + 1}-{end_idx} of {len(self.full_output)}\n"
            f"{'='*50}\n\n"
            f"{current_chunk}"
        )

    def _create_pagination_controls(self, debug_screen):
        """Create and add pagination control buttons"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        # Create a horizontal layout for pagination controls
        pagination_layout = BoxLayout(
            size_hint_y=None,
            height='48dp',
            spacing='10dp',
            padding='10dp'
        )
        
        # Previous page button
        prev_button = Button(
            text='Previous',
            size_hint_x=None,
            width='100dp',
            on_release=lambda x: self._change_page(-1)
        )
        
        # Next page button
        next_button = Button(
            text='Next',
            size_hint_x=None,
            width='100dp',
            on_release=lambda x: self._change_page(1)
        )
        
        pagination_layout.add_widget(prev_button)
        pagination_layout.add_widget(next_button)
        
        # Add the layout to the debug screen
        debug_screen.add_widget(pagination_layout)
        debug_screen.ids.pagination_controls = pagination_layout

    def _change_page(self, direction):
        """Change the current page by the specified direction (+1 or -1)"""
        new_page = self.current_page + direction
        
        if 1 <= new_page <= self.total_pages:
            self.current_page = new_page
            self._display_current_page(self.root.get_screen('debug'))
            
        

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
            directory = '/sdcard/1-kivy/'
            os.makedirs(directory, exist_ok=True)  # Create the directory if it does not exist
            
            python_code = self.root.get_screen('main').ids.python_editor.text
            kv_code = self.root.get_screen('main').ids.kv_editor.text
            
            # Save Python code
            python_file = os.path.join(directory, 'saved_code.py')
            with open(python_file, 'w') as f:
                f.write(python_code)
            
            # Save KV code
            kv_file = os.path.join(directory, 'saved_code.kv')
            with open(kv_file, 'w') as f:
                f.write(kv_code)
            
            # self.show_message("Code saved successfully!")
            
        except Exception as e:
            self.show_error(f"Error saving code: {str(e)}")

    def load_code(self):
        """Load code with error handling"""
        try:
            directory = '/sdcard/1-kivy/'
            
            # Load Python code
            python_file = os.path.join(directory, 'saved_code.py')
            kv_file = os.path.join(directory, 'saved_code.kv')
            
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
