import os, json, math, re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse
import discord
from discord import app_commands
from discord.ext import commands, tasks

BASE=Path(__file__).parent
DATA=BASE/"data"; EXPORTS=BASE/"exports"
DATA.mkdir(exist_ok=True); EXPORTS.mkdir(exist_ok=True)
DB=DATA/"db.json"

DEMO=[
{"id":"demo-ffx","title":"Free Fire x Tenxi","creator":"TernakKlip","category":"Clipping Music","status":"ACTIVE","platforms":["TikTok","Instagram","Facebook","YouTube"],"payment_type":"CPM","rate":2000,"min_views":20000,"max_views":1000000,"budget":20000000,"budget_used":0.94,"rules":["WAJIB TAKE SOUND dari TikTok Ad Library","Jangan take down setelah approval","Gunakan hashtag #ffxtenxii"],"ai_allowed":"UNKNOWN"},
{"id":"demo-qarrar","title":"Qarrar WSK Phase 3","creator":"TernakKlip","category":"Clipping Entertainment","status":"ACTIVE","platforms":["TikTok"],"payment_type":"CPM","rate":5000,"min_views":50000,"max_views":2000000,"budget":24036661,"budget_used":0,"rules":["Cek brief campaign sebelum produksi."],"ai_allowed":"UNKNOWN"},
{"id":"demo-wetv","title":"WeTV Original — 12 IPA 4","creator":"TernakKlip","category":"Clipping Entertainment","status":"ACTIVE","platforms":["TikTok"],"payment_type":"CPM","rate":8000,"min_views":0,"max_views":0,"budget":0,"budget_used":0,"rules":[],"ai_allowed":"UNKNOWN"}]

def fresh():
    return {"campaigns":DEMO,"posts":[],"settings":{"auto_alerts":True,"alert_channel_id":""},
            "connector":{"mode":"manual_import","status":"NOT_CONNECTED","last_sync":None}}
def load():
    if not DB.exists(): save(fresh())
    try: return json.loads(DB.read_text(encoding="utf8"))
    except: return fresh()
def save(x): DB.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf8")
db=load()

def money(n): return "Rp{:,.0f}".format(n).replace(",",".")
def rate(c): return money(c.get("rate",0)) + ("/video" if c.get("payment_type")=="PER_VIDEO" else "/1K views")
def rem(c):
    b=float(c.get("budget",0) or 0); u=float(c.get("budget_used",0) or 0)
    return max(0,b*(1-u)) if 0<=u<=1 else max(0,b-u)
def score(c):
    s=50; r=float(c.get("rate",0) or 0)
    if r: s+=min(20,math.log10(max(r,1))*2.8)
    m=int(c.get("min_views",0) or 0)
    s += 10 if m and m<=20000 else 6 if m and m<=50000 else 2 if m and m<=100000 else (-5 if m>100000 else 0)
    if c.get("budget") and rem(c)>0: s+=min(8,(rem(c)/float(c["budget"]))*8)
    if "TikTok" in c.get("platforms",[]): s+=5
    if c.get("status")!="ACTIVE": s-=30
    return max(0,min(100,round(s)))
def rules(text):
    must=[]; dont=[]; tech=[]
    for x in [z.strip(" -*•\t") for z in text.splitlines() if z.strip()]:
        u=x.upper()
        if any(k in u for k in ["WAJIB","HARUS","MUST","REQUIRED"]): must.append(x)
        if any(k in u for k in ["DILARANG","JANGAN","DON'T","FORBIDDEN","TIDAK BOLEH"]): dont.append(x)
        if any(k in u for k in ["DURASI","RESOLUSI","9:16","SOUND","HASHTAG","TAG","CAPTION"]): tech.append(x)
    return must,dont,tech
def tik(url):
    try: return "tiktok.com" in urlparse(url).netloc.lower()
    except: return False

