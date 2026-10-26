"""Audit/translate serialized visible UI strings only, entirely in memory.

No GameObject names, hierarchy, room keys, callbacks, asset names or metadata
are translated. Inactive menu pages are included because runtime can open them.
Native/runtime-generated text remains the native patch's responsibility.
"""
from pathlib import Path
import json,re,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from fix_gloves_v16 import hierarchy
from build_menu_v19 import set_raw

# Exact authored labels, including common prior Portuguese menu variants. These
# are applied only to verified UI.Text/TMP m_text fields, never arbitrary strings.
TRANSLATIONS={
 'PERSONALIZAÇÃO':'CUSTOMIZATION','Personalização':'Customization',
 'PERSONALIZACAO':'CUSTOMIZATION','Personalizacao':'Customization',
 'VOLTAR':'BACK','Voltar':'Back','voltar':'back',
 'RETOMAR':'RESUME','Retomar':'Resume','CONTINUAR':'RESUME','Continuar':'Resume',
 'SAIR':'LEAVE','Sair':'Leave','FECHAR':'CLOSE','Fechar':'Close',
 'CONFIGURAÇÕES':'SETTINGS','Configurações':'Settings','CONFIGURACOES':'SETTINGS','Configuracoes':'Settings',
 'PRONTO':'READY','Pronto':'Ready','CANCELAR':'CANCEL','Cancelar':'Cancel',
 'CRIAR SALA':'CREATE ROOM','Criar sala':'Create Room','ENTRAR NA SALA':'JOIN ROOM','Entrar na sala':'Join Room',
 'NA SALA':'IN ROOM','SOZINHO':'SOLO','Sozinho':'Solo','JOGAR':'PLAY','Jogar':'Play',
 'PRAIA':'BEACH','Praia':'Beach','PRAIA (NOITE)':'BEACH (NIGHT)','Praia (Noite)':'Beach (Night)',
 'PRAIA (DIA)':'BEACH (DAY)','Praia (Dia)':'Beach (Day)','GINÁSIO':'INDOOR','Ginásio':'Indoor',
 'GINASIO':'INDOOR','Ginasio':'Indoor','ARENA COBERTA':'INDOOR','Arena coberta':'Indoor',
 'TIME AZUL':'BLUE TEAM','Time azul':'Blue Team','TIME VERMELHO':'RED TEAM','Time vermelho':'Red Team',
 'TROCAR TIMES':'CHANGE TEAMS','Trocar times':'Change Teams',
 'ROSTO':'FACE','Rosto':'Face','ROUPA':'OUTFIT','Roupa':'Outfit','CONCLUÍDO':'DONE','Concluído':'Done',
 'ESCOLHA UM ROSTO. COMBINE UMA ROUPA.':'PICK A FACE. MIX AN OUTFIT.',
 'Escolha um rosto. Combine uma roupa.':'Pick a face. Mix an outfit.',
 'BONS RALIS. BOA COMPANHIA.':'BIG RALLIES. GOOD COMPANY.',
 'Bons ralis. Boa companhia.':'Big rallies. Good company.',
 'COMEÇANDO NOVO RALI':'STARTING NEW RALLY','Começando novo rali':'Starting new rally',
 'INICIANDO NOVO RALI':'STARTING NEW RALLY','Iniciando novo rali':'Starting new rally',
 'AGUARDANDO JOGADORES':'WAITING FOR PLAYERS','Aguardando jogadores':'Waiting for players',
 'PROCURANDO JOGADORES...':'SEARCHING FOR PLAYERS...','Procurando jogadores...':'Searching for players...',
 'ENTRANDO NA SALA...':'JOINING ROOM...','Entrando na sala...':'Joining room...',
 'CONECTANDO...':'CONNECTING...','Conectando...':'Connecting...',
}
PORTUGUESE_MARKERS=re.compile(r'\b(?:personaliza(?:ção|cao)|voltar|retomar|continuar|sair|fechar|configura(?:ções|coes)|pronto|cancelar|criar sala|entrar na sala|sozinho|jogar|praia|gin[aá]sio|time azul|time vermelho|trocar times|rosto|roupa|conclu[ií]do|aguardando jogadores|procurando jogadores|come[çc]ando|iniciando|conectando)\b',re.I)

def verify_metadata(metadata=None):
    metadata=metadata or UnityPy.load(str(R/'working/VolleyballFever_Data/globalgamemanagers.assets')).file
    layouts={};records=[]
    for i,o in metadata.objects.items():
        if o.type.name!='MonoScript':continue
        d=o.read_typetree();key=(d['m_ClassName'],d['m_Namespace'],d['m_AssemblyName'])
        if key==('Text','UnityEngine.UI','UnityEngine.UI.dll'):offset=128
        elif key in [('TextMeshProUGUI','TMPro','Unity.TextMeshPro.dll'),('TextMeshPro','TMPro','Unity.TextMeshPro.dll')]:offset=72
        else:continue
        layouts[i]=(key[0],offset);records.append(dict(script_id=i,classname=key[0],namespace=key[1],assembly=key[2],text_length_offset=offset,text_payload_offset=offset+4))
    assert layouts.get(572)==('Text',128) and layouts.get(1383)==('TextMeshProUGUI',72)
    return layouts,records

