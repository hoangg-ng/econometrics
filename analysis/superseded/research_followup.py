"""Reconstruct review incidences; pair-complete imputation and pair bootstrap.
Run from repository root with numpy/scipy installed. No API extraction.
"""
import csv, json, math, hashlib
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import chi2, norm

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/research_followup'
SEED=20261102
B=1000
BASE=['top1','top2','hhi','gini','author_hhi','review_minus_author_hhi','dual_role_share','repeated_dyad_share']
HIST=['incumbent_top1','fixed_core_share','outside_roster_share','historical_dyad_share']
# Extra exclusions are a sensitivity analysis, not a validated account classifier.
BOT_WORDS=('bot','assistant','copilot','coderabbit','gemini','devin','dependabot','renovate')

def indices(keys):
    lookup={v:i for i,v in enumerate(sorted(set(keys)))}
    return np.array([lookup[k] for k in keys]),len(lookup)

def concentration(counts):
    v=np.array(sorted(counts,reverse=True),float)
    if not len(v) or v.sum()<=0: return None
    s=v/v.sum(); n=len(v)
    g=(2*np.dot(np.arange(1,n+1),np.sort(v))/(n*v.sum())-(n+1)/n)
    return float(s[0]),float(s[:2].sum()),float(s@s),float(g)

def load(strict=False):
    pairs=list(csv.DictReader(open(ROOT/'output/matched_pairs.csv')))
    grouped=defaultdict(list); seen=set(); skipped=0
    for r in csv.DictReader(open(ROOT/'output/pr_level_data.csv')):
        if not r['pr_number'] or not r['n_distinct_reviewers']:
            skipped+=1; continue
        p=pairs[int(r['pair_id'])]
        assert r['repo']==p[r['role']+'_repo'] and r['t0']==p['treated_t0']
        key=(r['pair_id'],r['role'],r['pr_number'])
        assert key not in seen; seen.add(key)
        h=int(r['event_time']); period=(int(r['year']),int(r['month']))
        if period==(2026,9) or h not in list(range(-6,-1))+list(range(12)): continue
        reviewers={x.lower() for x in r['reviewer_logins'].split(';') if x}
        assert len(reviewers)==int(r['n_distinct_reviewers'])
        author=r['author_login'].lower()
        if strict:
            reviewers={x for x in reviewers if not any(w in x for w in BOT_WORDS)}
            if any(w in author for w in BOT_WORDS): author=''
        grouped[(int(r['pair_id']),r['role'],r['repo'])].append((h,period,reviewers,author))
    rows=[]
    for (pid,role,repo),prs in grouped.items():
        history=Counter(); roster=set(); historical_dyads=set()
        for h,period,reviewers,a in prs:
            if h in (-6,-5,-4):
                history.update(reviewers); roster.update(reviewers)
                historical_dyads.update((a,x) for x in reviewers if a and a!=x)
        ranked=sorted(history,key=lambda x:(-history[x],x))
        # Exclude tied history leaders from identity sample; do not break ties by row order.
        unique=bool(ranked) and (len(ranked)==1 or history[ranked[0]]>history[ranked[1]])
        month=defaultdict(list)
        for r in prs: month[(r[0],r[1])].append(r)
        for (h,period),items in month.items():
            reviews=Counter(); authors=Counter(); dyads=Counter()
            for _,_,rev,a in items:
                reviews.update(rev)
                if a: authors[a]+=1
                dyads.update((a,x) for x in rev if a and a!=x)
            c=concentration(list(reviews.values())); ac=concentration(list(authors.values()))
            if c is None: continue
            y=dict(zip(['top1','top2','hhi','gini'],c))
            if ac is None or not dyads:
                rows.append(dict(pair=pid,role=role,repo=repo,h=h,period=period,n_pr=len(items),n_reviewers=len(reviews),**y))
                continue
            total=sum(reviews.values()); dt=sum(dyads.values())
            y.update(author_hhi=ac[2],review_minus_author_hhi=c[2]-ac[2],
                     dual_role_share=sum(n for x,n in reviews.items() if x in authors)/total,
                     repeated_dyad_share=sum(n for n in dyads.values() if n>=2)/dt)
            # Selection window never contributes to historical-outcome estimation.
            if unique and h>=-3:
                leaders={x for x,n in reviews.items() if n==max(reviews.values())}
                y.update(incumbent_top1=(1/len(leaders) if ranked[0] in leaders else 0),
                         fixed_core_share=sum(reviews[x] for x in ranked[:2])/total,
                         outside_roster_share=sum(n for x,n in reviews.items() if x not in roster)/total,
                         historical_dyad_share=sum(n for d,n in dyads.items() if d in historical_dyads)/dt)
            rows.append(dict(pair=pid,role=role,repo=repo,h=h,period=period,n_pr=len(items),n_reviewers=len(reviews),**y))
    return rows,skipped

