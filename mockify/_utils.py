def is_cardinality_object(obj):
    return hasattr(obj, "_actual")


def format_call_count(count):
    if count == 1:
        return "once"
    elif count == 2:
        return "twice"
    else:
        return "{} times".format(count)
