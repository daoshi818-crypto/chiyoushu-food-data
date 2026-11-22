"""Publish only checksum-verified APKs to the public distribution repository."""
import hashlib,json,os,pathlib,re,urllib.request,urllib.error,urllib.parse

MAX_APK_BYTES=160*1024*1024
REPO='daoshi818-crypto/chiyoushu-food-data'
TOKEN=os.environ['GH_TOKEN']

def api(path, method='GET', data=None):
    req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/'+path,
        data=json.dumps(data).encode() if data is not None else None,method=method,
        headers={'Authorization':'Bearer '+TOKEN,'Accept':'application/vnd.github+json','Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=60) as response:
        return json.load(response) if response.status!=204 else {}

def upload(release, file):
    for asset in api('releases/'+str(release['id'])+'/assets'):
        if asset['name']==file.name:api('releases/assets/'+str(asset['id']),'DELETE')
    url=release['upload_url'].split('{')[0]+'?name='+urllib.parse.quote(file.name)
    req=urllib.request.Request(url,data=file.read_bytes(),method='POST',headers={
        'Authorization':'Bearer '+TOKEN,'Content-Type':'application/octet-stream'})
    with urllib.request.urlopen(req,timeout=120) as response:json.load(response)

def main():
    payload=json.loads(pathlib.Path('publication/request.json').read_text())
    m=payload['update']; n=payload['runNumber']; u=urllib.parse.urlparse(payload['apkUrl'])
    assert payload['schemaVersion']==1 and isinstance(n,int) and n>0
    assert m['schemaVersion']==1 and m['packageName']=='com.opennutritracker.ont.opennutritracker'
    assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',m['version'])
    assert isinstance(m['versionCode'],int) and m['versionCode']==1000+n
    assert isinstance(m['bytes'],int) and 0<m['bytes']<=MAX_APK_BYTES
    assert re.fullmatch(r'[a-f0-9]{64}',m['sha256'])
    assert re.fullmatch(r'[a-f0-9]{40}',payload['sourceCommit'])
    assert u.scheme=='https' and u.hostname in ('release-assets.githubusercontent.com','objects.githubusercontent.com')
    releases=api('releases?per_page=30')
    builds=[int(r['tag_name'][4:]) for r in releases if re.fullmatch(r'apk-[0-9]+',r['tag_name']) and not r['draft'] and not r['prerelease']]
    if builds and max(builds)>n:
        print('A newer APK is already published');return
    dist=pathlib.Path('dist');dist.mkdir(exist_ok=True)
    apk=dist/'diet-diary.apk';h=hashlib.sha256();count=0
    with urllib.request.urlopen(payload['apkUrl'],timeout=60) as stream, apk.open('wb') as out:
        while chunk:=stream.read(1024*1024):
            count+=len(chunk)
            if count>m['bytes']:raise ValueError('APK exceeds declared size')
            h.update(chunk);out.write(chunk)
    assert count==m['bytes'] and h.hexdigest()==m['sha256'],'APK checksum mismatch'
    (dist/'UPDATE.json').write_text(json.dumps(m,indent=2)+'\n')
    (dist/'BUILD_INFO.json').write_text(json.dumps(payload['buildInfo'],ensure_ascii=False,indent=2)+'\n')
    (dist/'SHA256SUMS.txt').write_text(m['sha256']+'  diet-diary.apk\n')
    body='下载 diet-diary.apk 安装。\n\n版本：'+m['version']+' ('+str(m['versionCode'])+')\n\n'+         '中文食物库、AI 记餐与营养目标；支持应用内检查更新。\n\n'+         'APK 与更新信息公开分发，个人记录不上传此仓库。\n\n'+         '基于 OpenNutriTracker，遵循 GNU GPLv3，保留版权与许可。对应版本信息：'+payload['sourceCommit']
    tag='apk-'+str(n)
    existing=next((r for r in releases if r['tag_name']==tag),None)
    release=existing or api('releases','POST',{'tag_name':tag,'target_commitish':os.environ['GITHUB_SHA'],
        'name':'饮食日记 '+m['version']+' ('+str(m['versionCode'])+')','body':body,'draft':True})
    for name in ('diet-diary.apk','UPDATE.json','BUILD_INFO.json','SHA256SUMS.txt'):
        upload(release,dist/name)
    api('releases/'+str(release['id']),'PATCH',{'draft':False,'make_latest':'true','body':body})
    print('Published '+release['html_url'])
    if 'GITHUB_STEP_SUMMARY' in os.environ:
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as out:out.write(release['html_url']+'\n')

if __name__=='__main__':main()
