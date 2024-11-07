
# Dependency Confusion Checker

**Dependency Confusion Checker** is a Python-based tool for identifying potential dependency confusion vulnerabilities in JavaScript (`package.json`) and Python (`requirements.txt`) projects. Dependency confusion occurs when there is an overlap between private and public package names, which can allow attackers to inject malicious packages.

## Features

- Checks for potential dependency confusion vulnerabilities in both JavaScript (`package.json`) and Python (`requirements.txt`) dependencies.
- Parses dependency files and checks for package availability in public registries.
- Flags dependencies that may cause dependency confusion based on version inconsistencies between private and public repositories.

## Prerequisites

- Python 3.6+
- Internet connection (to check against public registries)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/dependency-confusion-checker.git
   cd dependency-confusion-checker
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

This tool is designed to take input from `stdin` and expects a `requirements.txt` file (for Python) or `package.json` (for JavaScript) in the URL. The main script `check.py` reads the input and processes each dependency to detect potential dependency confusion vulnerabilities.

### Running the Tool

To run the tool, use the following command:

```bash
cat urls.txt | python check.py
```

Or, for a JavaScript project:

```bash
cat urls.txt | python check.py
```

### Example Output

The tool will output a list of dependencies that may be vulnerable to dependency confusion:

```plaintext
[VULN] https://redacted-js.com/package.json [package-notfound|404|js]
[VULN] https://redacted-py.com/requirements.txt [package-notfound|404|python]
```

### Exit Codes

- `0`: No issues found.
- `1`: Potential dependency confusion vulnerabilities detected.

## How It Works

1. The `check.py` script reads from `stdin` to receive the list of dependencies.
2. For each dependency, it:
   - Checks if the package exists on public registries such as PyPI (for Python) or npm (for JavaScript).
   - Compares versions to identify inconsistencies.
   - Flags any packages that may lead to dependency confusion.

3. Results are printed in the console, listing any vulnerable packages found.

## License

This project is licensed under the MIT License.

---

**Note**: This tool is intended for security analysis purposes. Always use responsibly and only on projects for which you have authorization.
