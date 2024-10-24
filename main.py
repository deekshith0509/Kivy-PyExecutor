import os
import subprocess
import logging
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
            size_hint_y: 0.07  # Top 15% for button row
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
            size_hint_y: 0.07  # Next 15% for view, save, load buttons
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
            size_hint_y: 0.55  # 70% for Python editor
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
                    spacing: (10)

                    MDRaisedButton:
                        text: 'Zoom In'
                        on_release: app.zoom_in('python_editor')

                    MDRaisedButton:
                        text: 'Zoom Out'
                        on_release: app.zoom_out('python_editor')

        MDCard:
            size_hint_y: 0.30  # 15% for KV editor
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

        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            padding: dp(10)
            spacing: dp(10)

            MDRaisedButton:
                text: 'Back'
                on_release: app.go_back()
                size_hint_x: None
                width: dp(100)

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height

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


<PreviewScreen>:
    name: 'preview'
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        pos_hint: {"x": 0, "y": 0.75}

        # BoxLayout for the Back button
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)

            MDRaisedButton:
                text: 'Back'
                on_release: app.go_back()
                size_hint_x: None
                width: dp(100)
                pos_hint: {"x": 0, "center_y": 1}  # Align to top left corner

        # BoxLayout for the display area
        BoxLayout:
            id: gui_display
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height

        # Label for the preview message
        MDLabel:
            id: preview_message
            text: "Run a GUI code of Kivy and it will be displayed here."
            halign: 'center'
            font_style: 'H5'
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
        self.zoom_level = 14  # Default font size

    def build(self):
        return Builder.load_string(KV_MAIN)

    def get_initial_python_code(self):
        return '''import sys

def get_system_info():
    print("System Information:")
    print("Platform:", sys.platform)
    print("Version:", sys.version)
    print("Executable:", sys.executable)

if __name__ == "__main__":
    get_system_info()
'''

    def get_initial_kv_code(self):
        return '''MDRaisedButton:
    text: 'Back'
    on_release: app.go_back()
    size_hint_x: None
    width: dp(100)
'''

    def run_code(self):
        """Run the main.py code."""
        python_code = self.root.get_screen('main').ids.python_editor.text.strip()
        user_data_dir = self.user_data_dir
        python_file_path = os.path.join(user_data_dir, 'main.py')

        # Save the Python code to the specified file
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
            debug_screen.ids.debug_text.text = (
                f"Output:\n{output}\n\nErrors:\n{error}"
                if output or error else "No output or errors."
            )

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
            # Dynamically load Kivy code
            root_widget = Builder.load_string(kv_code)
            preview_screen.ids.gui_display.add_widget(root_widget)  # Add the root widget
            preview_screen.ids.preview_message.text = ""
        except Exception as e:
            logger.error(f"Error loading KV code: {e}")
            preview_screen.ids.preview_message.text = f"Error loading KV code: {e}"
        
        # Navigate to the Preview screen after loading
        self.root.current = 'preview'





    def clear_all(self):
        """Clear all input fields."""
        self.root.get_screen('main').ids.python_editor.text = ""
        self.root.get_screen('main').ids.kv_editor.text = ""

    def save_code(self):
        """Save the current code to a file."""
        user_data_dir = self.user_data_dir
        python_code = self.root.get_screen('main').ids.python_editor.text.strip()
        kv_code = self.root.get_screen('main').ids.kv_editor.text.strip()

        with open(os.path.join(user_data_dir, 'saved_code.py'), 'w') as f:
            f.write(python_code)

        with open(os.path.join(user_data_dir, 'saved_code.kv'), 'w') as f:
            f.write(kv_code)

        logger.info("Code saved successfully.")

    def load_code(self):
        """Load the saved code from a file."""
        user_data_dir = self.user_data_dir

        try:
            with open(os.path.join(user_data_dir, 'saved_code.py'), 'r') as f:
                self.root.get_screen('main').ids.python_editor.text = f.read()

            with open(os.path.join(user_data_dir, 'saved_code.kv'), 'r') as f:
                self.root.get_screen('main').ids.kv_editor.text = f.read()

            logger.info("Code loaded successfully.")
        except FileNotFoundError:
            logger.warning("No saved code found.")

    def zoom_in(self, editor_id):
        """Zoom in the code editor by increasing font size."""
        code_input = self.root.get_screen('main').ids[editor_id]
        self.zoom_level += 2
        code_input.font_size = f'{self.zoom_level}sp'

    def zoom_out(self, editor_id):
        """Zoom out the code editor by decreasing font size."""
        code_input = self.root.get_screen('main').ids[editor_id]
        if self.zoom_level > 8:  # Prevent zooming out too much
            self.zoom_level -= 2
            code_input.font_size = f'{self.zoom_level}sp'

    def show_debug(self):
        """Switch to the Debug screen."""
        self.root.current = 'debug'

    def go_back(self):
        """Go back to the main screen."""
        self.root.current = 'main'


if __name__ == '__main__':
    KivyDualEditorApp().run()
