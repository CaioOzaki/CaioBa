import ctypes,pathlib,math,json
R=pathlib.Path(__file__).resolve().parent
class V(ctypes.Structure):
    _fields_=[('x',ctypes.c_float),('y',ctypes.c_float),('z',ctypes.c_float)]
    def tup(self):return (self.x,self.y,self.z)
lib=ctypes.CDLL(str(R/'tools/spin-native.dll'))
lib.compute_spin.argtypes=[V,V,V,V,ctypes.c_float,ctypes.c_float];lib.compute_spin.restype=V
lib.compute_magnus.argtypes=[V,V,ctypes.c_float,ctypes.c_float];lib.compute_magnus.restype=V
zero=V(0,0,0);r=V(0,-.105,0)
spin=lambda hand,omega=zero:lib.compute_spin(r,hand,zero,omega,.6,60)
assert max(map(abs,spin(V(0,4,0)).tup()))<1e-5,'Normal hit must not manufacture spin'
positive=spin(V(3,0,0));negative=spin(V(-3,0,0))
assert positive.z>0 and negative.z<0
assert abs(positive.z-3*.6/.105)<.0001
assert abs(positive.z+negative.z)<.0001
assert abs(spin(V(100,0,0)).z-60)<.0001
assert spin(V(0,0,0),V(0,0,10)).z<10,'Contact friction reduces slip'
a=lib.compute_magnus(V(0,0,20),V(10,0,0),.005,8)
b=lib.compute_magnus(V(0,0,-20),V(10,0,0),.005,8)
assert a.y>0 and b.y<0 and abs(a.x)+abs(a.z)<1e-6
assert max(map(abs,lib.compute_magnus(zero,V(10,0,0),.005,8).tup()))==0
assert max(map(abs,lib.compute_spin(zero,zero,zero,zero,.6,60).tup()))==0
c=lib.compute_magnus(V(0,0,60),V(100,0,0),.005,8)
assert abs(math.sqrt(sum(v*v for v in c.tup()))-8)<1e-5
report={'passed':10,'normal_hit_rad_s':spin(V(0,4,0)).tup(),'right_brush_rad_s':positive.tup(),'left_brush_rad_s':negative.tup(),'magnus_acceleration_m_s2':a.tup(),'scope':'Compiled C math only. No engine/headset integration test performed.'}
(R/'analysis/physics-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
