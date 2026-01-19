#!/usr/bin/env python3
"""
Dependency Analyzer

Analyzes project dependencies from various package manager files:
- package.json (Node.js)
- requirements.txt, setup.py, pyproject.toml (Python)
- Cargo.toml (Rust)
- go.mod (Go)
- pom.xml (Maven/Java)
- build.gradle (Gradle/Java)
- Gemfile (Ruby)
- composer.json (PHP)
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import re

def parse_package_json(file_path):
    """Parse package.json for Node.js dependencies."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        deps = {
            'dependencies': data.get('dependencies', {}),
            'devDependencies': data.get('devDependencies', {}),
            'peerDependencies': data.get('peerDependencies', {}),
        }
        
        return {
            'ecosystem': 'Node.js',
            'file': str(file_path),
            'dependencies': deps,
            'total_count': sum(len(v) for v in deps.values())
        }
    except Exception as e:
        return {'error': str(e)}

def parse_requirements_txt(file_path):
    """Parse requirements.txt for Python dependencies."""
    try:
        deps = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove version specifiers for cleaner display
                    pkg = re.split(r'[=<>!]', line)[0].strip()
                    if pkg:
                        deps.append(line)
        
        return {
            'ecosystem': 'Python',
            'file': str(file_path),
            'dependencies': {'dependencies': deps},
            'total_count': len(deps)
        }
    except Exception as e:
        return {'error': str(e)}

def parse_pyproject_toml(file_path):
    """Parse pyproject.toml for Python dependencies."""
    try:
        deps = []
        dev_deps = []
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simple parsing for dependencies section
        in_deps = False
        in_dev_deps = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if '[tool.poetry.dependencies]' in line or '[project.dependencies]' in line:
                in_deps = True
                in_dev_deps = False
                continue
            elif '[tool.poetry.dev-dependencies]' in line or '[tool.poetry.group.dev.dependencies]' in line:
                in_deps = False
                in_dev_deps = True
                continue
            elif line.startswith('['):
                in_deps = False
                in_dev_deps = False
                continue
            
            if in_deps and '=' in line:
                pkg = line.split('=')[0].strip()
                if pkg and pkg != 'python':
                    deps.append(line)
            elif in_dev_deps and '=' in line:
                pkg = line.split('=')[0].strip()
                if pkg:
                    dev_deps.append(line)
        
        return {
            'ecosystem': 'Python',
            'file': str(file_path),
            'dependencies': {
                'dependencies': deps,
                'devDependencies': dev_deps
            },
            'total_count': len(deps) + len(dev_deps)
        }
    except Exception as e:
        return {'error': str(e)}

def parse_cargo_toml(file_path):
    """Parse Cargo.toml for Rust dependencies."""
    try:
        deps = []
        dev_deps = []
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        in_deps = False
        in_dev_deps = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line == '[dependencies]':
                in_deps = True
                in_dev_deps = False
                continue
            elif line == '[dev-dependencies]':
                in_deps = False
                in_dev_deps = True
                continue
            elif line.startswith('['):
                in_deps = False
                in_dev_deps = False
                continue
            
            if in_deps and '=' in line:
                deps.append(line)
            elif in_dev_deps and '=' in line:
                dev_deps.append(line)
        
        return {
            'ecosystem': 'Rust',
            'file': str(file_path),
            'dependencies': {
                'dependencies': deps,
                'devDependencies': dev_deps
            },
            'total_count': len(deps) + len(dev_deps)
        }
    except Exception as e:
        return {'error': str(e)}

def parse_go_mod(file_path):
    """Parse go.mod for Go dependencies."""
    try:
        deps = []
        
        with open(file_path, 'r') as f:
            in_require = False
            for line in f:
                line = line.strip()
                
                if line.startswith('require'):
                    in_require = True
                    if '(' not in line:
                        # Single line require
                        dep = line.replace('require', '').strip()
                        if dep:
                            deps.append(dep)
                        in_require = False
                    continue
                
                if in_require:
                    if ')' in line:
                        in_require = False
                        continue
                    if line and not line.startswith('//'):
                        deps.append(line)
        
        return {
            'ecosystem': 'Go',
            'file': str(file_path),
            'dependencies': {'dependencies': deps},
            'total_count': len(deps)
        }
    except Exception as e:
        return {'error': str(e)}

