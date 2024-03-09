#!/usr/bin/env python3

# Filename: colorcat-config-wip.py (work in progress)
# Colorcat - A powerful yet simple syntax highlighter for the terminal viewing of files.
# (c) 2024 - Ben Gorlick | MIT License | Attribution to the original author is required - free to use, modify, and distribute.

# Initial colorcat framework that will get merged into colorcat.py -- it's a work in progress.
# The idea here is to migrate the configuration and management of the configuration to YAML (colorcat currently is hard-coded w/ a JSON style color config)

# This introduces themes, and will make supporting 'offsets' for foreground and background colors easier to manage. 
# The idea is to enable a user to create a theme, and then apply offsets to the theme to create a new theme. 
# This supports rapidly creating new themes, and also allows for the user to create a theme that is a 'child' of another theme, and then apply offsets to the child theme to create a new theme.

import os, sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
import json
import re, random
import io



def capture_help_message(parser):
    help_message = ""
    with io.StringIO() as help_message:
         parser.print_help(file=help_message)
         help_message = help_message.getvalue()
         return help_message
    

def apply_syntax_highlighting_to_help(help_message):
    colors = {
        'escape_sequence': '\033[38;5;93m',
        'curly_braces': '\033[38;5;1m',
        'parens': '\033[38;5;163m',
        'bracket_square': '\033[38;5;202m',
        'pacman_greaterthan_lessthan': '\033[38;5;201m',
        'single_quote': '\033[38;5;11m',
        'double_quote': '\033[38;5;51m',
        'smart_quote': '\033[38;5;84m',
        'curly_quote': '\033[38;5;86m',
        'double_low_9_quotation_mark': '\033[38;5;121m',
        'multi_line_comment': '\033[38;5;32m',
        'single_line_comment': '\033[38;5;36m',
        'backtick': '\033[38;5;47m',
        'comma': '\033[38;5;112m',
        'colon': '\033[38;5;172m',
        'semicolon': '\033[38;5;79m',
        'period': '\033[38;5;184m',
        'ellipsis': '\033[38;5;186m',
        'exclamation': '\033[38;5;155m',
        'question': '\033[38;5;87m',
    }
    symbol_colors = {
        '{': 'curly_braces',
        '}': 'curly_braces',
        '(': 'parens',
        ')': 'parens',
        '[': 'bracket_square',
        ']': 'bracket_square',
        '<': 'pacman_greaterthan_lessthan',
        '>': 'pacman_greaterthan_lessthan',
        "'": 'single_quote',
        '"': 'double_quote',
        '‘': 'smart_quote',
        '“': 'double_low_9_quotation_mark',
        '`': 'backtick',
        ',': 'comma',
        ':': 'colon',
        ';': 'semicolon',
        '.': 'period',
        '...': 'ellipsis',
        '!': 'exclamation',
        '?': 'question',
        
    }
    highlighted_message = ""
    for char in help_message:
        if char in symbol_colors:
            highlighted_message += f"{symbol_colors[char]}{char}{colors['reset']}"
        else:
            highlighted_message += f"{colors['strings']}{char}{colors['reset']}"
    return highlighted_message


sample_config = {'colorcat_root_dir': str(Path.home() / '.config/colorcat'), 'default_bg_hl_color': 239, 'color_upper_bound': 255, 'meow_colors': {'escape_sequence': 93, 'curly_braces': 1, 'parens': 163, 'bracket_square': 202, 'pacman_greaterthan_lessthan': 201, 'single_quote': 11, 'double_quote': 51, 'smart_quote': 84, 'curly_quote': 86, 'right_single_quotation_mark': 123, 'double_low_9_quotation_mark': 121, 'multi_line_comment': 32, 'single_line_comment': 36, 'backtick': 47, 'comma': 112, 'colon': 172, 'semicolon': 79, 'period': 184, 'ellipsis': 186, 'exclamation': 155, 'question': 87, 'strings': 81, 'function_names': 189, 'conditionals': 209, 'builtin_functions': 181, 'numbers': 11, 'operators': 207, 'punctuation': 87, 'variables': 203}, 'offset_settings': {'default_fg_offset': 0, 'default_bg_offset': 0, 'highlight_intensity': 5}, 'script_configs': {'line_numbering': False, 'theme_name': 'default', 'themes_dir': 'themes/', 'autogen_themes_directory': 'autogen-themes/', 'autogen_themes': True}}

