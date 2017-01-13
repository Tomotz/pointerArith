bottom = "bottom"  # artifricial bottomalue to avoid the need to know the set of used expressions
top= set()
iota=set()

def join(a, b):
    if a == bottom:
        return b
    elif b == bottom:
        return a
    else: return a & b

def meet(a, b):
    if a == bottom:
        return bottom
    elif b == bottom:
        return bottom
    else: return a | b

def args(expr_tree):
     yield expr_tree[0]
     for subtree in expr_tree[1]:
             for children in args(subtree):
                     yield children

def notArg(lhs, ae):
    if ae == bottom: return bottom
    return set (a for a in ae if lhs not in args(a))

def assign(ae, lhs, e):
    return notArg(lhs, ae | set([e]))
