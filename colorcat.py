#!/usr/bin/env python3

# Colorcat - A powerful yet simple syntax highlighter for the terminal viewing of files.
# (c) 2024 - Ben Gorlick | MIT License | Attribution to the original author is required - free to use, modify, and distribute.
# Colorcat enhances viewing of file contents in the terminal by colorizing syntax.
# Version: 0.0.0.2

# At times neither cat, nor bat are make seperating concerns when viewing dense files easy.  This is where colorcat comes in. 
# Colorcat is a simplified syntax highlighter for terminal use, utilizing Python's pygmentize.

# Features include language detection, bracket coloring, line numbers, and custom line highlighting.
# Designed to easily change colors, add new features and filters and to illustrate how to use pygments and filters.

# The concepts demonstrated are easily extendable to create your own custom syntax highlighting filters and styles in other projects.

# Pygments can apply the 256-color terminal formatter and also map colors to use the 8 default ANSI colors. 
# Those are: ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'].
# Usage: colorcat.py [filename] [-ln] [-hln]
#   filename: The file to be highlighted
#   -ln, --line-numbers: Display line numbers
#   -hln, --highlight-lines: Highlight lines with a grey background, separated by commas (e.g., "10,30")
#   -m, --meow: Make the cat go meow

# If you want to highlight specific lines in a file you can do so like this (eg. highlighting lines 279 and 281)
# python colorcat.py -hln 279,281 /path/to/file.py
# You can rename this file to colorcat and make it executable to use it as a drop-in replacement for cat or bat.

# Just rename it to colorcat, and move it to a directory in your PATH, such as /usr/local/bin, and make it executable with chmod +x colorcat.
# PS. --meow is a fun little easter egg that makes the cat go meow.

# Todo Ideas: 
# - A dynamic brute force method that tries a multitude of styles and filters, saving each to a file, outputting the # to the user as it goes.
# - Style templates that are easy to save and load, and can be shared with others.
# - A way to save and load custom styles and filters (coming soon)
# - A way to adjust the colors of the syntax highlighting (disabled for now, coming soon along with offesetting colors)

import re
from collections import defaultdict
import argparse
import sys
import io
import os
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename, guess_lexer, get_lexer_by_name
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.style import Style
from pygments.token import Token, Generic
from pygments.filters import Filter
from pygments.styles import get_all_styles, get_style_by_name
import traceback # for debugging
import random
import signal
import itertools


sys.stdout.write("\x1b[?7l")

# added this for illustrative purposes, to show how to create a custom style and extend an existing one
class CustomStyle(Style):
    default_style = ""
    styles_for_light_text = {
        Token.Generic.Subheading: 'bg:[48;47m', 
    }

    styles_for_dark_text = {
        Token.Generic.Subheading: 'bg:#f0f0f0', 
        Token.LineNumber: 'bg:#f0f0f0' 
    }

def extend_style(base_style_name):
    base = get_style_by_name(base_style_name)
    extended_styles = base.styles.copy()
    extended_styles.update(CustomStyle.styles)
    return type('ExtendedStyle', (base,), {'styles': extended_styles})

