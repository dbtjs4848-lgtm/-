from pathlib import Path
import json,hashlib,runpy,html,re,shutil
p=Path('/workspace/-/hobby-guarantee');o=p/'production-v3'
runpy.run_path('/tmp/package_hobby_v3.py')
m=json.loads((o/'manifest.json').read_text());changed=[]
for im in m['images']:
 old=p/'production-v2/images'/im['file'];h=hashlib.sha256(old.read_bytes()).hexdigest();assert h!=im['sha256'];changed.append(dict(file=im['file'],previous_sha256=h,sha256=im['sha256'],operation='imagegen redraw'))
m.update(status='story_physics_style_images_complete',images_regenerated=True,reused_image_count=0,camera_revised_images=134,revision_log=changed)
(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(o/'revision-report.md').write_text('''# v3 수정 내용

전체 71컷의 시작 71장·종료 63장, 총 134장을 새로 그렸습니다. 종료 공용 8컷은 시작 파일만 사용합니다.

- 휴대폰: 보는 사람에게 화면이 향하도록 하고, 뒷면 렌즈와 화면이 한 면에 섞인 오류를 제거합니다. H015·H055·H060의 뒷면 화면 혼합을 수정했습니다.
- 낚시: 릴 없는 가는 민물 민장대 한 대와 V 받침을 사용합니다. 찌는 H035/H037 독립 인서트에서만 보입니다.
- 살림망: 긴 원통형 몸통이 물속에 잠기고 입구를 물가에 고정합니다. 물고기를 받는 손잡이 뜰채는 별도 도구입니다.
- H041–H049: 입질 → 휘어진 낚싯대를 둘이 잡고 버팀 → 붕어 수면 반응 → 뜰채로 받음 → 포획 확인 → 살림망으로 옮김 → 주먹 인사로 보상합니다.
- H062: 빈 어망 사진 대신 앞서 함께 잡은 붕어와 뜰채 사진을 보여주는 회수 장면으로 바꿨습니다.
- H054/H055: 외출 복장과 컵, 휴대폰 방향을 맞췄습니다. H051 여주는 외출용 신발을 유지합니다.
- 질감: 같은 얼굴 기준을 유지하며 선 두께, 매트한 피부, 단순한 옷 색면과 주름 기준으로 전체를 다시 생성했습니다.
- 카메라: 손·수면·물고기 인서트, 반응 클로즈업, 낮은 전신 투숏, 틸트, 짧은 아크와 풀백을 행동 흐름에 맞춰 배치했습니다.

## 사용 파일

이 폴더의 images만 사용합니다. 이전 production-v1/v2 파일을 섞지 않습니다. [전체 콘티와 시간·파일 대응표](storyboard.md) · [영상 제작 지시 TXT](motion-prompts.txt)

음원 미리보기는 수정 시작·종료 이미지와 2D 팬·줌을 합친 스토리보드 영상입니다. 인물이 움직이는 완성 뮤비는 아닙니다.
''')
prompts=['취미 활동은 보장해 줍쇼 · production-v3 영상 생성 지시','입력 이미지는 production-v3/images만 사용. 이전 버전 혼용 금지.','낚시: 민장대 한 대(릴 없음), 찌는 H035/H037만. 긴 살림망은 물속. 별도 뜰채로 붕어 한 마리 받기. 폰 FRONT 화면 / BACK 렌즈 분리.','']
for r in m['cuts']:
 prompts += [f"{r['cut']} | {r['time']} | {r['title']}",f"START: {r['start_file']}",f"END: {r['effective_end_file']}"+(' (START 공용)' if r['end_uses_start'] else ''),f"길이: {r['duration']:.3f}초",f"장면: {r['action']}",f"시작: {r['start_state']}",f"종료: {r['end_state']}",f"카메라: {r['camera']}. {r['production_motion']}",f"연결: {r['edit_transition']}",'확정 얼굴·복장·물리적 소품 배치·손가락을 유지. 불필요한 패널·인물·소품 복제 금지. H054/H055만 좌우 분할. 매트 피부·단순한 옷 질감·같은 선과 채색 기준.','']
(o/'motion-prompts.txt').write_text('\n'.join(prompts))
for name in ['watch.html']:
 s=(p/'production-v2'/name).read_text();s=s.replace('수정본','v3 수정본');s=re.sub(r'const cuts=\[.*?\],v=document', 'const cuts='+json.dumps([{k:r[k] for k in ['cut','start','end','title']} for r in m['cuts']],ensure_ascii=False)+',v=document',s,count=1);(o/name).write_text(s)
body=html.escape((o/'flova-cut-files.txt').read_text());(o/'mapping-print.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><style>@page{size:A4;margin:15mm}body{font:11px/1.6 "Noto Sans CJK KR",sans-serif}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><pre>'+body+'</pre></html>')
raw='https://github.com/dbtjs4848-lgtm/-/raw/refs/heads/main/hobby-guarantee/production-v3/'
read=['# 취미 활동은 보장해 줍쇼 · 수정본 v3','', '**71컷 · 시작 71장 + 종료 63장 = 새로 생성한 이미지 134장. 종료 공용 8컷은 시작 파일을 사용합니다.**','',f'## [▶ 음원에 맞춘 전체 영상 보기·다운로드]({raw}full-song-preview.mp4)','', '휴대폰 방향·낚시장비·입질과 공동 포획 장면·후반 사진 회수·전체 그림 질감을 반영했습니다. [수정 내용](revision-report.md)','',f'[자세한 콘티](storyboard.md) · [플로바용 TXT]({raw}flova-cut-files.txt) · [플로바용 PDF]({raw}flova-cut-files.pdf) · [영상 생성 지시 TXT]({raw}motion-prompts.txt)','', '## 이미지 보기·다운로드','']
for z in json.loads((o/'download-parts.json').read_text()):read.append(f'- [{z["first"]:02}–{z["last"]:02}컷 시작·종료 보기](cuts-H{z["first"]:03}-H{z["last"]:03}.md) · [PNG 묶음 ZIP]({raw}{z["file"]})')
read+=['','## 재생 안내','','위 MP4를 다운로드하면 전체 음원과 수정 이미지가 함께 재생됩니다. 1280×720 / 24fps / 약 3분43초. START·END 전환과 2D 팬·줌으로 흐름을 확인하는 미리보기이며, 인물 모션을 생성한 완성 뮤비는 아닙니다. 제공 SRT의 타임코드를 사용했습니다.','', '[컷 선택 재생기](watch.html) · [원본 이미지 자동 전환](player.html) · [나란히 보기](gallery.html) — HTML은 저장소 파일을 받은 뒤 로컬 웹 서버에서 사용합니다. GitHub에서는 위 MP4와 Markdown 이미지 페이지를 이용하세요.','', '[연속성 기준](continuity.md) · [검사 결과](validation.md)','']
(o/'README.md').write_text('\n'.join(read))
q=p/'README.md';text=q.read_text();q.write_text('# 최신 수정본 v3\n\n[음원에 맞춘 전체 재생 영상·수정 이미지·콘티·다운로드](production-v3/README.md) — 휴대폰 방향, 낚시 공동 포획, 수중 살림망과 그림 질감 반영.\n\n'+text)
shutil.copy2('/tmp/prepare_hobby_v3.py',o/'scripts/prepare.py')
shutil.copy2('/tmp/finish_hobby_v3.py',o/'scripts/package.py')
shutil.copy2('/tmp/package_hobby_v3.py',o/'scripts/package-base.py')
shutil.copy2('/tmp/render_hobby_v3.py',o/'scripts/render-preview.py')
print('v3 packaged with revision log')
