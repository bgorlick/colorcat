#!/usr/bin/env python3

# Colorcat - A powerful yet simple syntax highlighter for the terminal viewing of files.
# (c) 2024 - Ben Gorlick | MIT License | Attribution to the original author is required - free to use, modify, and distribute.
# Colorcat enhances viewing of file contents in the terminal by colorizing syntax.
# Version: 0.1.0.0

# At times neither cat, nor bat are make seperating concerns when viewing dense files easy.  This is where colorcat comes in. 
# Colorcat is a simplified syntax highlighter for terminal use, utilizing Python's pygmentize.

# Features include language detection, bracket coloring, line numbers, and custom line highlighting.
# Designed to easily change colors, add new features and filters and to illustrate how to use pygments and filters.

# The concepts demonstrated are easily extendable to create your own custom syntax highlighting filters and styles in other projects.

# Usage: colorcat.py [filename] [-ln] [-aug] [-aug-font] [-aug-bg] [-hln]
#   filename: The file to be highlighted
#   -ln, --line-numbers: Display line numbers
#   -aug, --augment-lines: Specify lines to augment, separated by commas (e.g., "2,5,7")
#   -aug-font, --augment-font-style: Font style for augmented lines (e.g., "bold")
#   -aug-bg, --augment-background-color: Background color for augmented lines (e.g., "on grey")
#   -hln, --highlight-lines: Highlight lines with a grey background, separated by commas (e.g., "10,30")
#   -m, --meow: Make the cat go meow

# If you want to highlight specific lines in a file you can do so like this (eg. highlighting lines 279 and 281)
# python colorcat.py -hln 279,281 /path/to/file.py
# You can rename this file to colorcat and make it executable to use it as a drop-in replacement for cat or bat.

# Just rename it to colorcat, and move it to a directory in your PATH, such as /usr/local/bin, and make it executable with chmod +x colorcat.
# PS. --meow is a fun little easter egg that makes the cat go meow.



import argparse
import sys
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.style import Style
from pygments.token import Token, Generic
from pygments.filters import Filter
from pygments.styles import get_all_styles, get_style_by_name
import traceback
import random


#  how to Filter using hex colors and how to extend a style
class CustomStyle(Style):
    # we hex in pygments and not the terminal 5-bit color mode as [38;5 is not supported by pygments

    default_style = ""
    styles = {
        Token.Generic.Subheading: 'bg:#f0f0f0',
        Token.LineNumber: 'bg:#f0f0f0', # Line numbers are colored the same as subheadings
    }

def extend_style(base_style_name):
    base = get_style_by_name(base_style_name)
    extended_styles = base.styles.copy()
    extended_styles.update(CustomStyle.styles)
    return type(f'Extended{base_style_name}', (Style,), {'default_style': '', 'styles': extended_styles})


class LineAugmentationFilter(Filter):
    def __init__(self, lines_to_augment, **options):
        self.lines_to_augment = {int(line) for line in lines_to_augment.split(',')}
        super().__init__(**options)

    def filter(self, lexer, stream):
        line_number = 1
        for ttype, value in stream:
            if "\n" in value:
                for part in value.split('\n'):
                    if line_number in self.lines_to_augment:
                        yield Token.Generic.Subheading, part
                    else:
                        yield ttype, part
                    if part != value.split('\n')[-1]:  # Avoid incrementing on the last empty split result
                        line_number += 1
            else:
                yield ttype, value