def validate_and_backup_config(config_path):
    """Validate config keys and create a backup if necessary before returning the loaded config."""
    required_structure = {
        'colorcat_root_dir': str,
        'script_configs': {
            'themes_dir': str,
            'autogen_themes_directory': str,
            'autogen_themes': bool,
        }
    }
    
    def check_structure(config, structure, path=''):
        missing, incorrect_type = [], []
        for key, value_type in structure.items():
            full_key = f"{path}.{key}" if path else key
            if isinstance(value_type, dict):
                if key in config and isinstance(config[key], dict):
                    sub_missing, sub_incorrect = check_structure(config[key], value_type, full_key)
                    missing.extend(sub_missing)
                    incorrect_type.extend(sub_incorrect)
                else:
                    missing.append(full_key)
            else:
                if key not in config:
                    missing.append(full_key)
                elif not isinstance(config.get(key), value_type):
                    incorrect_type.append(full_key)
        return missing, incorrect_type

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    missing_keys, incorrect_type_keys = check_structure(config, required_structure)

    if missing_keys or incorrect_type_keys:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = config_path.with_name(f"{config_path.stem}_backup_{timestamp}{config_path.suffix}")
        config_path.rename(backup_path)
        print_colorcat(f"Missing or incorrect type keys: {', '.join(missing_keys + incorrect_type_keys)}.")
        print_colorcat(f"A backup of the current config has been created: {backup_path}")
        create_sample_config(config_path.parent, config_path.name)
    return config


def load_config(config_dir, config_filename):
    """Load YAML configuration, validating and handling missing keys."""
    config_path = Path(config_dir).expanduser() / config_filename
    config_path.parent.mkdir(parents=True, exist_ok=True)  

    if not config_path.exists():
        print_colorcat("No user config file found. Creating a sample config file...")
        create_sample_config(config_dir, config_filename)
    return validate_and_backup_config(config_path)

def create_sample_config(config_dir, config_filename):
    """Creates a new sample configuration with enhanced data types and default settings."""
    config_path = Path(config_dir).expanduser() / config_filename
    yaml.dump(sample_config, open(config_path, 'w'), default_flow_style=False)
    print_colorcat(f"Sample config created at {config_path}")

def get_full_path(config, key):
    """Return the full path for a given configuration key."""
    root_dir = Path(config['colorcat_root_dir']).expanduser()
    return root_dir / config['script_configs'].get(key, '')

def escape_unintended_sequences(text):
    """Escape unintended escape sequences in the text."""
    return re.sub(r'(\033)(?!\[\d+(?:;\d+)*m)', r'\\\1', text)

def apply_color(text, color_code, reset_code='\033[0m', default_code='\033[38;5;145m'):
    """Applies a color code to the given text, ensuring proper reset and reapplication of default color."""
    return f"{color_code}{text}{reset_code}{default_code}"

def print_colorcat(message, config=None):
    message = escape_unintended_sequences(message)
    color_codes = {
        'default': '\033[38;5;81m', 
        'special': {
            'period': '\033[38;5;184m',
            'slash': '\033[38;5;192m',
            'colon': '\033[38;5;172m',
            'semicolon': '\033[38;5;79m',
            'brackets': '\033[38;5;202m',
        },
        'reset': '\033[0m'
    }

    special_chars = {
        '.': 'period',
        '/': 'slash',
        ':': 'colon',
        ';': 'semicolon',
        '[': 'brackets',
        ']': 'brackets',
        '{': 'brackets',
        '}': 'brackets',
    }
    new_message = ''
    for char in message:
        if char in special_chars:
            new_message += apply_color(char, color_codes['special'][special_chars[char]], color_codes['reset'], color_codes['default'])
        else:
            new_message += char
    new_message += color_codes['reset']
    print(new_message)


