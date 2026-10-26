"""Build and test the v19 patch package, never modifying Steam or working files."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import struct
import subprocess
import uuid
import zipfile

R=Path(__file__).resolve().parent
VERSION='Cloudcourt-v20-1-middle-part'
OUT=R/'distribution'/VERSION
PRIOR=R/'versions/cloudcourt-v20-antes-middlepart'
ARCHIVE=R/'distribution'/(VERSION+'.zip')
NAMES=['GameAssembly.dll']+['VolleyballFever_Data/'+n for n in [
    'resources.assets','level1','level2','level3','sharedassets1.assets','sharedassets3.assets',
    'sharedassets0.assets','level0','globalgamemanagers.assets','sharedassets2.assets',
    'sharedassets4.assets','resources.resource','sharedassets0.resource','sharedassets1.resource',
    'sharedassets2.resource','sharedassets4.resource']]
H=lambda data:hashlib.sha256(data).hexdigest()


def file_hash(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def original_path(name):
    base=Path(name).name
    if base in ['sharedassets2.assets','sharedassets4.assets','resources.resource',
                'sharedassets0.resource','sharedassets1.resource','sharedassets2.resource','sharedassets4.resource']:
        return R/'versions/cloudcourt-v17-antes-v18'/base
    if base=='globalgamemanagers.assets':return R/'versions/cloudcourt-v16-antes-menu-fix'/base
    parent='backup' if base in ('GameAssembly.dll','resources.assets') else 'versions/v13-antes-personagens' if base in ('sharedassets0.assets','level0') else 'versions/v10-antes-mapas'
    return R/parent/base


def delta(src,dst):
    blocks=[(i,dst[i:i+4096]) for i in range(0,len(dst),4096) if src[i:i+4096]!=dst[i:i+4096]]
    result=bytearray(src[:len(dst)]);result.extend(bytes(max(0,len(dst)-len(result))))
    for offset,data in blocks:result[offset:offset+len(data)]=data
    assert result==dst
    return struct.pack('<qi',len(dst),len(blocks))+b''.join(struct.pack('<qi',i,len(data))+data for i,data in blocks)


def create_package():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={'version':VERSION,'steam_build':9216628,'previous_version':'Cloudcourt-v20-personagens-menu','files':[]}
    for i,name in enumerate(NAMES):
        src=original_path(name).read_bytes();dst=(R/'working'/name).read_bytes()
        record=dict(path=name,original_sha256=H(src),modified_sha256=H(dst))
        for direction,a,b in [('forward',src,dst),('reverse',dst,src)]:
            data=delta(a,b);filename=f'{i}-{direction}.bin';(OUT/filename).write_bytes(data)
            record[direction]=dict(name=filename,sha256=H(data))
        prior=(PRIOR/Path(name).name).read_bytes()
        if H(prior) not in (record['original_sha256'],record['modified_sha256']):
            record['previous_sha256']=H(prior)
            for key,direction,a,b in [('upgrade','forward',prior,dst),('previous_reverse','reverse',prior,src)]:
                data=delta(a,b);filename=f'{20+i}-{direction}.bin';(OUT/filename).write_bytes(data)
                record[key]=dict(name=filename,sha256=H(data))
        manifest['files'].append(record)
    (OUT/'patch.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (OUT/'Aplicar-mod.ps1').write_text((R/'Apply-Complete-Mod.ps1').read_text(encoding='utf-8'),encoding='utf-8-sig')
    for name,flag in [('Instalar.cmd',''),('Restaurar.cmd',' -Restore')]:
        (OUT/name).write_text('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Aplicar-mod.ps1"'+flag+'\r\npause\r\n',encoding='ascii')
    (OUT/'LEIA-ME.txt').write_text('''CLOUDCOURT VR v20.1 - MIDDLE PART RESTAURADO

Extraia TODO o ZIP e execute Instalar.cmd com o jogo fechado.
Aceita o original Steam build 9216628 ou Cloudcourt-v20-personagens-menu.
Abra pela Steam; cada computador continua precisando do jogo base.

O BOT1 asiatico volta ao cabelo middle part da versao anterior a v20.
A geometria foi conferida contra o backup v19. Rosto, roupa, texturas,
outros oito bots e todas as melhorias v20 permanecem iguais.
Esta e uma correcao visual: DLL/fisica/rede nao mudam e as salas continuam
Cloudcourt-2v2-v20 / Cloudcourt-4v4-v20.

Restaurar.cmd retorna os 17 arquivos ao original compativel.
Backups automaticos e validacao de hashes preservados. ZIPs anteriores mantidos.
Artes, previews, creditos e licencas incluidos.
''',encoding='utf-8-sig')
    return manifest


def test_package(manifest):
    # All mutations are restricted to this newly-created disposable fixture.
    fixture_root=R/'tools/v20-1-installer-test'
    fixture=fixture_root/uuid.uuid4().hex[:12]
    fixture.mkdir(parents=True,exist_ok=False)
    (fixture/'VolleyballFever.exe').write_bytes(b'fixture, not executable')
    for name in NAMES:
        target=fixture/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original_path(name),target)
    checks=[];backups_verified=0
    def snapshot():return {n:file_hash(fixture/n) for n in NAMES}
    def check(key,records=manifest['files']):
        for record in records:assert file_hash(fixture/record['path'])==record[key],record['path']
    def clean_fixture_stages():
        # Verify absolute targets before any recursive cleanup on Windows.
        fixed=fixture.resolve()
        assert R.resolve() in fixed.parents and fixture_root.resolve() in fixed.parents
        for directory in fixture.glob('Caioba-backup-*'):
            target=directory.resolve()
            assert target.parent==fixed and re.fullmatch(r'Caioba-backup-[0-9a-f]{32}',target.name)
            shutil.rmtree(target)
    def run(label,restore=False,expected=0,folder=OUT,verify_backup=True):
        nonlocal backups_verified
        prior=snapshot()
        result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(folder/'Aplicar-mod.ps1'),
                               '-GameDirectory',str(fixture)]+(['-Restore'] if restore else []),capture_output=True,text=True)
        assert result.returncode==expected,(label,result.stdout,result.stderr)
        if expected==0 and verify_backup:
            for stage in fixture.glob('Caioba-backup-*'):
                recovery=stage/'recovery.json'
                assert recovery.exists(),label
                jobs=json.loads(recovery.read_text(encoding='utf-8-sig'))
                if isinstance(jobs,dict):jobs=[jobs]
                for job in jobs:
                    assert file_hash(Path(job['backup']))==job['prior']==prior[job['relative']]
                    assert not Path(job['new']).exists(),label
                backups_verified+=1
        checks.append(dict(test=label,passed=True,exit_code=result.returncode,output=result.stdout.strip()))
        clean_fixture_stages()
        (R/'analysis/v20-1-installer-progress.json').write_text(json.dumps(dict(checks=checks,fixture=str(fixture)),indent=2),encoding='utf-8')
        return prior
    run('install_original');check('modified_sha256')
    run('repeat_install');check('modified_sha256')
    run('restore_v20_1',restore=True);check('original_sha256')
    run('repeat_restore',restore=True);check('original_sha256')
    for name in NAMES:shutil.copyfile(PRIOR/Path(name).name,fixture/name)
    run('upgrade_v20');check('modified_sha256')
    run('restore_after_upgrade',restore=True);check('original_sha256')
    for name in NAMES:shutil.copyfile(PRIOR/Path(name).name,fixture/name)
    run('restore_directly_from_v20',restore=True);check('original_sha256')
    bad=fixture/NAMES[-1];bad.write_bytes(bad.read_bytes()+b'incompatible')
    prior=snapshot();run('reject_unknown_file',expected=1);assert snapshot()==prior
    shutil.copyfile(original_path(NAMES[-1]),bad)
    patch=OUT/manifest['files'][-1]['forward']['name'];saved=patch.read_bytes()
    try:
        patch.write_bytes(saved+b'corrupted');run('reject_corrupt_delta',expected=1);check('original_sha256')
    finally:patch.write_bytes(saved)
    saved_manifest=(OUT/'patch.json').read_bytes()
    try:
        evil=json.loads(saved_manifest);evil['files'][0]['path']='../outside.dll'
        (OUT/'patch.json').write_text(json.dumps(evil),encoding='utf-8')
        run('reject_manifest_path_traversal',expected=1);check('original_sha256')
        missing=json.loads(saved_manifest);missing['files'].pop()
        (OUT/'patch.json').write_text(json.dumps(missing),encoding='utf-8')
        run('reject_missing_manifest_file',expected=1);check('original_sha256')
    finally:(OUT/'patch.json').write_bytes(saved_manifest)
    # The updated installer must continue to honor an unmodified v20 manifest.
    old_folder=R/'distribution/Cloudcourt-v20-personagens-menu'
    compat=fixture/'v20-package-with-current-installer';compat.mkdir()
    old=json.loads((old_folder/'patch.json').read_text(encoding='utf-8'))
    for source in old_folder.glob('*.bin'):shutil.copyfile(source,compat/source.name)
    shutil.copyfile(old_folder/'patch.json',compat/'patch.json')
    shutil.copyfile(OUT/'Aplicar-mod.ps1',compat/'Aplicar-mod.ps1')
    run('updated_installer_accepts_v20_manifest',folder=compat);check('modified_sha256',old['files'])
    run('updated_installer_restores_v20_manifest',restore=True,folder=compat);check('original_sha256',old['files'])
    # Explicitly check all shipped delta bytes after temporary corruption tests.
    for record in manifest['files']:
        for key in ('forward','reverse','upgrade','previous_reverse'):
            if key in record:assert file_hash(OUT/record[key]['name'])==record[key]['sha256']
    return dict(checks=checks,backups_verified=backups_verified,fixture=str(fixture),
                fixture_final_state='original',live_game_modified=False)


def add_docs_and_zip():
    for source,target in [
        ('CHECKPOINT-V20-1-MIDDLEPART.md','CHECKPOINT-V20-1-MIDDLEPART.md'),
        ('assets/cloudcourt-v16/Baloo2-OFL.txt','Baloo2-OFL.txt'),
        ('CLOUDCOURT-GAME-DESIGN.md','CLOUDCOURT-GAME-DESIGN.md'),
        ('assets/audio-v18/CREDITS.md','AUDIO-CREDITS.md'),
        ('assets/audio-v18/impact/License.txt','Kenney-Impact-License.txt'),
        ('assets/audio-v18/interface/License.txt','Kenney-Interface-License.txt'),
        ('assets/customization-v19/README.md','AVATAR-CREDITS.md')]:shutil.copyfile(R/source,OUT/target)
    with zipfile.ZipFile(ARCHIVE,'w',zipfile.ZIP_DEFLATED) as archive:
        # Only current manifest patch names are shipped; no stale deltas from a rebuild.
        config=json.loads((OUT/'patch.json').read_text())
        required={r[k]['name'] for r in config['files'] for k in ('forward','reverse','upgrade','previous_reverse') if k in r}
        for file in sorted(OUT.iterdir()):
            if file.suffix=='.bin' and file.name not in required:continue
            if file.is_file():archive.write(file,VERSION+'/'+file.name)
        for file in sorted((R/'assets/customization-v19').iterdir()):
            if file.suffix in ('.png','.json','.md'):archive.write(file,VERSION+'/Previa-texturas/'+file.name)
        for file in sorted((R/'assets/beach-v18').glob('*.png')):archive.write(file,VERSION+'/Previa-praia/'+file.name)
        for file in sorted((R/'assets/bots-v20').iterdir()):
            if file.suffix in ('.png','.json','.md'):archive.write(file,VERSION+'/Bots/'+file.name)
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        paths=set(archive.namelist())
        for name in ('Instalar.cmd','Restaurar.cmd','Aplicar-mod.ps1','patch.json','AVATAR-CREDITS.md',
                     'AUDIO-CREDITS.md','Kenney-Impact-License.txt','Kenney-Interface-License.txt','Baloo2-OFL.txt',
                     'Previa-texturas/preview-faces.png','Previa-texturas/preview-outfits.png','Previa-texturas/catalog.json'):
            assert VERSION+'/'+name in paths,name
        for name in paths:
            assert not name.startswith(('/', '\\')) and '..' not in Path(name).parts
            assert not name.endswith(('.dll','.assets','.resource','.resS')),'Full base-game binaries must not be distributed.'


def main():
    previous_archive=R/'distribution/Cloudcourt-v20-personagens-menu.zip'
    previous_hash=file_hash(previous_archive)
    baseline={name:file_hash(R/'working'/name) for name in NAMES}
    manifest=create_package();test=test_package(manifest);add_docs_and_zip()
    assert baseline=={name:file_hash(R/'working'/name) for name in NAMES},'Working files changed during packaging; rebuild required.'
    assert previous_hash==file_hash(previous_archive),'Previous ZIP changed.'
    report=dict(version=VERSION,zip=str(ARCHIVE),bytes=ARCHIVE.stat().st_size,sha256=file_hash(ARCHIVE),
                files=len(NAMES),previous_zip_preserved=True,working_unchanged=True,zip_crc_valid=True,
                manifest=str(OUT/'patch.json'),**test)
    (R/'analysis/complete-package-v20-1-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


def refresh_docs_zip():
    """Refresh release notes after root review without repeating binary tests."""
    path=R/'analysis/complete-package-v20-1-validation.json'
    report=json.loads(path.read_text(encoding='utf-8'))
    manifest=json.loads((OUT/'patch.json').read_text(encoding='utf-8'))
    for record in manifest['files']:
        assert file_hash(R/'working'/record['path'])==record['modified_sha256'],'Working binary changed; rebuild the package.'
        for key in ('forward','reverse','upgrade','previous_reverse'):
            if key in record:assert file_hash(OUT/record[key]['name'])==record[key]['sha256']
    add_docs_and_zip()
    report.update(bytes=ARCHIVE.stat().st_size,sha256=file_hash(ARCHIVE),zip_crc_valid=True,docs_refreshed=True)
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    if '--refresh-docs' in __import__('sys').argv:refresh_docs_zip()
    else:main()
