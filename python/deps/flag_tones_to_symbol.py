""" Flag to symbol definition """


def flag_tones_to_symbol(flag):
    """
    The flag_tones_to_symbol function takes a flag as input and
    returns the symbol that it represents.

    :param flag: Store the flag tones
    :return: The number of tones in the flag

    """
    return int(flag[1]) - int(flag[0])
