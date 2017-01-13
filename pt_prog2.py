
from chaotic import chaotic
from pointsto import join, bottom, top, set_addr, copy_var, load, store, iota

succ = {1:{2}, 2:{3}, 3:{4}, 4:{5, 6}, 5: {7}, 6:{7}, 7: {8}, 8: {}} # CFG edges
tr = {(1,2): lambda pt: set_addr(pt, 't', 'a'), \
      (2,3): lambda pt: set_addr(pt, 'y', 'b'), \
      (3,4): lambda pt: set_addr(pt, 'z', 'c'), \
      (4, 5): lambda pt: pt,\
      (4, 6): lambda pt: pt,\
      (5, 7): lambda pt: set_addr(pt, 'p', 'y'), \
      (6, 7): lambda pt: set_addr(pt, 'p', 'z'), \
     (7, 8): lambda pt: store(pt, 'p', 't')} # transfer function
tr_txt  = {(1,2): "t := &a", \
           (2,3): "y := &b", \
           (3,4): "z := &c", \
           (4,5): "assume x >0", \
           (4,6): "assume x <=0", \
           (5, 7): "p := &y", \
           (6, 7): "p := &z", \
           (7, 8): "*p := t"}  # for debugging


chaotic(succ, 1, iota, join, bottom, tr, tr_txt)
