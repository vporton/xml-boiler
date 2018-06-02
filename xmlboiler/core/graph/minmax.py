class Supremum(float):
    r"""
    We will use NetworkX with this number class instead of float.
    """
    def __add__(self, other):
        return Supremum(max(self, other))

    def __sub__(self, other):
        raise NotImplementedError

    def __neg__(self):
        return Supremum(-float(self))