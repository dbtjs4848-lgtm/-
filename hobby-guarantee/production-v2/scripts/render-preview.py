from pathlib import Path
import json,subprocess,concurrent.futures,math
p=Path('/workspace/-/hobby-guarantee/production-v2');tmp=Path('/tmp/hobby-v2-render');tmp.mkdir(exist_ok=True)
m=json.loads((p/'manifest.json').read_text());cam={x['cut']:x for x in json.loads((p.parent/'camera-v2/manifest.json').read_text())['cuts']}
frames=[]
for r in m['cuts']:
 names=[r['start_file']]+([r['end_file']] if r['end_file'] else [])
 # Short reaction punch: land on END early and hold it for the expression.
 split=.18 if r['cut'] in ['H016','H038'] else .5
 times=[r['start'],r['start']+r['duration']*split,r['end']] if len(names)==2 else [r['start'],r['end']]
 for i,n in enumerate(names):frames.append(dict(start=times[i],end=times[i+1],file=n,cut=r['cut'],title=r['title'],lyrics=r['lyrics'],role='START' if i==0 else 'END'))
(p/'preview-frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
def render(task):
 idx,f=task;c=cam[f['cut']];n=round(f['end']*24)-round(f['start']*24);dest=tmp/f'{idx:03}.mp4';d=max(n-1,1);prog=f'min(on/{d},1)'
 moving='START 기준' in c['image_usage'];desc=c['camera'];z='1';x='iw/2-iw/zoom/2';y='ih/2-ih/zoom/2'
 if moving:
  if any(k in desc for k in ['풀백','후퇴']):z=f'1.04-0.04*{prog}'
  elif any(k in desc for k in ['횡이동','트럭','트래킹','슬라이드','아크','팬']):
   z='1.035';x=f'(iw-iw/zoom)*{prog}' if int(f['cut'][1:])%2 else f'(iw-iw/zoom)*(1-{prog})'
  elif '틸트' in desc or '상승' in desc:
   z='1.035';y=f'(ih-ih/zoom)*(1-{prog})' if '다운' not in desc else f'(ih-ih/zoom)*{prog}'
  else:z=f'1+0.035*{prog}'
  # Do not keep creeping forward after the short punch has landed.
  if f['cut'] in ['H016','H038'] and f['role']=='END':z='1';x='0';y='0'
 if f['cut']=='H055':z='1' if f['role']=='START' else '1.05'
 vf=f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,zoompan=z='{z}':x='{x}':y='{y}':d={n}:s=1280x720:fps=24,format=yuv420p"
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(p/'images'/f['file']),'-vf',vf,'-frames:v',str(n),'-an','-c:v','libx264','-preset','veryfast','-crf','24','-threads','2',str(dest)],check=True)
 return idx
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for done,i in enumerate(ex.map(render,enumerate(frames)),1):
  if done%20==0:print(f'Rendered {done}/{len(frames)} image segments',flush=True)
concat=tmp/'concat.txt';concat.write_text(''.join(f"file '{tmp/f'{i:03}.mp4'}'\n" for i in range(len(frames))))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(p/'audio.mp3'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','222.6','-movflags','+faststart',str(p/'full-song-preview.mp4')],check=True)
print('Full-song camera keyframe preview rendered',flush=True)
