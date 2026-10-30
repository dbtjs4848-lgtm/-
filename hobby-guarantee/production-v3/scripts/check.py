from pathlib import Path
import json,hashlib,re,subprocess,zipfile
p=Path('/workspace/-/hobby-guarantee/production-v3');m=json.loads((p/'manifest.json').read_text());frames=json.loads((p/'preview-frames.json').read_text());cuts={r['cut']:r for r in m['cuts']}
for f in frames:
 for k in ['title','lyrics']:f[k]=cuts[f['cut']][k]
(p/'preview-frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
s=(p/'player.html').read_text();s=re.sub(r'const frames=.*?,cuts=', 'const frames='+json.dumps(frames,ensure_ascii=False)+',cuts=',s,count=1);(p/'player.html').write_text(s)
assert len(frames)==134 and frames[0]['start']==0 and abs(frames[-1]['end']-222.6)<.001
assert all(abs(a['end']-b['start'])<.00001 for a,b in zip(frames,frames[1:]))
assert hashlib.sha256((p/'audio.mp3').read_bytes()).hexdigest()==hashlib.sha256((p.parent/'audio.mp3').read_bytes()).hexdigest()
for z in p.glob('*.zip'):
 with zipfile.ZipFile(z) as f:assert f.testzip() is None
assert max(f.stat().st_size for f in p.rglob('*') if f.is_file())<100*1024*1024
v=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p/'full-song-preview.mp4')]))
vs=next(x for x in v['streams'] if x['codec_type']=='video');aud=next(x for x in v['streams'] if x['codec_type']=='audio')
assert vs['width']==1280 and vs['height']==720 and vs['r_frame_rate']=='24/1'
assert abs(float(v['format']['duration'])-222.6)<.15
subprocess.run(['ffmpeg','-v','error','-i',str(p/'full-song-preview.mp4'),'-f','null','-'],check=True)
report=f'''# v3 파일·재생 확인

- 예상 이미지 134개, 실제 파일 일치. PNG 디코딩·가로 비율·고유 해시 확인.
- 이전 v2 이미지와 134개 모두 다른 파일 해시. 전 컷 재생성.
- 71컷 / START 71장 / END 63장 / START 공용 8컷.
- 시작 0초–종료 222.600초, 이미지 구간 누락·중첩 없음.
- 미리보기 MP4: {vs['width']}×{vs['height']}, 24fps, {v['format']['duration']}초, 영상 {vs['codec_name']} / 음원 {aud['codec_name']}.
- MP4 전체 디코딩 정상. 원본 MP3와 복사본 해시 일치.
- 8개 구간 ZIP CRC 확인. 저장소 개별 파일 100MiB 미만.
- 제공 SRT 타임코드 기준. 비트 그리드를 별도로 계측한 결과는 아님.
- MP4는 시작·종료 이미지 + 2D 팬·줌으로 구성한 음원 미리보기.
'''
(p/'validation.md').write_text(report)
print(report)
