#!/usr/bin/env python

import yaml
import subprocess
import sys
from pathlib import Path

def run_create_notebook(notebook_config):
    """Run create_notebook.py with the given configuration."""
    dandiset_id = notebook_config['dandiset_id']
    version = notebook_config['dandiset_version']
    chat_id = notebook_config.get('chat_id', None)
    prompt = notebook_config['prompt']
    model = notebook_config['model']
    skip_explore = notebook_config.get('skip_explore', False)

    # Construct the chat URL using the same pattern as in run.sh
    chat_id_8_or_skip_explore = chat_id[:8] if not skip_explore else 'skip-explore'
    if not skip_explore:
        chat_id_2 = chat_id[:2]
        chat_url = f"https://neurosift.org/dandiset-explorer-chats/{dandiset_id}/{version}/chats/{chat_id_2}/{chat_id}/chat.json"
    else:
        chat_url = None

    # Extract model name after '/' for output path
    model_second_part = model.split('/')[-1]

    # Construct output path using the same pattern as in run.sh
    output_path = f"notebooks/dandisets/{dandiset_id}/{version}/{chat_id_8_or_skip_explore}/{model_second_part}/{prompt}"

    # Construct prompt path
    prompt_path = f"prompts/prompt-{prompt}.txt"

    # Prepare command arguments
    cmd = [
        'python',
        'scripts/create_notebook.py',
        '--dandiset', str(dandiset_id),
        '--version', str(version),
        '--model', str(model),
        '--prompt', prompt_path,
        '--output', output_path
    ]
    if chat_url:
        cmd.extend(['--chat', chat_url])

    if skip_explore:
        cmd.append('--skip-explore')

    print(f"\nProcessing notebook for dandiset {dandiset_id}...")
    try:
        # Run the command and capture output
        subprocess.run(cmd, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing dandiset {dandiset_id}:")
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        return False

def main():
    # Load configuration from notebooks.yaml
    try:
        with open('notebooks.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("notebooks.yaml not found")
        sys.exit(1)

    if 'notebooks' not in config:
        print("No 'notebooks' section found in YAML file")
        sys.exit(1)

    # Track success/failure counts
    total = len(config['notebooks'])
    successful = 0
    failed = []

    # Process each notebook configuration
    for notebook in config['notebooks']:
        if run_create_notebook(notebook):
            successful += 1
        else:
            failed.append(notebook['dandiset_id'])

    # Print summary
    print("\nProcessing complete!")
    print(f"Successfully processed {successful} out of {total} notebooks")
    if failed:
        print("Failed to process the following dandisets:")
        for dandiset_id in failed:
            print(f"  - {dandiset_id}")
        sys.exit(1)

if __name__ == '__main__':
    main()
