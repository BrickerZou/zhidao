def Z(t):
    e = ""
    i = 0
    while i < len(t):
        e += str(t[i])+";"
        i += 1
    e = e[0:-1]
    return e


def X(t):
    _a = "AgrcepndtslzyohCia0uS@"
    _b = "A0ilndhga@usreztoSCpyc"
    _c = "d0@yorAtlhzSCeunpcagis"
    _d = "zzpttjd"
    e = ""
    i = 0
    # a = _c[8] + _a[4] + _c[15] + _a[1] + _a[8] + _b[6]
    while i < len(t):
        n = ord(t[i]) ^ ord(_d[(i % len(_d))])
        i += 1
        e += Y(n)
    return e

def Y(t):
    e = hex(t)
    if len(e) < 2:
        e = '0' + e
    else:
        e = e
    return e[-2:]

def get_ev(params):
    # s = [recruitid, lessonid, smalllessonid, lastviewid, chapterid, studystatus, doneplaytimes, totaltimes, doneplaytsp]
    s = params
    # s = [82599, 1000072798, 1000066374, 230863, 1000055384, '0', 150, 230, '00:03:49']
    e = Z(s)
    e = X(e)
    return e