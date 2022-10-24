import struct


class FileUtils:

    @staticmethod
    def get_content_from_byte_array(data: bytearray) -> str:
        """

        :rtype: object
        """
        result = data.decode('utf-8').strip().rstrip('\x00')
        print(data)
        return str(result)


class Block:
    def __init__(self, number: str, value: str, file: str = ""):
        self.number = number
        self.value = value
        self.file = file

    def __str__(self) -> str:
        return f"Block #{self.number} -> {self.value}, pertain={self.file}"


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
        in_file = open(path, "rb")  # opening for [r]eading as [b]inary
        self.bytes: bytearray = in_file.read()

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
        self.table = []
        for idx in range(self.idx_table_fat_start, self.idx_table_fat_end, 8):
            block_idx = struct.unpack('I', self.bytes[idx:idx + 4])[0]
            block_value = struct.unpack('I', self.bytes[idx + 4:idx + 8])[0]
            self.table.append(Block(block_idx, block_value))

    def __init_root_dir__(self):
        self.idx_root_dir_start = self.idx_table_fat_end
        self.idx_root_dir_end = self.idx_root_dir_start + (20 * self.size_root_dir)
        self.root_dir = []
        for idx in range(self.idx_root_dir_start, self.idx_root_dir_end, 20):
            first_block_number = struct.unpack('I', self.bytes[idx + 12: idx + 16])
            attr = "catalog" if struct.unpack('I', self.bytes[idx + 16: idx + 20]) == 1 else "file"
            name_extension = FileUtils.get_content_from_byte_array(self.bytes[idx: idx + 12]).split('.')
            name_extension.append("None")
            self.root_dir.append(Object(name_extension[0], name_extension[1], first_block_number, attr))

    def __init_data__(self):
        self.idx_data_start = self.idx_root_dir_end
        self.idx_data_end = self.idx_root_dir_start + (self.size_block * self.count_blocks)
        self.blocks = []
        for idx in range(self.count_blocks):
            begin = self.idx_data_start + (idx * self.size_block)
            end = begin + self.size_block
            self.blocks.append(self.bytes[begin:end])

    def print_table(self):
        print("Table FAT")
        for block in self.table:
            if block.value != 0 and block.file == "":
                print(block)

    def print_root_dir(self):
        for el in self.root_dir:
            print(el)

    def get_file(self, start_block: int, file: str = ""):
        print("-- start find file --")
        itr = start_block
        while True:
            block = self.table[itr]
            block.file = file
            if block.value == 0:
                break
            else:
                itr = block.value
                # Выходим т.к это значит что указан блок == конец файла
                if itr > self.size_table_element:
                    block.file = file + "end"
                    break

    def get_block(self, index: int):
        print(f"Get block with index={index}")
        block = self.blocks[index]
        print(FileUtils.get_content_from_byte_array(block))

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
    fs.print_table()
    fs.print_root_dir()
    fs.get_file(97, "source")
    fs.get_file(231, "w9")
    fs.get_file(451, "Akh9")
    fs.print_markup()
    fs.print_table()
    fs.get_block(97)

# 451 306 431 453 226 497 407 5 385 264 507 200 493 449 265 455 126 158 341
