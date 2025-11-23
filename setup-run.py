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


def setup_evaluation_template(target_path, use_case_path, is_orchestration):
    """Copy evaluation template and create .report/ folder."""
    repo_root = get_repo_root()
    
    # Determine which evaluation template to use
    # First try use-case specific template, fall back to generic
    if is_orchestration:
        use_case_template = use_case_path / 'EVALUATION_ORCHESTRATION.md'
        generic_template = repo_root / 'EVALUATION_REPORT_ORCHESTRATION.md'
    else:
        use_case_template = use_case_path / 'EVALUATION_CODING_AGENT.md'
        generic_template = repo_root / 'EVALUATION_REPORT_CODING_AGENT.md'
    
    # Choose template source
    if use_case_template.exists():
        template_source = use_case_template
        print_info(f"Using use-case specific template")
    elif generic_template.exists():
        template_source = generic_template
        print_info(f"Using generic template")
    else:
        print_error("No evaluation template found!")
        return False
    
    try:
        # Create .report/ folder
        report_dir = target_path / '.report'
        report_dir.mkdir(exist_ok=True)
        
        # Create screenshots subfolder
        (report_dir / 'screenshots').mkdir(exist_ok=True)
        
        # Copy evaluation template to .report/ folder
        eval_dest = report_dir / 'EVALUATION.md'
        shutil.copy(template_source, eval_dest)
        
        # Create a README in .report explaining its purpose
        report_readme = report_dir / 'README.md'
        with open(report_readme, 'w') as f:
            f.write("""# Evaluation Assets

This folder contains all assets related to evaluating this agent run:

- **EVALUATION.md** - Structured evaluation checklist for this run
- **screenshots/** - Screenshots of the application, errors, interesting moments
- **chat-log.md** - Conversation history with the agent (optional)
- **transcript.json** - Full session transcript (optional)
- **session-notes.md** - Manual notes about the session (optional)

Fill out EVALUATION.md after completing your run to document what worked and what didn't.
""")
        
        print_success(f"Created .report/ folder with evaluation template")
        return True
    except Exception as e:
        print_error(f"Error setting up evaluation: {e}")
        return False


def scaffold_index_entry(use_case_path, target_path, is_orchestration, agent_harness, model_name, paradigm_name=None):
    """Add a scaffolded entry to the appropriate index file."""
    try:
        # Determine index file path
        if is_orchestration:
            index_file = use_case_path / 'INDEX_ORCHESTRATION.md'
        else:
            index_file = use_case_path / 'INDEX_CODING_AGENTS.md'
        
        if not index_file.exists():
            print_info(f"Index file not found, skipping scaffolding")
            return False
        
        # Read existing index
        with open(index_file, 'r') as f:
            content = f.read()
        
        # Build relative path from use case to target
        try:
            rel_path = target_path.relative_to(use_case_path)
        except ValueError:
            rel_path = target_path
        
        # Get current date
        from datetime import datetime
        today = datetime.now().strftime("%b %d, %Y")
        
        # Create scaffolded entry
        if is_orchestration:
            entry = f"""
## {paradigm_name.upper()} - {agent_harness.title()} - {model_name.title()} - {today}

![Main Screenshot]({rel_path}/.report/screenshot.png)

**Status:** ✅ Success | ⚠️ Partial | ❌ Failed  
**Time:** `[X hours]`  
**Score:** `[X/30]` ([detailed report]({rel_path}/.report/EVALUATION.md))

**Quick Summary:**
```
[Fill in after run - 2-3 sentences about how orchestration worked]
```

**Workflow:**
- [ ] Specification phase completed
- [ ] Architecture phase completed
- [ ] Implementation phase completed
- [ ] Testing phase completed

**Core Features:**
- [ ] [Feature 1]
- [ ] [Feature 2]
- [ ] [Feature 3]
- [ ] [Feature 4]

**Rating:** ⭐⭐⭐⭐⭐ `X/5` - `[Recommendation]`

---
"""
        else:
            entry = f"""
## {agent_harness.title()} - {model_name.title()} - {today}

![Main Screenshot]({rel_path}/.report/screenshot.png)

**Status:** ✅ Success | ⚠️ Partial | ❌ Failed  
**Time:** `[X hours]`  
**Score:** `[X/30]` ([detailed report]({rel_path}/.report/EVALUATION.md))

**Quick Summary:**
```
[Fill in after run - 2-3 sentences about what worked/didn't work]
```

**Core Features:**
- [ ] [Feature 1]
- [ ] [Feature 2]
- [ ] [Feature 3]
- [ ] [Feature 4]

**Rating:** ⭐⭐⭐⭐⭐ `X/5` - `[Recommendation]`

---
"""
        
        # Find insertion point (before "## Summary Statistics")
        summary_marker = "## Summary Statistics"
        if summary_marker in content:
            # Insert before summary
            parts = content.split(summary_marker, 1)
            new_content = parts[0] + entry + "\n" + summary_marker + parts[1]
        else:
            # Append to end
            new_content = content + "\n" + entry
        
        # Write updated index
        with open(index_file, 'w') as f:
            f.write(new_content)
        
        print_success(f"Scaffolded entry in {index_file.name}")
        return True
    except Exception as e:
        print_error(f"Error scaffolding index entry: {e}")
        return False


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
    
    # Setup evaluation template and .report/ folder
    setup_evaluation_template(target_path, use_case['path'], is_orchestration)
    
    # Scaffold index entry
    scaffold_index_entry(
        use_case['path'], 
        target_path, 
        is_orchestration, 
        agent_harness, 
        model_name, 
        paradigm_name
    )
    
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
    print(f"  2. Read {Colors.BOLD}prompt.md{Colors.ENDC}")
    print(f"  3. Start your agent with the prompt")
    print(f"  4. After completion:")
    print(f"     - Add screenshot as {Colors.BOLD}.report/screenshot.png{Colors.ENDC}")
    print(f"     - Fill out {Colors.BOLD}.report/EVALUATION.md{Colors.ENDC}")
    print(f"     - Update the index entry in {Colors.BOLD}{'INDEX_ORCHESTRATION.md' if is_orchestration else 'INDEX_CODING_AGENTS.md'}{Colors.ENDC}")
    print(f"     - Optional: Add session logs to {Colors.BOLD}.report/session-logs/{Colors.ENDC}")
    print()
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n")
        print_error("Interrupted by user")
        sys.exit(1)
