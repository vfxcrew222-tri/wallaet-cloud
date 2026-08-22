from flask import Flask, request, jsonify, render_template_string
import time, os

app = Flask(__name__)

# ---------------- state ----------------
def fresh():
    return {
        "mode": "mvp",          # mvp = owner-approve | flex = auto-verify (Amazon/Flipkart)
        "status": "idle",       # idle -> requested -> approved -> unlocked -> delivered
        "partner_id": "",
        "platform": "",
        "photo": False,
        "weight": 0,
        "unit": "W-304",
        "flat": "Flat 304",
        "last": time.time(),
    }
S = fresh()
def setst(x): S["status"]=x; S["last"]=time.time()

GOLD="#C9A24B"; BLACK="#0B0B0C"; PANEL="#16161A"; WHITE="#F4F1EA"; GREY="#9A968C"; GREEN="#6FA07A"; RED="#C0563F"

BASE_CSS = f"""
<style>
 *{{box-sizing:border-box}} body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:{BLACK};color:{WHITE};margin:0;padding:16px;max-width:460px;margin:auto}}
 h1{{color:{GOLD};font-size:26px;letter-spacing:2px;margin:8px 0 2px}} .sub{{color:{GREY};font-size:13px;margin-bottom:14px}}
 .card{{background:{PANEL};border:1px solid #26262c;border-radius:14px;padding:18px;margin:12px 0}}
 .gold{{border-color:{GOLD}}}
 input,select{{width:100%;padding:12px;border-radius:8px;border:1px solid #333;background:#0f0f12;color:{WHITE};font-size:15px;margin:6px 0}}
 button{{width:100%;padding:14px;border:none;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer;margin-top:8px}}
 .b-gold{{background:{GOLD};color:{BLACK}}} .b-green{{background:{GREEN};color:#fff}} .b-red{{background:{RED};color:#fff}} .b-dark{{background:#26262c;color:{WHITE}}}
 .status{{font-size:16px;margin-top:12px;padding:12px;border-radius:8px;background:#0f0f12;text-align:center}}
 .big{{font-size:30px;font-weight:800;color:{GOLD};text-align:center;margin:10px 0}}
 .row{{display:flex;gap:8px}} .row button{{flex:1}}
 .tag{{display:inline-block;background:#0f0f12;color:{GOLD};padding:4px 10px;border-radius:20px;font-size:12px;margin:2px}}
 .muted{{color:{GREY};font-size:12px}} a{{color:{GOLD}}}
 .pill{{padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700}}
 .p-mvp{{background:#2a2410;color:{GOLD}}} .p-flex{{background:#12261a;color:{GREEN}}}
</style>
"""

# ---------------- home ----------------
@app.route("/")
def home():
    return f"""{BASE_CSS}
    <h1>WALLAET</h1><div class="sub">Live demo · secured delivery reception</div>
    <div class="card gold">
      <b style="color:{GOLD}">Open these on different phones / networks:</b>
      <div style="margin-top:12px">
        <a href="/courier"><button class="b-gold">📦 Courier screen</button></a>
        <a href="/owner"><button class="b-dark">🏠 Owner app</button></a>
        <a href="/box"><button class="b-dark">📡 Box simulator (demo without Pi)</button></a>
      </div>
    </div>
    <div class="card">
      <div class="muted">Demo mode</div>
      <div class="row" style="margin-top:8px">
        <button class="b-dark" onclick="setMode('mvp')">MVP · owner approves</button>
        <button class="b-dark" onclick="setMode('flex')">FLEX · auto-verify</button>
      </div>
      <div id="mode" class="status">loading…</div>
      <button class="b-red" onclick="reset()" style="margin-top:10px">↺ Reset demo</button>
    </div>
    <script>
      async function ping(){{let r=await fetch('/state');let s=await r.json();
        document.getElementById('mode').innerHTML='Current: <b class="pill '+(s.mode=='mvp'?'p-mvp':'p-flex')+'">'+(s.mode=='mvp'?'MVP (owner approves)':'FLEX (auto-verify)')+'</b>';}}
      async function setMode(m){{await fetch('/mode/'+m);ping();}}
      async function reset(){{await fetch('/reset');ping();}}
      ping();setInterval(ping,2000);
    </script>"""

# ---------------- courier ----------------
COURIER = """<CSS>
<h1>WALLAET</h1><div class="sub">Courier · <span id="unit">W-304</span></div>
<div class="card gold" id="box">
  <div id="step1">
    <div class="muted">1 · Select platform</div>
    <select id="plat">
      <option>Amazon</option><option>Flipkart</option><option>Meesho</option><option>Ajio</option><option>JioMart</option><option>Blinkit</option>
    </select>
    <div class="muted">2 · Delivery Partner ID (required)</div>
    <input id="pid" placeholder="e.g. AMZ-DEL-48213">
    <button class="b-gold" onclick="req()">Request Delivery</button>
    <div class="muted" style="margin-top:8px">Box limit 40×35×40cm. Bigger parcel → normal doorstep delivery.</div>
  </div>
  <div id="live" style="display:none">
    <div class="status" id="st">…</div>
  </div>
</div>
<script>
let poll;
async function req(){
  let pid=document.getElementById('pid').value, plat=document.getElementById('plat').value;
  if(pid.trim().length<3){alert('Enter Delivery Partner ID');return;}
  await fetch('/courier/request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({partner_id:pid,platform:plat})});
  document.getElementById('step1').style.display='none';
  document.getElementById('live').style.display='block';
  poll=setInterval(tick,1200);tick();
}
async function tick(){
  let s=await (await fetch('/state')).json();
  let el=document.getElementById('st');
  if(s.status=='requested') el.innerHTML=(s.mode=='flex'?'🔎 '+s.platform+' verifying order…':'⏳ Waiting for owner approval…');
  else if(s.status=='approved') el.innerHTML='✅ Verified! Box unlocking…';
  else if(s.status=='unlocked') el.innerHTML='🔓 <b>Flap OPEN</b><br>Drop the parcel now';
  else if(s.status=='delivered'){el.innerHTML='📦 <b>Delivered!</b> Thank you.';clearInterval(poll);}
}
</script>"""

