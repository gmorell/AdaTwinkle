def rgb_grb_fix(read_rgb_func):
    def wrapper(*args):
        val = read_rgb_func()
        if args[0].grb:
            val = val[val[1],val[0],val[2]]

        return val
        return read_rgb_func