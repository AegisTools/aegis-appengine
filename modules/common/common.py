def build_keys(key_builder, list):
    # Split a string apart into separate items
    if isinstance(list, basestring):
        list = list.split(' ')

    # Iterate over all non-empty keys and use the keybuilder to build them.
    return [key_builder(key) for key in filter(lambda a: a, list)]

