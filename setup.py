from setuptools import setup, find_packages
packages = find_packages()
print(f'{packages = }')
setup(
    name='splitfile',
    version='0.1.0',
        description='Small tool to split and join binary files',
packages=packages,
        install_requires=['rich'],
entry_points = {
        "console_scripts": ["joinpy=splitfile.join:main", "splitpy=splitfile.split:main"]
    }
        )