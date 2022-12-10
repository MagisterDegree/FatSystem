from src.fs.block import Block


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
