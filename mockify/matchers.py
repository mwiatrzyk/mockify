class Any:

    def __repr__(self):
        return "_"

    def __eq__(self, other):
        return True


_ = Any()
