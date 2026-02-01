# Past Paper Retrieve CLI

A terminal-based CLI tool to download CIE AS & A Level past papers from pastpapers.co. Supports question papers (qp) and mark schemes (ms) in PDF format.

## Features

- Interactive terminal interface with intuitive navigation
- Download by subject, paper type, session, and year
- Progress tracking during downloads
- Organized file structure for downloaded papers
- Support for multiple paper numbers and years

## Requirements

- Python 3.6+
- Terminal with support for curses (most modern terminals)
- Internet connection

## Installation

### Option 1: Local Installation

1. Clone or download this repository:
```bash
git clone https://github.com/your-username/pastpaper-retrieve-aslevel.git
cd pastpaper-retrieve-aslevel
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: System-Wide Installation (Recommended)

To use this tool from any directory, you can install it system-wide:

1. Clone the repository:
```bash
git clone https://github.com/your-username/pastpaper-retrieve-aslevel.git
cd pastpaper-retrieve-aslevel
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Create a symbolic link in `/usr/local/bin`:
```bash
sudo ln -s "$(pwd)/pastpaper/cli.py" /usr/local/bin/pastpaper
```

4. Make the script executable:
```bash
chmod +x pastpaper/cli.py
```

5. Add shebang line to the script (if not already present):
```bash
sed -i '1i#!/usr/bin/env python3' pastpaper/cli.py
```

Now you can run the tool from anywhere:
```bash
pastpaper
```

## Usage

### Running Locally
```bash
# If using virtual environment
source venv/bin/activate
python3 -m pastpaper.cli

# If installed system-wide
pastpaper
```

### Navigation

The tool uses keyboard navigation:

- **Arrow Keys** (↑↓): Navigate through options
- **Space**: Select/deselect items (for multi-select)
- **Enter**: Confirm selection
- **Esc**: Quit the application

### Download Process

1. **Select Level**: Choose between AS Level, A Level, etc.
2. **Select Subject**: Choose your subject (e.g., Mathematics, Physics)
3. **Select Paper Type**: Choose between Question Paper (qp) or Mark Scheme (ms)
4. **Select Sessions**: Choose exam sessions (Feb/May, Oct/Nov)
5. **Enter Years**: Input years in 2-digit format (e.g., 23,24,25 for 2023-2025)
6. **Enter Paper Numbers**: Optional - specify paper numbers (e.g., 11,12,13) or leave blank for all
7. **Confirm**: Review your selection and press any key to start downloading

### Output

Downloaded files are organized as:
```
pastpaper/
└── Subject_Name/
    ├── subject_code_year_session_paper_type_paper_number_qp.pdf
    └── subject_code_year_session_paper_type_paper_number_ms.pdf
```

Example:
```
pastpaper/
└── Mathematics/
    ├── 9709_23_m22_qp_11.pdf
    └── 9709_23_m22_ms_11.pdf
```

## Dependencies

The tool requires the following Python packages:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `tqdm` - Progress bars

These are automatically installed when running `pip install -r requirements.txt`.

## Terminal Requirements

- Minimum terminal size: 80x24 characters
- Color support recommended for better experience
- Standard arrow keys and Enter/Space/Esc keys required

## Troubleshooting

### "Command not found" error
If you installed system-wide but get a "command not found" error:
1. Ensure `/usr/local/bin` is in your PATH: `echo $PATH`
2. If not, add it to your shell profile: `export PATH="/usr/local/bin:$PATH"`
3. Check the symlink exists: `ls -la /usr/local/bin/pastpaper`

### Permission denied
If you get permission errors:
1. Ensure the script is executable: `chmod +x pastpaper/cli.py`
2. Use sudo for creating the symlink: `sudo ln -s ...`

### Terminal issues
If the interface doesn't display correctly:
1. Ensure your terminal is at least 80x24 characters
2. Try resizing your terminal
3. Make sure your terminal supports curses (most modern terminals do)

### Virtual environment issues
If you can't activate the virtual environment:
```bash
# Try this alternative activation method
source venv/bin/activate
# or if that fails, recreate the venv
python3 -m venv --clear venv
source venv/bin/activate
pip install -r requirements.txt
```

## Credits

All credits go to [Past Paper Co](https://pastpapers.co) for providing the past papers. This tool is only a client interface to facilitate downloads.

## License

This project is open source. Please check the LICENSE file for details.

## Contributing

Feel free to submit issues and pull requests to improve this tool.
