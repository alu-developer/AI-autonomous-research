import os,sys
sys.path.insert(0,os.path.dirname(__file__))
import build_materials as b
t=b.gen_para("lexical",0)
print("WORDS",b.wc(t),"anchor",b.wc(b.anchor)); print(b.auto_ok("lexical",t)); print(t[:300])
print(b.review_para(t))
