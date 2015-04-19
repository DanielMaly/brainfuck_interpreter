__author__ = 'Daniel Maly'


def string_from_array(arr):
    return ''.join(chr(i) for i in arr)


brainloller_color_map = {
    b'\xff\x00\x00': '>',
    b'\x80\x00\x00': '<',
    b'\x00\xff\x00': '+',
    b'\x00\x80\x00': '-',
    b'\x00\x00\xff': '.',
    b'\x00\x00\x80': ',',
    b'\xff\xff\x00': '[',
    b'\x80\x80\x00': ']',
    b'\x00\x80\x80': 'L',
    b'\x00\xff\xff': 'R',
    b'\x00\x00\x00': None
}

braincopter_command_map = {
    0: '>',
    1: '<',
    2: '+',
    3: '-',
    4: '.',
    5: ',',
    6: '[',
    7: ']',
    8: 'R',
    9: 'L',
    10: None
}


def paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c