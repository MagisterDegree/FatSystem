from src.file_type import FileType


class TreeNode:
    def __init__(self, name: str, extension: str, idx_start_block: int, file_type: FileType):
        self.name = name
        self.extension = extension
        self.idx_start_block = idx_start_block
        self.file_type = file_type
        self.children = []

    def __str__(self, is_child: bool = False):
        l = 15 if is_child else 20
        if self.extension != 'None':
            title = (self.name + '.' + self.extension).ljust(l)
        else:
            title = self.name.ljust(l)
        return f"- {title} | {str(self.idx_start_block).ljust(4)} | {self.file_type}"

    def print(self):
        print(self)
        for child in self.children:
            print(f"     {child.__str__(True)}")

    def add_child(self, node):
        if node.name == "":
            raise ValueError("Имя не может быть пустым")
        self.children.append(node)
