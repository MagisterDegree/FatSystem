import struct

from src.fs.block import Block
from src.fs.file_type import FileType
from src.fs.file_utils import FileUtils
from src.fs.table_fat import TableFAT
from src.fs.tree_files import TreeFiles
from src.fs.tree_node import TreeNode


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
