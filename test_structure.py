#!/usr/bin/env python3
"""Test script to verify project structure is set up correctly."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Core imports
        from shadow_it_generator import __version__
        print(f"✓ Package version: {__version__}")
        
        from shadow_it_generator.core import LogGenerator, SessionGenerator, UserManager
        print("✓ Core modules imported")
        
        from shadow_it_generator.config import ConfigLoader, EnterpriseConfig, CloudService
        print("✓ Config modules imported")
        
        from shadow_it_generator.services import ServiceManager, ServiceCategory
        print("✓ Services modules imported")
        
        from shadow_it_generator.formatters import LogFormatter, LEEFFormatter, CEFFormatter
        print("✓ Formatter modules imported")
        
        from shadow_it_generator.utils import setup_logging, FileHandler, IPGenerator
        print("✓ Utils modules imported")
        
        from shadow_it_generator.generators import UserAgentGenerator, ResponseGenerator
        print("✓ Generator modules imported")
        
        from shadow_it_generator.main import cli
        print("✓ CLI imported")
        
        print("\nAll imports successful!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def check_structure():
    """Check that all expected directories and files exist."""
    print("\nChecking project structure...")
    
    expected_files = [
        'setup.py',
        'requirements.txt',
        'requirements-dev.txt',
        'main.py',
        'src/shadow_it_generator/__init__.py',
        'src/shadow_it_generator/main.py',
        'src/shadow_it_generator/core/__init__.py',
        'src/shadow_it_generator/config/__init__.py',
        'src/shadow_it_generator/services/__init__.py',
        'src/shadow_it_generator/formatters/__init__.py',
        'src/shadow_it_generator/utils/__init__.py',
        'src/shadow_it_generator/generators/__init__.py',
    ]
    
    project_root = Path(__file__).parent
    all_exist = True
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

if __name__ == '__main__':
    print("Shadow IT Log Generator - Structure Test\n")
    
    structure_ok = check_structure()
    imports_ok = test_imports()
    
    if structure_ok and imports_ok:
        print("\n✓ Project structure is set up correctly!")
        sys.exit(0)
    else:
        print("\n✗ There are issues with the project structure.")
        sys.exit(1)