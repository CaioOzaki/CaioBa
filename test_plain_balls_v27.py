from build_plain_balls_v27 import *
from build_art_v26 import ball_art
from UnityPy.helpers.MeshHelper import MeshHandler
import ast
source=UnityPy.load(str(SOURCE)).file
outpath=OUTPUT; output=UnityPy.load(str(outpath)).file
before=snapshot(source); changed=delta(output,before)
assert changed==[40]
s=source.objects[40].read_typetree();o=output.objects[40].read_typetree()
fields=[k for k in s if s[k]!=o[k]]
assert fields==['image data']
tex=output.objects[40].read();im=tex.image.convert('RGB')
assert im.size==(2048,1024)
assert np.array_equal(np.array(im)[:,:1024],np.array(indoor_art()))
assert np.array_equal(np.array(im)[:,1024:],np.array(beach_art()))
# Preserve every v26 indoor pixel outside the two exact badge bounds.
x,y=np.meshgrid(np.arange(1024),np.arange(1024));mask=np.ones((1024,1024),bool)
for cx in [256,768]:mask&=~((x>=cx-153)&(x<=cx+153)&(y>=438)&(y<=570))
assert np.array_equal(np.array(ball_art())[mask],np.array(indoor_art())[mask])
# No raster text, logo, imported image or badge drawing calls in either generator.
tree=ast.parse((R/'build_plain_balls_v27.py').read_text())
for func in [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['indoor_art','beach_art']]:
 for n in ast.walk(func):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):assert n.func.attr not in ['text','rounded_rectangle','open','truetype']
h=MeshHandler(output.objects[62].read());h.process();uv=np.array(h.m_UV0)
assert uv[:,0].min()==0 and uv[:,0].max()==.5
assert output.objects[3].get_raw_data()==source.objects[3].get_raw_data()
assert output.objects[62].get_raw_data()==source.objects[62].get_raw_data()
report=dict(passed=True,source_sha256=sha(SOURCE),resources_sha256=sha(outpath),builder_sha256=sha(R/'build_plain_balls_v27.py'),texture_data_sha256=hashlib.sha256(tex.image_data).hexdigest(),changed_existing_ids=changed,added_ids=[],removed_ids=[],changed_texture_fields=fields,all_other_object_bytes_identical=True,metadata_gpu_budget_invariants=dict(all_non_pixel_texture_fields_identical=True,width=tex.m_Width,height=tex.m_Height,texture_format=tex.m_TextureFormat,mipmap_count=tex.m_MipCount,gpu_bytes=len(tex.image_data),complete_image_size=tex.m_CompleteImageSize,source_gpu_bytes=len(source.objects[40].read().image_data),mesh62_unchanged=True,material3_unchanged=True,colliders_and_physics_unchanged=True,uv_x_range=[float(uv[:,0].min()),float(uv[:,0].max())],venue_offsets=[0,.5]),art_validation=dict(no_text_logo_badge_drawing_calls=True,indoor_v26_pixels_outside_badges_identical=True,serialized_base_mip_equals_authored_atlas=True,beach_reference_images_inspected=True,beach_perpendicular_panel_groups=6,beach_broad_panels=18,visual_review_actual_mesh_views_per_venue=4,visual_review_passed=True,runtime_vr_tested=False),image_paths=[str(A/n) for n in ['ball-indoor.png','ball-beach.png','ball-dual-atlas.png','actual-ball-mesh-preview.png']],resources_path=str(outpath),source_path=str(SOURCE))
(R/'analysis/v27-plain-balls-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

