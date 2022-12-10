import struct

from src.block import Block
from src.file_type import FileType
from src.file_utils import FileUtils
from src.tree_node import TreeNode


class TreeFiles:
    def __init__(self):
        self.tree = TreeNode("root", "None", -1, FileType.CATALOG)

    def add_child(self, node: TreeNode):
        self.tree.add_child(node)

    def add_child_for_node(self, base_node_idx_start_block: int, node: TreeNode):
        for child in self.tree.children:
            if child.idx_start_block == base_node_idx_start_block:
                child.add_child(node)

    def delete_node(self, idx_start_block: int):
        # ТУТ РЕКУРСИВНО НАДО ЗАПИЛИТЬ
        self.__check_and_delete_node(self.tree, idx_start_block)

    def __check_and_delete_node(self, tree_node: TreeNode, idx_start_block: int):
        tree_node.children = [x for x in tree_node.children if x.idx_start_block != idx_start_block]
        for node in tree_node.children:
            self.__check_and_delete_node(node, idx_start_block)

    def print(self):
        self.tree.print()


class TableFAT:
    def __init__(self, size: int):
        self.size = size
        self.table = []  # [Block(i, 0) for i in range(self.size)]

    def add(self, block: Block):
        self.table.append(block)

    def clear(self, idx_block: int):
        self.table[idx_block].value = 0

    def print(self, show_empty: bool = False):
        print(" === Table FAT === ")
        for block in self.table:
            if not show_empty and block.value == 0:
                pass
            else:
                print(block)


class Object:
    # или директория или файл
    def __init__(self, name: str, extension: str, idx_block: int, type: str):
        self.name = name
        self.extension = extension
        self.idx_block = idx_block
        self.type = type

    def __str__(self) -> str:
        return f"Object(name={self.name}, extension={self.extension}, idx={self.idx_block}, type={self.type}"