@app.route("/courier")
def courier(): return COURIER.replace("<CSS>", BASE_CSS)

# ---------------- owner ----------------
OWNER = """<CSS>
<h1>WALLAET</h1><div class="sub">Owner · <span id="flat">Flat 304</span></div>
<div class="card" id="box"><div id="c" class="status">Waiting for delivery…</div></div>
<script>
async function tick(){
  let s=await (await fetch('/state')).json();
  let c=document.getElementById('c');
  if(s.status=='idle') c.innerHTML='<span class="muted">Waiting for delivery…</span>';
  else if(s.status=='requested'){
    if(s.mode=='flex') c.innerHTML='🔎 <b>'+s.platform+' delivery incoming</b><br><span class="muted">Verified by '+s.platform+' — no action needed</span>';
    else c.innerHTML='🔔 <b>Courier at your box!</b><br>Platform: '+s.platform+'<br>Partner ID: '+s.partner_id+'<br><button class="b-green" onclick="ok()">APPROVE DELIVERY</button>';
  }
  else if(s.status=='approved'||s.status=='unlocked') c.innerHTML='✅ Approved — delivery in progress…';
  else if(s.status=='delivered') c.innerHTML='📦 <b>Delivered ✓</b><br>Platform: '+s.platform+'<br>🪪 Partner ID: '+s.partner_id+'<br>⚖️ Weight: '+s.weight+' g'+(s.photo?'<br>📸 Photo captured':'');
}
async function ok(){await fetch('/owner/approve',{method:'POST'});}
tick();setInterval(tick,1200);
</script>"""

@app.route("/owner")
def owner(): return OWNER.replace("<CSS>", BASE_CSS)

# ---------------- box simulator (stand-in for Pi) ----------------
BOX = """<CSS>
<h1>WALLAET</h1><div class="sub">📡 Box simulator — use until the Pi is connected</div>
<div class="card gold"><div id="s" class="status">…</div></div>
<div class="card">
  <div class="muted">Simulate the box hardware:</div>
  <button class="b-gold" id="b1" onclick="drop()">📦 Parcel dropped (weight + photo)</button>
  <div class="muted" style="margin-top:10px">The flap unlocks automatically when a delivery is verified. Then press the button above to simulate the parcel landing.</div>
</div>
<script>
async function tick(){
  let s=await (await fetch('/state')).json();
  let el=document.getElementById('s');
  if(s.status=='idle') el.innerHTML='😴 Standby — locked';
  else if(s.status=='requested') el.innerHTML='⏳ Verification in progress…';
  else if(s.status=='approved'){el.innerHTML='🔓 UNLOCK signal received — flap opening';await fetch('/box/unlocked',{method:'POST'});}
  else if(s.status=='unlocked') el.innerHTML='🔓 FLAP OPEN — waiting for parcel drop';
  else if(s.status=='delivered') el.innerHTML='✅ Delivered — locked again';
}
async function drop(){await fetch('/box/delivered',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({weight:640,photo:true})});}
tick();setInterval(tick,1200);
</script>"""

@app.route("/box")
def box(): return BOX.replace("<CSS>", BASE_CSS)

# ---------------- api ----------------
@app.route("/state")
def state(): return jsonify(S)

@app.route("/mode/<m>")
def mode(m):
    if m in ("mvp","flex"): S["mode"]=m; 
    return jsonify(ok=True, mode=S["mode"])

@app.route("/courier/request", methods=["POST"])
def creq():
    d=request.get_json() or {}
    S["partner_id"]=d.get("partner_id",""); S["platform"]=d.get("platform","")
    setst("requested")
    if S["mode"]=="flex":            # auto-verify, no owner approve
        setst("approved")
    return jsonify(ok=True)

@app.route("/owner/approve", methods=["POST"])
def app_ok(): setst("approved"); return jsonify(ok=True)

# box/Pi endpoints (real Pi will call these too)
@app.route("/box/poll")
def bpoll():
    cmd="none"
    if S["status"]=="approved": cmd="unlock"
    return jsonify(command=cmd, status=S["status"], mode=S["mode"])

@app.route("/box/unlocked", methods=["POST"])
def bunlock(): 
    if S["status"]=="approved": setst("unlocked")
    return jsonify(ok=True)

@app.route("/box/delivered", methods=["POST"])
def bdel():
    d=request.get_json() or {}
    S["weight"]=d.get("weight",0); S["photo"]=bool(d.get("photo",False))
    setst("delivered")
    return jsonify(ok=True)

@app.route("/reset")
def reset():
    m=S["mode"]; S.update(fresh()); S["mode"]=m
    return jsonify(ok=True)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