def sample(rows,keys,balanced=False):
    rows=[r for r in rows if all(k in r for k in keys)]
    groups=defaultdict(list)
    for r in rows: groups[(r['pair'],r['role'])].append(r)
    eligible=set()
    for pid in {r['pair'] for r in rows}:
        ok=True
        for role in ('treated','control'):
            hs={r['h'] for r in groups[pid,role]}
            ok &= bool(hs & set(range(-6,-1))) and bool(hs & set(range(12)))
            if balanced: ok &= set(range(6))<=hs
        if ok: eligible.add(pid)
    return [r for r in rows if r['pair'] in eligible and (not balanced or r['h']<=5)]

def design(rows,keys):
    e,ne=indices([r['repo'] for r in rows]); t,nt=indices([r['period'] for r in rows]); p,npair=indices([r['pair'] for r in rows])
    h=np.array([r['h'] for r in rows]); tr=np.array([r['role']=='treated' for r in rows])
    y=np.array([[r[k] for k in keys] for r in rows])
    return e,t,p,h,tr,y,ne,nt,npair

def fe(y,e,t,w,ne,nt):
    if y.ndim==1:y=y[:,None]
    de=np.bincount(e,weights=w,minlength=ne); dt=np.bincount(t,weights=w,minlength=nt)
    a=np.zeros((ne,y.shape[1])); b=np.zeros((nt,y.shape[1]))
    for it in range(1500):
        aa=np.column_stack([np.bincount(e,weights=w*(y[:,j]-b[t,j]),minlength=ne)/np.maximum(de,1) for j in range(y.shape[1])])
        bb=np.column_stack([np.bincount(t,weights=w*(y[:,j]-aa[e,j]),minlength=nt)/np.maximum(dt,1) for j in range(y.shape[1])])
        delta=max(np.max(np.abs(aa-a)),np.max(np.abs(bb-b))); a,b=aa,bb
        if delta<1e-9: break
    else: raise RuntimeError('FE did not converge')
    return a[e]+b[t],(de[e]>0)&(dt[t]>0)

def estimate(d,weights=None):
    e,t,p,h,tr,y,ne,nt,npair=d
    w=np.ones(len(p)) if weights is None else weights[p]
    train=(~tr)|(h<0)
    pred,support=fe(y,e,t,w*train,ne,nt)
    use=tr&(h>=0)&support&(w>0)
    return np.average((y-pred)[use],axis=0,weights=w[use])

def pretrend(d):
    # Untreated-only FE regression with treated lead indicators; earliest pre month omitted.
    e,t,p,h,tr,y,ne,nt,npair=d
    use=(~tr)|(h<0); leads=sorted(set(h[tr&(h<0)])); tested=leads[1:]
    x=np.column_stack([tr&(h==v) for v in tested]).astype(float)
    z=np.column_stack([x,y]); pred,_=fe(z,e,t,use.astype(float),ne,nt)
    rz=(z-pred)[use]; xx=rz[:,:len(tested)]; yy=rz[:,len(tested):]
    inv=np.linalg.pinv(xx.T@xx); beta=inv@xx.T@yy; err=yy-xx@beta
    out=[]
    for j in range(y.shape[1]):
        scores=np.zeros((npair,len(tested)))
        np.add.at(scores,p[use],xx*err[:,j,None])
        cov=inv@scores.T@scores@inv*npair/(npair-1)
        rank=np.linalg.matrix_rank(cov)
        stat=float(beta[:,j]@np.linalg.pinv(cov)@beta[:,j])
        out.append(dict(p=float(chi2.sf(stat,rank)),df=int(rank),stat=stat,leads=[int(v) for v in tested],coefficients=beta[:,j].tolist()))
    return out

