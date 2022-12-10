from src.fs.file_system import FileSystem


class FileSystemMenu:
    def __init__(self, file_system: FileSystem):
        self.fs = file_system

    def start(self):
        while True:
            print(
                f"""
                Menu:
                1) Show SuperBlock
                2) Show Root Directory
                3) Show TableFat
                4) Delete file in File System
                5) Show Tree
                6) Save file
                7) Show content txt file
                8) Exit
                """
            )
            input_menu_item = int(input())
            if input_menu_item == 1:
                self.fs.print_super_block()
                print()
            elif input_menu_item == 2:
                self.fs.print_root_dir()
                print()
            elif input_menu_item == 3:
                self.fs.print_table()
                print()
            elif input_menu_item == 4:
                print("Please, select item and input first idx block:")
                idx = int(input())
                self.fs.delete_file(idx)
                print("File success deleted!")
            elif input_menu_item == 5:
                self.fs.print_root_dir()
                print()
            elif input_menu_item == 6:
                print("Please, select item and input first idx block:")
                idx = int(input())
                print("Ok, and please input absolute path:")
                path = input()
                self.fs.save_file(idx, path)
                print("File success save!")
            elif input_menu_item == 7:
                print("Please, select item and input first idx block:")
                idx = int(input())
                self.fs.print_file(idx)
            elif input_menu_item == 8:
                exit()
            else:
                print("This menu item not exist")
            print("Select next menu item ...")