class SpecificHighlightFilter(Filter):
    meow_colors = {
        'escape_sequence': '\033[38;5;93m',
        'curly_braces': '\033[38;5;1m', # curly braces
        'parens': '\033[38;5;163m', 
        'bracket_square': '\033[38;5;202m', 
        'pacman_greaterthan_lessthan': '\033[38;5;201m',
        'single_quote': '\033[38;5;11m',
        'double_quote': '\033[38;5;51m',
        'smart_quote': '\033[38;5;84m',
        'curly_quote': '\033[38;5;86m',
        'right_single_quotation_mark': '\033[38;5;123m',
        'double_low_9_quotation_mark': '\033[38;5;121m', # german/polish quotes :) sprechen sie deutsch?
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
        'strings': '\033[38;5;81m',
        'function_names': '\033[38;5;189m',
        'conditionals': '\033[38;5;209m',
        'builtin_functions': '\033[38;5;181m',
        'numbers': '\033[38;5;11m',
        'operators': '\033[38;5;207m',
        'punctuation': '\033[38;5;87m',
        'variables': '\033[38;5;203m',
        'reset': '\033[0m'
    }
    def filter(self, _, stream):
        reset_color = SpecificHighlightFilter.meow_colors['reset']
        for ttype, value in stream:
            if value in "[]":
                yield Token.Text,  SpecificHighlightFilter.meow_colors['bracket_square'] + value + reset_color
            elif value in "{}":
                yield Token.Text,  SpecificHighlightFilter.meow_colors['curly_braces'] + value + reset_color
            elif value in "()":
                yield Token.Text,  SpecificHighlightFilter.meow_colors['parens'] + value + reset_color
            elif value in "<>":
                yield Token.Text,  SpecificHighlightFilter.meow_colors['pacman_greaterthan_lessthan'] + value + reset_color
            # highlight the escape sequences
            elif value in "\\": 
                yield Token.Text,  SpecificHighlightFilter.meow_colors['escape_sequence'] + value + reset_color
            elif value in "'": 
                yield Token.Text,  SpecificHighlightFilter.meow_colors['single_quote'] + value + reset_color
            elif value in "\"": # backslash to escape the double quote
                yield Token.Text,  SpecificHighlightFilter.meow_colors['double_quote'] + value + reset_color
            elif value in "`": # backtick
                yield Token.Text,  SpecificHighlightFilter.meow_colors['backtick'] + value + reset_color
            elif value in "“”":
                yield Token.Text,  SpecificHighlightFilter.meow_colors['curly_quote'] + value + reset_color
            elif value in "’": # right single quotation mark
                yield Token.Text,  SpecificHighlightFilter.meow_colors['right_single_quotation_mark'] + value + reset_color
            elif value in "„": # double low-9 quotation mark
                yield Token.Text,  SpecificHighlightFilter.meow_colors['double_low_9_quotation_mark'] + value + reset_color
            elif value in ",": # comma
                yield Token.Text,  SpecificHighlightFilter.meow_colors['comma'] + value + reset_color
            elif value in ":": # colon
                yield Token.Text,  SpecificHighlightFilter.meow_colors['colon'] + value + reset_color
            elif value in ";": # semicolon
                yield Token.Text,  SpecificHighlightFilter.meow_colors['semicolon'] + value + reset_color
            elif value in ".": # period
                yield Token.Text,  SpecificHighlightFilter.meow_colors['period'] + value + reset_color
            elif value in "…": # ellipsis
                yield Token.Text,  SpecificHighlightFilter.meow_colors['ellipsis'] + value + reset_color
            elif value in "!": # exclamation
                yield Token.Text,  SpecificHighlightFilter.meow_colors['exclamation'] + value + reset_color
            elif value in "?": # question
                yield Token.Text,  SpecificHighlightFilter.meow_colors['question'] + value + reset_color
            elif ttype in Token.Comment.Multiline: # Multi-line comments
                yield Token.Comment.Multiline,  SpecificHighlightFilter.meow_colors['multi_line_comment'] + value + reset_color
            elif ttype in Token.Comment.Single: # Single-line comments
                yield Token.Comment.Single,  SpecificHighlightFilter.meow_colors['single_line_comment'] + value + reset_color
            elif ttype in Token.Literal.String: # Strings
                yield Token.Literal.String,  SpecificHighlightFilter.meow_colors['strings'] + value + reset_color
            elif ttype in Token.Literal.String.Single:
                yield Token.Literal.String.Single,  SpecificHighlightFilter.meow_colors['strings'] + value + reset_color 
            # function names like this
            elif ttype in Token.Name.Function: #  function names
                yield Token.Name.Function,  SpecificHighlightFilter.meow_colors['function_names'] + value + reset_color
            # conditionals like if else while for etc
            elif ttype in Token.Keyword: # conditionals
                yield Token.Keyword,  SpecificHighlightFilter.meow_colors['conditionals'] + value + reset_color
            # things like print, input, etc
            elif ttype in Token.Name.Builtin:
                yield Token.Name.Builtin,  SpecificHighlightFilter.meow_colors['builtin_functions'] + value + reset_color
            # numbers
            elif ttype in Token.Number:
                yield Token.Number,  SpecificHighlightFilter.meow_colors['numbers'] + value + reset_color
            # operators like + - * / etc
            elif ttype in Token.Operator:
                yield Token.Operator,  SpecificHighlightFilter.meow_colors['operators'] + value + reset_color
            elif ttype in Token.Name: # variables
                yield Token.Name,  SpecificHighlightFilter.meow_colors['variables'] + value + reset_color
            elif ttype in Token.Generic.Subheading:
                yield Token.Generic.Subheading,  SpecificHighlightFilter.meow_colors['light_grey'] + value + reset_color
            else:
                yield ttype, value