class FileSystem:

    def __init__(self, path: str):
        self.__init_file__(path)
        self.__init_super_block__()
        self.__init_table_fat__()
        self.__init_root_dir_border__()  # Инициализация чтобы удобно определить init_data
        self.__init_data__()
        self.__init_root_dir__()
        self.len_root_directory = self.size_root_dir * self.size_block

    def print_super_block(self):
        print(
            f"""SuperBlock 
            path            =   {self.path}, 
            size_block      =   {self.size_block} bytes, 
            size_table      =   {self.size_table} bytes, 
            size_table_el   =   {self.size_table_element}, 
            size_root_dir   =   {self.size_root_dir}
            """
        )

    def __init_file__(self, path: str):
        self.path = path
        try:
            in_file = open(path, "rb")  # opening for [r]eading as [b]inary
            self.bytes: bytearray = in_file.read()
        except:
            print("Файл не был найден")
        else:
            # Ошибки не было
            pass
        finally:
            # Выполнить в любом случае
            pass

    def __init_super_block__(self):
        self.idx_super_block_start = 0
        self.size_block: int = struct.unpack('I', self.bytes[0:4])[0]
        self.size_table: int = struct.unpack('I', self.bytes[4:8])[0]
        self.size_root_dir: int = struct.unpack('I', self.bytes[8:12])[0]
        self.size_table_element: int = self.size_table // 4
        self.count_blocks = self.size_table_element // 2
        self.idx_super_block_end = 12

    def __init_table_fat__(self):
        self.idx_table_fat_start = self.idx_super_block_end
        self.idx_table_fat_end = self.idx_table_fat_start + self.size_table
        self.table = TableFAT(self.size_table)
        for idx in range(self.idx_table_fat_start, self.idx_table_fat_end, 8):
            block_idx = struct.unpack('I', self.bytes[idx:idx + 4])[0]
            block_value = struct.unpack('I', self.bytes[idx + 4:idx + 8])[0]
            self.table.add(Block(int(block_idx), int(block_value)))

    def __init_root_dir_border__(self):
        self.idx_root_dir_start = self.idx_table_fat_end
        self.idx_root_dir_end = self.idx_root_dir_start + (20 * self.size_root_dir)

    def __init_root_dir__(self):
        self.root_dir = TreeFiles()
        for idx in range(self.idx_root_dir_start, self.idx_root_dir_end, 20):
            tree_node = self.__define_root_element__(self.bytes[idx:idx + 20])
            if tree_node.name != "":
                self.root_dir.add_child(tree_node)
                if tree_node.file_type == FileType.CATALOG:
                    self.child_root_dir(tree_node.idx_start_block)

    def __init_data__(self):
        self.idx_data_start = self.idx_root_dir_end
        self.idx_data_end = self.idx_root_dir_start + (self.size_block * self.count_blocks)
        self.blocks = []
        for idx in range(self.count_blocks):
            begin = self.idx_data_start + (idx * self.size_block)
            end = begin + self.size_block
            self.blocks.append(self.bytes[begin:end])

    def print_table(self):
        self.table.print()

    def print_root_dir(self):
        self.root_dir.print()

    # === CRUD ===
    def __print_block__(self, index: int):
        block = self.blocks[index]
        print(FileUtils.get_content_from_byte_array(block))

    def print_file(self, start_block: int):
        chain = self.__get_chain_file__(start_block)
        for block_idx in chain:
            self.__print_block__(block_idx)

    def delete_file(self, start_block: int):
        # удаляем данные из TreeFiles
        self.root_dir.delete_node(start_block)
        # удаляем данные в таблице FAT
        for block_number in self.__get_chain_file__(start_block):
            self.table.clear(block_number)

    def save_file(self, start_block: int, path: str):
        chain = self.__get_chain_file__(start_block)
        with open(path, "wb") as binary_file:
            # Write bytes to file
            for block_index in chain:
                binary_file.write(self.blocks[block_index])

    def child_root_dir(self, block_number: int):
        block = self.blocks[block_number]
        tree_node = self.__define_root_element__(block[0:20])
        self.root_dir.add_child_for_node(block_number, tree_node)

    @classmethod
    def __define_root_element__(cls, data: bytearray):
        first_block_number = struct.unpack('I', data[12:16])[0]
        attr = FileType.CATALOG if struct.unpack('I', data[16:20])[0] == 1 else FileType.FILE
        name_extension = FileUtils.get_content_from_byte_array(data[:12]).split('.')
        name_extension.append('None')
        return TreeNode(name_extension[0], name_extension[1], first_block_number, attr)

    def __get_chain_file__(self, start_block: int) -> list[int]:
        result = []
        itr = start_block
        while True:
            if itr > self.size_table_element:
                break
            else:
                result.append(itr)
                block = self.table.table[itr]
                if block.value == 0:
                    break
                else:
                    itr = block.value
        return result

    def print_markup(self):
        print(f"------------------------")
        print(f"Markup superblock   : {self.idx_super_block_start}-{self.idx_super_block_end}")
        print(f"Markup table fat    : {self.idx_table_fat_start}-{self.idx_table_fat_end}")
        print(f"Markup root dir     : {self.idx_root_dir_start}-{self.idx_root_dir_end}")
        print(f"Markup data         : {self.idx_data_start}-{self.idx_data_end}")
        print(f"Size all image      = {len(self.bytes)}")
        print(f"------------------------")

    def __str__(self) -> str:
        return f"""FileSystem(path={self.path}, size_block={self.size_block} bytes, size_table={self.size_table} bytes, size_table_el={self.size_table_element}, size_root_dir={self.size_root_dir}, len_root_directory={self.len_root_directory})"""


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


if __name__ == '__main__':
    fs = FileSystem("v9.dat")
    menu = FileSystemMenu(fs)
    menu.start()

# 451 306 431 453 226 497 407 5 385 264 507 200 493 449 265 455 126 158 341

# Удаление файла это по сути зануление блока в корневом каталоге? да
# Дерево
# Сохранение файла - он может быть на несколько блоков? В памяти программы сохраняем или пишем в dat файл?
