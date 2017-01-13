
from chaotic import chaotic
from cp_one import join, bottom, top, iota

succ = {1:{2}, 2:{2,3}, 3:{}} # CFG edges
tr = {(1,2): lambda x: 3, (2, 2): lambda x: x, (2, 3): lambda x: x} # transfer function
tr_txt  = {(1,2): "x := 3", (2, 2): "nop", (2, 3): "nop"}  # for debugging


chaotic(succ, 1, iota, join, bottom, tr, tr_txt)