def embed_campaign(c):
    e=discord.Embed(title="📌 "+c["title"],description=f'{c.get("category","-")} • {c.get("creator","-")}')
    e.add_field(name="💰 Rate",value=rate(c),inline=True)
    e.add_field(name="📊 Score",value=f'{score(c)}/100',inline=True)
    e.add_field(name="🎯 Platform",value=", ".join(c.get("platforms",[])) or "-",inline=True)
    e.add_field(name="👀 Views",value=f'{c.get("min_views",0):,} – {c.get("max_views",0):,}'.replace(",","."),inline=True)
    e.add_field(name="💵 Budget",value=money(rem(c)) if c.get("budget") else "Unknown",inline=True)
    e.add_field(name="🤖 AI",value=c.get("ai_allowed","UNKNOWN"),inline=True)
    e.add_field(name="⚠️ Rules",value="\n".join("• "+x for x in c.get("rules",[])[:6]) or "Belum tersedia",inline=False)
    return e

class CView(discord.ui.View):
    def __init__(self,c): super().__init__(timeout=180); self.c=c
    @discord.ui.button(label="Brief",style=discord.ButtonStyle.primary)
    async def b(self,i,_):
        m,d,t=rules("\n".join(self.c.get("rules",[])))
        e=discord.Embed(title="📋 Brief — "+self.c["title"])
        e.add_field(name="WAJIB",value="\n".join("• "+x for x in m) or "Tidak terdeteksi",inline=False)
        e.add_field(name="DILARANG",value="\n".join("• "+x for x in d) or "Tidak terdeteksi",inline=False)
        e.add_field(name="TEKNIS",value="\n".join("• "+x for x in t) or "Cek brief asli",inline=False)
        await i.response.send_message(embed=e,ephemeral=True)
    @discord.ui.button(label="Generate",style=discord.ButtonStyle.success)
    async def g(self,i,_):
        title=self.c["title"]
        angles=[f"Hook cepat: buka dengan momen paling bikin penasaran dari {title}.",
        f"Takeaway: rangkum satu insight utama dari {title}.",
        f"Emosi: bangun reaksi sebelum reveal/punchline.",
        f"Debat: pilih momen yang mengundang komentar tanpa memelintir konteks.",
        f"Story: hook → konteks → payoff."]
        await i.response.send_message(embed=discord.Embed(title="🧠 Content Factory",description="\n\n".join(f"**{n+1}.** {x}" for n,x in enumerate(angles))),ephemeral=True)
    @discord.ui.button(label="Check",style=discord.ButtonStyle.secondary)
    async def c(self,i,_):
        w=[]
        if self.c.get("ai_allowed")=="NO": w.append("⛔ AI dilarang.")
        if self.c.get("ai_allowed")=="UNKNOWN": w.append("⚠️ Status AI UNKNOWN.")
        if not self.c.get("rules"): w.append("⚠️ Rules belum tersedia.")
        await i.response.send_message(embed=discord.Embed(title="🛡️ Compliance",description="\n".join(w) or "✅ Tidak ada warning otomatis.\nChecklist: platform • durasi • sound • caption • hashtag • tag • asset • take-down • originality"),ephemeral=True)

class CSelect(discord.ui.Select):
    def __init__(self,cs):
        super().__init__(placeholder="Pilih campaign…",options=[discord.SelectOption(label=c["title"][:100],value=c["id"],description=f"{score(c)}/100 • {rate(c)}"[:100]) for c in cs[:25]])
    async def callback(self,i):
        c=next((x for x in db["campaigns"] if x["id"]==self.values[0]),None)
        await i.response.send_message(embed=embed_campaign(c),view=CView(c),ephemeral=True)
class CList(discord.ui.View):
    def __init__(self,cs): super().__init__(timeout=180); self.add_item(CSelect(cs))

async def show(i,cs=None):
    cs=cs or [c for c in db["campaigns"] if c.get("status")=="ACTIVE"]
    cs=sorted(cs,key=score,reverse=True)
    desc="\n".join(f"**{n+1}. {c['title']}** — `{score(c)}/100` — {rate(c)}" for n,c in enumerate(cs[:10])) or "Kosong"
    await i.response.send_message(embed=discord.Embed(title="📡 Campaign Radar",description=desc),view=CList(cs),ephemeral=True)

intents=discord.Intents.default()
bot=commands.Bot(command_prefix="!",intents=intents)

@bot.event
async def on_ready():
    try:
        s=await bot.tree.sync()
        print(f"Bot online sebagai {bot.user} • {len(s)} commands")
    except Exception as e: print("sync:",e)

