import os
import subprocess
import tempfile
import logging
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.codeinput import CodeInput
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup

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
            spacing: "10dp"  # Optional spacing

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

        MDCard:
            size_hint_y: 0.5
            padding: "10dp"
            MDBoxLayout:
                orientation: 'vertical'
                
                MDLabel:
                    text: "Python Code"
                    size_hint_y: None
                    height: "30dp"
                    bold: True
                
                CodeInput:
                    id: python_editor
                    size_hint_y: None
                    height: "200dp"
                    font_size: '14sp'
                    text: app.get_initial_python_code()

        MDCard:
            size_hint_y: 0.5
            padding: "10dp"
            MDBoxLayout:
                orientation: 'vertical'
                
                MDLabel:
                    text: "KV Language"
                    size_hint_y: None
                    height: "30dp"
                    bold: True
                
                CodeInput:
                    id: kv_editor
                    size_hint_y: None
                    height: "200dp"
                    font_size: '14sp'
                    text: app.get_initial_kv_code()

        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "10dp"
            spacing: "10dp"

            MDRaisedButton:
                text: 'View Preview'
                on_release: app.view_preview()

            MDRaisedButton:
                text: 'Save Code'
                on_release: app.save_code()

            MDRaisedButton:
                text: 'Load Code'
                on_release: app.load_code()

