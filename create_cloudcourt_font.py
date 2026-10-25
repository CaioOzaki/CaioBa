"""Prepare the OFL Baloo 2 typeface used in the Figma design and game."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
A=R/'assets/cloudcourt-v16'
# Source: https://github.com/google/fonts/tree/main/ofl/baloo2
# Keep Baloo2-OFL.txt alongside any redistributed font.
f=TTFont(A/'Baloo2-Variable.ttf')
instantiateVariableFont(f,{'wght':800},inplace=True).save(A/'CloudcourtBubble.ttf')
print('Baloo 2 ExtraBold prepared for Cloudcourt VR')