# SpecificHighlightFilter is a filter that highlights brackets and quotes and various other things using ascii 5-bit color codes
class SpecificHighlightFilter(Filter):
    bracket_colors = {
    #sometimes brackets are hard to see and often they are used together like this {()[]} so we will give them each a slightly different shade seperated by 2 colors in the 5-bit color mode
        'bracket_braces': '\033[38;5;194m',
        'bracket_parens': '\033[38;5;196m', 
        'bracket_square': '\033[38;5;199m', 
        'bracket_angle': '\033[38;5;201m',
        'pink': '\033[38;5;198m',
        'white': '\033[38;5;231m',
        'light_grey': '\033[38;5;243m',
        'grey': '\033[38;5;245m',
        'yellow': '\033[38;5;224m',
        'orange': '\033[38;5;211m',
        'purple': '\033[38;5;141m',
        'red': '\033[38;5;196m',
        'green': '\033[38;5;120m',
        'blue': '\033[38;5;117m',
        'cyan': '\033[38;5;87m',
        'between_cyan_and_blue': '\033[38;5;81m',
        'light_blue': '\033[38;5;117m',
        'light_green': '\033[38;5;120m',
        'light_red': '\033[38;5;196m',
        'light_purple': '\033[38;5;141m',
        'light_yellow': '\033[38;5;226m',
        'blood_orange': '\033[38;5;203m',
        'light_orange': '\033[38;5;214m',
        'light_pink': '\033[38;5;207m', 
        'black': '\033[38;5;0m',
        'reset': '\033[0m'
    }
    def filter(self, _, stream):
        reset_color = SpecificHighlightFilter.bracket_colors['reset']
        for ttype, value in stream:
            if value in "[]":
                yield Token.Text,  SpecificHighlightFilter.bracket_colors['bracket_square'] + value + reset_color
            elif value in "{}":
                yield Token.Text,  SpecificHighlightFilter.bracket_colors['bracket_braces'] + value + reset_color
            elif value in "()":
                yield Token.Text,  SpecificHighlightFilter.bracket_colors['bracket_parens'] + value + reset_color
            elif value in "<>":
                yield Token.Text,  SpecificHighlightFilter.bracket_colors['bracket_angle'] + value + reset_color
            elif value in "\"'":
                yield Token.Text,  SpecificHighlightFilter.bracket_colors['yellow'] + value + reset_color
            elif ttype in Token.Comment: # Multi-line comments
                yield Token.Comment,  SpecificHighlightFilter.bracket_colors['light_blue'] + value + reset_color
            elif ttype in Token.Comment.Single: # Single-line comments, but wont be used because its already defined above (just showing to illustrate the point)
                yield Token.Comment.Single,  SpecificHighlightFilter.bracket_colors['light_green'] + value + reset_color
            elif ttype in Token.Literal.String: # Strings
                yield Token.Literal.String,  SpecificHighlightFilter.bracket_colors['light_grey'] + value + reset_color
            elif ttype in Token.Literal.String.Single: # Single-quoted strings (but wont be used because its already defined above)
                yield Token.Literal.String.Single,  SpecificHighlightFilter.bracket_colors['light_red'] + value + reset_color 
            # function names like this
            elif ttype in Token.Name.Function:
                yield Token.Name.Function,  SpecificHighlightFilter.bracket_colors['light_purple'] + value + reset_color
            # conditionals like if else while for etc
            elif ttype in Token.Keyword:
                yield Token.Keyword,  SpecificHighlightFilter.bracket_colors['light_green'] + value + reset_color
            # things like print, input, etc
            elif ttype in Token.Name.Builtin:
                yield Token.Name.Builtin,  SpecificHighlightFilter.bracket_colors['between_cyan_and_blue'] + value + reset_color
            # numbers
            elif ttype in Token.Number:
                yield Token.Number,  SpecificHighlightFilter.bracket_colors['light_yellow'] + value + reset_color
            # operators like + - * / etc
            elif ttype in Token.Operator:
                yield Token.Operator,  SpecificHighlightFilter.bracket_colors['light_pink'] + value + reset_color
            # punctuation like , . : ; etc
            elif ttype in Token.Punctuation:
                yield Token.Punctuation,  SpecificHighlightFilter.bracket_colors['cyan'] + value + reset_color
            # variables
            elif ttype in Token.Name:
                yield Token.Name,  SpecificHighlightFilter.bracket_colors['blood_orange'] + value + reset_color
            # handle subheadings for the background highlight filter ensuring the background is colored grey
            elif ttype in Token.Generic.Subheading:
                yield Token.Generic.Subheading,  SpecificHighlightFilter.bracket_colors['light_grey'] + value + reset_color
            else:
                yield ttype, value

