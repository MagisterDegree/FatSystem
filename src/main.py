import struct

from src.block import Block
from src.file_type import FileType
from src.file_utils import FileUtils
from src.tree_node import TreeNode


class TreeFiles:
    def __init__(self):
        self.name = "root"
        self.children = []

    def add_child(self, node: TreeNode):
        self.children.append(node)

    def add_child_for_node(self, base_node_idx_start_block: int, node: TreeNode):
        for child in self.children:
            if child.idx_start_block == base_node_idx_start_block:
                child.add_child(node)

    def print(self):
        print(f"/{self.name}")
        for child in self.children:
            child.print()


class TableFAT:
    def __init__(self, size: int):
        self.size = size
        self.table = []  # [Block(i, 0) for i in range(self.size)]

    def add(self, block: Block):
        self.table.append(block)

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
        self.__init_root_dir__()
        self.__init_data__()
        self.len_root_directory = self.size_root_dir * self.size_block

    def print_super_block(self):
        print(
            f"SuperBlock path={self.path}, size_block={self.size_block} bytes, size_table={self.size_table} bytes, size_table_el={self.size_table_element}, size_root_dir={self.size_root_dir}")

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

    def __init_root_dir__(self):
        self.idx_root_dir_start = self.idx_table_fat_end
        self.idx_root_dir_end = self.idx_root_dir_start + (20 * self.size_root_dir)
        self.root_dir = TreeFiles()
        for idx in range(self.idx_root_dir_start, self.idx_root_dir_end, 20):
            tree_node = self.__define_root_element__(self.bytes[idx:idx + 20])
            if tree_node.name != "":
                self.root_dir.add_child(tree_node)

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
    def get_block(self, index: int):
        block = self.blocks[index]
        print(FileUtils.get_content_from_byte_array(block))

    def get_file(self, start_block: int):
        chain = self.__get_chain_file__(start_block)
        for block_idx in chain:
            self.get_block(block_idx)

    def delete_file(self, start_block: int):
        for block_number in self.__get_chain_file__(start_block):
            self.table[block_number].value = 0

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
        attr = FileType.CATALOG if struct.unpack('I', data[16:20]) == 1 else FileType.FILE
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
        print(f"Markup superblock: {self.idx_super_block_start}-{self.idx_super_block_end}")
        print(f"Markup table fat: {self.idx_table_fat_start}-{self.idx_table_fat_end}")
        print(f"Markup root dir: {self.idx_root_dir_start}-{self.idx_root_dir_end}")
        print(f"Markup data: {self.idx_data_start}-{self.idx_data_end}")
        print(f"Size all image = {len(self.bytes)}")
        print(f"------------------------")

    def __str__(self) -> str:
        return f"""FileSystem(path={self.path}, size_block={self.size_block} bytes, size_table={self.size_table} bytes, size_table_el={self.size_table_element}, size_root_dir={self.size_root_dir}, len_root_directory={self.len_root_directory})"""


if __name__ == '__main__':
    print("Hello")
    fs = FileSystem("v9.dat")
    fs.print_super_block()
    fs.print_root_dir()
    fs.child_root_dir(97)
    fs.print_root_dir()
    # fs.get_file(231)
    # fs.save_file(231, "text.txt")
    # fs.get_file(272)
    fs.print_markup()

# 451 306 431 453 226 497 407 5 385 264 507 200 493 449 265 455 126 158 341

# Удаление файла это по сути зануление блока в корневом каталоге? да
# Дерево
# Сохранение файла - он может быть на несколько блоков? В памяти программы сохраняем или пишем в dat файл?