class BackgroundHighlightFilter(Filter):

    default_bg_hl_color = 239 

    #def __init__(self, lines_to_highlight, bg_hl_color=None, **options):
    def __init__(self, lines_to_highlight, bg_hl_color=None, font_style=None, font_color=None, **options):
        if isinstance(lines_to_highlight, str):
            self.lines_to_highlight = set(parse_line_ranges(lines_to_highlight))
        elif isinstance(lines_to_highlight, set):
            self.lines_to_highlight = lines_to_highlight
        else:
            raise ValueError("lines_to_highlight must be a set or a string.")
        
        self.bg_hl_color = bg_hl_color or BackgroundHighlightFilter.default_bg_hl_color
        self.bg_color = f'\033[48;5;{self.bg_hl_color}m'

        self.font_style = self.font_style_mapping(font_style) if font_style else ''
        self.font_color = self.font_color_mapping(font_color) if font_color else ''
        self.reset_color = '\033[0m'
        super().__init__(**options)

    def filter(self, lexer, stream):
        line_number = 1
        for ttype, value in stream:
            lines = value.split('\n')
            for i, line in enumerate(lines):
                if line_number in self.lines_to_highlight:
                    # Here we call apply_styles to get the styled line
                    styled_line = self.apply_styles(line)
                    yield ttype, styled_line
                    if i < len(lines) - 1:
                        yield Token.Text, '\n'
                else:
                    yield ttype, line + ('\n' if i < len(lines) - 1 else '')
                if i < len(lines) - 1:
                    line_number += 1 

    def apply_styles(self, line):
        # Apply background color
        bg_color_code = f'\033[48;5;{self.bg_hl_color}m' if self.bg_hl_color else ''
        
        # Apply font style and color
        font_style_code = self.font_style_mapping(self.font_style) if self.font_style else ''
        font_color_code = self.font_color_mapping(self.font_color) if self.font_color else ''
        
        return f"{bg_color_code}{font_style_code}{font_color_code}{line}{self.reset_color}"

    @staticmethod
    def font_style_mapping(style):
        styles = {
            'bold': '\033[1m',
        }
        return styles.get(style, '')

    @staticmethod
    def font_color_mapping(color):
        colors = {
            'red': '\033[31m',
        }
        return colors.get(color, '')


def read_input(filename):
    code = None
    if not sys.stdin.isatty():
        code = sys.stdin.read()
        filename = filename or "stdin_input"
    elif filename:
        try:
            with open(filename, 'r') as file:
                code = file.read()
        except FileNotFoundError:
            print(f"File not found: {filename}", file=sys.stderr)
            sys.exit(1)
    return code, filename

def highlight_with_colorcat_colors(code, filename=None, show_line_numbers=False, lines_to_highlight='', language=None):
    try:
        lexer = detect_language_type(code, filename, language) 
    except Exception as e:
        print(f"Fallback to plain text due to error: {e}", file=sys.stderr)
        lexer = get_lexer_by_name("text")
    lexer.add_filter(SpecificHighlightFilter())
    base_style_name = lexer.analyse_text(code) or 'friendly'
    if base_style_name not in get_all_styles():
        base_style_name = 'friendly'
    ExtendedStyle = extend_style(base_style_name)
    formatter = Terminal256Formatter(style=ExtendedStyle, linenos=show_line_numbers)
    if lines_to_highlight:
        bg_hl_color = BackgroundHighlightFilter.default_bg_hl_color
        lexer.add_filter(BackgroundHighlightFilter(lines_to_highlight, bg_hl_color))
    #    lexer.add_filter(BackgroundHighlightFilter(lines_to_highlight, bg_hl_color))
    highlighted_code = highlight(code, lexer, formatter)
    return highlighted_code

