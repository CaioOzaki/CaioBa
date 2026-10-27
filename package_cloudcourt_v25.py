"""Build and test the v25 patch package, never modifying Steam or working files."""
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
VERSION='Cloudcourt-v25-trigger-fix'
OUT=R/'distribution'/VERSION
PRIOR=R/'versions/cloudcourt-v24-antes-v25'
ARCHIVE=R/'distribution'/(VERSION+'.zip')
NAMES=['GameAssembly.dll']+['VolleyballFever_Data/'+n for n in [
    'resources.assets','level1','level2','level3','sharedassets1.assets','sharedassets3.assets',
    'sharedassets0.assets','level0','globalgamemanagers.assets','sharedassets2.assets',
    'sharedassets4.assets','resources.resource','sharedassets0.resource','sharedassets1.resource',
    'sharedassets2.resource','sharedassets4.resource']]
README="""CLOUDCOURT VR v25 - TRIGGER PRESSURE REPAIR

Close the game, extract the ENTIRE ZIP and run Instalar.cmd.
Accepts the compatible original Steam build 9216628 or Cloudcourt-v24-celebracao-graficos.
Launch through Steam. Each computer needs a separately owned compatible base game.
Online room namespaces remain Cloudcourt-2v2-v24 / Cloudcourt-4v4-v24.

TRIGGER spawning now accepts both digital input and analog trigger pressure,
including devices where digital GetTrigger stays false. The same pressure
reaches the original hand acquisition/release path, so the ball can actually
attach and be thrown. Press at 60%; release at 35% or less to avoid noisy flicker.
Both hands work independently. GRAB alone and A do not spawn or recall balls.
The native ordinary grip holding behavior and original throwing methods remain.
UI buttons suppress serve/lobby ball acquisition. One owned practice ball,
remote-hand exclusion and fresh-trigger lobby recall are retained.

No graphics, artwork, physics or network protocol changes from v24. Existing
presets, bot celebrations, sleeves and other approved features are retained.

Restaurar.cmd returns all 17 files to the compatible original. The installer
checks every input/output hash and preserves an automatic recovery backup.
Previous ZIPs are preserved. Only binary differences are included; no full
base-game executable or extracted base-game artwork is redistributed.

Native tests include independent analog/digital inputs through original
interface dispatch, Hand.Update, WantsToGrab and WantsToRelease. These checks
do not replace a physical Quest 3 or real two-PC playtest.
See included credits and CHECKPOINT-V25.md.
"""
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
    manifest={'version':VERSION,'steam_build':9216628,'previous_version':'Cloudcourt-v24-celebracao-graficos','files':[]}
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
    (OUT/'README.txt').write_text(README,encoding='utf-8-sig')
    return manifest


def test_package(manifest):
    # All mutations are restricted to this newly-created disposable fixture.
    fixture_root=R/'tools/v25-installer-test'
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
        (R/'analysis/v25-installer-progress.json').write_text(json.dumps(dict(checks=checks,fixture=str(fixture)),indent=2),encoding='utf-8')
        return prior
    run('install_original');check('modified_sha256')
    run('repeat_install');check('modified_sha256')
    run('restore_v25',restore=True);check('original_sha256')
    run('repeat_restore',restore=True);check('original_sha256')
    for name in NAMES:shutil.copyfile(PRIOR/Path(name).name,fixture/name)
    run('upgrade_v24');check('modified_sha256')
    run('restore_after_upgrade',restore=True);check('original_sha256')
    for name in NAMES:shutil.copyfile(PRIOR/Path(name).name,fixture/name)
    run('restore_directly_from_v24',restore=True);check('original_sha256')
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
    # Continue honoring the unmodified previous v23 package and its 17-file manifest.
    old_folder=R/'distribution/Cloudcourt-v24-celebracao-graficos'
    compat=fixture/'v24-package-with-current-installer';compat.mkdir()
    old=json.loads((old_folder/'patch.json').read_text(encoding='utf-8'))
    for source in old_folder.glob('*.bin'):shutil.copyfile(source,compat/source.name)
    shutil.copyfile(old_folder/'patch.json',compat/'patch.json')
    shutil.copyfile(OUT/'Aplicar-mod.ps1',compat/'Aplicar-mod.ps1')
    run('updated_installer_accepts_v24_manifest',folder=compat);check('modified_sha256',old['files'])
    run('updated_installer_restores_v24_manifest',restore=True,folder=compat);check('original_sha256',old['files'])
    # Explicitly check all shipped delta bytes after temporary corruption tests.
    for record in manifest['files']:
        for key in ('forward','reverse','upgrade','previous_reverse'):
            if key in record:assert file_hash(OUT/record[key]['name'])==record[key]['sha256']
    return dict(checks=checks,backups_verified=backups_verified,fixture=str(fixture),
                fixture_final_state='original',live_game_modified=False)