def run(name,rows,keys):
    d=design(rows,keys); point=estimate(d); rng=np.random.default_rng(SEED)
    draws=[]
    cache=OUT/(name+'_bootstrap.npz')
    signature=hashlib.sha256(repr(rows).encode()+repr((keys,SEED,B)).encode()).hexdigest()
    if cache.exists():
        saved=np.load(cache)
        assert list(saved['keys'])==keys
        if 'signature' in saved:
            assert str(saved['signature'])==signature, 'Input changed: archive stale bootstrap cache before rerunning'
        draws=saved['draws']
    else:
        for b in range(B):
            weights=np.bincount(rng.integers(0,d[-1],d[-1]),minlength=d[-1])
            draws.append(estimate(d,weights))
    draws=np.array(draws); se=draws.std(axis=0,ddof=1); pre=pretrend(d)
    results=[]
    for j,k in enumerate(keys):
        y=d[5][:,j]; pre_mask=d[4]&(d[3]<0)
        results.append(dict(spec=name,outcome=k,att=float(point[j]),se=float(se[j]),
           p=float(2*norm.sf(abs(point[j]/se[j]))),ci_low=float(point[j]-1.96*se[j]),ci_high=float(point[j]+1.96*se[j]),
           pretrend_p=pre[j]['p'],baseline=float(y[pre_mask].mean()),pairs=d[-1],rows=len(rows),post_rows=int((d[4]&(d[3]>=0)).sum())))
    np.savez_compressed(OUT/(name+'_bootstrap.npz'),draws=draws,keys=keys,signature=signature)
    (OUT/(name+'_pretrend.json')).write_text(json.dumps(pre,indent=2))
    print(json.dumps(results),flush=True)
    return results

def selftest():
    assert concentration([10,10])==(0.5,1.,0.5,0.)
    assert concentration([10])==(1.,1.,1.,0.)
    rows=[]
    for p in range(12):
        for role in ['treated','control']:
            for h in range(-3,4):
                rows.append(dict(pair=p,repo=f'{p}-{role}',role=role,h=h,period=(2020,h+4),y=p+2*h+(3 if role=='treated' and h>=0 else 0)))
    d=design(rows,['y'])
    assert abs(estimate(d)[0]-3)<1e-7
    e,t,p,h,tr,y,ne,nt,npair=d
    rng=np.random.default_rng(91); noisy=y+rng.normal(size=y.shape)
    w=rng.integers(1,4,len(rows))*((~tr)|(h<0))
    fitted,support=fe(noisy,e,t,w,ne,nt)
    x=np.column_stack([np.eye(ne)[e],np.eye(nt)[t]])
    beta=np.linalg.lstsq(x*np.sqrt(w[:,None]),noisy*np.sqrt(w[:,None]),rcond=None)[0]
    assert np.max(np.abs(fitted[support]-(x@beta)[support]))<1e-6
    pre=pretrend(d)
    assert max(abs(v) for v in pre[0]['coefficients'])<1e-6
    assert len(sample(rows,['y']))==len(rows)
    assert not sample([r for r in rows if r['role']=='treated'],['y'])

if __name__=='__main__':
    selftest(); OUT.mkdir(parents=True,exist_ok=True)
    rows,skipped=load(); results=[]
    specs=[('all_review_months',sample(rows,BASE[:4]),BASE[:4]),
           ('common_incidence',sample(rows,BASE),BASE),
           ('balanced_six_month',sample(rows,BASE,True),BASE),
           ('independent_history',sample(rows,HIST),HIST)]
    strict,_=load(True); specs.append(('bot_name_sensitivity',sample(strict,BASE),BASE))
    for name,rr,keys in specs:
        print('RUN',name,'rows',len(rr),flush=True)
        results.extend(run(name,rr,keys))
    # Holm correction across all new task-allocation/identity outcomes and specifications.
    family=[r for r in results if r['outcome'] not in ['top1','top2','hhi','gini']]
    order=sorted(family,key=lambda r:r['p']); prev=0
    for i,r in enumerate(order):
        prev=max(prev,min(1.,r['p']*(len(order)-i))); r['holm_p']=prev
    fields=list(results[0])+['holm_p']
    with open(OUT/'results.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(results)
    meta=dict(seed=SEED,bootstrap_reps=B,skipped_sentinel_rows=skipped,
      data_sha256=hashlib.sha256((ROOT/'output/pr_level_data.csv').read_bytes()).hexdigest(),
      notes=['Merged PRs only; no active-review months are imputed as zero.',
       'All BASE outcomes use the same rows, conditional on review and non-self author-reviewer links.',
       'Bootstrap refits FE with matched-pair multiplicities, matching fixed; shared reviewers not clustered.',
       'Historical roster selected h=-6,-5,-4; estimation pre h=-3,-2; ties in history leader excluded; monthly ties fractional.',
       'Gini uses active reviewers, singleton Gini=0; HHI and top2=1 for singleton.',
       'Untreated-only joint lead regression uses full pair-cluster covariance; short historical baseline has low power.',
       'Uncapped means no 40-PR monthly cap; original upstream retrieval coverage is not proven exhaustive.'])
    (OUT/'metadata.json').write_text(json.dumps(meta,indent=2))
