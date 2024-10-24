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
from kivy.uix.scrollview import ScrollView
from kivy.uix.codeinput import CodeInput
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


    def dynamic_preview_load(self, kv_code):
        """Dynamically load and create widgets from KV code."""
        from kivy.lang import Builder

        try:
            # Load the KV code
            new_container = Builder.load_string(kv_code)

            # Clear previous content in the display area
            gui_display = self.root.get_screen('preview').ids.gui_display
            gui_display.clear_widgets()  # Clear previous content

            # Add all widgets from the loaded KV code to the GUI display
            gui_display.add_widget(new_container)

        except Exception as e:
            logger.error(f"Error dynamically loading KV code: {e}")

            # Provide a user-friendly error message based on the exception type
            if 'ValueError' in str(e):
                error_message = "Value Error: Please check the values you entered in the KV code. Make sure numeric values are in the correct format."
            elif 'AttributeError' in str(e):
                error_message = "Attribute Error: There might be an issue with a property or an attribute in your KV code."
            elif 'SyntaxError' in str(e):
                error_message = "Syntax Error: Please check for any syntax mistakes in your KV code."
            else:
                error_message = f"An error occurred while loading the KV code: {str(e)}"

            # Show the user-friendly error message
            raise Exception(error_message)  # Raise a new exception with the user-friendly message


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
            preview_screen.ids.preview_message.text = f"Error loading KV code: {str(e)}"  # Display the detailed error

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
            'MDBoxLayout', 'MDGridLayout', 'MDStackLayout', 'MDFloatLayout', 'MDAnchorLayout',
            'MDLabel', 'MDRaisedButton', 'MDTextField', 'MDCard', 'MDIconButton', 'MDSwitch',
            'MDCheckbox', 'MDScreen', 'MDToolbar', 'MDTopAppBar', 'MDBottomNavigation',
            'MDFillRoundFlatButton', 'MDFlatButton', 'MDTextButton', 'MDTabs', 'MDDialog',
            'MDSnackbar', 'MDSlider', 'MDProgressBar', 'MDList', 'MDFloatLayout', 'MDCarousel'
        ]
        
        return any(component in code for component in kivy_components)




    def clear_all(self):
        """Clear all text fields."""
        self.root.get_screen('main').ids.python_editor.text = ""
        self.root.get_screen('main').ids.kv_editor.text = ""
        self.root.get_screen('preview').ids.gui_display.clear_widgets()
        self.root.get_screen('preview').ids.preview_message.text = "Run a GUI code of Kivy and it will be displayed here."
        self.root.get_screen('debug').ids.debug_text.text = ""

    def show_debug(self):
        """Navigate to the Debug screen."""
        self.root.current = 'debug'

    def go_back(self):
        """Navigate back to the previous screen."""
        self.root.current = 'main'

if __name__ == '__main__':
    KivyDualEditorApp().run()
