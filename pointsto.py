bottom = set()
top = 'top' # artifricial top value to avoid the need to know how many variables are used via FrontEnd
iota=set()

def join(a, b):
    if a == top:
        return top
    elif b == top:
        return top
    else: return a | b

def meet(a, b):
    if a == top:
        return b
    elif b == top:
        return a
    else: return a & b

def removeLhs(lhs, pt):
     return set(p for p in pt if p[0] != lhs)

def set_addr(pt, lhs, a):
    # lhs = &a
    return removeLhs(lhs, pt) | set([(lhs, a)])

def copy_var(pt, lhs, rhs):
    # lhs = rhs
    return removeLhs(lhs, pt) | set((lhs, y) for (x, y) in pt if x == rhs)

def load(pt, lhs, rhs):
    # lhs = *rhs
    return removeLhs(lhs, pt) | set((lhs, y) for (x, y) in pt if (rhs, x) in pt)


def store(pt, lhs, rhs):
    # *lhs = rhs
    return pt | set((x, y) for (l, x) in pt for (r, y) in pt if (l, r)==(lhs, rhs))