@bot.tree.command(name="home",description="Buka Clipper OS")
async def home(i):
    e=discord.Embed(title="🚀 CLIPPER OS",description="Campaign → AI → Video → Manual TikTok → Tracking → Earnings")
    e.add_field(name="📡 Radar",value="/campaigns /detail /filter /score")
    e.add_field(name="🧠 AI",value="/brief /generate /check")
    e.add_field(name="📈 Money",value="/track /analytics /earnings")
    e.add_field(name="🔌 System",value="/connector /import_campaigns /export_data /settings")
    await i.response.send_message(embed=e,ephemeral=True)
@bot.tree.command(name="campaigns",description="Campaign Radar")
async def campaigns(i): await show(i)
@bot.tree.command(name="detail",description="Detail campaign")
async def detail(i,campaign:str):
    x=[c for c in db["campaigns"] if campaign.lower() in c["title"].lower()]
    if not x:return await i.response.send_message("Campaign tidak ditemukan.",ephemeral=True)
    await i.response.send_message(embed=embed_campaign(x[0]),view=CView(x[0]),ephemeral=True)
@bot.tree.command(name="filter",description="Filter campaign")
async def filter_cmd(i,keyword:str):
    k=keyword.lower(); x=[c for c in db["campaigns"] if k in c["title"].lower() or k in c.get("category","").lower() or any(k in p.lower() for p in c.get("platforms",[]))]
    await show(i,x)
@bot.tree.command(name="score",description="Ranking Opportunity Score")
async def score_cmd(i):
    x=sorted(db["campaigns"],key=score,reverse=True)
    await i.response.send_message(embed=discord.Embed(title="🏆 Opportunity Score",description="\n".join(f"**{n+1}. {c['title']}** — `{score(c)}/100` — {rate(c)}" for n,c in enumerate(x[:15]))),ephemeral=True)
@bot.tree.command(name="brief",description="Analisis brief")
async def brief(i,text:str):
    m,d,t=rules(text); e=discord.Embed(title="🧠 Brief Reader")
    e.add_field(name="WAJIB",value="\n".join("• "+x for x in m) or "Tidak terdeteksi",inline=False)
    e.add_field(name="DILARANG",value="\n".join("• "+x for x in d) or "Tidak terdeteksi",inline=False)
    e.add_field(name="TEKNIS",value="\n".join("• "+x for x in t) or "Tidak terdeteksi",inline=False)
    await i.response.send_message(embed=e,ephemeral=True)
@bot.tree.command(name="generate",description="Generate angles/hooks")
async def generate(i,topic:str):
    a=["Hook cepat","Takeaway","Emosi","Debat","Story"]
    await i.response.send_message(embed=discord.Embed(title="🧠 Content Factory — "+topic,description="\n".join(f"**{n+1}. {x}**" for n,x in enumerate(a))+"\n\nHook: “Ternyata bagian ini yang bikin…”\nHook: “Kalau kamu lihat sampai akhir…”"),ephemeral=True)
@bot.tree.command(name="check",description="Compliance gate")
async def check(i,campaign:str,caption:str=""):
    x=[c for c in db["campaigns"] if campaign.lower() in c["title"].lower()]
    if not x:return await i.response.send_message("Campaign tidak ditemukan.",ephemeral=True)
    c=x[0]; lines=[("Campaign active",c.get("status")=="ACTIVE"),("TikTok tersedia","TikTok" in c.get("platforms",[])),("Rules tersedia",bool(c.get("rules"))),("AI permission known",c.get("ai_allowed") in ("YES","NO")),("Caption tidak kosong",bool(caption.strip()))]
    desc="\n".join(("✅" if ok else "⚠️")+" "+n for n,ok in lines)
    if c.get("ai_allowed")=="NO": desc+="\n⛔ BLOCK: AI dilarang."
    await i.response.send_message(embed=discord.Embed(title="🛡️ Compliance Gate",description=desc),ephemeral=True)
@bot.tree.command(name="track",description="Catat URL TikTok yang kamu upload manual")
async def track(i,url:str):
    if not tik(url):return await i.response.send_message("❌ URL TikTok tidak valid.",ephemeral=True)
    db["posts"].append({"url":url,"user_id":str(i.user.id),"views":0,"status":"TRACKED","created_at":datetime.now(timezone.utc).isoformat()});save(db)
    await i.response.send_message("✅ Tercatat. Bot tidak meng-upload ke TikTok. Views awal: 0.",ephemeral=True)
