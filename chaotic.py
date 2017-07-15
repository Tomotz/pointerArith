

FILTER_NEGATIVES = True

def has_negation(tup):
    for t in tup:
        if not t.is_pos: return False
    return True


def remove_weak_clauses(statements):
    trivials = []
    res = []
    for s in statements:
        # if p is a sure thing
        if len(s) == 1 or s[0] == s[1]:
            trivials.append(s[0])
    for s in statements:
        if len(s) == 2 and s[0] != s[1]:
            if s[0] in trivials or s[1] in trivials:
                continue
        res.append(s)

    return res

def remove_unwanted_literals_for_print(statements):
    statements = remove_weak_clauses(statements)
    return set(filter(lambda s : (not FILTER_NEGATIVES) or has_negation(s), statements))

def divide_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
    
def chaotic(succ, first_line_number, statement_set, join, uninitialized_set, transition_functions, tr_txt):
    """
    succ is the successor nodes in the CFG
    first_line_number in nodes is the start vertex
    statement_set is the initial value at the start
    uninitialized_set is the minimum value
    transition_functions is the transfer function
    tr_txt is the edge annotations
    """
    lines_to_handle = [first_line_number]
    all_statement_sets = dict([(x, uninitialized_set) for x in succ])
    all_statement_sets[first_line_number] = statement_set
    while lines_to_handle != []:
        print "worklist is {}\n".format(lines_to_handle)
        u = lines_to_handle.pop()
        print "Handling:", u
        for v in succ[u]:
            new = join(transition_functions[(u,v)](all_statement_sets[u]), all_statement_sets[v])
            if (new != all_statement_sets[v]):
                all_statement_sets[v] = new
                lines_to_handle.append(v)
                print "    Adding {} to the worklist".format(v)
                lines_to_handle.sort(key=lambda x:-x) # sort in backward key order
            else:
                print "    New dataflow value at {} equal to the old value".format(v)
            print
        print
    print "Worklist empty"
    print

    import os
    f = open("temp_chaotic.dt", "w")
    f.write("digraph cfg {\n")
    last_form = ""
    # write nodes and all_statement_sets values
    for node in succ:
        filtered = remove_unwanted_literals_for_print(all_statement_sets[node])
        last_form = filtered
        f.write("    {} [label=\"{}: {}\"]\n".format(
            node, node, "\n".join(
                                    map(str, divide_list(list(filtered),5))
                                 )
                                                     )
                )

    for u in succ:
        for v in succ[u]:
            f.write("\t" + str(u) + "->" + str(v) + " [label=\"" + tr_txt[(u,v)]+"\"]\n")
    f.write("\t}\n")
    f.close()
    open("text_result.txt","w").write(str(last_form))
    os.system("dot temp_chaotic.dt -Tpng > chaotic.png")
    os.system("start chaotic.png") # to open the png file
