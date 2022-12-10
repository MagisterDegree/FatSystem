class Block:
    def __init__(self, number: int, value: int):
        self.number = number
        self.value = value

    def __str__(self) -> str:
        return f"Block #{self.number} -> {self.value}"
