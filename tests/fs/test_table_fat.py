from src.fs.file_system import FileSystem


class TestTableFat:
    fs = FileSystem("v9.dat")

    def test_superblock(self):
        assert self.fs.path == 'v9.dat', 'Incorrect SuperBlock path'
        assert self.fs.size_block == 2048, 'Incorrect SuperBlock size_block'
        assert self.fs.size_table == 4096, 'Incorrect SuperBlock size_table'
        assert self.fs.size_root_dir == 16, 'Incorrect SuperBlock size_root_dir'

    def test_tablefat(self):
        assert len(self.fs.table.table) == 512, 'Incorrect Table Fat size'

    def test_filetree(self):
        assert self.fs.root_dir.tree.name == 'root', "Incorrect name root catalog"
        assert self.fs.root_dir.tree.children[0].name == 'source', "Incorrect name child root catalog"
        assert self.fs.root_dir.tree.children[0].children[0].name == 'misc', "Incorrect filename in catalog 'misc'"
        assert self.fs.root_dir.tree.children[1].name == 'w9', "Incorrect filename in catalog 'root'"
        assert self.fs.root_dir.tree.children[2].name == 'Akh9', "Incorrect filename in catalog 'root'"
