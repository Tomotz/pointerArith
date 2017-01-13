from sys import argv
from chaotic import chaotic
from pointstoSAT import join, bottom, top, set_addr, copy_var, load, store, iota
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


# chaotic(succ, 1, iota, join, bottom, tr, tr_txt)
varGroupRegex = "([a-zA-Z]+)"
possibleWhitespacesRegex = " *"
eqRegex = "(?:=|:=)"
refernceRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+re.escape("&")+varGroupRegex # x := &y
assignRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+varGroupRegex # x := y
derefRegex = varGroupRegex+possibleWhitespacesRegex+eqRegex+possibleWhitespacesRegex+re.escape("*")+varGroupRegex # x := *y

def main(fileName):
  succ = dict()
  tr = dict()
  tr_txt = dict()
  if_stack = []
  with open(fileName, "r") as codeFile:
    lineNum = 1
    for line in codeFile.read().split("\n"):
      stripped = line.strip()
      if stripped == "" or stripped.startswith("{") or stripped.startswith("#"):
        continue
      if stripped.startswith("if"):
        succ[lineNum]={lineNum + 1}
        tr[(lineNum, lineNum+1)] = lambda pt: pt
        tr_txt[(lineNum, lineNum+1)] = "assume x>0"
        if_stack.append(lineNum)
        lineNum += 1

      elif stripped.startswith("}"):
        if (if_stack == []):
          raise Exception("unbalanced brackets")
        else:
          prev = if_stack[-1]
          if_stack = if_stack[:-1]
          succ[prev].add(lineNum+1)
          tr[(prev, lineNum+1)] = lambda pt: pt
          tr_txt[(prev, lineNum+1)] = "assume x<=0"


      else:
        succ[lineNum]={lineNum + 1}
        refReg = re.search(refernceRegex, line)
        assReg = re.search(assignRegex, line)
        derefReg = re.search(derefRegex, line)
        if None != refReg:
          tr[(lineNum, lineNum+1)] = lambda pt,a=refReg.group(1),b=refReg.group(2) : set_addr(pt,a,b)
          tr_txt[(lineNum, lineNum+1)] = refReg.group(1) + " := &" + refReg.group(2)
        elif None != assReg:
          tr[(lineNum, lineNum+1)] = lambda pt,a=assReg.group(1),b=assReg.group(2) : copy_var(pt,a,b)
          tr_txt[(lineNum, lineNum+1)] = assReg.group(1) + " := " + assReg.group(2)
        elif None != derefReg:
          tr[(lineNum, lineNum+1)] = lambda pt,a=derefReg.group(1),b=derefReg.group(2) : load(pt,a,b)
          tr_txt[(lineNum, lineNum+1)] = derefReg.group(1) + " := *" + derefReg.group(2)
        else:
          raise Exception("unimplemented line type: " + str(line))
        lineNum += 1
    succ[lineNum] = {}
  print "succ: ", succ
  print "tr: ", tr
  print "tr_txt: ", tr_txt
  chaotic(succ, 1, iota, join, bottom, tr, tr_txt)


if __name__ == "__main__":
  if len(argv) != 2:
    print "usage: ", argv[0], " file_to_parse"
  else:
    main(argv[1])
