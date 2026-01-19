#!/usr/bin/env python3
"""
Repository Statistics Generator

Generates comprehensive statistics about a repository including:
- Lines of code by language
- File counts
- Directory structure depth
- Largest files
- Language distribution
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import json

# Common file extensions to language mapping
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.jsx': 'JavaScript (JSX)',
    '.tsx': 'TypeScript (TSX)',
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.h': 'C/C++ Header',
    '.hpp': 'C++ Header',
    '.cs': 'C#',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.zsh': 'Zsh',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'Sass',
    '.less': 'Less',
    '.sql': 'SQL',
    '.md': 'Markdown',
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.xml': 'XML',
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', 'venv', 'env', 
    '.venv', 'dist', 'build', 'target', '.next', '.cache',
    'vendor', 'coverage', '.pytest_cache', '.mypy_cache'
}

def count_lines(file_path):
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def get_file_size(file_path):
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

def analyze_repository(repo_path):
    """Analyze repository and return statistics."""
    repo_path = Path(repo_path).resolve()
    
    if not repo_path.exists():
        print(f"Error: Path '{repo_path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    stats = {
        'total_files': 0,
        'total_lines': 0,
        'total_size': 0,
        'languages': defaultdict(lambda: {'files': 0, 'lines': 0, 'size': 0}),
        'largest_files': [],
        'max_depth': 0,
    }
    
    all_files = []
    
    # Walk through repository
    for root, dirs, files in os.walk(repo_path):
        # Remove skip directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        # Calculate depth
        depth = len(Path(root).relative_to(repo_path).parts)
        stats['max_depth'] = max(stats['max_depth'], depth)
        
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            
            # Skip hidden files
            if file.startswith('.'):
                continue
            
            stats['total_files'] += 1
            
            # Count lines and size
            lines = count_lines(file_path)
            size = get_file_size(file_path)
            
            stats['total_lines'] += lines
            stats['total_size'] += size
            
            # Track by language
            language = LANGUAGE_EXTENSIONS.get(ext, f'Other ({ext})')
            stats['languages'][language]['files'] += 1
            stats['languages'][language]['lines'] += lines
            stats['languages'][language]['size'] += size
            
            # Track for largest files
            all_files.append({
                'path': str(file_path.relative_to(repo_path)),
                'lines': lines,
                'size': size,
                'language': language
            })
    
    # Get top 10 largest files by line count
    stats['largest_files'] = sorted(all_files, key=lambda x: x['lines'], reverse=True)[:10]
    
    # Convert defaultdict to regular dict
    stats['languages'] = dict(stats['languages'])
    
    return stats

def format_size(size_bytes):
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def print_stats(stats):
    """Print statistics in a readable format."""
    print("=" * 70)
    print("REPOSITORY STATISTICS")
    print("=" * 70)
    
    print(f"\nTotal Files: {stats['total_files']:,}")
    print(f"Total Lines: {stats['total_lines']:,}")
    print(f"Total Size: {format_size(stats['total_size'])}")
    print(f"Max Directory Depth: {stats['max_depth']}")
    
    print("\n" + "=" * 70)
    print("LANGUAGE DISTRIBUTION")
    print("=" * 70)
    
    # Sort languages by line count
    sorted_langs = sorted(
        stats['languages'].items(),
        key=lambda x: x[1]['lines'],
        reverse=True
    )
    
    print(f"\n{'Language':<20} {'Files':<10} {'Lines':<15} {'Size':<12}")
    print("-" * 70)
    
    for lang, data in sorted_langs:
        percentage = (data['lines'] / stats['total_lines'] * 100) if stats['total_lines'] > 0 else 0
        print(f"{lang:<20} {data['files']:<10} {data['lines']:<10,} ({percentage:>5.1f}%) {format_size(data['size']):<12}")
    
    print("\n" + "=" * 70)
    print("LARGEST FILES (by line count)")
    print("=" * 70)
    
    print(f"\n{'File':<50} {'Lines':<10} {'Language':<15}")
    print("-" * 70)
    
    for file in stats['largest_files']:
        # Truncate long paths
        path = file['path']
        if len(path) > 47:
            path = "..." + path[-44:]
        print(f"{path:<50} {file['lines']:<10,} {file['language']:<15}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python repo_stats.py <repository_path> [--json]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    output_json = '--json' in sys.argv
    
    stats = analyze_repository(repo_path)
    
    if output_json:
        print(json.dumps(stats, indent=2, default=str))
    else:
        print_stats(stats)

if __name__ == '__main__':
    main()
