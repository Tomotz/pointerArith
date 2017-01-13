bottom = "bottom"
top = "top"
iota = 0

def join(a, b):
    if a == bottom:
        return b
    elif b == bottom:
        return a
    elif a == b:
        return a
    else: return top

def meet(a, b):
    if a == top:
        return b
    elif b == top:
        return a
    elif a == b:
        return a
    else: return bottom
