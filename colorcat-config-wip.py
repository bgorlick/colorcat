#!/usr/bin/env python3

# Filename: colorcat-config-wip.py (work in progress)
# Colorcat - A powerful yet simple syntax highlighter for the terminal viewing of files.
# (c) 2024 - Ben Gorlick | MIT License | Attribution to the original author is required - free to use, modify, and distribute.

# Initial colorcat framework that will get merged into colorcat.py -- it's a work in progress.
# The idea here is to migrate the configuration and management of the configuration to YAML (colorcat currently is hard-coded w/ a JSON style color config)

# This introduces themes, and will make supporting 'offsets' for foreground and background colors easier to manage.
# The idea is to enable a user to create a theme, and then apply offsets to the theme to create a new theme. 
# This supports rapidly creating new themes, and also allows for the user to create a theme that is a 'child' of another theme, and then apply offsets to the child theme to create a new theme.

from collections import defaultdict
import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
import json
import re, random
import io
import shlex
import argparse

class AugmentParser(argparse.ArgumentParser):
    def __init__(self, color_cat_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.color_cat_instance = color_cat_instance

    def apply_syntax_highlighting(self, help_message):
        light_blue = '\033[38;5;45m'
        bg_black = '\033[48;5;0m'
        reset_code = '\033[0m'
        new_message = ''
        for line in help_message.split('\n'):
            new_line = ''
            for char in line:
                color_code = None
                for color_name, color_data in self.color_cat_instance.colorcat_current_theme_config['color_settings'].items():
                    if char in color_data['chars']:
                        color_code = color_data['fg_color'] + color_data['bg_color']
                        #print(f"Found color code for {char}: {color_code}") # Debugging
                        break
                if color_code:
                    new_line += color_code + char + reset_code + light_blue
                else:
                    new_line += char
            new_message += new_line + '\n'
        return new_message
    
    def print_help(self, file=None):
        if file is None:
            file = sys.stdout
        help_message = self.format_help()
        highlighted_help = self.apply_syntax_highlighting(help_message)
        self._print_message(highlighted_help, file)


    def print_version(self, file=None):
        if file is None:
            file = sys.stdout
        version_message = self.format_version()
        highlighted_version = self.apply_syntax_highlighting(version_message)
        self._print_message(highlighted_version, file)

class ColorCatThemes:
    def __init__(self, theme_name='default', colorcat_root_dir=None):
        self.theme_name = theme_name
        self.colorcat_root_dir = Path(colorcat_root_dir or Path.home() / '.config/colorcat').expanduser()
        self.themes_dir = 'themes'  
        self.autogen_themes_dir = self.colorcat_root_dir / 'autogen-themes'
        
        # check if the themes directory exists, if not, create it
        self.themes_dir_path = self.colorcat_root_dir / self.themes_dir
        self.themes_dir_path.mkdir(parents=True, exist_ok=True)
        self.autogen_themes_dir.mkdir(parents=True, exist_ok=True)
        
        #  whether to load a user-provided theme or the default theme
        if self.theme_name and self.theme_name != 'default':
            self.colorcat_current_theme_config = self.load_theme_config()
        else:
            self.colorcat_current_theme_config = self.get_default_theme_config()
            self.create_default_theme_config_file()

    def load_theme_config(self):
        """Load the theme configuration from a YAML file."""
        theme_path = self.themes_dir_path / f"{self.theme_name}.yaml"
        if theme_path.exists():
            with open(theme_path, 'r') as file:
                print(f"Theme '{self.theme_name}' loaded successfully from {theme_path}")
                return yaml.safe_load(file)
        else:
            print(f"Theme '{self.theme_name}' not found, using default theme configuration.")
            return self.get_default_theme_config()

    def save_theme_config_file(self, theme_name):
        """Saves the current theme configuration to a YAML file."""
        if not theme_name:
            print("No theme name provided. Cannot save theme configuration.")
            return

        theme_dir = self.colorcat_root_dir / self.themes_dir
        theme_dir.mkdir(parents=True, exist_ok=True)  

        theme_path = theme_dir / f"{theme_name}.yaml"

        with open(theme_path, 'w') as file:
            yaml.dump(self.colorcat_current_theme_config, file, default_flow_style=False)
        print(f"Theme '{theme_name}' saved successfully at {theme_path}")

    def apply_modifications(self, modifications_str):
        """Applies modifications to the current theme configuration based on a string of key=value pairs."""
        modifications = shlex.split(modifications_str)
        for modification in modifications:
            key, value = modification.split('=')
            # Navigate nested dictionaries
            dict_ref = self.colorcat_current_theme_config
            path_parts = key.split('.')
            for part in path_parts[:-1]:  
                if part not in dict_ref:
                    print(f"Key '{part}' not found in the configuration. Modification skipped.")
                    break
                dict_ref = dict_ref[part]
            
            if path_parts[-1] in dict_ref:
                if isinstance(dict_ref[path_parts[-1]], str):
                    dict_ref[path_parts[-1]] = value
                elif isinstance(dict_ref[path_parts[-1]], list):
                    dict_ref[path_parts[-1]] = value.split(',')
                else:
                    print(f"Unsupported modification for '{key}'.")
            else:
                print(f"Key '{path_parts[-1]}' not found in the configuration. Modification skipped.")

        print("Modifications applied successfully.")

    def show_theme_config(self, theme_name=None):
        """Displays the full YAML data of the specified or current theme and shows a sample of the colors."""
        display_theme_name = theme_name or self.theme_name

        if display_theme_name == 'default':
            theme_config = self.get_default_theme_config()
            print("Using default theme configuration:")
        else:
            theme_path = self.themes_dir_path / f'{display_theme_name}.yaml'
            if not theme_path.exists():
                print(f"Theme '{display_theme_name}' not found. Falling back to default theme configuration.")
                theme_config = self.get_default_theme_config()
            else:
                with open(theme_path, 'r') as file:
                    theme_config = yaml.safe_load(file)
                    print(f"Theme '{display_theme_name}' configuration:")

        yaml.dump(theme_config, stream=sys.stdout, sort_keys=False)

        if 'color_settings' in theme_config:
            print(f"\n{self.apply_color('Displaying theme settings for theme: ' + display_theme_name, theme_config['color_settings']['default_color']['fg_color'], theme_config['color_settings']['default_color']['bg_color'])}")
            print(f"-{'-' * 110}-")
            color_samples = [
            (setting_name, ''.join(setting_values['chars']) or 'Abc')
            for setting_name, setting_values in theme_config['color_settings'].items()
            if setting_name != 'reset'  # Skip 'reset' setting
            ]
            max_name_length = max(len(name) for name, _ in color_samples) + 2  # plus 2 for ": "
            max_sample_length = max(len(sample) for _, sample in color_samples)

            #  3 columns; easy to change
            for i, (name, sample) in enumerate(color_samples):
                fg_color, bg_color = theme_config['color_settings'][name]['fg_color'], theme_config['color_settings'][name]['bg_color']
                colored_sample = self.apply_color(sample, fg_color, bg_color)
            
                # right padding for sample
                sample_padding = max_sample_length - len(sample)
                
                # prepare name with padding
                name_with_colon = f"{name}: ".ljust(max_name_length)
                
                # entry with the calculated padding to maintain column alignment
                print(f"| {name_with_colon}{colored_sample}{' ' * sample_padding} ", end="")
                
                # break line after every 3rd column or at the end
                if (i + 1) % 3 == 0 or i == len(color_samples) - 1:
                    print("|")
        print(f"-{'-' * 110}-")
        self.draw_ascii_color_grid()

    def apply_color(self, text, fg_color, bg_color):
        """Applies foreground and background colors to the given text."""
        reset_color = '\033[0m'
        return f"{fg_color}{bg_color}{text}{reset_color}"

    def get_default_theme_config(self):
        """Generate and return a fresh copy of the default theme configuration."""
        return { 
            'offset_settings': {
            'default_fg_offset': 0,
            'default_bg_offset': 0,
            'highlight_intensity': 5
            },
            'config_settings': {
            'color_upper_bound': 255,
            'colorcat_root_dir': '~/.config/colorcat',
            'line_numbering': False,
            'theme_name': 'default',
            'themes_dir': 'themes/',
            'autogen_themes_directory': 'autogen-themes/',
            'autogen_themes': True
            },
        'color_settings': {
            'default_color': {'fg_color': '\033[38;5;15m', 'bg_color': '\033[48;5;0m', 'chars': []},
            'error': {'fg_color': '\033[38;5;181m', 'bg_color': '\033[48;5;0m', 'chars': ['ERR']},
            'reset': {'fg_color': '\033[0m', 'bg_color': '\033[0m', 'chars': ['\033[0m']},
            'curly_braces': {'fg_color': '\033[38;5;1m', 'bg_color': '\033[48;5;0m', 'chars': ['{', '}']},
            'parens': {'fg_color': '\033[38;5;163m', 'bg_color': '\033[48;5;0m', 'chars': ['(', ')']},
            'bracket_square': {'fg_color': '\033[38;5;195m', 'bg_color': '\033[48;5;0m', 'chars': ['[', ']']},
            'greater_than_less_than': {'fg_color': '\033[38;5;201m', 'bg_color': '\033[48;5;0m', 'chars': ['<', '>']},
            'single_quote': {'fg_color': '\033[38;5;11m', 'bg_color': '\033[48;5;0m', 'chars': ["'"]},
            'double_quote': {'fg_color': '\033[38;5;207m', 'bg_color': '\033[48;5;0m', 'chars': ['"']},
            'smart_quote': {'fg_color': '\033[38;5;84m', 'bg_color': '\033[48;5;0m', 'chars': ['“', '”']},
            'curly_quote': {'fg_color': '\033[38;5;86m', 'bg_color': '\033[48;5;0m', 'chars': ['‘', '’']},
            'double_low_9_quotation_mark': {'fg_color': '\033[38;5;121m', 'bg_color': '\033[48;5;0m', 'chars': ['„', '‟']},
            'multi_line_comment': {'fg_color': '\033[38;5;32m', 'bg_color': '\033[48;5;0m', 'chars': ['/*', '*/']},
            'single_line_comment': {'fg_color': '\033[38;5;36m', 'bg_color': '\033[48;5;0m', 'chars': ['//']},
            'backtick': {'fg_color': '\033[38;5;47m', 'bg_color': '\033[48;5;0m', 'chars': ['`']},
            'comma': {'fg_color': '\033[38;5;112m', 'bg_color': '\033[48;5;0m', 'chars': [',']},
            'colon': {'fg_color': '\033[38;5;172m', 'bg_color': '\033[48;5;0m', 'chars': [':']},
            'semicolon': {'fg_color': '\033[38;5;79m', 'bg_color': '\033[48;5;0m', 'chars': [';']},
            'period': {'fg_color': '\033[38;5;184m', 'bg_color': '\033[48;5;0m', 'chars': ['.']},
            'ellipsis': {'fg_color': '\033[38;5;186m', 'bg_color': '\033[48;5;0m', 'chars': ['...']},
            'exclamation': {'fg_color': '\033[38;5;155m', 'bg_color': '\033[48;5;0m', 'chars': ['!']},
            'question': {'fg_color': '\033[38;5;87m', 'bg_color': '\033[48;5;0m', 'chars': ['?']},
            'forward_slash': {'fg_color': '\033[38;5;192m', 'bg_color': '\033[48;5;0m', 'chars': ['/']},
            'backslash': {'fg_color': '\033[38;5;220m', 'bg_color': '\033[48;5;0m', 'chars': ['\\']},
            'plus': {'fg_color': '\033[38;5;208m', 'bg_color': '\033[48;5;0m', 'chars': ['+']},
            'minus': {'fg_color': '\033[38;5;127m', 'bg_color': '\033[48;5;0m', 'chars': ['-']},
            'equals': {'fg_color': '\033[38;5;202m', 'bg_color': '\033[48;5;0m', 'chars': ['=']},
            'greater_than': {'fg_color': '\033[38;5;201m', 'bg_color': '\033[48;5;0m', 'chars': ['>']},
            'less_than': {'fg_color': '\033[38;5;201m', 'bg_color': '\033[48;5;0m', 'chars': ['<']},
            'ampersand': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['&']},
            'pipe': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['|']},
            'caret': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['^']},
            'tilde': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['~']},
            'at': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['@']},
            'hash': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['#']},
            'dollar': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['$']},
            'percent': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['%']},
            'asterisk': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['*']},
            'underscore': {'fg_color': '\033[38;5;39m', 'bg_color': '\033[48;5;0m', 'chars': ['_']},
            'hyphen': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['-']},
            'plus_minus': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['±']},
            'section': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['§']},
            'pound': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['£']},
            'period_centered': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['·']},
            'degree': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['°']},
            'multiply': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['×']},
            'divide': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['÷']},
            'infinity': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['∞']},
            'not_equal': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['≠']},
            'less_than_or_equal': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['≤']},
            'greater_than_or_equal': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['≥']},
            'integral': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['∫']},
            'sum': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['∑']},
            'product': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['∏']},
            'square_root': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['√']},
            'proportional_to': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['∝']},
            'logical_and': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['∧']},
            'logical_or': {'fg_color': '\033[38;5;226m', 'bg_color': '\033[48;5;0m', 'chars': ['∨']},
        }
        }


    @staticmethod
    def get_colorcat_root_dir(args):
        """Return the colorcat root directory."""
        if args.colorcat_root_dir:
            return Path(args.colorcat_root_dir).expanduser()
        else:
            return Path.home() / '.config/colorcat'
        

    def create_default_theme_config_file(self):
        """Generate a default theme configuration file if it doesn't exist."""
        default_theme_path = self.themes_dir_path / "default.yaml"
        if not default_theme_path.exists():
            with open(default_theme_path, 'w') as file:
                yaml.dump(self.get_default_theme_config(), file)
            print(f"Default theme configuration file created at {default_theme_path}")


    def escape_unintended_sequences(text):
        """Escape unintended escape sequences in the text."""
        return re.sub(r'(\033)(?!\[\d+(?:;\d+)*m)', r'\\\1', text)


    def apply_theme(theme_name, theme_config, colorcat_current_theme_config):
        """ Applies a theme configuration to the colorcat_current_theme_config."""
        if theme_config:
            for color_name, color_data in theme_config.items():
                if color_name in colorcat_current_theme_config:
                    colorcat_current_theme_config[color_name].update(color_data)
            print(f"Theme '{theme_name}' applied successfully.")
        else:
            print(f"Theme '{theme_name}' not found.")
    global colorcat_current_theme_config


    def print_colorcat(text, color_code, reset_code='\033[0m', default_code='\033[38;5;145m'):
        """Prints the given text with the specified color code, ensuring proper reset and reapplication of default color."""
        print(f"{color_code}{text}{reset_code}{default_code}")


    def validate_theme_config(self, theme_name):
        """Validate the configuration of a given theme."""
        config_path = self.themes_dir_path / f"{theme_name}.yaml"

        if not config_path.exists():
            print(f"Configuration for theme '{theme_name}' not found.")
            return None

        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"Error parsing the YAML configuration: {exc}")
            return None
        
        required_structure = {
            'offset_settings': {
            'default_fg_offset': int,
            'default_bg_offset': int,
            'highlight_intensity': int
            },
            'config_settings': {
            'color_upper_bound': int,
            'colorcat_root_dir': str,
            'line_numbering': bool,
            'theme_name': str,
            'themes_dir': str,
            'autogen_themes_directory': str,
            'autogen_themes': bool
            },
            'color_settings': {
            'default_color': {'fg_color': str, 'bg_color': str, 'chars': list},
            'error': {'fg_color': str, 'bg_color': str, 'chars': list},
            'reset': {'fg_color': str, 'bg_color': str, 'chars': list},
            'curly_braces': {'fg_color': str, 'bg_color': str, 'chars': list},
            'parens': {'fg_color': str, 'bg_color': str, 'chars': list},
            'bracket_square': {'fg_color': str, 'bg_color': str, 'chars': list},
            'greater_than_less_than': {'fg_color': str, 'bg_color': str, 'chars': list},
            'single_quote': {'fg_color': str, 'bg_color': str, 'chars': list},
            'double_quote': {'fg_color': str, 'bg_color': str, 'chars': list},
            'smart_quote': {'fg_color': str, 'bg_color': str, 'chars': list},
            'curly_quote': {'fg_color': str, 'bg_color': str, 'chars': list},
            'double_low_9_quotation_mark': {'fg_color': str, 'bg_color': str, 'chars': list},
            'multi_line_comment': {'fg_color': str, 'bg_color': str, 'chars': list},
            'single_line_comment': {'fg_color': str, 'bg_color': str, 'chars': list},
            'backtick': {'fg_color': str, 'bg_color': str, 'chars': list},
            'comma': {'fg_color': str, 'bg_color': str, 'chars': list},
            'colon': {'fg_color': str, 'bg_color': str, 'chars': list},
            'semicolon': {'fg_color': str, 'bg_color': str, 'chars': list},
            'period': {'fg_color': str, 'bg_color': str, 'chars': list},
            'ellipsis': {'fg_color': str, 'bg_color': str, 'chars': list},
            'exclamation': {'fg_color': str, 'bg_color': str, 'chars': list},
            'question': {'fg_color': str, 'bg_color': str, 'chars': list},
            'forward_slash': {'fg_color': str, 'bg_color': str, 'chars': list},
            'backslash': {'fg_color': str, 'bg_color': str, 'chars': list},
            'plus': {'fg_color': str, 'bg_color': str, 'chars': list},
            'minus': {'fg_color': str, 'bg_color': str, 'chars': list},
            'equals': {'fg_color': str, 'bg_color': str, 'chars': list},
            'greater_than': {'fg_color': str, 'bg_color': str, 'chars': list},
            'less_than': {'fg_color': str, 'bg_color': str, 'chars': list},
            'ampersand': {'fg_color': str, 'bg_color': str, 'chars': list},
            'pipe': {'fg_color': str, 'bg_color': str, 'chars': list},
            'caret': {'fg_color': str, 'bg_color': str, 'chars': list},
            'tilde': {'fg_color': str, 'bg_color': str, 'chars': list},
            'at': {'fg_color': str, 'bg_color': str, 'chars': list},
            'hash': {'fg_color': str, 'bg_color': str, 'chars': list},
            'dollar': {'fg_color': str, 'bg_color': str, 'chars': list},
            'percent': {'fg_color': str, 'bg_color': str, 'chars': list},
            'asterisk': {'fg_color': str, 'bg_color': str, 'chars': list},
            'underscore': {'fg_color': str, 'bg_color': str, 'chars': list},
            'hyphen': {'fg_color': str, 'bg_color': str, 'chars': list},
            'plus_minus': {'fg_color': str, 'bg_color': str, 'chars': list},
            'section': {'fg_color': str, 'bg_color': str, 'chars': list},
            'pound': {'fg_color': str, 'bg_color': str, 'chars': list},
            'period_centered': {'fg_color': str, 'bg_color': str, 'chars': list},
            'degree': {'fg_color': str, 'bg_color': str, 'chars': list},
            'multiply': {'fg_color': str, 'bg_color': str, 'chars': list},
            'divide': {'fg_color': str, 'bg_color': str, 'chars': list},
            'infinity': {'fg_color': str, 'bg_color': str, 'chars': list},
            'not_equal': {'fg_color': str, 'bg_color': str, 'chars': list},
            'less_than_or_equal': {'fg_color': str, 'bg_color': str, 'chars': list},
            'greater_than_or_equal': {'fg_color': str, 'bg_color': str, 'chars': list},
            'integral': {'fg_color': str, 'bg_color': str, 'chars': list},
            'sum': {'fg_color': str, 'bg_color': str, 'chars': list},
            'product': {'fg_color': str, 'bg_color': str, 'chars': list},
            'square_root': {'fg_color': str, 'bg_color': str, 'chars': list},
            'proportional_to': {'fg_color': str, 'bg_color': str, 'chars': list},
            'logical_and': {'fg_color': str, 'bg_color': str, 'chars': list},
            'logical_or': {'fg_color': str, 'bg_color': str, 'chars': list},
            }
        }
        
        missing_keys, incorrect_type_keys = self.check_structure(config, required_structure, [])

        if missing_keys or incorrect_type_keys:
            print(f"Configuration validation issues found for theme '{theme_name}':")
            if missing_keys:
                print(f"Missing keys: {missing_keys}")
            if incorrect_type_keys:
                print(f"Incorrect type for keys: {incorrect_type_keys}")
            print("Please update the configuration file as necessary.")
        else:
            print(f"Configuration for theme '{theme_name}' validated successfully.")
            return config
        

    def check_structure(self, config, structure, path):
        """Recursively checks the config against the required structure."""
        missing, incorrect_type = [], []
        for key, expected_type in structure.items():
            actual_value = config.get(key)
            new_path = path + [key]  
            if isinstance(expected_type, dict):
                if actual_value is None or not isinstance(actual_value, dict):
                    missing.append('.'.join(new_path))
                    print(f"Missing key: {'.'.join(new_path)}") 
                else:
                    sub_missing, sub_incorrect_type = self.check_structure(actual_value, expected_type, new_path)
                    missing.extend(sub_missing)
                    incorrect_type.extend(sub_incorrect_type)
            else:
                if actual_value is None:
                    missing.append('.'.join(new_path))
                    print(f"Missing key: {'.'.join(new_path)}")  
                elif not isinstance(actual_value, expected_type):
                    incorrect_type.append('.'.join(new_path))
                    print(f"Incorrect type for key: {'.'.join(new_path)}")  
        return missing, incorrect_type

    def delete_theme(self, theme_name):
        """Deletes a theme configuration file based on the theme name provided."""
        theme_path = self.themes_dir_path / f"{theme_name}.yaml"

        if theme_path.exists():
            try:
                theme_path.unlink()
                print(f"Theme '{theme_name}' deleted successfully.")
            except Exception as e:
                print(f"Error deleting theme '{theme_name}': {e}")
        else:
            print(f"Theme '{theme_name}' not found. No file deleted.")


    def list_themes(self):
        """Lists all themes available in the themes directory."""
        themes_dir_path = self.colorcat_root_dir / 'themes'
        if not themes_dir_path.exists() or not themes_dir_path.is_dir():
            print("Themes directory does not exist or is not a directory.")
            return
        theme_files = list(themes_dir_path.glob('*.yaml'))
        if theme_files:
            print("Available themes:")
            for theme_file in theme_files:
                print(f"- {theme_file.stem}")
        else:
            print("No themes found.")


    def save_generated_theme_file(self, theme_name, updated_theme_config):
        """Saves the updated theme configuration to a file."""
        save_location = self.autogen_themes_dir / f"{theme_name}.yaml"
        with open(save_location, 'w') as file:
            yaml.dump(updated_theme_config, file, default_flow_style=False)
        print(f"Theme '{theme_name}' saved successfully at {save_location}")

    def generate_theme(self, theme_name, theme_config, offset_settings):
        """Generates a theme configuration file based on the provided theme configuration combined with the offset settings."""
        """saved t othe autogen folder"""
        updated_theme_config = self.apply_offsets_to_config(theme_config, offset_settings)
        self.save_generated_theme_file(theme_name, updated_theme_config)


    def clean_themes_directory(self):
        """This just cleans themes directory of YAML files"""
        light_purple = '\033[38;5;207m'
        pink = '\033[38;5;208m'
        themes_dir_path = self.colorcat_root_dir / 'themes'
        
        if not themes_dir_path.exists() or not themes_dir_path.is_dir():
            print("Themes directory does not exist or is not a directory.")
            return
        
        theme_files = list(themes_dir_path.glob('*.yaml'))
        if theme_files:
            for theme_file in theme_files:
                try:
                    theme_file.unlink()  
                    print(f"Deleted theme file: {theme_file.name}")
                except Exception as e:
                    print(f"Error deleting file {theme_file.name}: {e}")
        else:
            print("No theme files found to clean.")

    
    # TODO: This is just the foundation for this feature, it's not fully implemented yet
    def offset_color(offset_args: str, config: dict) -> dict:
        """
        Adjusts color values based on user-defined offsets.
        Supports global, foreground, and background offsetting with wrapping.
        """
        def parse_offset_args(offset_args):
            pattern = r"(all|\w+)\s*(\d+)?,?\s*(\d+)?"
            matches = re.finditer(pattern, offset_args, re.IGNORECASE)
            offsets = defaultdict(lambda: {'fg': 0, 'bg': 0})
            for match in matches:
                key, fg_offset, bg_offset = match.groups()
                if fg_offset:
                    offsets[key]['fg'] = int(fg_offset)
                if bg_offset:
                    offsets[key]['bg'] = int(bg_offset)
            return offsets

        def wrap_color_value(value, offset, max_value=255):
            return (value + offset) % max_value

        def apply_offsets_to_config(config, offsets):
            for category, color_codes in config['meow_colors'].items():
                if category in offsets or 'all' in offsets:
                    fg_offset = offsets.get(category, offsets['all'])['fg']
                    bg_offset = offsets.get(category, offsets['all'])['bg']
                    # Assumes color codes are stored as integers in the config
                    if 'fg' in color_codes:
                        color_codes['fg'] = wrap_color_value(color_codes.get('fg', 0), fg_offset)
                    if 'bg' in color_codes:
                        color_codes['bg'] = wrap_color_value(color_codes.get('bg', 0), bg_offset)
            return config

        offsets = parse_offset_args(offset_args)
        updated_config = apply_offsets_to_config(config.copy(), offsets)
        return updated_config
    

    colorcat_furballs = ["            .';::::::::::::::::::::::::::::::::::::::::::::::::::;,..           ","         .:dOKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKOxc'         ","       .ck0KXXNNNNNNXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXKNNNNNNNXXKOo'       ","      'd0KXXNNNNNWKc,;;cd0NWWWWWWWWWWWWWWWWWWWWWWWWWWWXkl;;;;kWNNNNNNXXKk;      ","     .d0KXXNNNNWWWo.:x,.'.:kNMMMMMMMMMMMMMMMMMMMMMMWOl..''od.;XWWNNNNXXXKk,     ","     ;kKXXXNNWWWMWc ;x;'l' .;xXMMMMMMMMMMMMMMMMMMWO:. .c;.do ,KMMWWNNXXXK0l.    ","     ;kKXXXNNWMMMWc :x;';l:;;.;kWWX0OkkxxxkO0KNW0c.,;;cc',do.'0MMMWNNXXKK0l.    ","     ;kKXXXNNWMMMWl ,d;cl;;c:;,.,,.'........'.',..;:c:;cl;lc ;XMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMk..l:';c'c;;c'c;.co;cc,c:lo.'l,::,c,;c';l,.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNc ;d:.ccc;;c,x:'ldclc;clld,,x:::;ccl';dc.'0MMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMM0,.locc'l,:c.;l';c.cl,c,:l'c:.;c'l;:llo'.xWMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMMWo.ccloc;.'::.:c;:.cc,c,;ccc.,c,.'colcl';XMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMWk..:ccol,lo.:;::;:.cc,c,;cc:,c'cd,:dccc'.lNMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMK,.::,co;.;:...,,,;,c;.c:;;;,.. ,c.'ll,;c'.xMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMd.,' 'lo:''.   '..:ol. :dc'..   .,,;lo;..;.;XMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMWc.;c,ox; ;o.  .oo.:o,...ll.,c   .dx..dx;;c.'0MMMWNNXXXKOl.    ","     ;kKXXXNNWMMMWl.::.cxdc;lc'.,oc..:c'';l'.,oc'.;lc;oxo',c.,KMMMWNNXXXKOl.    ","     ;kKXXNNNWMMMMx.':,,;;coccc:c'.,:,cc,c;;:..:c:cllc;;,,:;.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNl.,c,.;oxko:::c;';;cl;c:;,,::::cxxdc..c:.;KMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMMXl',:::c::::cld0O,.:olc..d0xlc::::cc::;':0MMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMWx..col:,:lclkWWO:....,xNM0ocl:,:cll..lNMMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMM0,;xl;;;;;:okXMMNo. ;XMMW0dc;;;;,cxc'xMMMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMWx..lc.;,'c:,,:colcclclol:;':l,';';o' cNMMMMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMMMM0'':okclccc;';;.:x0NNXkl.,:';:cclcxdc'.dWMMMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMMMK;.,,,ccccc,;'.:;'.,;,;..,c'.;,clccl;,,..kWMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNc.''';:cod'.cl..cl;:c,:;:l'.:l..ldcc:,''.,0MMMMWNNXXXX0l.    ","     ;kKXXXNNWMMMMk.'oc::;:l;':o::::l::c,::cc:c:lc',c:;::co;.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMWc :ko:dk:.'c:;.:l;;;l;.cc,;cl.':c: 'xkccko.,KMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMWc :l.,kd'.clcxcl:.;c:;,;cc.,lcdocl'.ckc.cl.'0MMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMd';'.;;'''cc;d;c;.l,;ddc'l;'l;oc;l,'',;,.;'cNMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMXl.'ko:;ccc:...:l.:c'',':c':l...,lcc:;lk:.;0MMMMWNNXXXK0l.    ","     ;kKXXXNNWWMMMMNo.;,;ccdoo,;d:''.:l;'cc'.';oc,codlc:,:':KMMMMMWNNXXXK0l.    ","     ,xKXXXNNWWWMMMMW0l..':oco,.';':dclc;clol',,..lllc,..:kNMMMMMWWNNXXXKOc.    ","     .lOKXXNNNNWWWMMMMWKxc;..,...::...cc,c,..;c.. ''.,:o0WMMMMWWWNNNNXXKKx'     ","      .lOKXXNNNNNNNNNNNNNNXOxl:;','....'......,',:cokKNNNNNNNNNNNNNNNXK0d'      ","        ,dOKXXXXXNNNXXNNNNNNNNNNK0OkxdddddddxkOKXNNNNNNNNNNNNNNNNNXXK0x:.       ","         .,cdk00KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000KKK0Oxl;.         ","             ..'''''''''''''''''''''''''''''''''''''''''''''''''''.             ","             Colorcat by Ben Gorlick (github: bgorlick) (c) 2024 | MIT     \n",]

    # this is just for meow
    def meow(self, colorcat=None, s_col=1):
        """Prints a colorful ASCII cat."""
        if colorcat is None:
            colorcat = self.colorcat_furballs
        width = max(len(furball) for furball in colorcat)
        c_col = s_col
        grad_meow = []
        print("\n")
        for row in colorcat:
            grad_l = ""
            c_col = s_col
            for char in row:
                if char != ' ':
                    while c_col % 32 == 0:
                        c_col += 1
                    grad_l += f"\x1b[38;5;{c_col % 32}m{char}\x1b[0m"
                    c_col += 1
                else:
                    grad_l += ' '
            grad_meow.append(grad_l)
        for furball in grad_meow:
            print(furball)
        print("\n")

    def print_color_block(self, fg_color, bg_color, text):
        return f'\x1b[38;5;{fg_color}m\x1b[48;5;{bg_color}m{text}\x1b[0m'

    def draw_ascii_color_grid(self):
        print("Standard colors 0-15:")
        for color in range(0, 16):
            fg_color = 15 if color < 6 else 0
            print(self.print_color_block(fg_color, color, f"  {str(color).ljust(3)}"), end=' ')
        print("\n")
        print("Colors 16-231:")
        fg_color = 15
        for color in range(16, 232):
            if (color - 16) % 36 == 0:
                fg_color = 15  
            elif (color - 16) % 2 == 0:
                fg_color -= 1  
                fg_color = max(fg_color, 232)  
            print(self.print_color_block(fg_color, color, f" {str(color).ljust(3)}"), end='')
            if (color - 15) % 36 == 0:
                print()  
        print() 
        print("Grayscale colors 232-255:")
        for color in range(232, 256):
            fg_color = 256-8 if color < 236 else 16
            print(self.print_color_block(fg_color, color, f" {str(color).ljust(3)} "), end='')
        print()
        sys.exit(0)


