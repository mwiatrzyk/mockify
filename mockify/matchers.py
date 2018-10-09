class Any:

    def __str__(self):
        return "_"

    def __eq__(self, other):
        return True


_ = Any()
