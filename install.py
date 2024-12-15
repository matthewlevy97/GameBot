import pip

_all_ = open("requirements.txt", "r").read().split("\n")

windows = []

linux = []

darwin = ["pyobjc"]

def install(packages):
    for package in packages:
        pip.main(['install', package])

if __name__ == '__main__':
    from sys import platform
    install(_all_) 
    if platform == 'windows':
        install(windows)
    if platform.startswith('linux'):
        install(linux)
    if platform == 'darwin': # MacOS
        install(darwin)