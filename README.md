# Git Repository Manager

![Git Repository Manager](https://via.placeholder.com/800x200?text=Git+Repository+Manager)

## Overview

The **Git Repository Manager** is a powerful Python module designed to streamline the management of Git repositories and maintain clean working directories. With an array of features, it allows developers to efficiently clone, clean, and manage multiple repositories, all while providing robust error handling and logging capabilities.

## 🚀 Features

### 1. **Directory Cleanup**
   - Remove files and folders that do not match specified patterns to maintain a clutter-free workspace.

### 2. **CSV-Based Cloning**
   - Clone multiple repositories specified in a CSV file, supporting both default and custom file patterns.

### 3. **Post-Cloning Hooks**
   - Execute custom shell commands after cloning repositories, allowing for automated setup or configuration tasks.

### 4. **Multi-Threaded Cloning**
   - Utilize concurrent threads for cloning multiple repositories, significantly improving performance and reducing wait times.

### 5. **Interactive CLI**
   - User-friendly command-line interface that guides users through cleanup and cloning operations.

### 6. **Error Handling Improvements**
   - Comprehensive error logging with detailed context, ensuring a smoother user experience and easier debugging.

### 7. **Summary Report**
   - Generate a summary report detailing operations performed, including total repositories cloned and any errors encountered.

### 8. **Environment Configuration**
   - Load and customize settings from a JSON configuration file, enabling quick adjustments to module behavior.

### 9. **Dry Run Mode**
   - Safely simulate operations without making any actual changes, allowing users to preview the effects of their commands.

### 10. **Custom Patterns**
   - Specify unique file patterns directly in the CSV file for granular control over what files to keep after cloning.

### 11. **Cleanup Options**
   - Choose specific types of files to clean, such as logs and temporary files, ensuring that your working directory remains organized.

### 12. **Enhanced Logging Levels**
   - Control the verbosity of logging output with adjustable logging levels, making it easier to focus on critical information.

### 13. **Summary Report**
   - Automatically generate a comprehensive summary of operations, providing insight into what was cloned, deleted, and any issues that occurred.

## 📦 Requirements

- **Python 3.6 or higher**
- **Git** must be installed and available in your system's PATH

## 🛠️ Installation

1. **Clone this repository:**

   ```bash
   git clone https://github.com/yourusername/git-repo-manager.git
   cd git-repo-manager
   ```

2. **(Optional) Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install required packages:**

   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

The module uses a JSON configuration file (`config.json`) to load default settings. Here’s a sample configuration:

```json
{
    "default_csv_file": "repositories.csv",
    "clean_directory": ".",
    "default_patterns": ["*.txt", "*.log", "*~"],
    "log_level": "info",
    "max_workers": 4
}
```

You can customize the settings to suit your needs. If the configuration file is not found, the module will revert to default values.

## 🖥️ Usage

To run the Git Repository Manager, execute the following command in your terminal:

```bash
python git_repo_manager.py
```

You will be presented with an interactive menu to choose from the following options:

1. **Clean Files and Folders**
2. **Clone Repositories from CSV**
3. **Generate Summary Report**
4. **Exit**

### Example CSV Format

The CSV file for cloning repositories should have the following format:

```csv
repo_url|target_directory|is_active|depth|custom_patterns
https://github.com/user/repo.git|./repo|true|1|*.py,*.txt
```

- `repo_url`: The URL of the Git repository.
- `target_directory`: The directory where the repository will be cloned.
- `is_active`: Whether the repository should be cloned (`true`/`false`).
- `depth`: The depth of the clone operation.
- `custom_patterns`: Patterns for files to keep after cloning.

## 📜 Logging

The module logs operations and errors to `git_repo_manager.log`. Adjust the log level in the configuration file as needed to control verbosity.

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues or pull requests to enhance this module.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions or support, feel free to reach out via [GitHub Issues](https://github.com/yourusername/git-repo-manager/issues).

---

Thank you for using the Git Repository Manager! Happy coding! 🎉
```

### Key Enhancements:
- **Visual Elements**: Added emojis to make sections more engaging.
- **Feature Details**: Each feature now has a concise description for clarity.
- **Sections**: Organized sections with headings for better readability.
- **Contact Information**: Provided a way for users to get support.

Feel free to customize it further to match your project’s branding or specific needs!