def detect_language_type(code, filename=None, language=None):
    """
    Determine the appropriate lexer for the given code, filename, or language.
    """
    try:
        if language:
            return get_lexer_by_name(language, stripall=True)
        elif filename:
            return guess_lexer_for_filename(filename, code, stripall=True)
        else:
            return guess_lexer(code, stripall=True)
    except Exception as e:
        print(f"Error detecting language type: {e}", file=sys.stderr)
        return get_lexer_by_name("text", stripall=True)

# extending arg parser to accept line ranges
def parse_line_ranges(line_ranges_str):
    line_numbers = set()
    ranges = line_ranges_str.split(',')
    for part in ranges:
        if '-' in part:
            start, end = part.split('-')
            line_numbers.update(range(int(start), int(end) + 1))
        else:
            line_numbers.add(int(part))
    return line_numbers

def print_language_detected(lexer):
    random_color = f'\033[38;5;{random.randint(1, 255)}m'
    reset_color = '\033[0m'
    yellow_color = '\033[38;5;226m'
    print(f"Language Detected: {yellow_color}[{random_color}{lexer.name}{reset_color}{yellow_color}]{reset_color}")

colorcat_furballs = [
"            .';::::::::::::::::::::::::::::::::::::::::::::::::::;,..           ","         .:dOKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKOxc'         ","       .ck0KXXNNNNNNXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXKNNNNNNNXXKOo'       ","      'd0KXXNNNNNWKc,;;cd0NWWWWWWWWWWWWWWWWWWWWWWWWWWWXkl;;;;kWNNNNNNXXKk;      ","     .d0KXXNNNNWWWo.:x,.'.:kNMMMMMMMMMMMMMMMMMMMMMMWOl..''od.;XWWNNNNXXXKk,     ","     ;kKXXXNNWWWMWc ;x;'l' .;xXMMMMMMMMMMMMMMMMMMWO:. .c;.do ,KMMWWNNXXXK0l.    ","     ;kKXXXNNWMMMWc :x;';l:;;.;kWWX0OkkxxxkO0KNW0c.,;;cc',do.'0MMMWNNXXKK0l.    ","     ;kKXXXNNWMMMWl ,d;cl;;c:;,.,,.'........'.',..;:c:;cl;lc ;XMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMk..l:';c'c;;c'c;.co;cc,c:lo.'l,::,c,;c';l,.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNc ;d:.ccc;;c,x:'ldclc;clld,,x:::;ccl';dc.'0MMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMM0,.locc'l,:c.;l';c.cl,c,:l'c:.;c'l;:llo'.xWMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMMWo.ccloc;.'::.:c;:.cc,c,;ccc.,c,.'colcl';XMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMWk..:ccol,lo.:;::;:.cc,c,;cc:,c'cd,:dccc'.lNMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMK,.::,co;.;:...,,,;,c;.c:;;;,.. ,c.'ll,;c'.xMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMd.,' 'lo:''.   '..:ol. :dc'..   .,,;lo;..;.;XMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMWc.;c,ox; ;o.  .oo.:o,...ll.,c   .dx..dx;;c.'0MMMWNNXXXKOl.    ","     ;kKXXXNNWMMMWl.::.cxdc;lc'.,oc..:c'';l'.,oc'.;lc;oxo',c.,KMMMWNNXXXKOl.    ","     ;kKXXNNNWMMMMx.':,,;;coccc:c'.,:,cc,c;;:..:c:cllc;;,,:;.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNl.,c,.;oxko:::c;';;cl;c:;,,::::cxxdc..c:.;KMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMMXl',:::c::::cld0O,.:olc..d0xlc::::cc::;':0MMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMWx..col:,:lclkWWO:....,xNM0ocl:,:cll..lNMMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMM0,;xl;;;;;:okXMMNo. ;XMMW0dc;;;;,cxc'xMMMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMWx..lc.;,'c:,,:colcclclol:;':l,';';o' cNMMMMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMMMM0'':okclccc;';;.:x0NNXkl.,:';:cclcxdc'.dWMMMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMMMK;.,,,ccccc,;'.:;'.,;,;..,c'.;,clccl;,,..kWMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNc.''';:cod'.cl..cl;:c,:;:l'.:l..ldcc:,''.,0MMMMWNNXXXX0l.    ","     ;kKXXXNNWMMMMk.'oc::;:l;':o::::l::c,::cc:c:lc',c:;::co;.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMWc :ko:dk:.'c:;.:l;;;l;.cc,;cl.':c: 'xkccko.,KMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMWc :l.,kd'.clcxcl:.;c:;,;cc.,lcdocl'.ckc.cl.'0MMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMd';'.;;'''cc;d;c;.l,;ddc'l;'l;oc;l,'',;,.;'cNMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMXl.'ko:;ccc:...:l.:c'',':c':l...,lcc:;lk:.;0MMMMWNNXXXK0l.    ","     ;kKXXXNNWWMMMMNo.;,;ccdoo,;d:''.:l;'cc'.';oc,codlc:,:':KMMMMMWNNXXXK0l.    ","     ,xKXXXNNWWWMMMMW0l..':oco,.';':dclc;clol',,..lllc,..:kNMMMMMWWNNXXXKOc.    ","     .lOKXXNNNNWWWMMMMWKxc;..,...::...cc,c,..;c.. ''.,:o0WMMMMWWWNNNNXXKKx'     ","      .lOKXXNNNNNNNNNNNNNNXOxl:;','....'......,',:cokKNNNNNNNNNNNNNNNXK0d'      ","        ,dOKXXXXXNNNXXNNNNNNNNNNK0OkxdddddddxkOKXNNNNNNNNNNNNNNNNNXXK0x:.       ","         .,cdk00KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000KKK0Oxl;.         ","             ..'''''''''''''''''''''''''''''''''''''''''''''''''''.             ","             Colorcat by Ben Gorlick (github: bgorlick) (c) 2024 | MIT     \n",
]

