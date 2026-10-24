"""Render a static TextMeshPro SDF atlas from the licensed font (not an image edit)."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
def make_font(font_path):
 font=ImageFont.truetype(str(font_path),44);ascent,descent=font.getmetrics()
 atlas=Image.new('L',(1024,1024));glyphs=[];chars=[];legacy=[]
 codes=list(range(32,256))+[8230]
 for n,cp in enumerate(codes):
  text=chr(cp);left,top,right,bottom=font.getbbox(text,anchor='ls');w=max(0,right-left);h=max(0,bottom-top)
  x=(n%16)*64+6;y=(n//16)*64+6
  tile=Image.new('L',(64,64));ImageDraw.Draw(tile).text((6-left,6-top),text,font=font,fill=255,anchor='ls')
  inside=np.array(tile)>=128;distance=np.zeros((64,64),dtype=np.float32)
  a=Image.fromarray(inside.astype('uint8')*255);b=Image.fromarray((~inside).astype('uint8')*255)
  for step in range(1,7):
   distance+=(np.array(b)<128).astype('float32')-(np.array(a)<128).astype('float32')
   a=a.filter(ImageFilter.MaxFilter(3));b=b.filter(ImageFilter.MaxFilter(3))
  sdf=np.clip(128+distance*127/6,0,255).astype('uint8');atlas.paste(Image.fromarray(sdf),((n%16)*64,(n//16)*64))
  metrics={'m_Width':float(w),'m_Height':float(h),'m_HorizontalBearingX':float(left),'m_HorizontalBearingY':float(-top),'m_HorizontalAdvance':font.getlength(text)}
  rect={'m_X':x,'m_Y':1024-y-h,'m_Width':w,'m_Height':h}
  glyphs.append({'m_Index':cp,'m_Metrics':metrics,'m_GlyphRect':rect,'m_Scale':1.,'m_AtlasIndex':0})
  chars.append({'m_ElementType':1,'m_Unicode':cp,'m_GlyphIndex':cp,'m_Scale':1.})
  legacy.append({'id':cp,'x':float(x),'y':float(y),'width':float(w),'height':float(h),'xOffset':float(left),'yOffset':float(-top),'xAdvance':font.getlength(text),'scale':1.})
 return atlas,glyphs,chars,legacy,ascent,descent
