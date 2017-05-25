from sys import argv
from chaotic import chaotic
from pointstoSAT import join, uninitialized_set, top, set_addr, copy_var, load, store, iota, store_value
import re

# succ = {1:{2}, 2:{3}, 3:{4}, 4:{5, 6}, 5: {7}, 6:{7}, 7: {8}, 8: {}} # CFG edges
# tr = {(1,2): lambda pt: set_addr(pt, 't', 'a'), \
#       (2,3): lambda pt: set_addr(pt, 'y', 'b'), \
#       (3,4): lambda pt: set_addr(pt, 'z', 'c'), \
#       (4, 5): lambda pt: pt,\
#       (4, 6): lambda pt: pt,\
#       (5, 7): lambda pt: set_addr(pt, 'p', 'y'), \
#       (6, 7): lambda pt: set_addr(pt, 'p', 'z'), \
#      (7, 8): lambda pt: store(pt, 'p', 't')} # transfer function
# tr_txt  = {(1,2): "t := &a", \
#            (2,3): "y := &b", \
#            (3,4): "z := &c", \
#            (4,5): "assume x >0", \
#            (4,6): "assume x <=0", \
#            (5, 7): "p := &y", \
#            (6, 7): "p := &z", \
#            (7, 8): "*p := t"}  # for debugging


# chaotic(succ, 1, iota, join, uninitialized_set, tr, tr_txt)
varGroupRegex = "([a-zA-Z]+)"
possibleWhitespacesRegex = " *"
eqRegex = "(?:=|:=)"
refernceRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+re.escape("&")+varGroupRegex # x := &y
assignRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+varGroupRegex # x := y
derefRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+re.escape("*")+varGroupRegex # x := *y
storeRegex = re.escape("*")+varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+re.escape("&")+varGroupRegex # *x := &y
storeValueRegex = re.escape("*")+varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+varGroupRegex # *x := y

def addOp(succ, tr, tr_txt, line, lineNum, nextLineNum):
  #if not "else" in next_line:
  succ[lineNum]={nextLineNum}
  refReg = re.match(refernceRegex, line)
  assReg = re.match(assignRegex, line)
  derefReg = re.match(derefRegex, line)
  storeReg = re.match(storeRegex, line)
  storeValueReg = re.match(storeValueRegex, line)
  if None != refReg:
    print 1
    tr[(lineNum, nextLineNum)] = lambda pt,a=refReg.group(1),b=refReg.group(2) : set_addr(pt,a,b)
    tr_txt[(lineNum, nextLineNum)] = refReg.group(1) + " := &" + refReg.group(2)
  elif None != assReg:
    print 2
    tr[(lineNum, nextLineNum)] = lambda pt,a=assReg.group(1),b=assReg.group(2) : copy_var(pt,a,b)
    tr_txt[(lineNum, nextLineNum)] = assReg.group(1) + " := " + assReg.group(2)
  elif None != derefReg:
    print 3
    tr[(lineNum, nextLineNum)] = lambda pt,a=derefReg.group(1),b=derefReg.group(2) : load(pt,a,b)
    tr_txt[(lineNum, nextLineNum)] = derefReg.group(1) + " := *" + derefReg.group(2)
  elif None != storeReg:
    tr[(lineNum, nextLineNum)] = lambda pt,a=storeReg.group(1),b=storeReg.group(2) : store(pt,a,b)
    tr_txt[(lineNum, nextLineNum)] = "*" + storeReg.group(1) + " := &" + storeReg.group(2)
  elif None != storeValueReg:
    tr[(lineNum, nextLineNum)] = lambda pt,a=storeValueReg.group(1),b=storeValueReg.group(2) : store_value(pt,a,b)
    tr_txt[(lineNum, nextLineNum)] = "*" + storeValueReg.group(1) + " := " + storeValueReg.group(2)
  else:
    raise Exception("unimplemented line type: " + str(line))

def main(fileName):
  succ = dict()
  tr = dict()
  tr_txt = dict()
  if_stack = []
  with open(fileName, "r") as codeFile:
    lineNum = 1
    lines = codeFile.read().split("\n")
    for input_line_num in range(len(lines)):
      line = lines[input_line_num]
      try:
        next_line = lines[input_line_num+1]
      except:
          next_line = ""

      stripped = line.strip()
      if stripped == "" or stripped.startswith("{") or stripped.startswith("#"):
        continue
      if stripped.startswith("if"):
        succ[lineNum]={lineNum + 1}
        tr[(lineNum, lineNum+1)] = lambda pt: pt
        tr_txt[(lineNum, lineNum+1)] = "cond True"
        if_stack.append(("if", lineNum, line))
        lineNum += 1

      elif stripped.startswith("}"):
        if (if_stack == []):
          raise Exception("unbalanced brackets")
        cond, prev, prev_line_text = if_stack[-1]
        if_stack = if_stack[:-1]
        if cond == "if":
          succ[prev].add(lineNum)
          tr[(prev, lineNum)] = lambda pt: pt
          tr_txt[(prev, lineNum)] = "cond False"
        else:
          print 
          addOp(succ, tr, tr_txt, prev_line_text, prev, lineNum)
        if "else" in stripped:
          if_stack.append(last_state)

      else:
        if "else" in next_line:
          last_state = "else", lineNum, line
        else:
          addOp(succ, tr, tr_txt, line, lineNum, lineNum+1)
        lineNum += 1
    succ[lineNum] = {}
  print "succ: ", succ
  print "tr: ", tr
  print "tr_txt: ", tr_txt
  chaotic(succ, 1, iota, join, uninitialized_set, tr, tr_txt)


if __name__ == "__main__":
  # main("test1.txt")
  print argv
  if len(argv) != 2:
    print "usage: ", argv[0], " file_to_parse"
  else:
    main(argv[1])