def purge_directory(directory, config=None):
    red = '\033[38;5;181m'
    reset = '\033[0m'
    default = '\033[38;5;81m'
    semicolon = '\033[38;5;79m'
    period = '\033[38;5;184m'
    critical_directories = [str(Path.home() / '.config'), str(Path.home()), '/', '/home/ai/bad', '/bin', '/boot', '/dev', '/etc', '/lib', '/lib64', '/opt', '/proc', '/root', '/sbin', '/srv', '/sys', '/usr', '/var']
    if str(directory) in critical_directories:

        print(f"\n{red}!WARNING!: {reset}{default}Attempting to remove {reset}{red}{directory}{reset}{default} could result in a non-functional system{period}{reset}\n")
        print(f"{default}Colorcat was designed to attempt to avoid removing potentially {reset}{red}system-critical{reset} {default}directories{period}.{reset}\n")
        print_colorcat(f"Please remove critical directories manually, and only if necessary.\n", config)
        print(f"{default}Critical directories include{semicolon}: {red}{', '.join(critical_directories)}{reset}\n")
        return
    
    
    confirmation = input(f"{default}You must WOOF (in CAPS) to permanently delete {reset}{red}{directory}{reset}{default} -- [WOOF (for yes) / Meow (for no)]: {reset}")
    if confirmation == 'WOOF':
        print(f"{reset}{red}WOOF{reset}{default} received... Permanently deleting {reset}{red}{directory}{default}...")
        for item in Path(directory).iterdir():
            if item.is_dir():
                purge_directory(item, config)
            else:
                item.unlink()  
        Path(directory).rmdir()  
        print_colorcat(f"Permanently deleted {directory}", config)
    else:
        print_colorcat("Purge cancelled. No files were deleted.", config)