def main():
    color_cat_instance = ColorCatThemes(theme_name='default', colorcat_root_dir=Path.home() / '.config/colorcat')
    def parse_args():
        parser = AugmentParser(description='Colorcat is a tool for managing and applying color themes to the terminal.', color_cat_instance=color_cat_instance)
        parser.add_argument('-l', '--list', action='store_true', help='List available themes')
        parser.add_argument('-g', '--generate', action='store_true', help='Generate a new theme')
        parser.add_argument('-d', '--delete', action='store_true', help='Delete a theme')
        parser.add_argument('-o', '--offset', type=str, help='Offset the colors of the current theme')
        parser.add_argument('-m', '--meow', action='store_true', help='Meow')
        parser.add_argument('-mod', '--modify-theme', type=str, help='Modify the current theme with key=value pairs separated by commas, e.g., -mod "default_color.fg_color=\\033[38;5;82m,default_color.bg_color=\\033[48;5;239m,default_color.chars=[\'@\']"')
        parser.add_argument('-save', '--save-theme', type=str, help='Takes a name e.g., -save "MyTheme" and saves the current theme settings to a YAML file in the themes directory')
        parser.add_argument('-t', '--theme', default='default', help='Specify the theme name to use')
        parser.add_argument('-dir', '--colorcat-dir', default=str(Path.home() / '.config/colorcat'), help='The directory where colorcat configuration is stored')
        parser.add_argument('-col', '--colors', action='store_true', help='Display an ASCII color grid')
        parser.add_argument('-show', '--show-theme-config', action='store_true', help='Show the current theme configuration')
        parser.add_argument('--clean', action='store_true', help='Clean the colorcat directory (delete all theme files)')
        args = parser.parse_args()
        return args
  
    args = parse_args()

    if args.colors:
        color_cat_instance.draw_ascii_color_grid()
    
    if args.theme:
        color_cat_instance.validate_theme_config(args.theme)

    if args.modify_theme:
        color_cat_instance.apply_modifications(args.modify_theme)

    if args.save_theme:
        color_cat_instance.save_theme_config_file(args.save_theme)

    if args.show_theme_config:
        color_cat_instance.show_theme_config(theme_name=args.theme)

    if args.list:
        color_cat_instance.list_themes()
    
    if args.delete:
        color_cat_instance.delete_theme(args.theme, args.colorcat_dir)

    if args.generate:
        color_cat_instance.generate_theme(args.theme, args.colorcat_dir, args.autogen_themes_directory)

    if args.meow:
        print("Meow...")
        color_cat_instance.meow(color_cat_instance.colorcat_furballs, random.randint(1, 255))
        sys.exit(0)

    if args.offset:
        color_cat_instance.offset_color(args.theme, color_cat_instance.current_theme_config)

    if args.clean:
        color_cat_instance.clean_themes_directory(args.colorcat_dir)

    if args is None:
        print("No arguments provided. Exiting.")
        color_cat_instance.meow(color_cat_instance.colorcat_furballs, random.randint(1, 255))
        sys.exit(0)
    
if __name__ == '__main__':
    main()
    sys.exit(0)