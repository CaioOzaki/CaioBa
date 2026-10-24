"""Reuse authored v15 geometry and add a continuous rear hair volume."""
import ast,math,copy,struct
import numpy as np
from pathlib import Path
def repaired_model():
 source=(Path(__file__).resolve().parent/'create_caioba_characters_v15.py').read_text(encoding='utf8')
 tree=ast.parse(source)
 keep=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['uv_palette','v3','aabb','Model','character']]
 ns={'np':np,'math':math,'copy':copy,'struct':struct}
 exec(compile(ast.Module(body=keep,type_ignores=[]),'<authored v15 geometry>','exec'),ns)
 m=ns['character'](3)
 # Back-facing shell covers the exposed occipital area; facial UVs stay intact.
 m.ellipsoid((0,2.47,-.34),(.43,.49,.19),12,4,segments=28,rings=20)
 return m