colorcat_furballs = ["            .';::::::::::::::::::::::::::::::::::::::::::::::::::;,..           ","         .:dOKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKOxc'         ","       .ck0KXXNNNNNNXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXKNNNNNNNXXKOo'       ","      'd0KXXNNNNNWKc,;;cd0NWWWWWWWWWWWWWWWWWWWWWWWWWWWXkl;;;;kWNNNNNNXXKk;      ","     .d0KXXNNNNWWWo.:x,.'.:kNMMMMMMMMMMMMMMMMMMMMMMWOl..''od.;XWWNNNNXXXKk,     ","     ;kKXXXNNWWWMWc ;x;'l' .;xXMMMMMMMMMMMMMMMMMMWO:. .c;.do ,KMMWWNNXXXK0l.    ","     ;kKXXXNNWMMMWc :x;';l:;;.;kWWX0OkkxxxkO0KNW0c.,;;cc',do.'0MMMWNNXXKK0l.    ","     ;kKXXXNNWMMMWl ,d;cl;;c:;,.,,.'........'.',..;:c:;cl;lc ;XMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMk..l:';c'c;;c'c;.co;cc,c:lo.'l,::,c,;c';l,.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNc ;d:.ccc;;c,x:'ldclc;clld,,x:::;ccl';dc.'0MMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMM0,.locc'l,:c.;l';c.cl,c,:l'c:.;c'l;:llo'.xWMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMMWo.ccloc;.'::.:c;:.cc,c,;ccc.,c,.'colcl';XMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMWk..:ccol,lo.:;::;:.cc,c,;cc:,c'cd,:dccc'.lNMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMK,.::,co;.;:...,,,;,c;.c:;;;,.. ,c.'ll,;c'.xMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMd.,' 'lo:''.   '..:ol. :dc'..   .,,;lo;..;.;XMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMWc.;c,ox; ;o.  .oo.:o,...ll.,c   .dx..dx;;c.'0MMMWNNXXXKOl.    ","     ;kKXXXNNWMMMWl.::.cxdc;lc'.,oc..:c'';l'.,oc'.;lc;oxo',c.,KMMMWNNXXXKOl.    ","     ;kKXXNNNWMMMMx.':,,;;coccc:c'.,:,cc,c;;:..:c:cllc;;,,:;.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNl.,c,.;oxko:::c;';;cl;c:;,,::::cxxdc..c:.;KMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMMXl',:::c::::cld0O,.:olc..d0xlc::::cc::;':0MMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMWx..col:,:lclkWWO:....,xNM0ocl:,:cll..lNMMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMM0,;xl;;;;;:okXMMNo. ;XMMW0dc;;;;,cxc'xMMMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMWx..lc.;,'c:,,:colcclclol:;':l,';';o' cNMMMMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMMMM0'':okclccc;';;.:x0NNXkl.,:';:cclcxdc'.dWMMMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMMMK;.,,,ccccc,;'.:;'.,;,;..,c'.;,clccl;,,..kWMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNc.''';:cod'.cl..cl;:c,:;:l'.:l..ldcc:,''.,0MMMMWNNXXXX0l.    ","     ;kKXXXNNWMMMMk.'oc::;:l;':o::::l::c,::cc:c:lc',c:;::co;.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMWc :ko:dk:.'c:;.:l;;;l;.cc,;cl.':c: 'xkccko.,KMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMWc :l.,kd'.clcxcl:.;c:;,;cc.,lcdocl'.ckc.cl.'0MMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMd';'.;;'''cc;d;c;.l,;ddc'l;'l;oc;l,'',;,.;'cNMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMXl.'ko:;ccc:...:l.:c'',':c':l...,lcc:;lk:.;0MMMMWNNXXXK0l.    ","     ;kKXXXNNWWMMMMNo.;,;ccdoo,;d:''.:l;'cc'.';oc,codlc:,:':KMMMMMWNNXXXK0l.    ","     ,xKXXXNNWWWMMMMW0l..':oco,.';':dclc;clol',,..lllc,..:kNMMMMMWWNNXXXKOc.    ","     .lOKXXNNNNWWWMMMMWKxc;..,...::...cc,c,..;c.. ''.,:o0WMMMMWWWNNNNXXKKx'     ","      .lOKXXNNNNNNNNNNNNNNXOxl:;','....'......,',:cokKNNNNNNNNNNNNNNNXK0d'      ","        ,dOKXXXXXNNNXXNNNNNNNNNNK0OkxdddddddxkOKXNNNNNNNNNNNNNNNNNXXK0x:.       ","         .,cdk00KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000KKK0Oxl;.         ","             ..'''''''''''''''''''''''''''''''''''''''''''''''''''.             ","             Colorcat by Ben Gorlick (github: bgorlick) (c) 2024 | MIT     \n",]

def meow(colorcat=None, s_col=1):
    if colorcat is None:
        colorcat = colorcat_furballs
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

def clean_directory(directory):
    light_purple = '\033[38;5;207m'
    pink = '\033[38;5;208m'
    reset = '\033[0m'
    default = '\033[38;5;81m'
    red = '\033[38;5;181m'
    semicolon = '\033[38;5;79m'
    period = '\033[38;5;184m'
    critical_directories = [str(Path.home() / '.config'), str(Path.home()), '/', '/home/ai/bad', '/bin', '/boot', '/dev', '/etc', '/lib', '/lib64', '/opt', '/proc', '/root', '/sbin', '/srv', '/sys', '/usr', '/var']
    if str(directory) in critical_directories:
        print(f"\n{red}!WARNING!: {reset}{default}Attempting to remove {reset}{red}{directory}{reset}{default} could result in a non-functional system{period}{reset}\n")
        print(f"{default}Colorcat was designed to attempt to avoid removing potentially {reset}{red}system-critical{reset} {default}directories{period}.{reset}\n")
        print_colorcat(f"Please remove critical directories manually, and only if necessary.\n", config)
        print(f"{default}Critical directories include{semicolon}: {red}{', '.join(critical_directories)}{reset}\n")
        return
    
    for item in Path(directory).iterdir():
        if item.is_dir():
            clean_directory(item)  
            item.rmdir()  
        else:
            item.unlink() 
    print(f"{default}Directory {light_purple}{directory}{default} has been {pink}cleaned recursively.{reset}")