# This will make the cat go meow
def meow(colorcat=None, s_col=1):
    if colorcat is None:
        colorcat = colorcat_furballs
    width = max(len(furball) for furball in colorcat)
    c_col = s_col
    grad_meow = []
    print ("\n")
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

def c_new_furball(input_text):
    let_to_p = ["k", "K", "0", "X", "N", "W", "M", "c", "d", "l", "x", "o", "O"]
    rep_chars = [char for char in input_text if char.isalnum()]
    if not rep_chars:
        return colorcat_furballs
    new_furball = list(colorcat_furballs)
    rep_i = itertools.cycle(rep_chars)
    for i, line in enumerate(new_furball[:-1]):  
        new_line = ""
        for char in line:
            if char in let_to_p:
                new_line += next(rep_i)
            else:
                new_line += char
        new_furball[i] = new_line
    new_furball.append("\n      Look carefully at the furball you just created... meow it contains your code :)")
    return new_furball

def capture_help_message(parser):
    help_message = ""
    with io.StringIO() as help_message:
         parser.print_help(file=help_message)
         help_message = help_message.getvalue()
         return help_message
    

def apply_syntax_highlighting_to_help(help_message):
    colors = SpecificHighlightFilter.meow_colors
    symbol_colors = {
        '-': colors['operators'],
        ':': colors['colon'],
        '[': colors['bracket_square'],
        ']': colors['bracket_square'],
        ',': colors['comma'],
        '.': colors['period'],
        '(': colors['parens'],
        ')': colors['parens']
    }
    highlighted_message = ""
    for char in help_message:
        if char in symbol_colors:
            highlighted_message += f"{symbol_colors[char]}{char}{colors['reset']}"
        else:
            highlighted_message += f"{colors['strings']}{char}{colors['reset']}"
    return highlighted_message


