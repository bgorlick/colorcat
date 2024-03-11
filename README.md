# colorcat
ColorCat: Enhanced Syntax Highlighting for the Terminal, Code, Standard Input and Error detection in development.

![image](https://github.com/bgorlick/colorcat/assets/5460972/89907ca7-5b5e-49ce-8633-57010427d34d)

![image](https://github.com/bgorlick/colorcat/assets/5460972/5ea2e5c2-5046-4b1e-a3db-bb82a9769082)

### What Is Colorcat?
ColorCat is an innovative command-line tool designed to bring vibrant, context-aware syntax highlighting to your terminal, making it easier to read and understand code. Unlike traditional utilities like cat or bat, ColorCat leverages the powerful Pygments library to offer a wide range of language support and customization options, ensuring your code is not just displayed but brought to life with color.

### Key Features

- **Automatic Language Detection**: Automatically identifies the programming language of the input file, applying the most suitable syntax highlighting.
- **Custom Line Highlighting**: Highlight specific lines of code to focus on important sections or for debugging purposes.
- **Flexible Styling**: Customize font styles and background colors for specific lines or sections of code to provide visual cues and emphasis.
- **Bracket Coloring**: Applies subtle color differences to brackets, braces, and parentheses to improve code navigation and readability.
- **Extended Pygments Support**: Offers additional styles, filters, and customization options beyond Pygments' default capabilities.
- **Simple Command-Line Interface**: Designed to integrate seamlessly into your workflow with an easy-to-use command-line interface.
- **Open Source and Community-Driven**: Welcomes contributions, feature requests, and feedback from the developer community.

![image](https://github.com/bgorlick/colorcat/assets/5460972/ff0e68fc-b893-4787-a757-9557a6effc2c)

# Just rename it to colorcat, and move it to a directory in your PATH, such as /usr/local/bin, and make it executable with chmod +x colorcat.
# PS. --meow is a fun little easter egg that makes the cat go meow.
** Usage (text version **
```usage: colorcat [-ln] [-hln HIGHLIGHT_LINES] [-lang LANGUAGE] [-regex REGEX_PATTERN] [-o OUTPUT] [-oln ONLY_SHOW_LINES] [-bgcolor BACKGROUND_COLOR] [-meow] [-h] [filename]

ColorCat: Enhanced source code highlighting.

positional arguments:
  filename              The file to be highlighted

options:
  -ln, --line-numbers   Display line numbers
  -hln HIGHLIGHT_LINES, --highlight-lines HIGHLIGHT_LINES
                        Highlight specific lines
  -lang LANGUAGE, -l LANGUAGE, --language LANGUAGE
                        Explicitly specify the programming language
  -regex REGEX_PATTERN, --regex-pattern REGEX_PATTERN
                        Regex pattern to highlight matching lines
  -o OUTPUT, --output OUTPUT
                        Output formatting option. Can be 'formatted' or 'plain'.
  -oln ONLY_SHOW_LINES, --only-show-lines ONLY_SHOW_LINES
                        Only show specific lines
  -bgcolor BACKGROUND_COLOR, --background-color BACKGROUND_COLOR
                        Specify a background color for highlighted lines [0-255]
  -meow, --meow         Cat goes meow
  -h, --help            Custom help message
```
![image](https://github.com/bgorlick/colorcat/assets/5460972/7e61dbb7-c1a2-408f-bac7-e661a6952826)

Whether you're reviewing dense code bases, debugging, or simply prefer to work within the terminal, ColorCat enhances your experience by making code easier to read and understand. It's the perfect tool for developers, system administrators, and anyone who appreciates the power and simplicity of the command line.

# (c) 2024 - Ben Gorlick | MIT License | Attribution to the original author and this repository is required - free to use, modify, and distribute.
