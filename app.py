from flask import Flask, request, jsonify
import time, os

app = Flask(__name__)

def fresh():
    return {"mode":"mvp","status":"idle","partner_id":"","platform":"",
            "photo":False,"weight":0,"unit":"W-304","flat":"Flat 304","t":0,"last":time.time()}
S = fresh()
def setst(x): S["status"]=x; S["last"]=time.time()

CSS = """
<meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
 :root{--gold:#C9A24B;--goldl:#E6C976;--bk:#0B0B0C;--pan:#16161A;--pan2:#1E1E24;--wh:#F4F1EA;--gr:#9A968C;--grn:#6FA07A;--red:#C0563F}
 *{box-sizing:border-box}
 body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:radial-gradient(circle at 50% -10%,#181820,#0B0B0C 60%);color:var(--wh);margin:0;min-height:100vh}
 .wrap{max-width:470px;margin:auto;padding:18px}
 .hdr{display:flex;align-items:center;justify-content:space-between;padding:6px 2px 14px;border-bottom:1px solid #26262c}
 .logo{font-size:22px;font-weight:800;letter-spacing:3px;color:var(--gold)}
 .role{font-size:12px;color:var(--gr)}
 .pill{padding:5px 12px;border-radius:20px;font-size:11px;font-weight:800;letter-spacing:.5px}
 .p-mvp{background:#2a2410;color:var(--gold)} .p-flex{background:#12261a;color:var(--grn)}
 .card{background:var(--pan);border:1px solid #26262c;border-radius:16px;padding:20px;margin:14px 0;box-shadow:0 8px 30px rgba(0,0,0,.4)}
 .gold{border-color:var(--gold)}
 .lbl{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--gr);margin:14px 0 6px}
 input,select{width:100%;padding:13px;border-radius:10px;border:1px solid #333;background:#0d0d10;color:var(--wh);font-size:15px}
 button{width:100%;padding:15px;border:none;border-radius:12px;font-size:16px;font-weight:800;cursor:pointer;margin-top:12px;transition:.15s}
 button:active{transform:scale(.98)}
 .b-gold{background:linear-gradient(135deg,#E6C976,#C9A24B);color:#0B0B0C} .b-grn{background:var(--grn);color:#fff}
 .b-red{background:var(--red);color:#fff} .b-dark{background:#26262c;color:var(--wh);border:1px solid #33333a}
 .st{text-align:center;padding:22px 14px;border-radius:12px;background:#0d0d10;font-size:16px;margin-top:6px}
 .st .em{font-size:34px;display:block;margin-bottom:8px}
 .big{font-size:44px;font-weight:800;color:var(--gold);line-height:1}
 .muted{color:var(--gr);font-size:12px} .row{display:flex;gap:10px} .row>*{flex:1}
 .badge{display:inline-flex;align-items:center;gap:6px;background:#0d0d10;border:1px solid #2a2a30;padding:7px 12px;border-radius:10px;font-size:13px;margin:4px 4px 0 0}
 .steps{display:flex;justify-content:space-between;margin:6px 0 14px}
 .dot{width:26px;height:26px;border-radius:50%;background:#26262c;color:var(--gr);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800}
 .dot.on{background:var(--gold);color:#0B0B0C} .dot.done{background:var(--grn);color:#fff}
 .line{flex:1;height:2px;background:#26262c;margin:12px 2px 0}
 .dcard{border-left:4px solid var(--grn);background:var(--pan2);border-radius:10px;padding:14px;margin-top:12px}
 .photo{height:120px;border-radius:10px;background:repeating-linear-gradient(45deg,#1a1a20,#1a1a20 10px,#15151a 10px,#15151a 20px);display:flex;align-items:center;justify-content:center;color:var(--gr);font-size:13px;margin-top:10px}
 a{color:var(--gold);text-decoration:none} .link-btn{display:block;margin-top:10px}
 .footer{text-align:center;color:#555;font-size:11px;margin-top:20px;letter-spacing:2px}
</style>"""

def shell(role, body, js=""):
    return f"""{CSS}<div class='wrap'>
    <div class='hdr'><div><div class='logo'>WALLAET</div><div class='role'>{role}</div></div><span id='pill' class='pill'></span></div>
    {body}
    <div class='footer'>SECURED DELIVERY RECEPTION</div></div>
    <script>
    async function _mode(){{try{{let s=await(await fetch('/state')).json();let p=document.getElementById('pill');
      if(p){{p.className='pill '+(s.mode=='mvp'?'p-mvp':'p-flex');p.textContent=(s.mode=='mvp'?'MVP':'FLEX');}}}}catch(e){{}}}}
    _mode();setInterval(_mode,3000);
    {js}</script>"""

