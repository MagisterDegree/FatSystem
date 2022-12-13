from src.fs.file_type import FileType
from src.fs.tree_node import TreeNode


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

    def print_children(self):
        for child in self.tree.children:
            print(child)
