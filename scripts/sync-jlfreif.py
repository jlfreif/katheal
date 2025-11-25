#!/usr/bin/env python3
"""
Sync script for the jlfreif/katheal remote repository.

This script helps synchronize the local repository with jlfreif/katheal
by managing a separate remote called 'jlfreif'.

Usage:
    python scripts/sync-jlfreif.py pull   # Pull from jlfreif/katheal
    python scripts/sync-jlfreif.py push   # Push to jlfreif/katheal

The script will automatically:
- Set up the jlfreif remote if it doesn't exist
- Use the current branch for pull/push operations
- Provide clear feedback on the operation status
"""

import sys
import subprocess
import argparse

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def error(message):
    """Print error message in red."""
    print(f"{RED}✗ ERROR: {message}{RESET}")

def success(message):
    """Print success message in green."""
    print(f"{GREEN}✓ {message}{RESET}")

def info(message):
    """Print info message in blue."""
    print(f"{BLUE}ℹ {message}{RESET}")

def warning(message):
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠ {message}{RESET}")

def run_command(cmd, capture_output=True):
    """Run a shell command and return the result."""
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip(), result.stderr.strip()
        else:
            subprocess.run(cmd, shell=True, check=True)
            return None, None
    except subprocess.CalledProcessError as e:
        return None, e.stderr if capture_output else str(e)

def get_current_branch():
    """Get the current git branch name."""
    stdout, stderr = run_command("git branch --show-current")
    if stdout is None:
        error(f"Failed to get current branch: {stderr}")
        sys.exit(1)
    return stdout

def remote_exists(remote_name):
    """Check if a git remote exists."""
    stdout, _ = run_command("git remote")
    if stdout is None:
        return False
    remotes = stdout.split('\n')
    return remote_name in remotes

def setup_remote():
    """Set up the jlfreif remote if it doesn't exist."""
    if remote_exists('jlfreif'):
        info("Remote 'jlfreif' already exists")
        return True

    info("Setting up remote 'jlfreif' -> git@github.com:jlfreif/katheal.git")
    stdout, stderr = run_command("git remote add jlfreif git@github.com:jlfreif/katheal.git")

    if stdout is None and stderr:
        error(f"Failed to add remote: {stderr}")
        return False

    success("Remote 'jlfreif' added successfully")
    return True

def pull_from_jlfreif(branch):
    """Pull from the jlfreif remote (main branch)."""
    info(f"Pulling from jlfreif/main into {branch}...")

    # First fetch
    info("Fetching from jlfreif...")
    _, stderr = run_command("git fetch jlfreif", capture_output=False)
    if stderr:
        error(f"Failed to fetch from jlfreif: {stderr}")
        return False

    # Then pull from main branch
    info(f"Merging jlfreif/main into {branch}...")
    _, stderr = run_command("git pull jlfreif main", capture_output=False)
    if stderr:
        error(f"Failed to pull from jlfreif/main: {stderr}")
        return False

    success(f"Successfully pulled from jlfreif/main into {branch}")
    return True

def push_to_jlfreif(branch):
    """Push to the jlfreif remote (main branch)."""
    info(f"Pushing {branch} to jlfreif/main...")

    _, stderr = run_command(f"git push jlfreif {branch}:main", capture_output=False)
    if stderr:
        error(f"Failed to push to jlfreif/main: {stderr}")
        return False

    success(f"Successfully pushed {branch} to jlfreif/main")
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sync with jlfreif/katheal repository',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s pull    Pull from jlfreif/katheal
  %(prog)s push    Push to jlfreif/katheal
        """
    )
    parser.add_argument(
        'action',
        choices=['pull', 'push'],
        help='Action to perform: pull from or push to jlfreif remote'
    )

    args = parser.parse_args()

    print("\n" + "="*80)
    print(f"SYNC WITH jlfreif/katheal - {args.action.upper()}")
    print("="*80 + "\n")

    # Get current branch
    branch = get_current_branch()
    info(f"Current branch: {branch}")

    # Set up remote if needed
    if not setup_remote():
        return 1

    print()

    # Perform the requested action
    if args.action == 'pull':
        success_result = pull_from_jlfreif(branch)
    else:  # push
        success_result = push_to_jlfreif(branch)

    print()

    if success_result:
        success(f"{args.action.capitalize()} operation completed successfully!")
        return 0
    else:
        error(f"{args.action.capitalize()} operation failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