class BackgroundHighlightFilter(Filter):
    def __init__(self, lines_to_highlight, bg_color='on grey', **options):
        self.lines_to_highlight = set(int(line) for line in lines_to_highlight.split(','))
        self.bg_color = bg_color
        super().__init__(**options)

    def filter(self, lexer, stream):
        line_number = 1
        for ttype, value in stream:
            if line_number in self.lines_to_highlight:
                yield Token.Generic.Subheading, value
            else:
                yield ttype, value
            if "\n" in value:
                line_number += value.count('\n')

def highlight_with_bracket_coloring(code, filename, show_line_numbers, lines_to_augment='', lines_to_highlight=''):
    lexer = guess_lexer_for_filename(filename, code)
    lexer.add_filter(SpecificHighlightFilter())
    if lines_to_augment:
        lexer.add_filter(LineAugmentationFilter(lines_to_augment))
    if lines_to_highlight:
        lexer.add_filter(BackgroundHighlightFilter(lines_to_highlight))

    base_style_name = lexer.analyse_text(code) or 'friendly'  
    if base_style_name not in get_all_styles():
        base_style_name = 'friendly'  

    ExtendedStyle = extend_style(base_style_name)

    formatter = Terminal256Formatter(style=ExtendedStyle, linenos=show_line_numbers)
    return highlight(code, lexer, formatter)


def augment_lines_with_color_and_style(code, filename, show_line_numbers, lines_to_augment):
    lexer = guess_lexer_for_filename(filename, code)
    lexer.add_filter(LineAugmentationFilter(lines_to_augment))
    formatter = Terminal256Formatter(linenos=show_line_numbers)
    highlighted_code = highlight(code, lexer, formatter)
    return highlighted_code

