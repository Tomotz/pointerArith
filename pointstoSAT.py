from collections import namedtuple
Literal = namedtuple("Literal", "lhs rhs rhsType")



bottom = set()
top = 'top' # artifricial top value to avoid the need to know how many variables are used via FrontEnd
iota=set()

def join(a, b):
    if a == top or b == top:
        return top
    elif a == bottom:
        return b
    elif b == bottom:
        return a
    else: 
        out = set()
        for aclause in a:
            for bclause in b:
                out.add(aclause+bclause)
        return out

# def meet(a, b):
#     if a == top:
#         return b
#     elif b == top:
#         return a
#     else: return a & b

#checks if the variable appears as left hand size of one of the literals in the given clause
def isLhsInClause(variable, clause):
    return (True in [variable == c.lhs for c in clause])

#filter out of pt all the literals where lhs is on their left hand side
def removeLhs(lhs, pt):
    #itterate the or clauses in the pt, and remove each clause that has a literal with lhs as his left hand side
    return set(clause for clause in pt if (not isLhsInClause(lhs, clause)))

def set_addr(pt, lhs, rhs):
    # lhs = &rhs
    print "in set_addr", lhs, rhs
    pt = removeLhs(lhs, pt) 
    appended = set()
    appended.add((Literal(lhs, rhs, "reference"),))
    return pt | appended

#replaces all the lhs recurences of the variable 'old' with the variable 'new' in the given clause
def replaceLhsInClause(clause, old, new):
    outClause = set()
    for c in clause:
        if c.lhs == old:
            outClause.add(Literal(new, c.rhs, c.rhsType))
        else:
            outClause.add(c)
    return tuple(outClause)


def copy_var(pt, lhs, rhs):
    # lhs = rhs
    # print "in copy_var", lhs, rhs
    # print "pt: ", pt
    pt = removeLhs(lhs, pt)
    # print "pt: ", pt
    pt |= set(replaceLhsInClause(clause, rhs, lhs) for clause in pt if isLhsInClause(rhs, clause))
    # print "pt: ", pt
    return pt

def getAllVars(pt):
    outVars = set()
    for clause in pt:
        for c in clause:
            outVars.add(c.lhs)
            outVars.add(c.rhs)
    return outVars

def load(pt, lhs, rhs):
    # lhs = *rhs
    print "in load", lhs, rhs
    newPT = removeLhs(lhs, pt)
    toBeJoined = []
    for var in getAllVars(newPT):
        litTuple = {(Literal(lhs, var, "reference"),)}
        toBeJoined.append(newPT | litTuple)
    return reduce(join, toBeJoined)


#TODO:
def store(pt, lhs, rhs):
    # *lhs = rhs
    print "in store", lhs, rhs
    return pt | set((x, y) for (l, x) in pt for (r, y) in pt if (l, r)==(lhs, rhs))



# temp = *p
# *p = t
# *p=temp