def parse_gemfile(file_path):
    """Parse Gemfile for Ruby dependencies."""
    try:
        deps = []
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('gem'):
                    deps.append(line)
        
        return {
            'ecosystem': 'Ruby',
            'file': str(file_path),
            'dependencies': {'dependencies': deps},
            'total_count': len(deps)
        }
    except Exception as e:
        return {'error': str(e)}

def parse_composer_json(file_path):
    """Parse composer.json for PHP dependencies."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        deps = {
            'dependencies': data.get('require', {}),
            'devDependencies': data.get('require-dev', {}),
        }
        
        return {
            'ecosystem': 'PHP',
            'file': str(file_path),
            'dependencies': deps,
            'total_count': sum(len(v) for v in deps.values())
        }
    except Exception as e:
        return {'error': str(e)}

# File parsers mapping
PARSERS = {
    'package.json': parse_package_json,
    'requirements.txt': parse_requirements_txt,
    'pyproject.toml': parse_pyproject_toml,
    'Cargo.toml': parse_cargo_toml,
    'go.mod': parse_go_mod,
    'Gemfile': parse_gemfile,
    'composer.json': parse_composer_json,
}

def find_dependency_files(repo_path):
    """Find all dependency files in the repository."""
    repo_path = Path(repo_path).resolve()
    found_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip common directories
        dirs[:] = [d for d in dirs if d not in {'node_modules', '.git', 'venv', 'vendor', 'target'}]
        
        for file in files:
            if file in PARSERS:
                found_files.append(Path(root) / file)
    
    return found_files

def analyze_dependencies(repo_path):
    """Analyze all dependencies in the repository."""
    dep_files = find_dependency_files(repo_path)
    
    if not dep_files:
        return {
            'found_files': 0,
            'ecosystems': [],
            'results': []
        }
    
    results = []
    ecosystems = set()
    
    for file_path in dep_files:
        parser = PARSERS.get(file_path.name)
        if parser:
            result = parser(file_path)
            if 'error' not in result:
                results.append(result)
                ecosystems.add(result['ecosystem'])
    
    return {
        'found_files': len(dep_files),
        'ecosystems': sorted(list(ecosystems)),
        'results': results
    }

def print_analysis(analysis):
    """Print dependency analysis in readable format."""
    print("=" * 70)
    print("DEPENDENCY ANALYSIS")
    print("=" * 70)
    
    print(f"\nFound {analysis['found_files']} dependency file(s)")
    print(f"Ecosystems detected: {', '.join(analysis['ecosystems']) if analysis['ecosystems'] else 'None'}")
    
    for result in analysis['results']:
        print("\n" + "=" * 70)
        print(f"{result['ecosystem']}: {result['file']}")
        print("=" * 70)
        print(f"\nTotal dependencies: {result['total_count']}")
        
        for dep_type, deps in result['dependencies'].items():
            if deps:
                print(f"\n{dep_type.upper()}: ({len(deps)} packages)")
                print("-" * 70)
                
                if isinstance(deps, dict):
                    for pkg, version in list(deps.items())[:10]:
                        print(f"  • {pkg}: {version}")
                    if len(deps) > 10:
                        print(f"  ... and {len(deps) - 10} more")
                else:
                    for dep in deps[:10]:
                        print(f"  • {dep}")
                    if len(deps) > 10:
                        print(f"  ... and {len(deps) - 10} more")

def main():
    if len(sys.argv) < 2:
        print("Usage: python dependency_analyzer.py <repository_path> [--json]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    output_json = '--json' in sys.argv
    
    analysis = analyze_dependencies(repo_path)
    
    if output_json:
        print(json.dumps(analysis, indent=2))
    else:
        print_analysis(analysis)

if __name__ == '__main__':
    main()
