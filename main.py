from src.fs.file_system_menu import FileSystemMenu
from src.fs.file_system import FileSystem

if __name__ == '__main__':
    fs = FileSystem("v9.dat")
    menu = FileSystemMenu(fs)
    menu.start()