@app.route("/")
def home():
    body="""
    <div class='card gold'>
      <div class='lbl'>Open on different phones / networks</div>
      <a class='link-btn' href='/courier'><button class='b-gold'>📦  Courier screen</button></a>
      <a class='link-btn' href='/owner'><button class='b-dark'>🏠  Owner app</button></a>
      <a class='link-btn' href='/box'><button class='b-dark'>📡  Box simulator (demo without Pi)</button></a>
    </div>
    <div class='card'>
      <div class='lbl'>Demo mode</div>
      <div class='row'>
        <button class='b-dark' onclick="fetch('/mode/mvp').then(_mode).then(md)">MVP · owner approves</button>
        <button class='b-dark' onclick="fetch('/mode/flex').then(_mode).then(md)">FLEX · auto-verify</button>
      </div>
      <div id='mdesc' class='muted' style='margin-top:12px;text-align:center'></div>
      <button class='b-red' onclick="fetch('/reset').then(()=>location.reload())">↺  Reset demo</button>
    </div>"""
    js="""async function md(){let s=await(await fetch('/state')).json();
      document.getElementById('mdesc').innerHTML=s.mode=='mvp'
        ?'MVP: courier requests, <b>owner approves</b>, box opens. Works with no integration.'
        :'FLEX: platform verifies the order, box <b>auto-opens</b>. No owner action (the v003 vision).';}
      md();setInterval(md,2500);"""
    return shell("Live demo", body, js)

@app.route("/courier")
def courier():
    body="""
    <div id='s0' class='card gold' style='text-align:center'>
      <div class='lbl'>Step 1 · Scan the box</div>
      <div style='font-size:64px;margin:14px 0'>🔳</div>
      <div class='muted' style='margin-bottom:6px'>Point your delivery app at the Wallaet QR sticker on the box.</div>
      <button class='b-gold' onclick='scan()'>📷  Scan box QR</button>
    </div>
    <div id='s1' class='card gold' style='display:none'>
      <div class='st' style='margin-bottom:14px'>✅ Box identified: <b style='color:var(--gold)'>W-304</b><br><span class='muted'>Flat 304</span></div>
      <div class='lbl'>Platform</div>
      <select id='plat'><option>Amazon</option><option>Flipkart</option><option>Meesho</option><option>Ajio</option><option>JioMart</option><option>Blinkit</option></select>
      <div class='lbl'>Delivery Partner ID (required)</div>
      <input id='pid' placeholder='e.g. AMZ-DEL-48213'>
      <button class='b-gold' onclick='req()'>Request Delivery</button>
      <div class='muted' style='margin-top:10px'>Box limit 40x35x40 cm. Larger parcel &rarr; normal doorstep delivery.</div>
    </div>
    <div id='s2' class='card' style='display:none'>
      <div class='steps'>
        <div id='d1' class='dot'>1</div><div class='line'></div>
        <div id='d2' class='dot'>2</div><div class='line'></div>
        <div id='d3' class='dot'>3</div><div class='line'></div>
        <div id='d4' class='dot'>4</div>
      </div>
      <div id='st' class='st'>&hellip;</div>
    </div>"""
    js="""let poll;
    function scan(){document.getElementById('s0').style.display='none';document.getElementById('s1').style.display='block';}
    async function req(){let pid=document.getElementById('pid').value,plat=document.getElementById('plat').value;
      if(pid.trim().length<3){alert('Enter Delivery Partner ID');return;}
      await fetch('/courier/request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({partner_id:pid,platform:plat})});
      document.getElementById('s1').style.display='none';document.getElementById('s2').style.display='block';poll=setInterval(tick,1000);tick();}
    function dots(n){for(let i=1;i<=4;i++){let d=document.getElementById('d'+i);d.className='dot'+(i<n?' done':i==n?' on':'');if(i<n)d.innerHTML='&check;';else d.innerHTML=i;}}
    async function tick(){let s=await(await fetch('/state')).json();let el=document.getElementById('st');
      if(s.status=='requested'){dots(2);el.innerHTML=s.mode=='flex'?"<span class='em'>🔎</span>"+s.platform+" is verifying the order…":"<span class='em'>⏳</span>Waiting for owner approval…";}
      else if(s.status=='approved'){dots(3);el.innerHTML="<span class='em'>✅</span>Verified! Box unlocking…";}
      else if(s.status=='unlocked'){dots(3);el.innerHTML="<span class='em'>🔓</span><b>Flap is OPEN</b><br>Drop the parcel now";}
      else if(s.status=='delivered'){dots(5);el.innerHTML="<span class='em'>📦</span><b>Delivered!</b><br>Thank you.";clearInterval(poll);}}"""
    return shell("Courier · scan to start", body, js)

