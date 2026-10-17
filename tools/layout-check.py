import json
from playwright.sync_api import sync_playwright
import os
# Aufruf: im Repo 'python3 -m http.server 8766' starten, dann 'python3 tools/layout-check.py'.
# Prüft Handy, iPad (hoch/quer) und Laptop auf horizontales Scrollen, überstehende und überlappende Bedienelemente.
S=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots') + '/'
os.makedirs(S, exist_ok=True)
d={}
for dd in range(1,15):
    d['2026-10-%02d'%dd]={'weight':80+dd/10,'sports':[{'id':'s%d'%dd,'type':'Tischtennis','min':90,'note':'','ex':[]}],'tasks':[{'id':'t%d'%dd,'text':'Übungsblatt Technische Mechanik','done':dd%2==0}],'note':'Notiz','custom':{},'evnotes':{},'checks':{}}
CHK="""(()=>{const W=document.documentElement.clientWidth,out=[];
document.querySelectorAll('body *').forEach(e=>{if(!e.offsetParent&&getComputedStyle(e).position!=='fixed')return;const r=e.getBoundingClientRect();if(r.width&&r.right>W+1&&!e.closest('.tabs'))out.push((e.id||e.className||e.tagName)+':'+Math.round(r.right))});
const sc=document.documentElement.scrollWidth>W;
// Überlappung von Buttons in derselben Zeile
const bs=[...document.querySelectorAll('button,input,select')].filter(e=>e.offsetParent).map(e=>[e,e.getBoundingClientRect()]);const ov=[];
for(let i=0;i<bs.length;i++)for(let j=i+1;j<bs.length;j++){const a=bs[i][1],b=bs[j][1];if(bs[i][0].contains(bs[j][0])||bs[j][0].contains(bs[i][0]))continue;const x=Math.min(a.right,b.right)-Math.max(a.left,b.left),y=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);if(x>2&&y>2)ov.push((bs[i][0].textContent||bs[i][0].id).trim().slice(0,15)+' x '+(bs[j][0].textContent||bs[j][0].id).trim().slice(0,15))}
return {hscroll:sc,over:out.slice(0,5),overlap:ov.slice(0,5)}})()"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,(w,h) in {'handy':(390,844),'ipad-hoch':(820,1180),'ipad-quer':(1180,820),'laptop':(1366,768)}.items():
        c=b.new_context(service_workers='block', viewport={'width':w,'height':h}, color_scheme='dark')
        UNI=[{'id':'uni1','name':'Uni','kind':'uni','items':[],
              'lessons':[{'id':'l%d'%i,'s':'Technische Mechanik 3 – Festigkeitslehre','a':'Vorlesung','r':'Raum B 123 (Campus Minden)','d':i,'f':'08:15','t':'09:45'} for i in range(1,8)],
              'todos':[{'id':'t1','x':'Übungsblatt 3 Technische Mechanik abgeben','from':'2026-10-01','due':'2026-12-24'},{'id':'t2','x':'Skript lesen','from':'2026-10-01','day':'2026-10-15'}]}]
        c.add_init_script("if(!sessionStorage.x){sessionStorage.x=1;localStorage.setItem('tagesbuch:days',%s);localStorage.setItem('tagesbuch:ctabs',%s)}"%(json.dumps(json.dumps(d)),json.dumps(json.dumps(UNI))))
        pg=c.new_page(); pg.goto('http://localhost:8766/'); pg.wait_for_timeout(700)
        for mode in ['Tag','Woche','Monat','Jahr']:
            pg.click('.mode:has-text("%s")'%mode); pg.wait_for_timeout(150)
            tabs=pg.locator('#tabs .tab:not(.add)')
            n=tabs.count() if tabs.first.is_visible() else 0
            if not n:
                r=pg.evaluate(CHK)
                if r['hscroll'] or r['over'] or r['overlap']: print(name,mode,r)
            for i in range(n):
                tabs.nth(i).click(); pg.wait_for_timeout(120)
                if mode=='Tag' and i==0:
                    pg.click('[data-act="rem-open"]'); pg.wait_for_timeout(100)
                r=pg.evaluate(CHK)
                if r['hscroll'] or r['over'] or r['overlap']: print(name,mode,tabs.nth(i).inner_text(),r)
                if mode=='Tag' and pg.query_selector('[data-act=uni-view]'):
                    pg.click('summary:has-text("Stundenplan bearbeiten")'); pg.wait_for_timeout(100)
                    for v in ('plan','todo'):
                        pg.click('[data-act=uni-view][data-v=%s]'%v); pg.wait_for_timeout(100)
                        r=pg.evaluate(CHK)
                        if r['hscroll'] or r['over'] or r['overlap']: print(name,'Uni',v,r)
                        pg.locator('#panel').screenshot(path=S+'L_%s_uni_%s.png'%(name,v))
                    pg.click('[data-act=uni-view][data-v=plan]')
            pg.screenshot(path=S+'L_%s_%s.png'%(name,mode))
        pg.click('.mode:has-text("Tag")'); pg.click('button[data-act="add-tab"]'); pg.wait_for_timeout(200); r=pg.evaluate(CHK)
        if r['hscroll'] or r['over'] or r['overlap']: print(name,'plus',r)
        print(name,'ok-checked')
