
FILTER_NEGATIVES = True

def has_negation(tup):
    for t in tup:
        if not t.is_pos: return False
    return True

def remove_unwanted_literals_for_print(statments):
    return set(filter(lambda s : (not FILTER_NEGATIVES) or has_negation(s), statments))

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
                print "    Changing the dataflow value at {} from {} to {}".format(v, all_statement_sets[v], new)
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

    print "Dataflow results"
    for node in succ:
        print "    {}: {}".format(node, all_statement_sets[node])

    import os
    f = open("temp_chaotic.dt", "w")
    f.write("digraph cfg {\n")
    # write nodes and all_statement_sets values
    for node in succ:
        f.write("    {} [label=\"{}: {}\"]\n".format(
            node, node, remove_unwanted_literals_for_print(all_statement_sets[node])))

    for u in succ:
        for v in succ[u]:
            f.write("\t" + str(u) + "->" + str(v) + " [label=\"" + tr_txt[(u,v)]+"\"]\n")
    f.write("\t}\n")
    f.close()
    os.system("dot temp_chaotic.dt -Tpng > chaotic.png")
    os.system("chaotic.png") # to open the png file