@app.route("/owner")
def owner():
    body="<div class='card'><div id='c'></div></div>"
    js="""async function tick(){let s=await(await fetch('/state')).json();let c=document.getElementById('c');
      if(s.status=='idle'){c.innerHTML="<div class='st'><span class='em'>🏠</span>Waiting for a delivery…</div>";}
      else if(s.status=='requested'){
        if(s.mode=='flex')c.innerHTML="<div class='st'><span class='em'>🔎</span><b>"+s.platform+" delivery incoming</b><br><span class='muted'>Verified by "+s.platform+" — no action needed</span></div>";
        else c.innerHTML="<div class='st'><span class='em'>🔔</span><b>Courier at your box!</b></div><div style='margin-top:10px'><span class='badge'>🛍️ "+s.platform+"</span><span class='badge'>🪪 "+s.partner_id+"</span></div><button class='b-grn' onclick='ok()'>APPROVE DELIVERY</button>";}
      else if(s.status=='approved'||s.status=='unlocked'){c.innerHTML="<div class='st'><span class='em'>✅</span>Approved — delivery in progress…</div>";}
      else if(s.status=='delivered'){c.innerHTML="<div class='dcard'><b style='color:var(--grn)'>📦 DELIVERED ✓</b><div style='margin-top:8px'><span class='badge'>🛍️ "+s.platform+"</span><span class='badge'>🪪 "+s.partner_id+"</span></div><div style='margin-top:12px'><span class='muted'>Weight captured</span><div class='big'>"+s.weight+" <span style='font-size:18px'>g</span></div></div>"+(s.photo?"<div class='photo'>📸 Delivery photo captured</div>":"")+"</div>";}}
    async function ok(){await fetch('/owner/approve',{method:'POST'});}
    tick();setInterval(tick,1000);"""
    return shell("Owner · Flat 304", body, js)

@app.route("/box")
def box():
    body="""
    <div class='card gold'><div id='s' class='st'>&hellip;</div></div>
    <div class='card'>
      <div class='lbl'>Simulate the box hardware</div>
      <button class='b-gold' onclick='drop()'>📦  Parcel dropped (weight + photo)</button>
      <div class='muted' style='margin-top:10px'>Flap unlocks automatically once a delivery is verified. Then tap above to simulate the parcel landing on the platform.</div>
    </div>"""
    js="""async function tick(){let s=await(await fetch('/state')).json();let el=document.getElementById('s');
      if(s.status=='idle')el.innerHTML="<span class='em'>😴</span>Standby — locked";
      else if(s.status=='requested')el.innerHTML="<span class='em'>⏳</span>Verification in progress…";
      else if(s.status=='approved'){el.innerHTML="<span class='em'>🔓</span>UNLOCK received — opening flap";await fetch('/box/unlocked',{method:'POST'});}
      else if(s.status=='unlocked')el.innerHTML="<span class='em'>🔓</span>FLAP OPEN — waiting for drop";
      else if(s.status=='delivered')el.innerHTML="<span class='em'>✅</span>Delivered — locked again";}
    async function drop(){await fetch('/box/delivered',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({weight:640,photo:true})});}
    tick();setInterval(tick,1000);"""
    return shell("Box simulator", body, js)

@app.route("/state")
def state(): return jsonify(S)
@app.route("/mode/<m>")
def mode(m):
    if m in ("mvp","flex"): S["mode"]=m
    return jsonify(ok=True,mode=S["mode"])
@app.route("/courier/request",methods=["POST"])
def creq():
    d=request.get_json() or {}; S["partner_id"]=d.get("partner_id",""); S["platform"]=d.get("platform","")
    setst("requested")
    if S["mode"]=="flex": setst("approved")
    return jsonify(ok=True)
@app.route("/owner/approve",methods=["POST"])
def aok(): setst("approved"); return jsonify(ok=True)
@app.route("/box/poll")
def bpoll(): return jsonify(command=("unlock" if S["status"]=="approved" else "none"),status=S["status"],mode=S["mode"])
@app.route("/box/unlocked",methods=["POST"])
def bunl():
    if S["status"]=="approved": setst("unlocked")
    return jsonify(ok=True)
@app.route("/box/delivered",methods=["POST"])
def bdel():
    d=request.get_json() or {}; S["weight"]=d.get("weight",0); S["photo"]=bool(d.get("photo",False)); setst("delivered")
    return jsonify(ok=True)
@app.route("/reset")
def reset():
    m=S["mode"]; S.update(fresh()); S["mode"]=m; return jsonify(ok=True)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
