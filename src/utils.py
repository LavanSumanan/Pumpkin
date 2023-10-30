def geometric_mean(*args):
    mean = 1
    n = 0
    for arg in args:
        n += 1
        mean *= arg
    return mean**(1/n)