from collections import namedtuple
Literal = namedtuple("Literal", "lhs rhs rhsType")



bottom = set()
top = 'top' # artifricial top value to avoid the need to know how many variables are used via FrontEnd
iota=set()

Pos = 0
Neg = 1


import collections

# returs all nodes that are reachable from root
def BFS(graph, root): 
    visited, queue = set(), collections.deque([root])
    while queue: 
        vertex = queue.popleft()
        for neighbour in graph[vertex]: 
            if neighbour not in visited: 
                visited.add(neighbour) 
                queue.append(neighbour)
    return visited

# input: set of sets: < <,> , <,> , ...>
# outer relation: conjunction, inner realtion: disjunction
# output: a list of edges of reachable nodes
def blow(s):
    nodes = set()
    # edges = set()
    neighbours = {}
    blown_edegs = set()
    # create adjecent list
    for disj_clause in s:
        a = disj_clause[0]
        b = (len(disj_clause) == 1 and a) or disj_clause[1]
        nodes = nodes.union(set([(Neg, a), (Pos, a), (Neg, b), (Pos, b) ]))
        if not (Neg, a) in neighbours:
            neighbours[(Neg, a)] = set()       
        neighbours[(Neg, a)].add((Pos, b))
        if not (Neg, b) in neighbours:
            neighbours[(Neg, b)] = set()       
        neighbours[(Neg, b)].add((Pos, a))
    
    for node in nodes:
        if node not in neighbours:
            neighbours[node] = []

    # run BFS from each node
    for node in nodes:
        reachble_list = BFS(neighbours, node)
        for distant_neighbour in reachble_list:
            blown_edegs.add((node, distant_neighbour))

    return blown_edegs

# output: a set of sets, with all the pairs (a,b) for which exist a path a->b in the 2SAT graph
def join(a, b):
    print(["*********", a,b])
    blown_edges_a = blow(a)
    blown_edges_b = blow(b)
    intersection = blown_edges_a.intersection(blown_edges_b)
    result = set()
    for edge in intersection:
        if edge[0][0] == Neg and edge[1][0] == Pos:
            result.add(set([edge[0][1], edge[1][1]]))
    return result


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
    pt = removeLhs(lhs, pt)
    pt |= set(replaceLhsInClause(clause, rhs, lhs) for clause in pt if isLhsInClause(rhs, clause))
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