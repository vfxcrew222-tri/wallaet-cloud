from flask import Flask, request, jsonify
import time, os

app = Flask(__name__)

INTEGRATED = ["Amazon","Flipkart"]   # these = FLEX (auto). Others = MVP (owner approve)

def fresh():
    return {"mode":"mvp","status":"idle","partner_id":"","platform":"",
            "photo":False,"weight":0,"unit":"W-304","flat":"Flat 304","last":time.time()}
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
 .logo{font-size:22px;font-weight:800;letter-spacing:3px;color:var(--gold)} .role{font-size:12px;color:var(--gr)}
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
 .dot{width:24px;height:24px;border-radius:50%;background:#26262c;color:var(--gr);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800}
 .dot.on{background:var(--gold);color:#0B0B0C} .dot.done{background:var(--grn);color:#fff}
 .line{flex:1;height:2px;background:#26262c;margin:11px 2px 0}
 .dcard{border-left:4px solid var(--grn);background:var(--pan2);border-radius:10px;padding:14px;margin-top:12px}
 .photo{height:120px;border-radius:10px;background:repeating-linear-gradient(45deg,#1a1a20,#1a1a20 10px,#15151a 10px,#15151a 20px);display:flex;align-items:center;justify-content:center;color:var(--gr);font-size:13px;margin-top:10px}
 a{color:var(--gold);text-decoration:none} .link-btn{display:block;margin-top:10px}
 .modebox{font-size:12px;padding:10px;border-radius:8px;margin-top:8px}
 .footer{text-align:center;color:#555;font-size:11px;margin-top:20px;letter-spacing:2px}
 @keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}
 @keyframes glow{0%,100%{box-shadow:0 0 0 0 rgba(111,160,122,.5)}50%{box-shadow:0 0 30px 6px rgba(111,160,122,.55)}}
 .blink{animation:blink 1s infinite} .active{animation:glow 1.4s infinite;border-color:var(--grn)!important}
 .notif{background:#12261a;border:1px solid var(--grn);border-radius:12px;padding:16px;text-align:center;animation:glow 1.4s infinite}
</style>"""

def shell(role, body, js=""):
    return f"""{CSS}<div class='wrap'>
    <div class='hdr'><div><div class='logo'>WALLAET</div><div class='role'>{role}</div></div><span id='pill' class='pill'></span></div>
    {body}<div class='footer'>SECURED DELIVERY RECEPTION</div></div>
    <script>
    async function _mode(){{try{{let s=await(await fetch('/state')).json();let p=document.getElementById('pill');
      if(p){{if(s.status=='idle'){{p.className='pill';p.textContent='';}}else{{p.className='pill '+(s.mode=='mvp'?'p-mvp':'p-flex');p.textContent=(s.mode=='mvp'?'MVP':'FLEX');}}}}}}catch(e){{}}}}
    _mode();setInterval(_mode,2000);
    {js}</script>"""

@app.route("/")
def home():
    return LANDING

@app.route("/demo")
def demo():
    body="""
    <div class='card gold'>
      <div class='lbl'>Open on different phones / networks</div>
      <a class='link-btn' href='/courier'><button class='b-gold'>📦  Courier screen</button></a>
      <a class='link-btn' href='/owner'><button class='b-dark'>🏠  Owner app</button></a>
      <a class='link-btn' href='/box'><button class='b-dark'>📡  Box simulator (demo without Pi)</button></a>
    </div>
    <div class='card'>
      <div class='lbl'>How the mode is decided</div>
      <div class='modebox' style='background:#12261a;color:var(--grn)'><b>FLEX (auto-verify)</b> — Amazon, Flipkart. Platform is integrated, box auto-opens. No owner action.</div>
      <div class='modebox' style='background:#2a2410;color:var(--gold)'><b>MVP (owner approves)</b> — Meesho & others. Not integrated, so the owner approves the delivery.</div>
      <div class='muted' style='margin-top:10px;text-align:center'>The courier just picks the platform — Wallaet decides the mode automatically.</div>
      <button class='b-red' onclick="fetch('/reset').then(()=>location.reload())">↺  Reset demo</button>
    </div>"""
    return shell("Live demo", body)

@app.route("/courier")
def courier():
    body="""
    <div id='s0' class='card gold' style='text-align:center'>
      <div class='lbl'>Step 1 · At the address</div>
      <div style='font-size:60px;margin:12px 0'>📍</div>
      <div class='muted' style='margin-bottom:6px'>You've reached the delivery address. Tap to notify the customer.</div>
      <button class='b-gold' onclick='reached()'>📍  Reached location</button>
    </div>
    <div id='s1' class='card gold' style='display:none;text-align:center'>
      <div class='lbl'>Step 2 · Find the box</div>
      <div id='qricon' style='font-size:56px;margin:12px 0'>🔳</div>
      <div id='reader' style='width:100%;border-radius:12px;overflow:hidden;display:none'></div>
      <div class='muted' style='margin:8px 0 6px' id='scanhint'>Scan the Wallaet QR sticker on the box.</div>
      <button class='b-gold' onclick='scan()'>📷  Scan box QR</button>
      <button class='b-dark' onclick='manualScan()' style='margin-top:8px'>Enter code manually</button>
    </div>
    <div id='s2' class='card gold' style='display:none'>
      <div class='st' style='margin-bottom:12px'>✅ Box: <b style='color:var(--gold)'>W-304</b> · <span class='muted'>Flat 304</span></div>
      <div class='lbl'>Step 3 · Platform</div>
      <select id='plat' onchange='modeHint()'>
        <option value='Amazon'>Amazon — Integrated (FLEX)</option>
        <option value='Flipkart'>Flipkart — Integrated (FLEX)</option>
        <option value='Meesho'>Meesho — Standard (MVP)</option>
        <option value='Ajio'>Ajio — Standard (MVP)</option>
        <option value='JioMart'>JioMart — Standard (MVP)</option>
        <option value='Blinkit'>Blinkit — Standard (MVP)</option>
      </select>
      <div id='mh' class='modebox'></div>
      <div class='lbl'>Delivery Partner ID (required)</div>
      <input id='pid' placeholder='e.g. AMZ-DEL-48213'>
      <button class='b-gold' onclick='req()'>Request Delivery</button>
      <div class='muted' style='margin-top:10px'>Box limit 40x35x40 cm. Larger parcel &rarr; normal doorstep delivery.</div>
    </div>
    <div id='s3' class='card' style='display:none'>
      <div class='steps'><div id='d1' class='dot'>1</div><div class='line'></div><div id='d2' class='dot'>2</div><div class='line'></div><div id='d3' class='dot'>3</div><div class='line'></div><div id='d4' class='dot'>4</div></div>
      <div id='stt' class='st'>&hellip;</div>
    </div>"""
    js="""let poll;const INTEG=['Amazon','Flipkart'];
    async function reached(){await fetch('/courier/reached',{method:'POST'});document.getElementById('s0').style.display='none';document.getElementById('s1').style.display='block';}
    function goForm(){fetch('/courier/scan',{method:'POST'});document.getElementById('s1').style.display='none';document.getElementById('s2').style.display='block';modeHint();}
    function manualScan(){goForm();}
    let qr;
    function scan(){
      document.getElementById('qricon').style.display='none';
      document.getElementById('reader').style.display='block';
      document.getElementById('scanhint').textContent='Point the camera at the Wallaet QR…';
      if(typeof Html5Qrcode==='undefined'){document.getElementById('scanhint').textContent='Scanner not loaded — use manual.';return;}
      qr=new Html5Qrcode('reader');
      qr.start({facingMode:'environment'},{fps:10,qrbox:220},
        (txt)=>{qr.stop().then(()=>{goForm();});},
        ()=>{}
      ).catch(e=>{document.getElementById('scanhint').textContent='Camera unavailable — tap “Enter code manually”.';});
    }
    function modeHint(){let p=document.getElementById('plat').value;let m=document.getElementById('mh');
      if(INTEG.includes(p)){m.style.background='#12261a';m.style.color='#6FA07A';m.innerHTML='<b>FLEX</b> — '+p+' is integrated. Box will auto-verify & open (no owner approval).';}
      else{m.style.background='#2a2410';m.style.color='#C9A24B';m.innerHTML='<b>MVP</b> — '+p+' not integrated. The owner will approve this delivery.';}}
    async function req(){let pid=document.getElementById('pid').value,plat=document.getElementById('plat').value;
      if(pid.trim().length<3){alert('Enter Delivery Partner ID');return;}
      await fetch('/courier/request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({partner_id:pid,platform:plat})});
      document.getElementById('s2').style.display='none';document.getElementById('s3').style.display='block';poll=setInterval(tick,1000);tick();}
    function dots(n){for(let i=1;i<=4;i++){let d=document.getElementById('d'+i);d.className='dot'+(i<n?' done':i==n?' on':'');d.innerHTML=i<n?'✓':i;}}
    async function tick(){let s=await(await fetch('/state')).json();let el=document.getElementById('stt');
      if(s.status=='requested'){dots(2);el.innerHTML=s.mode=='flex'?"<span class='em'>🔎</span>"+s.platform+" is verifying the order…":"<span class='em'>⏳</span>Waiting for owner approval…";}
      else if(s.status=='approved'){dots(3);el.innerHTML="<span class='em'>✅</span>Verified! Box unlocking…";}
      else if(s.status=='unlocked'){dots(3);el.innerHTML="<span class='em'>🔓</span><b>Flap is OPEN</b><br>Drop the parcel now";}
      else if(s.status=='delivered'){dots(5);el.innerHTML="<span class='em'>📦</span><b>Delivered!</b><br>Thank you.";clearInterval(poll);}}"""
    return shell("Courier", "<script src='https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'></script>"+body, js)

@app.route("/owner")
def owner():
    body="<div class='card'><div id='c'></div></div>"
    js="""async function tick(){let s=await(await fetch('/state')).json();let c=document.getElementById('c');
      if(s.status=='idle')c.innerHTML="<div class='st'><span class='em'>🏠</span>Waiting for a delivery…</div>";
      else if(s.status=='reached')c.innerHTML="<div class='notif'><div style='font-size:40px'>📍🔔</div><b style='font-size:18px;color:var(--grn)'>Courier reached your address</b><br><span class='blink' style='color:var(--grn);font-weight:700'>● WALLAET ACTIVE</span><br><span class='muted'>Get ready — a delivery is starting</span></div>";
      else if(s.status=='scanned')c.innerHTML="<div class='st'><span class='em'>🔳</span><b>Courier at your box</b><br><span class='muted'>W-304 · identifying delivery…</span></div>";
      else if(s.status=='requested'){
        if(s.mode=='flex')c.innerHTML="<div class='st'><span class='em'>🔎</span><b>"+s.platform+" delivery incoming</b><br><span class='muted'>Verified by "+s.platform+" — no action needed</span></div>";
        else c.innerHTML="<div class='st'><span class='em'>🔔</span><b>Approve this delivery?</b></div><div style='margin-top:10px'><span class='badge'>🛍️ "+s.platform+"</span><span class='badge'>🪪 "+s.partner_id+"</span></div><button class='b-grn' onclick='ok()'>APPROVE DELIVERY</button>";}
      else if(s.status=='approved'||s.status=='unlocked')c.innerHTML="<div class='st'><span class='em'>✅</span>Approved — delivery in progress…</div>";
      else if(s.status=='delivered')c.innerHTML="<div class='dcard'><b style='color:var(--grn)'>📦 DELIVERED ✓</b><div style='margin-top:8px'><span class='badge'>🛍️ "+s.platform+"</span><span class='badge'>🪪 "+s.partner_id+"</span></div><div style='margin-top:12px'><span class='muted'>Weight captured</span><div class='big'>"+s.weight+" <span style='font-size:18px'>g</span></div></div>"+(s.photo?"<div class='photo'>📸 Delivery photo captured</div>":"")+"</div>";}
    async function ok(){await fetch('/owner/approve',{method:'POST'});}
    tick();setInterval(tick,1000);"""
    return shell("Owner · Flat 304", body, js)

@app.route("/box")
def box():
    body="""
    <div class='card gold'><div id='s' class='st'>&hellip;</div></div>
    <div class='card'><div class='lbl'>Simulate the box hardware</div>
      <button class='b-gold' onclick='drop()'>📦  Parcel dropped (weight + photo)</button>
      <div class='muted' style='margin-top:10px'>Flap unlocks automatically once a delivery is verified. Then tap above to simulate the parcel landing.</div></div>"""
    js="""async function tick(){let s=await(await fetch('/state')).json();let el=document.getElementById('s');if(s.status!='reached')el.className='st';
      if(s.status=='idle')el.innerHTML="<span class='em'>😴</span>Standby — locked";
      else if(s.status=='reached'){el.className='st active';el.innerHTML="<span class='em blink'>🟢</span><b class='blink' style='color:var(--grn)'>WALLAET ACTIVE</b><br><span class='muted'>Light blinking · ready for courier</span>";}
      else if(s.status=='scanned')el.innerHTML="<span class='em'>🔦</span>Scanned — beep + light ON";
      else if(s.status=='requested')el.innerHTML="<span class='em'>⏳</span>Verification in progress…";
      else if(s.status=='approved'){el.innerHTML="<span class='em'>🔓</span>UNLOCK received — opening flap";await fetch('/box/unlocked',{method:'POST'});}
      else if(s.status=='unlocked')el.innerHTML="<span class='em'>🔓</span>FLAP OPEN — waiting for drop";
      else if(s.status=='delivered')el.innerHTML="<span class='em'>✅</span>Delivered — locked again";}
    async function drop(){await fetch('/box/delivered',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({weight:640,photo:true})});}
    tick();setInterval(tick,1000);"""
    return shell("Box simulator", body, js)

@app.route("/state")
def state(): return jsonify(S)
@app.route("/courier/reached",methods=["POST"])
def creach():
    if S["status"]=="idle": setst("reached")
    return jsonify(ok=True)
@app.route("/courier/scan",methods=["POST"])
def cscan():
    if S["status"] in ("idle","reached"): setst("scanned")
    return jsonify(ok=True,unit=S["unit"])
@app.route("/courier/request",methods=["POST"])
def creq():
    d=request.get_json() or {}; S["partner_id"]=d.get("partner_id",""); S["platform"]=d.get("platform","")
    S["mode"] = "flex" if S["platform"] in INTEGRATED else "mvp"   # platform decides mode
    setst("requested")
    if S["mode"]=="flex": setst("approved")
    return jsonify(ok=True,mode=S["mode"])
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
def reset(): S.update(fresh()); return jsonify(ok=True)

LANDING = """
<!doctype html><html><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Wallaet — secured delivery reception</title>
<style>
 :root{--gold:#C9A24B;--goldl:#E6C976;--bk:#0B0B0C;--pan:#16161A;--pan2:#1E1E24;--wh:#F4F1EA;--gr:#9A968C;--grn:#6FA07A}
 *{box-sizing:border-box;margin:0;padding:0}
 body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bk);color:var(--wh);line-height:1.5}
 .bar{position:sticky;top:0;z-index:9;display:flex;justify-content:space-between;align-items:center;padding:16px 22px;background:rgba(11,11,12,.85);backdrop-filter:blur(10px);border-bottom:1px solid #1e1e24}
 .logo{font-size:20px;font-weight:800;letter-spacing:4px;color:var(--gold)}
 .bar a{color:var(--bk);background:var(--gold);text-decoration:none;padding:9px 18px;border-radius:10px;font-weight:800;font-size:14px}
 .hero{text-align:center;padding:90px 22px 70px;background:radial-gradient(circle at 50% 0%,#1c1c24,#0B0B0C 70%);position:relative;overflow:hidden}
 .hero:before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,var(--gold),transparent)}
 .tag{display:inline-block;border:1px solid var(--gold);color:var(--goldl);padding:6px 16px;border-radius:20px;font-size:12px;letter-spacing:2px;margin-bottom:26px}
 h1{font-size:56px;font-weight:800;letter-spacing:3px;color:var(--gold);margin-bottom:18px}
 .hero p{font-size:20px;color:var(--wh);max-width:620px;margin:0 auto 12px}
 .hero .sub{font-size:15px;color:var(--gr);max-width:600px;margin:0 auto 34px}
 .cta{display:inline-block;background:linear-gradient(135deg,var(--goldl),var(--gold));color:var(--bk);text-decoration:none;padding:16px 40px;border-radius:12px;font-weight:800;font-size:17px;box-shadow:0 10px 40px rgba(201,162,75,.3)}
 .cta.dark{background:#1e1e24;color:var(--wh);border:1px solid #33333a;box-shadow:none;margin-left:10px}
 .wrap{max-width:1000px;margin:auto;padding:0 22px}
 .sec{padding:64px 0} .sec h2{font-size:32px;color:var(--wh);text-align:center;margin-bottom:8px}
 .sec .lead{text-align:center;color:var(--gr);max-width:640px;margin:0 auto 44px;font-size:15px}
 .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}
 .card{background:var(--pan);border:1px solid #26262c;border-radius:16px;padding:26px}
 .card .em{font-size:30px;margin-bottom:12px}
 .card h3{color:var(--gold);font-size:18px;margin-bottom:8px} .card p{color:var(--wh);font-size:13.5px}
 .steps{counter-reset:s} .step{display:flex;gap:18px;align-items:flex-start;padding:16px 0;border-bottom:1px solid #1e1e24}
 .step .n{flex:0 0 42px;height:42px;border-radius:50%;background:var(--gold);color:var(--bk);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px}
 .step h4{color:var(--wh);font-size:17px;margin-bottom:3px} .step p{color:var(--gr);font-size:14px}
 .demo{background:linear-gradient(135deg,#16161a,#0f0f12);border:1px solid var(--gold);border-radius:20px;padding:44px 30px;text-align:center}
 .demo h2{color:var(--gold)} .demo p{color:var(--gr);margin-bottom:28px}
 .dbtns{display:flex;flex-wrap:wrap;gap:14px;justify-content:center}
 .dbtn{background:var(--bk);border:1px solid #33333a;border-radius:14px;padding:20px 26px;text-decoration:none;color:var(--wh);min-width:180px;transition:.15s}
 .dbtn:hover{border-color:var(--gold);transform:translateY(-2px)}
 .dbtn .e{font-size:32px;display:block;margin-bottom:8px} .dbtn b{color:var(--gold);display:block;font-size:15px} .dbtn span{font-size:12px;color:var(--gr)}
 .stat{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:18px;text-align:center}
 .stat .b{font-size:38px;font-weight:800;color:var(--gold)} .stat .l{font-size:13px;color:var(--gr)}
 .foot{text-align:center;padding:40px 22px;color:#555;font-size:12px;letter-spacing:2px;border-top:1px solid #1e1e24}
 @media(max-width:600px){h1{font-size:38px}.hero p{font-size:17px}.cta.dark{margin-left:0;margin-top:10px}}
</style></head><body>
<div class='bar'><div class='logo'>WALLAET</div><a href='/demo'>Live demo →</a></div>

<div class='hero'>
  <div class='tag'>SECURED DELIVERY RECEPTION</div>
  <h1>WALLAET</h1>
  <p>Your parcel is safe — until it reaches you.</p>
  <p class='sub'>A smart box at your door that opens only for a verified delivery, records proof, and locks itself again. The reception layer every platform can plug into.</p>
  <a class='cta' href='/demo'>Try the live demo</a>
  <a class='cta dark' href='#how'>See how it works</a>
</div>

<div class='wrap'>
  <div class='sec'>
    <h2>The last step is broken</h2>
    <p class='lead'>Online orders are tracked every step — until the last one. Then it's dropped at the door with no lock, no check, no proof.</p>
    <div class='grid'>
      <div class='card'><div class='em'>🚪</div><h3>Stolen from the door</h3><p>Parcels left outside get taken. It happens every day, everywhere.</p></div>
      <div class='card'><div class='em'>🔁</div><h3>Failed delivery</h3><p>Nobody home → courier takes it back → comes again tomorrow. Wasted trip and cost.</p></div>
      <div class='card'><div class='em'>🔑</div><h3>The OTP problem</h3><p>You're told never to share your code — yet couriers still ask by phone.</p></div>
      <div class='card'><div class='em'>❓</div><h3>No proof</h3><p>Was it delivered? Who took it? Disputes with zero evidence.</p></div>
    </div>
  </div>

  <div class='sec' id='how'>
    <h2>How Wallaet works</h2>
    <p class='lead'>Five simple steps — from the courier reaching your door to a locked, proof-recorded delivery.</p>
    <div class='steps'>
      <div class='step'><div class='n'>1</div><div><h4>Courier reaches</h4><p>The courier taps “reached” in their app. You're notified and the box wakes up — light on, ready.</p></div></div>
      <div class='step'><div class='n'>2</div><div><h4>Scans the box</h4><p>The courier scans the Wallaet QR on your box — it's identified as yours.</p></div></div>
      <div class='step'><div class='n'>3</div><div><h4>Verified</h4><p>Amazon &amp; Flipkart auto-verify (no action needed). Others: you approve with one tap.</p></div></div>
      <div class='step'><div class='n'>4</div><div><h4>Opens &amp; records</h4><p>The box opens only now. Parcel drops in; weight and a photo are captured as proof.</p></div></div>
      <div class='step'><div class='n'>5</div><div><h4>Locks itself</h4><p>The flap closes and locks. Secured, and ready for the next one.</p></div></div>
    </div>
  </div>

  <div class='sec'>
    <h2>The cost it kills</h2>
    <p class='lead'>Failed deliveries are a silent, massive drain on Indian e-commerce.</p>
    <div class='stat'>
      <div><div class='b'>23%</div><div class='l'>deliveries fail the first time</div></div>
      <div><div class='b'>₹180-400</div><div class='l'>lost per failed delivery</div></div>
      <div><div class='b'>₹8,000 Cr</div><div class='l'>lost every year in India</div></div>
      <div><div class='b'>₹50,000 Cr</div><div class='l'>home-delivery market</div></div>
    </div>
  </div>

  <div class='sec'>
    <div class='demo'>
      <h2>See it live</h2>
      <p>Open these on separate phones — scan a real QR, watch the box unlock, see the proof.</p>
      <div class='dbtns'>
        <a class='dbtn' href='/courier'><span class='e'>📦</span><b>Courier</b><span>reach · scan · deliver</span></a>
        <a class='dbtn' href='/owner'><span class='e'>🏠</span><b>Owner</b><span>alerts · approve · proof</span></a>
        <a class='dbtn' href='/box'><span class='e'>📡</span><b>Box</b><span>the live box (demo)</span></a>
      </div>
    </div>
  </div>
</div>

<div class='foot'>WALLAET · Secured delivery reception · Patents filed · Nitin Jain (Ni3)</div>
</body></html>"""

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
