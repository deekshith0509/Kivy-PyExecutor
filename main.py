from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput



import os
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
import io
import builtins
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivy.uix.textinput import TextInput
from pygments.lexers import PythonLexer
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.clock import Clock
from kivy.factory import Factory
import threading
import importlib
import inspect



class FileListView(RecycleView):
    def __init__(self, user_data_dir, **kwargs):
        super(FileListView, self).__init__(**kwargs)
        self.user_data_dir = user_data_dir
        self.update_file_list()

    def update_file_list(self):
        # Update the displayed file list
        self.data = [{'text': f} for f in self.get_file_list()]

    def get_file_list(self):
        # Get list of Python files in user_data_dir
        return [f for f in os.listdir(self.user_data_dir) if f.endswith('.py')]

# Define screens first before loading KV
class MainScreen(Screen):
    pass

class CLIScreen(Screen):
    pass

# Register the screens with Kivy's Factory
Factory.register('MainScreen', cls=MainScreen)
Factory.register('CLIScreen', cls=CLIScreen)

class CodeEditor(CodeInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lexer = PythonLexer()
        self.highlight = True
        self.multiline = True
        self.background_color = (0.2, 0.2, 0.2, 1)
        self.foreground_color = (1, 1, 1, 1)

class LineNumbers(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = '1'
        self.color = (0.5, 0.5, 0.5, 1)
        self.size_hint_x = None
        self.width = 40
        self.padding = (5, 0)

    def update_numbers(self, lines):
        self.text = '\n'.join(str(i) for i in range(1, lines + 1))

class CodeEditorWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        
        self.line_numbers = LineNumbers()
        self.code_editor = CodeEditor()
        
        self.code_editor.bind(text=self._on_text_change)
        
        self.add_widget(self.line_numbers)
        self.add_widget(self.code_editor)
    
    def _on_text_change(self, instance, value):
        lines = value.count('\n') + 1
        self.line_numbers.update_numbers(lines)

# Register the CodeEditorWidget with Kivy's Factory
Factory.register('CodeEditorWidget', cls=CodeEditorWidget)

class SafeExecutor:
    def __init__(self):
        # Create a safe set of builtins
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
            'bin': bin, 'bool': bool, 'bytearray': bytearray, 'bytes': bytes,
            'chr': chr, 'complex': complex, 'dict': dict, 'divmod': divmod,
            'enumerate': enumerate, 'filter': filter, 'float': float,
            'format': format, 'frozenset': frozenset, 'hash': hash,
            'hex': hex, 'int': int, 'isinstance': isinstance,
            'issubclass': issubclass, 'iter': iter, 'len': len, 'list': list,
            'map': map, 'max': max, 'min': min, 'next': next, 'oct': oct,
            'ord': ord, 'pow': pow, 'print': print, 'range': range,
            'repr': repr, 'reversed': reversed, 'round': round, 'set': set,
            'slice': slice, 'sorted': sorted, 'str': str, 'sum': sum,
            'tuple': tuple, 'type': type, 'zip': zip,
            '__import__': self._safe_import,
            'help': help,
            'dir': dir,
            'vars': vars,
            'id': id,
        }
        
        self.globals = {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            '__doc__': None,
            '__package__': None,
        }
        
        self.locals = {}
        self.command_history = []
        self.history_index = 0

    def _safe_import(self, name, *args, **kwargs):
        """Import function that allows all imports and handles exceptions."""
        try:
            return importlib.import_module(name)
        except ImportError:
            return f"Module '{name}' is not available"
        except Exception as e:
            return f"Error importing '{name}': {str(e)}"

    def execute(self, code):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            try:
                # First try to eval for expressions
                try:
                    result = eval(code, self.globals, self.locals)
                    if result is not None:
                        print(repr(result))
                except SyntaxError:
                    # If eval fails, try exec for statements
                    exec(code, self.globals, self.locals)
            except Exception as e:
                print(f"Error: {type(e).__name__}: {str(e)}")
                traceback.print_exc(file=output)
        
        return output.getvalue()

    def get_help(self):
        """Return help text for CLI."""
        help_text = """
Available Commands:
------------------
help()          - Show this help message
clear()         - Clear the terminal
reset()         - Reset the interpreter state
dir()           - List available names in current scope
import <module> - Import an allowed module
vars()         - Display current variables
history()       - Show command history

Special Keys:
------------
Up Arrow   - Previous command
Down Arrow - Next command
Ctrl+C    - Stop execution
Ctrl+L    - Clear screen

Allowed Imports:
---------------
math, random, datetime, collections, itertools,
functools, operator, string, time, re, json,
csv, os.path, pathlib

Type Python code at the prompt to execute it.
"""
        return help_text

    def add_to_history(self, command):
        if command.strip():
            self.command_history.append(command)
            self.history_index = len(self.command_history)

KV = '''
ScreenManager:
    MainScreen:
        name: 'main'
    CLIScreen:
        name: 'cli'

<MainScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            MDRaisedButton:
                text: "New File"
                on_release: app.new_file()
                size_hint: None, None
                size: dp(100), dp(40)
            
            MDRaisedButton:
                text: "Open"
                on_release: app.open_file()
                size_hint: None, None
                size: dp(100), dp(40)
            
            MDRaisedButton:
                text: "Save"
                on_release: app.save_code()
                size_hint: None, None
                size: dp(100), dp(40)
                
            Widget:
                size_hint_x: 0.5
                
            MDRaisedButton:
                text: "Terminal"
                on_release: app.switch_screen('cli')
                size_hint: None, None
                size: dp(100), dp(40)

        CodeEditorWidget:
            id: code_editor_widget

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)

            MDRaisedButton:
                text: "Run Code"
                on_release: app.run_code()

            MDRaisedButton:
                text: "Stop"
                on_release: app.stop_code()

            MDRaisedButton:
                text: "Clear Output"
                on_release: app.clear_output()

        ScrollView:
            MDLabel:
                id: output_label
                text: "Output will appear here..."
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1]
                padding: dp(10)
                theme_text_color: "Primary"

<CLIScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            MDRaisedButton:
                text: "Clear Terminal"
                on_release: app.clear_terminal()
                size_hint: None, None
                size: dp(120), dp(40)
                
            Widget:
                size_hint_x: 0.7
                
            MDRaisedButton:
                text: "Editor"
                on_release: app.switch_screen('main')
                size_hint: None, None
                size: dp(100), dp(40)

        ScrollView:
            id: cli_scroll
            do_scroll_x: False
            
            TextInput:
                id: cli_output
                text: "Python " + app.python_version + "\\nType 'help()' for list of commands\\n>>> "
                readonly: True
                size_hint_y: None
                height: max(self.minimum_height, cli_scroll.height)
                multiline: True
                background_color: (0, 0, 0, 1)
                foreground_color: (1, 1, 1, 1)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(5)
            
            TextInput:
                id: cli_input
                multiline: False
                size_hint_y: None
                height: dp(50)
                background_color: (0.2, 0.2, 0.2, 1)
                foreground_color: (1, 1, 1, 1)
                on_text_validate: app.execute_cli_command(self.text)
'''

class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.python_version = sys.version.split()[0]
        self.executor = SafeExecutor()
        self.current_thread = None
        self.current_file = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        
        # Load KV string after classes are registered
        return Builder.load_string(KV)

    def switch_screen(self, screen_name):
        self.root.current = screen_name

    def new_file(self):
        self.current_file = None
        self.root.get_screen('main').ids.code_editor_widget.code_editor.text = ''
        self.root.get_screen('main').ids.output_label.text = "New file created"







    def save_code(self):
        # Create layout for saving the file
        layout = BoxLayout(orientation='vertical')
        
        # Text input for filename
        file_name_input = TextInput(hint_text="Enter file name...", size_hint_y=None, height=40)
        layout.add_widget(file_name_input)

        # Button to save file
        save_button = Button(text="Save File", size_hint_y=None, height=40)
        layout.add_widget(save_button)

        # Creating the popup
        popup = Popup(title="Save File", content=layout, size_hint=(0.8, 0.4))
        popup.open()

        save_button.bind(on_release=lambda instance: self.handle_save_file(file_name_input.text, popup))

    def handle_save_file(self, file_name, popup):
        if file_name.strip():
            user_data_dir = self.user_data_dir
            file_path = os.path.join(user_data_dir, f"{file_name}.py")
            code = self.root.get_screen('main').ids.code_editor_widget.code_editor.text
            with open(file_path, 'w') as f:
                f.write(code)
            self.current_file = file_path
            self.root.get_screen('main').ids.output_label.text = f"Saved as {file_path}"
            popup.dismiss()
        else:
            self.root.get_screen('main').ids.output_label.text = "Please enter a valid file name."


    def create_options_layout(self, selected_file):
        layout = BoxLayout(orientation='vertical')

        # Open button
        open_button = Button(text="Open", size_hint_y=None, height=40)
        open_button.bind(on_release=lambda x: self.open_selected_file(selected_file))
        layout.add_widget(open_button)

        # Delete button
        delete_button = Button(text="Delete", size_hint_y=None, height=40)
        delete_button.bind(on_release=lambda x: self.delete_selected_file(selected_file))
        layout.add_widget(delete_button)

        return layout


    def open_file(self):
        layout = BoxLayout(orientation='vertical')
        self.file_list_view = FileListView(user_data_dir=self.user_data_dir)

        # Add the file list view to the layout
        layout.add_widget(self.file_list_view)

        # Button to close the popup
        close_button = Button(text="Close", size_hint_y=None, height=40)
        layout.add_widget(close_button)

        # Creating the popup
        popup = Popup(title="Select File to Open", content=layout, size_hint=(0.8, 0.8))
        popup.open()

        close_button.bind(on_release=popup.dismiss)

        # Bind selection of files to show options
        self.file_list_view.bind(on_touch_down=self.file_option_selected)

    def file_option_selected(self, instance, touch):
        if not self.file_list_view.collide_point(touch.x, touch.y):
            return

        # Get the index of the selected file based on the touch position
        selected_index = int(touch.y // 56)  # Assuming each item is 56 dp high
        if selected_index >= len(self.file_list_view.data):
            return

        # Get the selected file name
        selected_file = self.file_list_view.data[selected_index]['text']

        # Create a popup with options for the selected file
        content = BoxLayout(orientation='vertical')
        open_button = Button(text="Open", size_hint_y=None, height=40)
        delete_button = Button(text="Delete", size_hint_y=None, height=40)

        content.add_widget(open_button)
        content.add_widget(delete_button)

        popup = Popup(title=f"Options for {selected_file}", content=content, size_hint=(0.5, 0.5))
        popup.open()

        open_button.bind(on_release=lambda x: self.open_selected_file(selected_file, popup))
        delete_button.bind(on_release=lambda x: self.delete_selected_file(selected_file, popup))

    def open_selected_file(self, file_name, popup):
        file_path = os.path.join(self.user_data_dir, file_name)
        with open(file_path, 'r') as f:
            self.root.ids.code_editor.text = f.read()  # Load file contents into code editor
        popup.dismiss()

    def delete_selected_file(self, file_name, popup):
        file_path = os.path.join(self.user_data_dir, file_name)
        os.remove(file_path)  # Delete the file
        self.file_list_view.update_file_list()  # Refresh the file list
        popup.dismiss()

        
        
    def run_code(self):
        if self.current_thread and self.current_thread.is_alive():
            self.root.get_screen('main').ids.output_label.text = "Code is already running..."
            return

        code = self.root.get_screen('main').ids.code_editor_widget.code_editor.text
        
        def execute():
            output = self.executor.execute(code)
            Clock.schedule_once(lambda dt: self.update_output(output))

        self.current_thread = threading.Thread(target=execute)
        self.current_thread.daemon = True
        self.current_thread.start()

    def stop_code(self):
        if self.current_thread and self.current_thread.is_alive():
            self.root.get_screen('main').ids.output_label.text = "Execution stopped."
            self.current_thread = None

    def update_output(self, text):
        self.root.get_screen('main').ids.output_label.text = text

    def clear_output(self):
        self.root.get_screen('main').ids.output_label.text = "Output will appear here..."

    def clear_terminal(self):
        cli_output = self.root.get_screen('cli').ids.cli_output
        cli_output.text = f"Python {self.python_version}\nType 'help()' for list of commands\n>>> "

    def execute_cli_command(self, command):
        if not command.strip():
            return
        
        cli_output = self.screen_manager.get_screen('cli').ids.cli_output
        cli_input = self.screen_manager.get_screen('cli').ids.cli_input
        
        # Handle special commands
        if command.strip() == 'help()':
            output = self.executor.get_help()
        elif command.strip() == 'clear()':
            self.clear_terminal()
            cli_input.text = ''
            return
        elif command.strip() == 'reset()':
            self.executor = SafeExecutor()
            output = "Interpreter state reset.\n"
        elif command.strip() == 'history()':
            output = '\n'.join(self.executor.command_history) + '\n'
        else:
            # Add command to history and execute
            self.executor.add_to_history(command)
            output = self.executor.execute(command)
        
        # Update CLI output
        cli_output.text += command + '\n' + output + '>>> '
        
        # Clear input and scroll to bottom
        cli_input.text = ''
        Clock.schedule_once(lambda dt: self._scroll_cli_to_bottom())

    def _scroll_cli_to_bottom(self):
        cli_output = self.screen_manager.get_screen('cli').ids.cli_output
        cli_output.cursor = (0, len(cli_output.text))

if __name__ == '__main__':
    MyApp().run()