@bot.tree.command(name="analytics",description="Analytics posting")
async def analytics(i):
    v=sum(int(p.get("views",0)) for p in db["posts"]); n=len(db["posts"])
    await i.response.send_message(embed=discord.Embed(title="📈 Analytics",description=f"Posts: **{n}**\nTotal views: **{v:,}**\nAvg/post: **{v/n:,.0f}**" .replace(",","." if n else ",")),ephemeral=True)
@bot.tree.command(name="earnings",description="Hitung estimasi earnings")
async def earnings(i,campaign:str,views:int):
    x=[c for c in db["campaigns"] if campaign.lower() in c["title"].lower()]
    if not x:return await i.response.send_message("Campaign tidak ditemukan.",ephemeral=True)
    c=x[0]; mn=int(c.get("min_views",0) or 0); mx=int(c.get("max_views",0) or 0)
    if mn and views<mn: p=0; note=f"Belum minimum {mn:,} views."
    else:
        ev=min(views,mx) if mx else views
        p=(float(c.get("rate",0)) if c.get("payment_type")=="PER_VIDEO" else ev/1000*float(c.get("rate",0)))
        note="Estimasi; approval/eligible views dapat berubah."
    await i.response.send_message(embed=discord.Embed(title="💰 Earnings",description=f"Campaign: **{c['title']}**\nEligible views: **{views:,}**\nEstimasi: **{money(p)}**\n{note}".replace(",",".")),ephemeral=True)
@bot.tree.command(name="connector",description="Status TernakKlip connector")
async def connector(i):
    c=db["connector"]; await i.response.send_message(embed=discord.Embed(title="🔌 Connector",description=f"Mode: `{c['mode']}`\nStatus: `{c['status']}`\nLast sync: `{c.get('last_sync')}`\n\nOfficial/permitted connector required before automatic account sync."),ephemeral=True)
@bot.tree.command(name="import_campaigns",description="Import JSON campaign dari sumber yang diizinkan")
async def import_campaigns(i,payload:str):
    try:
        x=json.loads(payload)
        if not isinstance(x,list): raise ValueError("JSON harus array")
        if any("id" not in c or "title" not in c for c in x): raise ValueError("Setiap campaign butuh id dan title")
        db["campaigns"]=x; db["connector"]={"mode":"manual_import","status":"IMPORTED","last_sync":datetime.now(timezone.utc).isoformat()}; save(db)
        await i.response.send_message(f"✅ {len(x)} campaign diimport.",ephemeral=True)
    except Exception as e: await i.response.send_message("❌ "+str(e),ephemeral=True)
@bot.tree.command(name="export_data",description="Export database")
async def export_data(i):
    p=EXPORTS/f"clipper-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"; p.write_text(json.dumps(db,ensure_ascii=False,indent=2),encoding="utf8")
    await i.response.send_message(file=discord.File(p),ephemeral=True)
@bot.tree.command(name="settings",description="Lihat settings")
async def settings(i):
    s=db["settings"]; await i.response.send_message(f"⚙️ Auto alerts: `{s['auto_alerts']}`\nAlert channel: `{s['alert_channel_id'] or 'not set'}`",ephemeral=True)

@tasks.loop(minutes=30)
async def alerts():
    cid=db["settings"].get("alert_channel_id")
    if not cid:return
    try:
        ch=bot.get_channel(int(cid))
        top=sorted([c for c in db["campaigns"] if c.get("status")=="ACTIVE"],key=score,reverse=True)[:3]
        if ch and top: await ch.send("🔥 **Campaign Radar**\n"+"\n".join(f"• {c['title']} — {score(c)}/100 — {rate(c)}" for c in top))
    except Exception as e: print("alert:",e)

@alerts.before_loop
async def before(): await bot.wait_until_ready()

token=os.getenv("DISCORD_TOKEN","").strip()
if not token: raise RuntimeError("DISCORD_TOKEN belum diatur. Gunakan TOKEN BARU.")
alerts.start()
bot.run(token)
