import sys
from chaotic import chaotic
from pointstoSAT import join, bottom, top, set_addr, copy_var, load, store, iota
import re

varGroupRegex = "([a-zA-Z]+)"
possibleWhitespacesRegex = " *"
eqRegex = "(?:=|:=)"
refernceRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+re.escape("&")+varGroupRegex # x := &y
assignRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+varGroupRegex # x := y
derefRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+re.escape("*")+varGroupRegex # x := *y

def parseOp(line):
  refReg = re.search(refernceRegex, line)
  assReg = re.search(assignRegex, line)
  derefReg = re.search(derefRegex, line)
  if None != refReg:
    transition = lambda pt,a=refReg.group(1),b=refReg.group(2) : set_addr(pt,a,b)
    description = refReg.group(1) + " := &" + refReg.group(2)
  elif None != assReg:
    transition = lambda pt,a=assReg.group(1),b=assReg.group(2) : copy_var(pt,a,b)
    description = assReg.group(1) + " := " + assReg.group(2)
  elif None != derefReg:
    transition = lambda pt,a=derefReg.group(1),b=derefReg.group(2) : load(pt,a,b)
    description = derefReg.group(1) + " := *" + derefReg.group(2)
  else:
    raise Exception("unimplemented line type: " + str(line))
    
  return transition, description

g_id = 0
def get_id():
    global g_id
    g_id += 1
    return g_id

class TransitionEdge:
    # transition - function from state to new state, or None for nop
    # original_line - string, original_line line
    # line_description - string, description of the transition function
    def __init__(self, to_node, transition, original_line_text="", line_description=""):
        self.to_node = to_node
        self.transition_func = transition
        self.original_line_text = original_line_text
        self.line_description = line_description

class TreeNode:
    def __init__(self, id):
        self.id = id
        self.transitions = []
    def add_transition(self, to_node, transition_func, line_text="", description=""):
        transition_edge = TransitionEdge(to_node, transition_func, line_text, description)
        self.transitions.append(transition_edge)
    def get_transitions(self):
        return self.transitions
        
# assumes non cyclic graph
# head - head of the graph of type TreeNode
def convert_graph_to_transition_table(head, successors={} , transition_functions = {}, transition_texts = {}):
    child_nodes = []
    start = head.id
    if not head.id in successors:
        successors[head.id] = set()
    for transition_edge in head.get_transitions():
        child_nodes.append(transition_edge.to_node)
        successors[head.id].add(transition_edge.to_node.id)
        tr_key = head.id, transition_edge.to_node.id
        transition_functions[tr_key] = transition_edge.transition_func
        transition_texts[tr_key] = transition_edge.line_description
    for child in child_nodes:
        convert_graph_to_transition_table(child, successors, transition_functions, transition_texts)
    return start, successors, transition_functions, transition_texts
    

def verify_code(code_lines):
    pass

def strip_one_tab(code_lines):
    return [line[1:] for line in code_lines if not line.startswith("#")]

# returns the head of the graph, and it's end
# we currently force that there is one most bottom node
def build_graph_for_code(code_lines):
    # add an empty line at the end - so we will never be out of bound
    code_lines = code_lines + [""]
    head = TreeNode(get_id())
    cur_node = head
    line_num = 0
    while line_num < len(code_lines):
        line = code_lines[line_num]
        if line.startswith("if "):
            condition = line[3:].strip()
            # Handle 'if' block
            if_block_start = line_num + 1
            if_block_end = line_num + 2
            while code_lines[if_block_end].startswith("\t") or code_lines[if_block_end].startswith(" "):
                if_block_end += 1
            if_block = code_lines[if_block_start:if_block_end]
            if_block = strip_one_tab(if_block)
            if_block_node, if_block_end_node = build_graph_for_code(if_block)
            cur_node.add_transition(if_block_node, None, description = "assert "+condition) # empty transition
            
            end = TreeNode(get_id())
            
            if_block_end_node.add_transition(end, None)
            line_num = if_block_end - 1 # line_num is advanced later
            
            # Handle 'else' block - if exists
            if code_lines[if_block_end].startswith("else"):
                else_block_start = if_block_end + 1
                else_block_end = if_block_end + 2
                
                while code_lines[else_block_end].startswith("\t") or code_lines[else_block_end].startswith(" "):
                    else_block_end += 1
                    
                else_block = code_lines[else_block_start:else_block_end]
                else_block = strip_one_tab(else_block)
                else_block_node, else_block_end_node = build_graph_for_code(else_block)
                cur_node.add_transition(else_block_node, None, description = "assert ! "+condition) # empty transition
                
                else_block_end_node.add_transition(end, None)
                
                # skip to next line
                line_num = else_block_end - 1
            else:
                cur_node.add_transition(end, None) # empty transition
                
            cur_node = end
        
        # regular line, no condition
        else:
            if line.strip() != "" and not line.startswith("#"):
                new_node = TreeNode(get_id())
                
                transition, description = parseOp(line)
                cur_node.add_transition(new_node, transition, line, description)
                cur_node = new_node
        
        
        line_num += 1
        
    return head, cur_node
        
def main():
    if len(sys.argv) < 2:
        print "usage: ", sys.argv[0], " file_to_parse"
        return
    code_file = sys.argv[1]
    
    # read code lines
    code_lines = open(code_file, "r").readlines()
    # parse the code : make a flow tree from it
    code_graph, _ = build_graph_for_code(code_lines)
    # convert the tree to the format needed by 'caotic'
    start, successors, transition_functions, transition_texts = convert_graph_to_transition_table(code_graph)
    
    # run caotic to see results
    chaotic(successors, start, iota, join, bottom, transition_functions, transition_texts)
    
if __name__ == "__main__":
    main()
