from pathlib import Path
import json,csv,zipfile,hashlib,shutil,html,re
from PIL import Image
p=Path('/workspace/-/hobby-guarantee');o=p/'production-v3';m=json.loads((o/'manifest.json').read_text());rows=m['cuts'];expected=[n for r in rows for n in [r['start_file'],r['end_file']] if n];actual={f.name for f in (o/'images').glob('*.png')};assert actual==set(expected),{'missing':sorted(set(expected)-actual),'unexpected':sorted(actual-set(expected))}
records=[]
for n in expected:
 f=o/'images'/n
 with Image.open(f) as im:im.verify()
 with Image.open(f) as im:w,h=im.size
 assert abs(w/h-16/9)<.04,(n,w,h)
 records.append(dict(file=n,width=w,height=h,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
assert len(set(r['sha256'] for r in records))==len(expected)
assert all(a['end']==b['start'] for a,b in zip(rows,rows[1:]))
for r in rows:r.update(image_status='generated',effective_end_file=r['end_file'] or r['start_file'])
m.update(status='images_complete',images=records,validation={'unique_images':len(records),'png_integrity':True,'timeline_continuous':True,'duration':222.6,'beat_grid_verified':False});(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
for n in ['audio.mp3','lyrics.srt']:shutil.copy2(p/n,o/n)
fields=['cut','time','start','end','duration','title','camera','action','comic_function','continuity','start_file','end_file','effective_end_file','end_uses_start','production_motion']
with (o/'cut-files.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)
lines=['# 취미 활동은 보장해 줍쇼 · 본편 이미지 대응표',f'71컷 / START 71장 + END {m["end_count"]}장 = {len(records)}장 / 공용 {m["shared_count"]}컷','시간은 사용자 SRT 기반이며 최종 음악 비트 대조는 편집 단계에서 수행합니다.','']
for r in rows:lines += [f'## {r["cut"]} · {r["title"]}',f'시간: {r["time"]} / {r["duration"]:.3f}초',f'START: {r["start_file"]}',f'END: {r["effective_end_file"]}'+(' (START 공용)' if r['end_uses_start'] else ''),f'카메라: {r["camera"]}',f'장면: {r["action"]}',f'웃음·감정: {r["comic_function"]}',f'연결: {r["continuity"]}',f'생성 START 상태: {r["start_state"]}',f'생성 END 상태: {r["end_state"]}',r['production_motion'],'']
(o/'storyboard.md').write_text('\n'.join(lines));(o/'flova-cut-files.txt').write_text('\n'.join(lines).replace('## ','').replace('# ',''))
parts=[]
for i,a in enumerate(range(1,72,10),1):
 b=min(a+9,71);name=f'images-part{i}-H{a:03}-H{b:03}.zip';names=[n for r in rows[a-1:b] for n in [r['start_file'],r['end_file']] if n]
 with zipfile.ZipFile(o/name,'w',zipfile.ZIP_DEFLATED) as z:
  for n in names:z.write(o/'images'/n,'images/'+n)
  z.write(o/'flova-cut-files.txt','flova-cut-files.txt');z.write(o/'continuity.md','continuity.md')
 with zipfile.ZipFile(o/name) as z:assert z.testzip() is None
 parts.append(dict(file=name,first=a,last=b,images=len(names),bytes=(o/name).stat().st_size))
 md=[f'# {a:02}–{b:02}컷 시작·종료 이미지','', '[전체 자료](README.md)','']
 for r in rows[a-1:b]:md += [f'## {r["cut"]} · {r["title"]}',r['time'],r['action'],'','| START | END |','| --- | --- |',f'| ![START](images/{r["start_file"]}) | '+(f'![END](images/{r["end_file"]})' if r['end_file'] else 'START 공용')+' |','']
 (o/f'cuts-H{a:03}-H{b:03}.md').write_text('\n'.join(md))
(o/'download-parts.json').write_text(json.dumps(parts,ensure_ascii=False,indent=2))
E=html.escape
cards=[]
for r in rows:
 ims=''.join(f'<figure><a href="images/{n}"><img loading="lazy" src="images/{n}" alt="{r["cut"]} {role}"></a><figcaption>{role} · {n}</figcaption></figure>' for role,n in [('START',r['start_file']),('END',r['end_file'])] if n)
 cards.append(f'<article id="{r["cut"]}"><h2>{r["cut"]} · {E(r["title"])}</h2><p>{r["time"]} · {E(r["camera"])}</p><div class="frames">{ims}</div>'+('<p>종료는 START 공용</p>' if not r['end_file'] else '')+f'<p>{E(r["action"])}</p><p>{E(r["comic_function"])}</p></article>')
(o/'gallery.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>취미활동 본편 71컷</title><style>body{background:#18252d;color:#f4ebdf;font:16px/1.65 system-ui;margin:20px}main{max-width:1440px;margin:auto}a{color:#ebcea0}.frames{display:flex;gap:14px}figure{margin:0;flex:1;min-width:0}img{width:100%;display:block}article{padding:20px 0;border-bottom:1px solid #667}figcaption{overflow-wrap:anywhere;font-size:12px}@media(max-width:700px){.frames{display:block}}</style><main><h1>취미 활동은 보장해 줍쇼 · 71컷</h1><p><a href="player.html">전체 음원 자동 재생</a> · <a href="README.md">다운로드</a></p>'+''.join(cards)+'</main></html>')
frames=[]
for r in rows:
 names=[r['start_file']]+([r['end_file']] if r['end_file'] else [])
 for i,n in enumerate(names):frames.append(dict(start=r['start']+r['duration']*i/len(names),end=r['start']+r['duration']*(i+1)/len(names),file=n,cut=r['cut'],title=r['title'],lyrics=r['lyrics'],role='START' if i==0 else 'END'))
# Reuse the previously checked one-screen player with fresh data, source title and video link.
s=Path('/workspace/-/biugo/final-v6/player.html').read_text();s=s.replace('비우고','취미 활동은 보장해 줍쇼').replace('biugo-v6-full-song-preview.mp4','full-song-preview.mp4').replace('전체 52컷 · 88장','전체 71컷 · '+str(len(records))+'장');s=re.sub(r'const frames=.*?,cuts=', 'const frames='+json.dumps(frames,ensure_ascii=False)+',cuts=',s,count=1);s=re.sub(r',cuts=\[.*?\],a=document', ',cuts='+json.dumps([{k:r[k] for k in ['cut','start','title']} for r in rows],ensure_ascii=False)+',a=document',s,count=1);(o/'player.html').write_text(s)
concat=['ffconcat version 1.0']
for f in frames:concat += ["file '"+str(o/'images'/f['file'])+"'",'duration '+str(f['end']-f['start'])]
concat.append("file '"+str(o/'images'/frames[-1]['file'])+"'");Path('/tmp/hobby-production.ffconcat').write_text('\n'.join(concat)+'\n')
read=['# 취미 활동은 보장해 줍쇼 · 카메라 반영 이미지 제작 v2','',f'**71컷 · START 71장 + END {m["end_count"]}장 = 총 {len(records)}장. 공용 {m["shared_count"]}컷은 START만 저장했습니다.**','', '사용자가 확정한 검은 단발 여주·기존 남주로 제작했습니다. 얼굴·복장·구도와 소품 수의 연결을 유지하며 게임·쇼핑·낚시 역할 역전을 구성했습니다.','', '[전체 음원 MP4 다운로드](https://github.com/dbtjs4848-lgtm/-/raw/refs/heads/main/hobby-guarantee/production-v3/full-song-preview.mp4)','', '[플로바 첨부용 TXT](https://github.com/dbtjs4848-lgtm/-/raw/refs/heads/main/hobby-guarantee/production-v3/flova-cut-files.txt) · [이미지 대응표·콘티](storyboard.md) · [연속성 기준](continuity.md)','', '## GitHub에서 이미지 보기 / 구간 ZIP','']
for z in parts:read.append(f'- [{z["first"]:02}–{z["last"]:02}컷 보기](cuts-H{z["first"]:03}-H{z["last"]:03}.md) · [ZIP 다운로드](https://github.com/dbtjs4848-lgtm/-/raw/refs/heads/main/hobby-guarantee/production-v3/{z["file"]})')
read += ['', '## 사용 안내','', '파일은 H001_START.png / H002_END.png 형식이며 images 폴더에 있습니다. 같은 START를 종료에도 쓰는 컷은 END 사본이 없습니다. 저장소를 다운로드한 뒤 player.html을 열면 전체 음원에 맞춰 START/END 이미지가 자동 전환됩니다. gallery.html은 나란히 비교용입니다. GitHub 자체는 HTML을 실행하지 않으므로 위 Markdown 이미지 페이지 또는 MP4를 이용하세요.','', 'MP4는 수정 START/END와 2D 팬·줌으로 구도·리듬을 확인하는 미리보기입니다. 실제 인물 모션·3D 카메라 이동을 생성한 완성 뮤비는 아닙니다. 타임코드는 제공 SRT 기준이고 최종 비트 그리드는 별도 검수 대상입니다. AI 컷 사이 천 주름·가구·미세한 얼굴 차이는 영상 연결 단계에서 맞춥니다.','']
(o/'README.md').write_text('\n'.join(read));(o/'validation.md').write_text(f'# 검사\n\n71컷·{len(records)}개 예상 파일과 실제 일치. PNG 디코딩·고유 해시·가로형 비율 확인. 0–222.600초 연속 타임라인. 구간별 ZIP 무결성 확인.\n')
print('Packaged',len(records),'images,',len(parts),'ZIP parts; player and concat ready')