# TODO: This is just the foundation for this feature, it's not fully implemented yet
def offset_color(offset_args: str, config: dict) -> dict:
    """Adjusts color values based on user-defined offsets. Supports global, foreground, and background offsetting with wrapping."""
    def parse_offset_args(offset_args):
        pattern = r"(all|\w+)(\d+),(\d+)"
        matches = re.finditer(pattern, offset_args, re.IGNORECASE)
        offsets = defaultdict(lambda: {'fg': 0, 'bg': 0})
        for match in matches:
            key, fg_offset, bg_offset = match.groups()
            offsets[key] = {'fg': int(fg_offset), 'bg': int(bg_offset)}
        return offsets

    def wrap_color_value(value, offset, max_value=255):
        return (value + offset) % max_value

    def apply_offsets_to_config(config, offsets):
        for key, value in config.items():
            if key in offsets or 'all' in offsets:
                fg_offset = offsets.get(key, offsets['all'])['fg']
                bg_offset = offsets.get(key, offsets['all'])['bg']
                config[key]['fg'] = wrap_color_value(value['fg'], fg_offset)
                config[key]['bg'] = wrap_color_value(value['bg'], bg_offset)
        return config

    offsets = parse_offset_args(offset_args)
    updated_config = apply_offsets_to_config(config, offsets)
    return updated_config



def main():
    parser = argparse.ArgumentParser(description='ColorCat: Enhanced source code highlighting.')
    parser.add_argument('filename', type=str, nargs='?', default=None, help='The file to be highlighted')
    parser.add_argument('-ln', '--line-numbers', action='store_true', help='Display line numbers')
    parser.add_argument('-hln', '--highlight-lines', type=str, default='', help='Highlight specific lines')
    parser.add_argument('-lang', '--language', type=str, help='Explicitly specify the programming language')
    parser.add_argument('-meow', '--meow', action='store_true', help='Cat goes meow')
    args, unknown = parser.parse_known_args()
    
    try:
        if '-h' in unknown or '--help' in unknown:
            help_message = capture_help_message(parser)
            highlighted_help_message = apply_syntax_highlighting_to_help(help_message)
            print(highlighted_help_message)
            sys.exit()

        if args.highlight_lines:
            lines_to_highlight = parse_line_ranges(args.highlight_lines)
        else:
            lines_to_highlight = set()


        if args.meow:
            input_text, filename = read_input(args.filename)
            if input_text:  
                new_furball = c_new_furball(input_text)
                meow(new_furball, random.randint(1, 255))
            else:
                meow(colorcat_furballs, random.randint(1, 255))
            return 

        code, filename = read_input(args.filename)
        if code:
            lexer = detect_language_type(code, filename, args.language)
            print_language_detected(lexer)
            highlighted_code = highlight_with_colorcat_colors(
                code, filename, args.line_numbers, 
                lines_to_highlight, args.language
            )
            print(highlighted_code)
        elif sys.stdin.isatty():  
            meow(colorcat_furballs, random.randint(1, 255))
            help_message = capture_help_message(parser)
            highlighted_help_message = apply_syntax_highlighting_to_help(help_message)
            print(f"\nNo input file was detected.\n {highlighted_help_message}\n")
        else:
            stdin_text = sys.stdin.read()
            if args.line_numbers and not (args.highlight_lines or args.language):
                print_with_line_numbers(stdin_text)
            else:
                highlighted_code = highlight_with_colorcat_colors(
                    stdin_text, None, args.line_numbers, 
                    lines_to_highlight, args.language
                )
                print(highlighted_code)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

def print_with_line_numbers(input_text):
    for line_number, line in enumerate(input_text.splitlines(), start=1):
        print(f"{line_number:4}: {line}")

if __name__ == "__main__":
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    main()
#    sys.stdout.write("\x1b[?7h")
    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit(0)