def text_field(raw,offset):
    assert len(raw)>=offset+4
    size=struct.unpack_from('<I',raw,offset)[0];end=offset+4+((size+3)//4)*4
    assert size<65536 and end<=len(raw),'Unexpected UI text schema'
    text=raw[offset+4:offset+4+size].decode('utf-8')
    assert not any(ord(c)<32 and c not in '\r\n\t' for c in text)
    return text,end

def replace_text(obj,offset,text):
    raw=obj.get_raw_data();old,end=text_field(raw,offset);b=text.encode('utf-8')
    value=raw[:offset]+struct.pack('<I',len(b))+b+b'\0'*((-len(b))%4)+raw[end:]
    set_raw(obj,value)
    # The entire component prefix and tail (font/color/material, raycast flags,
    # layout/options) stay byte-identical across the shifted string boundary.
    _,new_end=text_field(value,offset)
    assert value[:offset]==raw[:offset] and value[new_end:]==raw[end:]

def inventory_visible_text(files,layouts=None):
    layouts=layouts or verify_metadata()[0];rows=[]
    for name,f in files.items():
        gs,ts,paths=hierarchy(f);gpaths={ts[t]['m_GameObject']['m_PathID']:p for p,t in paths.items()}
        for i,o in f.objects.items():
            if o.type.name!='MonoBehaviour':continue
            raw=o.get_raw_data()
            if len(raw)<32:continue
            fileid,script=struct.unpack_from('<iq',raw,16)
            if script not in layouts or fileid<1 or fileid>len(f.externals):continue
            if not f.externals[fileid-1].path.endswith('globalgamemanagers.assets'):continue
            # All observed MonoBehaviour component names are empty; a nonempty
            # name would shift the known base layout and must be investigated.
            assert struct.unpack_from('<I',raw,28)[0]==0
            classname,offset=layouts[script];text,end=text_field(raw,offset);gid=struct.unpack_from('<q',raw,4)[0]
            rows.append(dict(file=name,id=i,script_id=script,classname=classname,path=gpaths.get(gid,str(gid)),
                text=text,text_length_offset=offset,enabled=bool(raw[12]),gameobject_active=gs.get(gid,{}).get('m_IsActive')))
    return rows

def apply_english_v21(files):
    layouts,metadata=verify_metadata(files.get('globalgamemanagers.assets'));before=inventory_visible_text(files,layouts);changes=[]
    for row in before:
        new=TRANSLATIONS.get(row['text'],row['text'])
        if new==row['text']:continue
        replace_text(files[row['file']].objects[row['id']],row['text_length_offset'],new)
        changes.append(dict(file=row['file'],id=row['id'],path=row['path'],before=row['text'],after=new))
    after=inventory_visible_text(files,layouts);residuals=[r for r in after if PORTUGUESE_MARKERS.search(r['text'])]
    assert not residuals,('Untranslated visible authored UI text',residuals)
    title=[r for r in after if r['path']=='Menu/Pages/Start/Cloudcourt CLOUDCOURT VR']
    tagline=[r for r in after if r['path']=='Menu/Pages/Start/Cloudcourt Big rallies. Good company.']
    return dict(changed_objects={n:sorted(c['id'] for c in changes if c['file']==n) for n in files},changes=changes,
      inventory=after,visible_text_count=len(after),script_metadata=metadata,portuguese_residuals=residuals,
      outline_targets=dict(title=title,tagline=tagline),hierarchy_network_keys_and_nontext_bytes_preserved=True,
      scope='Serialized UI.Text and TextMeshPro text, including inactive pages/prefabs. Native/runtime strings handled separately.')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=R/'working/VolleyballFever_Data');p.add_argument('--output',type=Path,default=R/'visuals-v21-english');a=p.parse_args()
    assert a.output.resolve()!=a.source_dir.resolve() and 'working' not in a.output.parts
    names=['level0','level1','level2','level3','level4','resources.assets']+[f'sharedassets{i}.assets' for i in range(5)]
    files={n:UnityPy.load(str(a.source_dir/n)).file for n in names};report=apply_english_v21(files);a.output.mkdir(exist_ok=True)
    for n,ids in report['changed_objects'].items():
        if ids:(a.output/n).write_bytes(files[n].save())
    (a.output/'english-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(dict(visible_text_count=report['visible_text_count'],changed_objects=report['changed_objects'],script_metadata=report['script_metadata'],outline_targets=report['outline_targets']),indent=2))
