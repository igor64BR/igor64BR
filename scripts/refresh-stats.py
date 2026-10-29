import subprocess,json,base64,datetime,collections,html,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def api(endpoint,payload=None):
 r=subprocess.run(['gh','api',endpoint]+(['--input','-'] if payload else []),input=json.dumps(payload) if payload else None,capture_output=True,text=True,check=True)
 return json.loads(r.stdout)

def generate(out):
 out.mkdir(parents=True,exist_ok=True)
 query='query { user(login:"igor64BR") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } } repositories(first:100,ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false) { pageInfo { hasNextPage } nodes { name stargazerCount languages(first:100) { edges { size node { name color } } pageInfo { hasNextPage } } } } } }'
 response=api('graphql',{'query':query})
 assert not response.get('errors'),response.get('errors')
 u=response['data']['user'];repos=u['repositories'];assert not repos['pageInfo']['hasNextPage']
 cal=u['contributionsCollection']['contributionCalendar'];days=[d for w in cal['weeks'] for d in w['contributionDays']]
 assert sum(d['contributionCount'] for d in days)==cal['totalContributions']
 months=collections.Counter();langs=collections.Counter();colors={}
 for d in days:months[d['date'][:7]]+=d['contributionCount']
 for r in repos['nodes']:
  assert not r['languages']['pageInfo']['hasNextPage']
  for e in r['languages']['edges']:
   n=e['node']['name'];langs[n]+=e['size'];colors[n]=e['node']['color'] or '#94a3b8'
 date=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
 def start(height,title,desc):
  return f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img"><title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc><rect x="1" y="1" width="1198" height="{height-2}" rx="18" fill="#111827" stroke="#334155"/><g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">'
 def text(x,y,s,size=16,color='#b8c7dc',weight=400):return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}">{html.escape(str(s))}</text>'
 svg=start(410,'GitHub contributions by month',f"GitHub contribution calendar, {days[0]['date']} to {days[-1]['date']}. Includes anonymized private activity where GitHub reports it. First and last months are partial.")
 svg+=text(32,42,'GitHub contributions',24,'#f8fafc',600)+text(32,71,f"{cal['totalContributions']:,} contributions · {days[0]['date']} to {days[-1]['date']}")
 maximum=max(months.values());step=max(1,((maximum+3)//4+99)//100*100);ceiling=step*4
 for i in range(5):
  y=310-i*49;svg+=f'<path d="M90 {y}H1160" stroke="#29384d"/>'+text(30,y+5,i*step,13)
 for i,(m,n) in enumerate(sorted(months.items())):
  x=105+i*81;h=n/ceiling*196
  svg+=f'<rect x="{x}" y="{310-h:.2f}" width="48" height="{h:.2f}" rx="4" fill="'+('#5eead4' if i==len(months)-1 else '#60a5fa')+'"/>'
  svg+=text(x,300-h,n,14,'#e2e8f0')+text(x,336,datetime.date.fromisoformat(m+'-01').strftime('%b'),13)+text(x,354,m[:4],11)
 svg+=text(32,389,f'GitHub GraphQL API · Snapshot {date} UTC · First and last months are partial; includes anonymized private activity.',13)+'</g></svg>'
 (out/'activity.svg').write_text(svg)
 total=sum(langs.values());ranked=langs.most_common(6);other=total-sum(v for _,v in ranked)
 if other:ranked.append(('Other',other));colors['Other']='#94a3b8'
 svg=start(470,'Languages in public repositories','Language share by bytes of code reported by GitHub Linguist. Owned public repositories only; forks excluded. This is not a proficiency score.')
 svg+=text(32,42,'Languages in my public repositories',24,'#f8fafc',600)+text(32,72,f"{len(repos['nodes'])} owned public repositories · Forks excluded · Share of code by bytes")
 for i,(name,n) in enumerate(ranked):
  y=110+i*43;pct=100*n/total
  svg+=text(32,y+18,name,16,'#e2e8f0')+f'<rect x="200" y="{y}" width="830" height="23" rx="5" fill="#243247"/><rect x="200" y="{y}" width="{830*pct/100:.3f}" height="23" rx="5" fill="{colors[name]}"/>'+text(1050,y+18,f'{pct:.1f}%',16,'#e2e8f0')
 svg+=text(32,438,f'GitHub Linguist / GraphQL API · Snapshot {date} UTC · Code volume is not a measure of proficiency.',13)+'</g></svg>'
 (out/'languages.svg').write_text(svg)
 evidence={'snapshot_utc':date,'contribution_range':[days[0]['date'],days[-1]['date']],'contribution_total':cal['totalContributions'],'monthly_contributions':dict(sorted(months.items())),'public_nonfork_repo_count':len(repos['nodes']),'language_bytes':dict(langs.most_common()),'scope':'Contributions may include anonymized private activity. Language bytes: owned public non-fork repositories only.'}
 (out/'github-data.json').write_text(json.dumps(evidence,indent=2)+'\n')
 return evidence

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('assets/stats'));args=p.parse_args()
 print(json.dumps(generate(args.output),indent=2))
