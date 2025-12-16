# setup.py
from setuptools import setup, find_packages

setup(
    # --- Basic Metadata ---
    name='myproject',
    version='1.0.0',
    description='A short description of what myproject does.',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/YourUsername/myproject_repo',
    
    # --- Package Configuration ---
    # Automatically finds all sub-packages in the current directory
    packages=find_packages(),
    
    # --- Dependencies ---
    # List packages your code needs to run
    install_requires=[
        'numpy>=1.20',
        'pandas',
        # Add your other dependencies here
    ],
    
    # --- Command-Line Executable ---
    # This section makes your script runnable directly from the command line
    # The format is: 'command_name = package.module:function'
    entry_points={
        'console_scripts': [
            'myproject_cli = myproject.main_script:main_function',
        ],
    },
    
    # Add classifiers, license, long_description, etc. here...
)