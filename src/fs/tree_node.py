from src.fs.file_type import FileType


class TreeNode:
    def __init__(self, name: str, extension: str, idx_start_block: int, file_type: FileType):
        self.name = name
        self.extension = extension
        self.idx_start_block = idx_start_block
        self.file_type = file_type
        self.children = []

    def __str__(self, length = 20):
        if self.extension != 'None':
            title = (self.name + '.' + self.extension).ljust(length)
        else:
            title = self.name.ljust(length)
        return f"- {title} | {str(self.idx_start_block).ljust(4)} | {self.file_type}"

    def print(self, level = 0):
        print("    " * level + self.__str__(length=20 - 4 * level))
        for child in self.children:
            child.print(level + 1)

    def add_child(self, node):
        if node.name == "":
            raise ValueError("Имя не может быть пустым")
        self.children.append(node)
