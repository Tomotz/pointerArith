from collections import namedtuple

import collections
# always reference: Literal of the form lhs = &rhs

class Literal(namedtuple("Literal", "lhs rhs is_pos")):
        __slots__ = ()
        def __repr__(self):
            if not self.is_pos:
                return "%s != &%s" % (self.lhs, self.rhs)
            else:
                return "%s = &%s" % (self.lhs, self.rhs)

#this is a disjunction clause. Makes all clauses comotetive indifferent.
class Disj_Clause(tuple): 
        def __new__(cls, a, b = None):
            sorted1 = b==None and [a] or [a,b]
            sorted1.sort()
            s = super(Disj_Clause, cls).__new__(cls, sorted1)
            return s
        def __repr__(self):
            if len(self) == 1:
                return "(%s)" % (self[0],)
            else:
                return "(%s v %s)" % (self[0], self[1])



uninitialized_set = 'uninit'
top = 'top' # artifricial top value to avoid the need to know how many variables are used via FrontEnd
iota=set() #initialization on the clauses set



def create_axioms_and_literals(cur_vars):
    axioms = set()
    allLiterals = set()
    for var1 in cur_vars:
        for var2 in cur_vars:
            # create all possible literals - all references and negation fo references
            allLiterals.add(Literal(var1, var2, True))
            allLiterals.add(Literal(var1, var2, False))

            # create conjunctions axioms
            # literlas of the form: (var1=var2) -> ~(var1=var3)
            for var3 in cur_vars:
                if var2 == var3:
                    continue

                new_clause = (Literal(var1, var2, False), Literal(var1, var3, False))
                axioms.add(new_clause)

    return axioms, allLiterals


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

def flip(literal):
    return Literal(literal.lhs, literal.rhs, not literal.is_pos)

#removes axioms from an edge list
def filter_trivial_edges(edges, axioms):
    return set(filter(lambda edge: not ((flip(edge[0]), edge[1]) in axioms), edges) )


# input: set of sets: < <,> , <,> , ...>
# outer relation: conjunction, inner realtion: disjunction
# output: a list of edges of reachable nodes
def blow(s, all_vars):
    nodes = set()
    # edges = set()
    neighbours = {}
    blown_edges = set()

    axioms, allLiterals = create_axioms_and_literals(all_vars)

    new_s = set(axioms)
    #add edges from and to single literal clauses
    for disj_clause in s:
        new_s.add(disj_clause)
        if len(disj_clause) == 1:
            for lit in allLiterals:
                new_s.add((lit, disj_clause[0]))


    # create adjecent list
    for disj_clause in new_s:
        a = disj_clause[0]
        b = (len(disj_clause) == 1 and a) or disj_clause[1]
        nodes = nodes.union({a, flip(a), b, flip(b)})
        if not flip(a) in neighbours:
            neighbours[flip(a)] = set()       
        neighbours[flip(a)].add(b)
        if not flip(b) in neighbours:
            neighbours[flip(b)] = set()       
        neighbours[flip(b)].add(a)
    
    for node in nodes:
        if node not in neighbours:
            neighbours[node] = []

    # run BFS from each node
    for node in nodes:
        reachble_list = BFS(neighbours, node)
        for distant_neighbour in reachble_list:
            blown_edges.add((node, distant_neighbour))

    return filter_trivial_edges(blown_edges, axioms)

# output: a set of sets, with all the pairs (a,b) for which exist a path a->b in the 2SAT graph
def join(a, b):

    print(["*********", a,b])
    if uninitialized_set in [a,b]: return a == uninitialized_set and b or a

    # we want to get a list of all the varibles - and it's enough
    # to list only the ones inside a / b that we got. No need
    # to look at other vars that maybe used somewhere else.
    all_vars = getAllVars(a) | getAllVars(b)

    blown_edges_a = blow(a, all_vars)
    #print "hi", blown_edges_a, "\n\n"
    blown_edges_b = blow(b, all_vars)
    #print "ji", blown_edges_b, "\n\n"
    intersection = blown_edges_a.intersection(blown_edges_b)
    result = set()
    for edge in intersection:
        result.add(Disj_Clause(flip(edge[0]), edge[1]))
    return result



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
    appended.add((Literal(lhs, rhs, True),))
    return pt | appended

#replaces all the lhs recurences of the variable 'old' with the variable 'new' in the given clause
# def replaceLhsInClause(clause, old, new):
#     outClause = set()
#     for c in clause:
#         if c.lhs == old:
#             outClause.add(Literal(new, c.rhs, c.is_pos))
#         else:
#             outClause.add(c)
#     return tuple(outClause)


def copy_var(pt, lhs, rhs):
    raise "copy_var is not implemented"
#     # lhs = rhs
#     # print "in copy_var", lhs, rhs
#     pt = removeLhs(lhs, pt)
#     pt |= set(replaceLhsInClause(clause, rhs, lhs) for clause in pt if isLhsInClause(rhs, clause))
#     return pt

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
        litTuple = {Disj_Clause(Literal(lhs, var, True))}
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