colorcat_furballs = [
"            .';::::::::::::::::::::::::::::::::::::::::::::::::::;,..           ","         .:dOKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKOxc'         ","       .ck0KXXNNNNNNXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXKNNNNNNNXXKOo'       ","      'd0KXXNNNNNWKc,;;cd0NWWWWWWWWWWWWWWWWWWWWWWWWWWWXkl;;;;kWNNNNNNXXKk;      ","     .d0KXXNNNNWWWo.:x,.'.:kNMMMMMMMMMMMMMMMMMMMMMMWOl..''od.;XWWNNNNXXXKk,     ","     ;kKXXXNNWWWMWc ;x;'l' .;xXMMMMMMMMMMMMMMMMMMWO:. .c;.do ,KMMWWNNXXXK0l.    ","     ;kKXXXNNWMMMWc :x;';l:;;.;kWWX0OkkxxxkO0KNW0c.,;;cc',do.'0MMMWNNXXKK0l.    ","     ;kKXXXNNWMMMWl ,d;cl;;c:;,.,,.'........'.',..;:c:;cl;lc ;XMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMk..l:';c'c;;c'c;.co;cc,c:lo.'l,::,c,;c';l,.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNc ;d:.ccc;;c,x:'ldclc;clld,,x:::;ccl';dc.'0MMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMM0,.locc'l,:c.;l';c.cl,c,:l'c:.;c'l;:llo'.xWMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMMWo.ccloc;.'::.:c;:.cc,c,;ccc.,c,.'colcl';XMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMWk..:ccol,lo.:;::;:.cc,c,;cc:,c'cd,:dccc'.lNMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMK,.::,co;.;:...,,,;,c;.c:;;;,.. ,c.'ll,;c'.xMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMd.,' 'lo:''.   '..:ol. :dc'..   .,,;lo;..;.;XMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMWc.;c,ox; ;o.  .oo.:o,...ll.,c   .dx..dx;;c.'0MMMWNNXXXKOl.    ","     ;kKXXXNNWMMMWl.::.cxdc;lc'.,oc..:c'';l'.,oc'.;lc;oxo',c.,KMMMWNNXXXKOl.    ","     ;kKXXNNNWMMMMx.':,,;;coccc:c'.,:,cc,c;;:..:c:cllc;;,,:;.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNl.,c,.;oxko:::c;';;cl;c:;,,::::cxxdc..c:.;KMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMMXl',:::c::::cld0O,.:olc..d0xlc::::cc::;':0MMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMWx..col:,:lclkWWO:....,xNM0ocl:,:cll..lNMMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMM0,;xl;;;;;:okXMMNo. ;XMMW0dc;;;;,cxc'xMMMMMMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMMMWx..lc.;,'c:,,:colcclclol:;':l,';';o' cNMMMMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMMMM0'':okclccc;';;.:x0NNXkl.,:';:cclcxdc'.dWMMMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMMMK;.,,,ccccc,;'.:;'.,;,;..,c'.;,clccl;,,..kWMMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMNc.''';:cod'.cl..cl;:c,:;:l'.:l..ldcc:,''.,0MMMMWNNXXXX0l.    ","     ;kKXXXNNWMMMMk.'oc::;:l;':o::::l::c,::cc:c:lc',c:;::co;.lWMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMWc :ko:dk:.'c:;.:l;;;l;.cc,;cl.':c: 'xkccko.,KMMMWNNXXXKOl.    ","     ;OKXXXNNWMMMWc :l.,kd'.clcxcl:.;c:;,;cc.,lcdocl'.ckc.cl.'0MMMWNNXXXKOl.    ","     ;kKXXXNNWMMMMd';'.;;'''cc;d;c;.l,;ddc'l;'l;oc;l,'',;,.;'cNMMMWNNXXXK0l.    ","     ;kKXXXNNWMMMMXl.'ko:;ccc:...:l.:c'',':c':l...,lcc:;lk:.;0MMMMWNNXXXK0l.    ","     ;kKXXXNNWWMMMMNo.;,;ccdoo,;d:''.:l;'cc'.';oc,codlc:,:':KMMMMMWNNXXXK0l.    ","     ,xKXXXNNWWWMMMMW0l..':oco,.';':dclc;clol',,..lllc,..:kNMMMMMWWNNXXXKOc.    ","     .lOKXXNNNNWWWMMMMWKxc;..,...::...cc,c,..;c.. ''.,:o0WMMMMWWWNNNNXXKKx'     ","      .lOKXXNNNNNNNNNNNNNNXOxl:;','....'......,',:cokKNNNNNNNNNNNNNNNXK0d'      ","        ,dOKXXXXXNNNXXNNNNNNNNNNK0OkxdddddddxkOKXNNNNNNNNNNNNNNNNNXXK0x:.       ","         .,cdk00KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000KKK0Oxl;.         ","             ..'''''''''''''''''''''''''''''''''''''''''''''''''''.             ","             Colorcat by Ben Gorlick (github: bgorlick) (c) 2024 | MIT     \n",
]

# This will make the cat go meow
def meow(colorcat, s_col):
    width = max(len(furball) for furball in colorcat)
    c_col = s_col
    grad_meow = []
    for row in colorcat:
        grad_l = ""
        c_col = s_col
        for column, char in enumerate(row):
            if char != ' ':
                grad_l += f"\x1b[38;5;{c_col % 32}m{char}\x1b[0m"
                c_col += 1
            else:
                grad_l += ' '
        grad_meow.append(grad_l)

        # make cat go meow
        # s_col += 50   # uncomment this to see variations in meow

    for furball in grad_meow:
        print(furball)


# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ColorCat: Enhanced source code highlighting.')
    parser.add_argument('filename', type=str, nargs='?', help='The file to be highlighted')
    parser.add_argument('-ln', '--line-numbers', action='store_true', help='Display line numbers')
    parser.add_argument('-aug', '--augment-lines', type=str, default='', help='Augment specific lines')
    parser.add_argument('-hln', '--highlight-lines', type=str, default='', help='Highlight specific lines')
    # this is for printing the furball
    parser.add_argument('-meow', '--meow', action='store_true', help='Cat goes meow')
    args = parser.parse_args()


    if args.meow:
        # cat meows in 256 different frequencies
        meow(colorcat_furballs, random.randint(1, 255))
        sys.exit(0)

    if not args.filename:
        meow(colorcat_furballs, random.randint(1, 255))
        parser.print_help()
        sys.exit(0)

    try:
        with open(args.filename, 'r') as file:
            code = file.read()
        lexer = guess_lexer_for_filename(args.filename, code)

        # unnecessary but I wanted to show the detect language and use colors based on language detected
        lexerColorProgrammingLanguage5BitColors = {
            'cpp': '\033[38;5;23m', 'c': '\033[38;5;23m', 'c++': '\033[38;5;23m', 'c#': '\033[38;5;23m', 'java': '\033[38;5;23m', 'javascript': '\033[38;5;23m',
            'typescript': '\033[38;5;23m', 'python': '\033[38;5;23m', 'ruby': '\033[38;5;23m', 'perl': '\033[38;5;23m', 'php': '\033[38;5;23m', 'go': '\033[38;5;23m',
            'rust': '\033[38;5;23m', 'swift': '\033[38;5;23m', 'kotlin': '\033[38;5;23m', 'scala': '\033[38;5;23m', 'groovy': '\033[38;5;23m', 'r': '\033[38;5;23m',
            'julia': '\033[38;5;23m', 'haskell': '\033[38;5;23m', 'dart': '\033[38;5;23m', 'lua': '\033[38;5;23m', 'elixir': '\033[38;5;23m', 'clojure': '\033[38;5;23m',
            'erlang': '\033[38;5;23m', 'ocaml': '\033[38;5;23m', 'f#': '\033[38;5;23m', 'nim': '\033[38;5;23m', 'crystal': '\033[38;5;23m', 'cobol': '\033[38;5;23m',
            'fortran': '\033[38;5;23m', 'ada': '\033[38;5;23m', 'pascal': '\033[38;5;23m', 'lisp': '\033[38;5;23m', 'scheme': '\033[38;5;23m', 'prolog': '\033[38;5;23m',
            'forth': '\033[38;5;23m', 'abap': '\033[38;5;23m', 'apex': '\033[38;5;23m', 'bash': '\033[38;5;23m', 'shell': '\033[38;5;23m', 'powershell': '\033[38;5;23m',
            'batch': '\033[38;5;23m', 'awk': '\033[38;5;23m', 'sed': '\033[38;5;23m', 'sql': '\033[38;5;23m', 'plsql': '\033[38;5;23m', 'tcl': '\033[38;5;23m',
            'racket': '\033[38;5;23m', 'verilog': '\033[38;5;23m', 'vhdl': '\033[38;5;23m', 'systemverilog': '\033[38;5;23m', 'v': '\033[38;5;23m', 'assembly': '\033[38;5;23m',
        }
        # We need to account for the fact that the above names are all defined in lowercase but lexer will come through as uppercase
        lexerBracketColor = {'yellow': '\033[38;5;226m', 'reset': '\033[0m'}
        lexerColors5Bit = {k: lexerColorProgrammingLanguage5BitColors.get(k, '') for k in lexerColorProgrammingLanguage5BitColors.keys()}
        lexerColor = lexerColors5Bit.get(lexer.name.lower(), '')

        if lexerColor:
            print(f"Language Detected: {lexerBracketColor['yellow']}[{lexerColor}{lexer.name}{lexerBracketColor['reset']}{lexerBracketColor['yellow']}]{lexerBracketColor['reset']}")
        else:
            print(f"Language Detected: {lexer.name}")

        highlighted_code = highlight_with_bracket_coloring(
            code, args.filename, args.line_numbers, args.augment_lines, args.highlight_lines)
        print(highlighted_code, end='')
    except FileNotFoundError:
        print(f"File not found: {args.filename}", file=sys.stderr)
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:\n{error_message}", file=sys.stderr)
        sys.exit(1)