def main():
    parser = argparse.ArgumentParser(description='Manage ColorCat configurations.')
    parser.add_argument('--colorcat_dir', type=str, default=str(Path.home() / '.config/colorcat/'), help='The directory where the config file is located')
    parser.add_argument('--config_file', type=str, default='colorcat.config.yaml', help='The name of the config file')
    parser.add_argument('--clean', action='store_true', help='Clean out all themes, configs, etc., from the specified colorcat_dir.')
    parser.add_argument('--purge', action='store_true', help='Prompt for confirmation before permanently deleting the specified colorcat_dir or its default.')
    parser.add_argument('--show-config', action='store_true', help='Show the current configuration settings.')  
    args, unknown = parser.parse_known_args()
    
    default = '\033[38;5;81m'
    reset = '\033[0m'
    brackets = '\033[38;5;202m'
    semicolon = '\033[38;5;79m'
    slash = '\033[38;5;192m'
    period = '\033[38;5;184m'

    try:
        if '-h' in unknown or '--help' in unknown:
            help_message = capture_help_message(parser)
            print(apply_syntax_highlighting_to_help(help_message))
            sys.exit(0)

        if args.show_config:
            config = load_config(args.colorcat_dir, args.config_file)
            print_colorcat(f"User config file found at {args.colorcat_dir}/{args.config_file}", config)
            print_colorcat(f"Themes directory: {get_full_path(config, 'themes_dir')}", config)
            print_colorcat(f"Autogen themes directory: {get_full_path(config, 'autogen_themes_directory')}", config)
            print_colorcat(json.dumps(config, indent=4))

            sys.exit(0)
        if args.clean:
            clean_directory(args.colorcat_dir)
        elif args.purge:
            print(f"Prompt for confirmation before permanently deleting {args.colorcat_dir} or its default.")
        else:
            print("No action specified. Please provide either --clean or --purge.")

        if args.purge:
            if args.colorcat_dir == str(Path.home() / '.config/colorcat/') and not Path(args.colorcat_dir).exists():
                print(f"{default}Colorcat directory not found at {reset}{brackets}{args.colorcat_dir}{reset}")
                make_sample = input(f"{default}Would you like to create a new sample config file? {brackets}[{default}Meow {slash}/{default} WOOF{brackets}]{reset}{semicolon}:{reset} ")
                if make_sample.lower() == 'meow':
                    print("\n")
                    config = load_config(args.colorcat_dir, args.config_file)
                else:
                    meow(colorcat_furballs, random.randint(1, 255))
                    print(f"\n{default}                For meow... no new sample config shall be created.{reset}\n")
                    #exit
                    sys.exit(0)
            else:
                purge_directory(args.colorcat_dir)
                make_sample = input(f"{default}Would you like to create a new sample config file? {brackets}[{default}Meow {slash}/{default} WOOF{brackets}]{reset}{semicolon}:{reset} ")
                if make_sample.lower() == 'meow':
                    print("\n")
                    config = load_config(args.colorcat_dir, args.config_file)
                else:
                    meow(colorcat_furballs, random.randint(1, 255))
                    print(f"\n{default}                For meow... no new sample config shall be created.{reset}\n")
                    sys.exit(0)

                    
        config = load_config(args.colorcat_dir, args.config_file)
        themes_dir = get_full_path(config, 'themes_dir')
        autogen_themes_directory = get_full_path(config, 'autogen_themes_directory')

        if config:
            print_colorcat(f"User config file found at {args.colorcat_dir}/{args.config_file}", config)
            print_colorcat(f"Themes directory: {themes_dir}", config)
            print_colorcat(f"Autogen themes directory: {autogen_themes_directory}", config)
            sys.exit(0)
        
        create_sample_config(args.colorcat_dir, args.config_file)
        print_colorcat(f"No user config file found. Creating a sample config file at {args.colorcat_dir}/{args.config_file}", config)
        print_colorcat(f"Themes directory: {themes_dir}", config)
        print_colorcat(f"Autogen themes directory: {autogen_themes_directory}", config)

    except Exception as e:
        print_colorcat(f"An error occurred: {e}", config)
        sys.exit(0)

if __name__ == '__main__':
    main()