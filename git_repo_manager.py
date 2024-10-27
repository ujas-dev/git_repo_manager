import os
import shutil
import fnmatch
import re
import subprocess
import csv
import logging
import json

class GitRepoManager:
    def __init__(self, config_file='config.json'):
        self.load_config(config_file)
        self.summary = {
            'total_cloned': 0,
            'total_deleted': 0,
            'errors': [],
        }
        logging.basicConfig(
            filename='git_repo_manager.log',
            level=self.log_level,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )

    def load_config(self, config_file):
        """Load configuration from a JSON file."""
        if not os.path.exists(config_file):
            logging.error(f"Configuration file '{config_file}' not found. Using defaults.")
            self.set_default_config()
            return
        
        with open(config_file, 'r') as file:
            config = json.load(file)
            self.default_csv_file = config.get("default_csv_file", "repositories.csv")
            self.clean_directory = config.get("clean_directory", ".")
            self.default_patterns = config.get("default_patterns", ['.git', '*.csv', '*.log', '*.py', '*.md'])
            log_level_str = config.get("log_level", "info").lower()
            self.log_level = LOG_LEVELS.get(log_level_str, logging.INFO)
            self.max_workers = config.get("max_workers", 4)
            self.post_cloning_command = config.get("post_cloning_command", None)

    def set_default_config(self):
        """Set default configuration values."""
        self.default_csv_file = "repositories.csv"
        self.clean_directory = "."
        self.default_patterns = ['.git', '*.csv', '*.log', '*.py', '*.md']
        self.log_level = logging.INFO
        self.max_workers = 4
        self.post_cloning_command = None

    @staticmethod
    def is_valid_regex(pattern):
        """Check if a given pattern is a valid regex."""
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False

    @staticmethod
    def matches_any_pattern(item, patterns):
        """Check if the item matches any of the specified patterns."""
        return any(
            fnmatch.fnmatch(item, pattern) or (GitRepoManager.is_valid_regex(pattern) and re.match(pattern, item))
            for pattern in patterns
        )
    
    def delete_files_and_folders(self, target_directory, patterns, delete_matched=True, dry_run=False):
        """Delete files and folders in the target directory based on matching patterns.
        
        Args:
            target_directory (str): The directory to clean.
            patterns (list): List of patterns to match against.
            delete_matched (bool): If True, delete items that match patterns; if False, delete items that do not match.
            dry_run (bool): If True, log the actions instead of executing them.
        """
        if not os.path.exists(target_directory):
            logging.warning(f"The directory '{target_directory}' does not exist.")
            return

        for item in os.listdir(target_directory):
            item_path = os.path.join(target_directory, item)
            try:
                matches = self.matches_any_pattern(item, patterns)
                if (matches and delete_matched) or (not matches and not delete_matched):
                    if dry_run:
                        logging.info(f"[DRY RUN] Would delete: {item_path}")
                    else:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                            logging.info(f"Deleted file: {item_path}")
                            self.summary['total_deleted'] += 1
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            logging.info(f"Deleted directory: {item_path}")
                            self.summary['total_deleted'] += 1
                else:
                    logging.info(f"Did not delete: {item_path}")
            except Exception as e:
                logging.error(f"Error deleting {item_path}: {e}")
                self.summary['errors'].append(f"Error deleting {item_path}: {e}")


    def delete_unmatched_files_and_folders(self, target_directory, patterns, dry_run=False):
        """Delete files and folders in the clean directory that do not match any specified patterns."""
        if not os.path.exists(target_directory):
            logging.warning(f"The directory '{target_directory}' does not exist.")
            return

        for item in os.listdir(target_directory):
            item_path = os.path.join(target_directory, item)
            try:
                if not self.matches_any_pattern(item, patterns):
                    if dry_run:
                        logging.info(f"[DRY RUN] Would delete: {item_path}")
                    else:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                            logging.info(f"Deleted file: {item_path}")
                            self.summary['total_deleted'] += 1
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            logging.info(f"Deleted directory: {item_path}")
                            self.summary['total_deleted'] += 1
                else:
                    logging.info(f"Matched: {item_path}")
            except Exception as e:
                logging.error(f"Error deleting {item_path}: {e}")
                self.summary['errors'].append(f"Error deleting {item_path}: {e}")

    def perform_cleanup(self, target_directory, dry_run=False):
        """Perform cleanup based on user-specified options."""
        cleanup_patterns = []
        if 'logs' in self.cleanup_options:
            cleanup_patterns.append('*.log')
        if 'temp' in self.cleanup_options:
            cleanup_patterns.append('*~')  # Temporary files
        if 'custom' in self.cleanup_options:
            cleanup_patterns.extend(self.default_patterns)

        if cleanup_patterns:
            self.delete_files_and_folders(target_directory, cleanup_patterns, delete_matched=False, dry_run=dry_run)

    def clone_repository(self, repo_url, target_directory, depth, dry_run=False):
        """Clone a Git repository into the specified directory with a specified depth."""
        try:
            if dry_run:
                logging.info(f"[DRY RUN] Would clone from {repo_url} to {target_directory} with depth {depth}")
                return
            
            command = ['git', 'clone', '--depth', str(depth), '--recurse-submodules', repo_url, target_directory]
            subprocess.run(command, check=True)
            logging.info(f"Successfully cloned repository to: {target_directory}")
            self.summary['total_cloned'] += 1
            
            self.remove_remote(target_directory)
            self.delete_git_folders(target_directory)
            self.clean_submodules(target_directory)
            
            # Execute post-cloning command if specified
            if self.post_cloning_command:
                self.run_post_cloning_hook(target_directory)

        except subprocess.CalledProcessError as e:
            logging.error(f"Error cloning repository: {e}")
            self.summary['errors'].append(f"Error cloning {repo_url}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in cloning process: {e}")
            self.summary['errors'].append(f"Unexpected error with {repo_url}: {e}")

    def run_post_cloning_hook(self, target_directory):
        """Run the specified post-cloning command."""
        try:
            command = self.post_cloning_command.replace("{target}", target_directory)
            subprocess.run(command, shell=True, check=True)
            logging.info(f"Post-cloning hook executed: {command}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing post-cloning hook: {e}")
            self.summary['errors'].append(f"Error executing post-cloning hook in {target_directory}: {e}")

    @staticmethod
    def remove_remote(directory):
        """Remove the remote origin from the cloned repository."""
        try:
            remote_check = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=directory,
                check=False,
                capture_output=True
            )
            if remote_check.returncode == 0:
                subprocess.run(['git', 'remote', 'remove', 'origin'], cwd=directory, check=True)
                logging.info(f"Removed remote 'origin' from: {directory}")
            else:
                logging.info(f"No remote 'origin' found in: {directory}")
        except Exception as e:
            logging.error(f"Error removing remote from {directory}: {e}")

    @staticmethod
    def delete_git_folders(directory):
        """Delete the .git folder in the specified directory."""
        git_folder_path = os.path.join(directory, '.git')
        if os.path.exists(git_folder_path):
            shutil.rmtree(git_folder_path)
            logging.info(f"Deleted .git folder in: {directory}")

    @staticmethod
    def clean_submodules(directory):
        """Delete .git folders from all submodules."""
        gitmodules_path = os.path.join(directory, '.gitmodules')
        
        if not os.path.exists(gitmodules_path):
            logging.info(f"No submodules found in {directory}. Skipping submodule cleanup.")
            return
        
        try:
            with open(gitmodules_path, 'r') as f:
                for line in f:
                    if 'path =' in line:
                        submodule_path = line.split('=')[1].strip()
                        GitRepoManager.delete_git_folders(os.path.join(directory, submodule_path))
                        GitRepoManager.remove_remote(os.path.join(directory, submodule_path))
        except Exception as e:
            logging.error(f"Error cleaning submodules in {directory}: {e}")

    @staticmethod
    def get_unique_directory(base_name, parent_directory):
        """Generate a unique directory name by appending a suffix."""
        new_directory = os.path.join(parent_directory, base_name)
        if not os.path.exists(new_directory):
            return new_directory
        
        for i in range(1, 101):
            new_directory = os.path.join(parent_directory, f"{base_name}_{i}")
            if not os.path.exists(new_directory):
                return new_directory
        
        raise Exception("Unable to create a unique directory name after 100 attempts.")
    
    def clone_repositories_from_csv(self, csv_file, dry_run=False):
        """Read the CSV file and clone repositories based on the provided information."""
        if not os.path.exists(csv_file):
            logging.error(f"The CSV file '{csv_file}' does not exist.")
            return
        
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file, delimiter='|')  # Set the pipe delimiter
            for row in reader:
                if row['is_active'].strip().lower() != 'true':
                    continue
                repo_url = row['repo_url'].strip()
                target_directory = row['target_directory'].strip() or self.clean_directory
                depth = int(row.get('depth', 1))  # Default depth is 1 if not provided
                
                # Get custom patterns from the CSV if provided
                custom_patterns = row.get('custom_patterns', '').strip()
                patterns = [pattern.strip() for pattern in custom_patterns.split(',')] if custom_patterns else self.default_patterns

                base_repo_name = repo_url.split('/')[-1].replace('.git', '')
                target_directory = self.get_unique_directory(base_repo_name, target_directory)
                
                # Submit the clone operation
                self.clone_repository(repo_url, target_directory, depth, dry_run)

                # Delete unmatched files and folders with the specified patterns
                self.delete_files_and_folders(target_directory, patterns, delete_matched=True, dry_run=dry_run)

    def generate_summary_report(self):
        """Generate and log a summary report after processing."""
        logging.info("\n=== Summary Report ===")
        logging.info(f"Total Repositories Cloned: {self.summary['total_cloned']}")
        logging.info(f"Total Files/Folders Deleted: {self.summary['total_deleted']}")
        if self.summary['errors']:
            logging.info(f"Total Errors: {len(self.summary['errors'])}")
            for error in self.summary['errors']:
                logging.error(error)
        else:
            logging.info("Total Errors: 0")
    
    def run(self):
        """Execute the interactive CLI for the cleaning and cloning process."""
        while True:
            print("\n=== Git Repository Manager ===")
            print("1. Clean Files and Folders")
            print("2. Clone Repositories from CSV")
            print("3. Generate Summary Report")
            print("4. Exit")

            choice = input("Select an option (1-4): ").strip()

            if choice == '1':
                self.clean_files_interactively()
            elif choice == '2':
                self.clone_repositories_interactively()
            elif choice == '3':
                self.generate_summary_report()
            elif choice == '4':
                print("Exiting the program.")
                break
            else:
                print("Invalid option. Please try again.")

    def clean_files_interactively(self):
        target_directory = input("Enter the directory to clean (or press Enter for current directory): ") or '.'
        dry_run = input("Enable dry run mode? (y/n): ").strip().lower() == 'y'
        
        patterns_input = input("Enter file patterns to keep (comma-separated, leave empty for defaults): ")
        if patterns_input:
            self.default_patterns = [pattern.strip() for pattern in patterns_input.split(',')]
        
        # Prompt user for cleanup options
        cleanup_options_input = input("Select cleanup options (logs, temp, custom, none) separated by commas: ")
        self.cleanup_options = [opt.strip() for opt in cleanup_options_input.split(',')] if cleanup_options_input else ['custom']
        
        self.perform_cleanup(target_directory, dry_run)

    def clone_repositories_interactively(self):
        csv_file_path = input(f"Enter the path to the CSV file (or press Enter for default: {self.default_csv_file}): ")
        if not csv_file_path.strip():
            csv_file_path = self.default_csv_file
        
        if not os.path.exists(csv_file_path):
            logging.error(f"The specified CSV file '{csv_file_path}' does not exist. Using default CSV.")
            csv_file_path = self.default_csv_file

        dry_run = input("Enable dry run mode? (y/n): ").strip().lower() == 'y'

        self.clone_repositories_from_csv(csv_file_path, dry_run)

if __name__ == "__main__":
    # Create an instance of the GitRepoManager with default parameters
    manager = GitRepoManager()
    # Run the cleaning and cloning process
    manager.run()
