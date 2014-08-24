class Undefined():
    pass


undefined = Undefined()


def is_undefined(obj):
    return isinstance(obj, Undefined)


def is_defined(obj):
    return not is_undefined(obj)