<PreviewScreen>:
    name: 'preview'
    MDBoxLayout:
        orientation: 'vertical'
        
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "10dp"
            spacing: "10dp"

            MDRaisedButton:
                text: 'Back'
                on_release: app.go_back()
                pos_hint: {"x": 0, "y": 1}  # Position at the top-left corner
                size_hint_x: None
                width: "100dp"  # Fixed width for the button

        BoxLayout:
            id: gui_display
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height

        MDLabel:
            id: preview_message
            text: "Run a GUI code of Kivy and it will be displayed here."
            halign: 'center'
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
            spacing: "10dp"

            MDRaisedButton:
                text: 'Back'
                on_release: app.go_back()
                pos_hint: {"x": 0, "y": 1}  # Position at the top-left corner
                size_hint_x: None
                width: "100dp"  # Fixed width for the button

        MDLabel:
            text: "Debug Output"
            halign: 'center'
            font_style: 'H5'
            size_hint_y: None
            height: self.texture_size[1] + dp(10)

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

    def build(self):
        return Builder.load_string(KV_MAIN)

    def get_initial_python_code(self):
        return '''# Your initial Python code here
# Example Python code
print("Hello, World!")'''

    def get_initial_kv_code(self):
        return '''# Your initial KV code here
# Example KV code
MDBoxLayout:
    orientation: 'vertical'
    padding: "10dp"
    
    MDTextField:
        hint_text: "Enter text"
        helper_text: "Helper text"
        helper_text_mode: "on_focus"'''

    def run_code(self):
        """Run the main.py code."""
        python_code = self.root.get_screen('main').ids.python_editor.text.strip()

        # Create a temporary directory to save files
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Save the Python code to a temporary file
            python_file_path = os.path.join(tmpdirname, 'main.py')
            with open(python_file_path, 'w') as python_file:
                python_file.write(python_code)

            try:
                # Run the Python file using subprocess
                logger.debug("Running Python file...")
                result = subprocess.run(
                    [os.sys.executable, python_file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Capture output and errors
                output = result.stdout.strip()
                error = result.stderr.strip()

                # Display output and errors in the Debug Screen
                debug_screen = self.root.get_screen('debug')
                debug_screen.ids.debug_text.text = f"Output:\n{output}\n\nErrors:\n{error}" if output or error else "No output or errors."

                # Navigate to the Debug screen to show output
                self.root.current = 'debug'

            except Exception as e:
                logger.error(f"Error running Python code: {e}")
                debug_screen.ids.debug_text.text = f"Error running code: {str(e)}"

    def view_preview(self):
        """View the Kivy GUI code in the preview screen."""
        kv_code = self.root.get_screen('main').ids.kv_editor.text.strip()
        preview_screen = self.root.get_screen('preview')
        preview_screen.ids.gui_display.clear_widgets()  # Clear previous widgets

        # Check if any GUI code is provided
        if not kv_code:
            preview_screen.ids.preview_message.text = "Please enter some KV code to display components."
            self.root.current = 'preview'
            return

        try:
            # Check if the Python code has any Kivy-related components
            if self.contains_kivy_components(kv_code):
                # Dynamically load Kivy code to the existing context
                self.dynamic_preview_load(kv_code)
                preview_screen.ids.preview_message.text = ""
            else:
                preview_screen.ids.preview_message.text = "No Kivy components detected in the code."

        except Exception as e:
            logger.error(f"Error loading KV code: {e}")
            preview_screen.ids.preview_message.text = f"Error loading KV code: {e}"

        # Navigate to the Preview screen after loading
        self.root.current = 'preview'

    def contains_kivy_components(self, code):
        """Check if the provided code contains any Kivy or KivyMD components."""
        # List of common Kivy and KivyMD components to check for
        kivy_components = [
            # Kivy components
            'BoxLayout', 'GridLayout', 'StackLayout', 'FloatLayout', 'AnchorLayout',
            'RelativeLayout', 'ScatterLayout', 'Popup', 'Label', 'Button', 'TextInput',
            'CheckBox', 'ToggleButton', 'Slider', 'Switch', 'Image', 'FileChooserListView',
            'ScrollView', 'Canvas', 'Color', 'Rectangle', 'Line', 'Ellipse', 'InstructionGroup',
            
            # KivyMD components
            'MDBoxLayout', 'MDGridLayout', 'MDRaisedButton', 'MDTextField', 'MDLabel', 'MDCard',
            'MDScreen', 'MDToolbar', 'MDNavigationLayout'
        ]
        return any(component in code for component in kivy_components)

    def dynamic_preview_load(self, kv_code):
        """Dynamically load the provided KV code into the GUI."""
        from kivy.lang import Builder

        try:
            # Load the KV code
            new_container = Builder.load_string(kv_code)

            # Clear previous content in the preview area
            self.root.get_screen('preview').ids.gui_display.clear_widgets()
            self.root.get_screen('preview').ids.gui_display.add_widget(new_container)

        except Exception as e:
            logger.error(f"Error loading dynamic KV code: {e}")

    def show_debug(self):
        """Navigate to the Debug screen."""
        self.root.current = 'debug'

    def go_back(self):
        """Navigate back to the main screen."""
        self.root.current = 'main'

    def clear_all(self):
        """Clear all inputs."""
        self.root.get_screen('main').ids.python_editor.text = ''
        self.root.get_screen('main').ids.kv_editor.text = ''
        self.root.get_screen('debug').ids.debug_text.text = ''
        self.root.get_screen('preview').ids.gui_display.clear_widgets()
        self.root.get_screen('preview').ids.preview_message.text = "Run a GUI code of Kivy and it will be displayed here."

    def save_code(self):
        """Save the current Python and KV code to user_data_dir."""
        from kivy.core.window import Window
        from kivy.utils import platform
        from kivy.uix.filechooser import FileChooserListView

        user_data_dir = self.user_data_dir
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        python_code = self.root.get_screen('main').ids.python_editor.text.strip()
        kv_code = self.root.get_screen('main').ids.kv_editor.text.strip()

        # Create file names
        python_file_path = os.path.join(user_data_dir, 'code.py')
        kv_file_path = os.path.join(user_data_dir, 'code.kv')

        # Save the Python code
        with open(python_file_path, 'w') as python_file:
            python_file.write(python_code)

        # Save the KV code
        with open(kv_file_path, 'w') as kv_file:
            kv_file.write(kv_code)

        logger.info(f"Saved Python code to {python_file_path} and KV code to {kv_file_path}")

    def load_code(self):
        """Load Python and KV code from user_data_dir."""
        user_data_dir = self.user_data_dir

        python_file_path = os.path.join(user_data_dir, 'code.py')
        kv_file_path = os.path.join(user_data_dir, 'code.kv')

        if os.path.exists(python_file_path) and os.path.exists(kv_file_path):
            with open(python_file_path, 'r') as python_file:
                self.root.get_screen('main').ids.python_editor.text = python_file.read()

            with open(kv_file_path, 'r') as kv_file:
                self.root.get_screen('main').ids.kv_editor.text = kv_file.read()

            logger.info(f"Loaded Python code from {python_file_path} and KV code from {kv_file_path}")
        else:
            logger.warning("No saved code found in user_data_dir.")

if __name__ == '__main__':
    KivyDualEditorApp().run()
