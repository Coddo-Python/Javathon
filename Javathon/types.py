from collections import Iterable


class u1(int):
    """A typehint class to represent an unsigned 8-bit integer"""

    def __init__(self
                 , value):
        super().__init__()
        self.javathon = u1


class u2(int):
    """A typehint class to represent an unsigned 16-bit integer"""

    def __init__(self, value):
        super().__init__()
        self.javathon = u2


class u4(int):
    """A typehint class to represent an unsigned 32-bit integer in big-edian byte order"""

    def __init__(self, value):
        super().__init__()
        self.javathon = u4


class table:
    """A typehint class to represent a table"""

    @staticmethod
    def flatten(lis):
        for item in lis:
            if isinstance(item, Iterable) and not isinstance(item, str):
                for x in table.flatten(item):
                    yield x
            else:
                yield item

    def __new__(cls, _table):
        value = list(table.flatten(_table))
        return value
