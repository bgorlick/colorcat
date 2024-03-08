# colorcat
ColorCat: Enhanced Syntax Highlighting for the Terminal

ColorCat is an innovative command-line tool designed to bring vibrant, context-aware syntax highlighting to your terminal, making it easier to read and understand code. Unlike traditional utilities like cat or bat, ColorCat leverages the powerful Pygments library to offer a wide range of language support and customization options, ensuring your code is not just displayed but brought to life with color.

Key Features:

    Automatic Language Detection: ColorCat automatically identifies the programming language of the input file, applying the most suitable syntax highlighting for enhanced readability.
    Custom Line Highlighting: With ColorCat, users can highlight specific lines of code, making it easier to focus on important sections or debug code.
    Flexible Styling: Users can customize font styles and background colors for specific lines or sections of code, providing visual cues and emphasis where needed.
    Bracket Coloring: To improve code navigation and readability, ColorCat applies subtle color differences to brackets, braces, and parentheses, helping users to match pairs at a glance.
    Extended Pygments Support: ColorCat extends the capabilities of Pygments, offering additional styles, filters, and customization options that are not available out of the box.
    Simple Command-Line Interface: The tool is designed to be easy to use, with a straightforward CLI that integrates seamlessly into your workflow.
    Open Source and Community-Driven: ColorCat is open source and welcomes contributions, feature requests, and feedback from the developer community.

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

Whether you're reviewing dense code bases, debugging, or simply prefer to work within the terminal, ColorCat enhances your experience by making code easier to read and understand. It's the perfect tool for developers, system administrators, and anyone who appreciates the power and simplicity of the command line.

# (c) 2024 - Ben Gorlick | MIT License | Attribution to the original author is required - free to use, modify, and distribute.
