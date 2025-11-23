#!/usr/bin/env python3
"""
Agent Comparison Setup Tool

A stylish CLI tool to set up new agent comparison runs.
No dependencies required - uses only Python standard library.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal styling."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def print_header(text):
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}\n")


def print_section(text):
    """Print a section title."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")


def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print an info message."""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.ENDC}")


def get_repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.resolve()


def discover_use_cases():
    """Discover all use cases by scanning directories."""
    repo_root = get_repo_root()
    use_cases = []
    
    for item in sorted(repo_root.iterdir()):
        # Match any directory starting with XX- where XX is 01-99
        if item.is_dir() and len(item.name) > 3 and item.name[:2].isdigit() and item.name[2] == '-':
            base_dir = item / '_base'
            if base_dir.exists():
                # Try to read README for description
                readme_path = item / 'README.md'
                description = "No description available"
                if readme_path.exists():
                    with open(readme_path, 'r') as f:
                        lines = f.readlines()
                        # Look for the first line after the title (usually a description)
                        for i, line in enumerate(lines):
                            if line.startswith('**') and '**' in line[2:]:
                                description = line.strip('*').strip()
                                break
                
                use_cases.append({
                    'id': item.name,
                    'name': item.name,
                    'path': item,
                    'description': description
                })
    
    return use_cases


def print_menu(items, title="Select an option"):
    """Print a numbered menu and return user selection."""
    print_section(title)
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            desc = item.get('description', '')
            name = item.get('name', str(item))
            print(f"  {Colors.CYAN}{i}.{Colors.ENDC} {Colors.BOLD}{name}{Colors.ENDC}")
            if desc:
                print(f"     {Colors.DIM}{desc}{Colors.ENDC}")
        else:
            print(f"  {Colors.CYAN}{i}.{Colors.ENDC} {item}")
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Enter your choice (1-{len(items)}): {Colors.ENDC}")
            choice_num = int(choice)
            if 1 <= choice_num <= len(items):
                return choice_num - 1
            else:
                print_error(f"Please enter a number between 1 and {len(items)}")
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n")
            print_error("Cancelled by user")
            sys.exit(0)


def get_text_input(prompt, allow_empty=False):
    """Get text input from user."""
    while True:
        try:
            value = input(f"{Colors.BOLD}{prompt}{Colors.ENDC}").strip()
            if value or allow_empty:
                return value
            else:
                print_error("Input cannot be empty")
        except KeyboardInterrupt:
            print("\n")
            print_error("Cancelled by user")
            sys.exit(0)


def sanitize_branch_name(name):
    """Sanitize a string to be valid as a git branch name."""
    # Replace invalid characters with hyphens
    valid = name.replace('/', '-').replace(' ', '-').replace('_', '-')
    # Remove any characters that aren't alphanumeric or hyphens
    valid = ''.join(c for c in valid if c.isalnum() or c == '-')
    # Remove duplicate hyphens
    while '--' in valid:
        valid = valid.replace('--', '-')
    # Remove leading/trailing hyphens
    return valid.strip('-').lower()


def check_git_status():
    """Check if we're in a git repository and it's clean."""
    try:
        # Check if we're in a git repo
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=get_repo_root(),
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return False, "Not in a git repository"
        
        # Check for uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=get_repo_root(),
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print_info("You have uncommitted changes:")
            print(result.stdout)
            response = get_text_input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False, "Uncommitted changes detected"
        
        return True, None
    except FileNotFoundError:
        return False, "Git is not installed"


def create_branch(branch_name):
    """Create and checkout a new git branch."""
    try:
        # Create and checkout new branch
        result = subprocess.run(
            ['git', 'checkout', '-b', branch_name],
            cwd=get_repo_root(),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            if 'already exists' in result.stderr:
                print_error(f"Branch '{branch_name}' already exists")
                response = get_text_input("Switch to existing branch? (y/n): ")
                if response.lower() == 'y':
                    subprocess.run(['git', 'checkout', branch_name], cwd=get_repo_root())
                    return True
                return False
            else:
                print_error(f"Failed to create branch: {result.stderr}")
                return False
        
        print_success(f"Created and switched to branch: {branch_name}")
        return True
    except Exception as e:
        print_error(f"Error creating branch: {e}")
        return False


def find_available_path(target_path):
    """Find an available path by enumerating if necessary."""
    if not target_path.exists():
        return target_path
    
    # Find the highest existing enumeration
    base_name = target_path.name
    parent = target_path.parent
    counter = 2
    
    # Check for existing enumerated folders
    while True:
        enumerated_name = f"{base_name}_{counter}"
        enumerated_path = parent / enumerated_name
        if not enumerated_path.exists():
            return enumerated_path
        counter += 1


def copy_base_to_target(base_path, target_path):
    """Copy _base folder contents to target location."""
    try:
        # Create parent directories if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Find available path (enumerate if needed)
        original_path = target_path
        target_path = find_available_path(target_path)
        
        if target_path != original_path:
            print_info(f"Target exists, using enumerated path: {target_path.name}")
        
        # Copy _base contents
        shutil.copytree(base_path, target_path)
        print_success(f"Copied base to: {target_path.relative_to(get_repo_root())}")
        return target_path
    except Exception as e:
        print_error(f"Error copying files: {e}")
        return None


def main():
    """Main application flow."""
    print_header("Agent Comparison Setup Tool")
    
    # Check git status
    git_ok, git_error = check_git_status()
    if not git_ok:
        print_error(f"Git check failed: {git_error}")
        print_info("Continuing without git branch creation...")
        create_git_branch = False
    else:
        print_success("Git repository is ready")
        create_git_branch = True
    
    # Discover use cases
    use_cases = discover_use_cases()
    if not use_cases:
        print_error("No use cases found!")
        return 1
    
    # Step 1: Select use case
    use_case_idx = print_menu(use_cases, "📋 Select Use Case")
    use_case = use_cases[use_case_idx]
    print_success(f"Selected: {use_case['name']}")
    
    # Step 2: Select run type (coding agent or orchestration)
    run_types = [
        "Coding Agent (one-shot)",
        "Orchestration Paradigm"
    ]
    run_type_idx = print_menu(run_types, "🎯 Select Run Type")
    is_orchestration = run_type_idx == 1
    
    # Step 3: Get paradigm name if orchestration
    paradigm_name = None
    if is_orchestration:
        print_section("🔧 Orchestration Paradigm")
        print_info("Examples: bmad, spec-kit, openspec, custom-flow")
        paradigm_name = get_text_input("Enter paradigm name: ")
        paradigm_name = sanitize_branch_name(paradigm_name)
        print_success(f"Paradigm: {paradigm_name}")
    
    # Step 4: Get agent harness
    print_section("🤖 Agent Harness")
    print_info("Examples: codexcli, geminicli, cursor, windsurf, aider")
    agent_harness = get_text_input("Enter agent harness name: ")
    agent_harness = sanitize_branch_name(agent_harness)
    print_success(f"Harness: {agent_harness}")
    
    # Step 5: Get model name
    print_section("🧠 Model")
    print_info("Examples: gpt-5-high, claude-sonnet, gemini-2-flash, codex-max")
    model_name = get_text_input("Enter model name: ")
    model_name = sanitize_branch_name(model_name)
    print_success(f"Model: {model_name}")
    
    # Build paths and branch name
    base_path = use_case['path'] / '_base'
    
    if is_orchestration:
        target_path = use_case['path'] / 'orchestration' / paradigm_name / f"{agent_harness}_{model_name}"
        branch_name = f"{paradigm_name}_{agent_harness}_{model_name}"
    else:
        target_path = use_case['path'] / 'coding_agents' / f"{agent_harness}_{model_name}"
        branch_name = f"{agent_harness}_{model_name}"
    
    # Summary
    print_header("Summary")
    print(f"{Colors.BOLD}Use Case:{Colors.ENDC} {use_case['name']}")
    print(f"{Colors.BOLD}Type:{Colors.ENDC} {'Orchestration' if is_orchestration else 'Coding Agent'}")
    if is_orchestration:
        print(f"{Colors.BOLD}Paradigm:{Colors.ENDC} {paradigm_name}")
    print(f"{Colors.BOLD}Agent Harness:{Colors.ENDC} {agent_harness}")
    print(f"{Colors.BOLD}Model:{Colors.ENDC} {model_name}")
    print(f"{Colors.BOLD}Target Path:{Colors.ENDC} {target_path.relative_to(get_repo_root())}")
    print(f"{Colors.BOLD}Branch Name:{Colors.ENDC} {branch_name}")
    
    # Confirm
    print()
    response = get_text_input("Proceed with setup? (y/n): ")
    if response.lower() != 'y':
        print_error("Setup cancelled")
        return 1
    
    # Execute setup
    print_header("Setting Up")
    
    # Copy files
    actual_target = copy_base_to_target(base_path, target_path)
    if not actual_target:
        return 1
    
    # Update target_path to actual location used
    target_path = actual_target
    
    # Create git branch
    if create_git_branch:
        if not create_branch(branch_name):
            print_info("Continuing without branch creation...")
    
    # Final message
    print_header("Setup Complete!")
    print(f"{Colors.GREEN}✓ Your workspace is ready at:{Colors.ENDC}")
    print(f"  {Colors.BOLD}{target_path.relative_to(get_repo_root())}{Colors.ENDC}")
    print()
    print(f"{Colors.CYAN}Next steps:{Colors.ENDC}")
    print(f"  1. cd {target_path.relative_to(get_repo_root())}")
    print(f"  2. Read {Colors.BOLD}_base/prompt.md{Colors.ENDC} (or the copied {Colors.BOLD}prompt.md{Colors.ENDC})")
    print(f"  3. Start your agent with the prompt")
    print(f"  4. Let it work and review the results!")
    print()
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n")
        print_error("Interrupted by user")
        sys.exit(1)