def add_docs_and_zip():
    """Package current v25 reference art and genuine dependency credits only."""
    for source,target in [
        ('CHECKPOINT-V25.md','CHECKPOINT-V25.md'),
        ('assets/cloudcourt-v16/Baloo2-OFL.txt','Baloo2-OFL.txt'),
        ('assets/audio-v18/CREDITS.md','BASE-AUDIO-CREDITS.md'),
        ('assets/audio-v18/impact/License.txt','Kenney-Impact-License.txt'),
        ('assets/audio-v18/interface/License.txt','Kenney-Interface-License.txt')]:
        shutil.copyfile(R/source,OUT/target)
    whistle=R/'assets/audio-v22/CREDITS.md'
    if whistle.exists():shutil.copyfile(whistle,OUT/'AUDIO-CREDITS.md')
    else:
        (OUT/'AUDIO-CREDITS.md').write_text(
            'Cloudcourt v22 serve whistle: original procedural tone authored in '
            'serve_feedback_v21.c. No sampled whistle recording is included. '
            'Retained sound dependencies: BASE-AUDIO-CREDITS.md and the Kenney licenses.\n',encoding='utf-8')
    (OUT/'ART-CREDITS.md').write_text(
        'Cloudcourt v25 environment, curved yellow/blue ball pattern without logos, '
        'bot artwork, historical authored hair restoration, hands and skin-tone previews are project artwork.\n'
        'The package contains binary differences requiring a compatible separately owned base game; '
        'no full base-game binaries or extracted base-game artwork are included.\n'
        'The retained Cloudcourt Bubble font is covered by Baloo2-OFL.txt.\n'
        'Previews are authored reference renders and diagrams, not headset captures.\n',encoding='utf-8')
    previews=[]
    with zipfile.ZipFile(ARCHIVE,'w',zipfile.ZIP_DEFLATED) as archive:
        config=json.loads((OUT/'patch.json').read_text())
        required={r[k]['name'] for r in config['files'] for k in ('forward','reverse','upgrade','previous_reverse') if k in r}
        # Explicit payload list excludes stale release previews and notes.
        docs=['Instalar.cmd','Restaurar.cmd','Aplicar-mod.ps1','patch.json','README.txt',
              'CHECKPOINT-V25.md','ART-CREDITS.md','AUDIO-CREDITS.md','BASE-AUDIO-CREDITS.md',
              'Kenney-Impact-License.txt','Kenney-Interface-License.txt','Baloo2-OFL.txt']
        for name in sorted(required|set(docs)):archive.write(OUT/name,VERSION+'/'+name)
        for source,target in previews:
            assert (R/source).exists(),('Missing v25 authored preview',source)
            archive.write(R/source,VERSION+'/'+target)
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        paths=set(archive.namelist())
        expected={VERSION+'/'+n for n in required|set(docs)}|{VERSION+'/'+target for _,target in previews}
        assert paths==expected,('Unexpected ZIP payload',paths^expected)
        for name in paths:
            assert not name.startswith(('/', '\\')) and '..' not in Path(name).parts
            assert not name.endswith(('.dll','.assets','.resource','.resS')),'Full base-game binaries must not be distributed.'


def main():
    previous_archive=R/'distribution/Cloudcourt-v24-celebracao-graficos.zip'
    previous_hash=file_hash(previous_archive)
    baseline={name:file_hash(R/'working'/name) for name in NAMES}
    manifest=create_package();test=test_package(manifest);add_docs_and_zip()
    assert baseline=={name:file_hash(R/'working'/name) for name in NAMES},'Working files changed during packaging; rebuild required.'
    assert previous_hash==file_hash(previous_archive),'Previous ZIP changed.'
    report=dict(version=VERSION,zip=str(ARCHIVE),bytes=ARCHIVE.stat().st_size,sha256=file_hash(ARCHIVE),
                files=len(NAMES),previous_zip_preserved=True,working_unchanged=True,zip_crc_valid=True,
                manifest=str(OUT/'patch.json'),**test)
    (R/'analysis/complete-package-v25-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


def refresh_docs_zip():
    """Refresh release notes after root review without repeating binary tests."""
    path=R/'analysis/complete-package-v25-validation.json'
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
