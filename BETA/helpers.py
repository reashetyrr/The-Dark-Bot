def memoize(func):
    mem = {}
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in mem:
            mem[key] = func(*args, **kwargs)
        return mem[key]
    return memoizer


@memoize
def calculate_levenstein_distance(name_one: str, name_two: str):
    if name_one == "":
        return len(name_two)
    if name_two == "":
        return len(name_one)
    if name_one[-1] == name_two[-1]:
        cost = 0
    else:
        cost = 1

    res = min([calculate_levenstein_distance(name_one[:-1], name_two) + 1,
               calculate_levenstein_distance(name_one, name_two[:-1]) + 1,
               calculate_levenstein_distance(name_one[:-1], name_two[:-1]) + cost])
    return res


if __name__ == '__main__':
    print(calculate_levenstein_distance('test', 'name'))