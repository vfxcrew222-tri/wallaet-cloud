from flask import Flask, request, jsonify
import time, os
from datetime import datetime

app = Flask(__name__)

INTEGRATED = ["Amazon","Flipkart"]   # these = FLEX (auto). Others = MVP (owner approve)
CAP_COUNT = 4        # box holds up to 4 parcels
CAP_WEIGHT = 5000    # or up to 5 kg

def fresh():
    return {"mode":"mvp","status":"idle","partner_id":"","platform":"",
            "photo":False,"weight":0,"unit":"W-304","flat":"Flat 304",
            "parcels":[], "total":0, "last":time.time(), "last_photo_id":None, "last_photo_ids":[],
            "otp":"", "mismatch":False}
S = fresh()
PHOTOS = {}        # id -> (content_type, raw_bytes) : asli camera photos Pi se
_photo_seq = 0
def setst(x): S["status"]=x; S["last"]=time.time()

CSS = """
<meta name='viewport' content='width=device-width,initial-scale=1'>
<link href='https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap' rel='stylesheet'>
<style>
 :root{--gold:#C9A24B;--goldl:#E6C976;--bk:#0B0B0C;--pan:#16161A;--pan2:#1E1E24;--wh:#F4F1EA;--gr:#9A968C;--grn:#6FA07A;--red:#C0563F;--blu:#5B8DEF}
 *{box-sizing:border-box;margin:0;padding:0}
 body{font-family:'Sora',-apple-system,Segoe UI,Roboto,sans-serif;background:#000;color:var(--wh);min-height:100vh;display:flex;justify-content:center;align-items:flex-start}
 .phone{width:100%;max-width:430px;min-height:100vh;background:radial-gradient(circle at 50% -8%,#1a1a24,#0B0B0C 55%);position:relative;padding:0 0 30px;overflow:hidden}
 .nav{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;padding:16px 20px 14px;background:rgba(11,11,12,.9);backdrop-filter:blur(14px);border-bottom:1px solid #1e1e24}
 .nav .l{display:flex;align-items:center;gap:9px}
 .nav .dotL{width:9px;height:9px;border-radius:50%;background:var(--grn);box-shadow:0 0 8px var(--grn)}
 .nav .logo{font-size:17px;font-weight:800;letter-spacing:3px;color:var(--gold)}
 .nav .role{font-size:11px;color:var(--gr);margin-top:1px}
 .pill{padding:5px 13px;border-radius:20px;font-size:11px;font-weight:800;letter-spacing:.5px}
 .p-mvp{background:#2a2410;color:var(--gold)} .p-flex{background:#12261a;color:var(--grn)}
 .body{padding:20px}
 .lbl{font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:var(--gr);margin:16px 4px 8px;font-weight:600}
 .card{background:linear-gradient(160deg,#191920,#141418);border:1px solid #26262c;border-radius:20px;padding:22px;margin-bottom:16px;box-shadow:0 10px 40px rgba(0,0,0,.5)}
 .gold{border-color:rgba(201,162,75,.5)}
 input,select{width:100%;padding:15px;border-radius:12px;border:1px solid #2e2e36;background:#0c0c10;color:var(--wh);font-size:15px;font-family:inherit}
 input:focus,select:focus{outline:none;border-color:var(--gold)}
 button{width:100%;padding:16px;border:none;border-radius:14px;font-size:16px;font-weight:800;cursor:pointer;margin-top:14px;transition:.15s;font-family:inherit}
 button:active{transform:scale(.97)}
 .b-gold{background:linear-gradient(135deg,var(--goldl),var(--gold));color:#0B0B0C;box-shadow:0 8px 24px rgba(201,162,75,.25)}
 .b-grn{background:linear-gradient(135deg,#7FB98A,var(--grn));color:#04120a;box-shadow:0 8px 24px rgba(111,160,122,.3)}
 .b-red{background:#26262c;color:#e88;border:1px solid #402424} .b-dark{background:#1e1e24;color:var(--wh);border:1px solid #2e2e36}
 .hero{text-align:center;padding:26px 14px 18px}
 .hero .em{font-size:60px;filter:drop-shadow(0 6px 20px rgba(201,162,75,.35))}
 .hero .t{font-size:19px;font-weight:700;margin-top:12px} .hero .s{font-size:13px;color:var(--gr);margin-top:6px}
 .st{text-align:center;padding:30px 16px;border-radius:16px;background:#0c0c10;font-size:16px;border:1px solid #1e1e24}
 .st .em{font-size:44px;display:block;margin-bottom:12px}
 .big{font-size:52px;font-weight:800;color:var(--gold);line-height:1;letter-spacing:-1px}
 .muted{color:var(--gr);font-size:12.5px} .row{display:flex;gap:12px} .row>*{flex:1}
 .badge{display:inline-flex;align-items:center;gap:6px;background:#0c0c10;border:1px solid #2a2a30;padding:9px 14px;border-radius:12px;font-size:13px;margin:5px 5px 0 0;font-weight:600}
 .steps{display:flex;justify-content:space-between;align-items:center;margin:4px 0 20px;padding:0 6px}
 .dot{width:30px;height:30px;border-radius:50%;background:#1e1e24;color:var(--gr);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;border:2px solid #2a2a30;transition:.3s}
 .dot.on{background:var(--gold);color:#0B0B0C;border-color:var(--gold);box-shadow:0 0 16px rgba(201,162,75,.5);transform:scale(1.12)}
 .dot.done{background:var(--grn);color:#04120a;border-color:var(--grn)}
 .line{flex:1;height:3px;background:#1e1e24;margin:0 4px;border-radius:2px}
 .dcard{background:linear-gradient(160deg,#14211a,#0f1712);border:1px solid rgba(111,160,122,.4);border-left:4px solid var(--grn);border-radius:16px;padding:20px}
 .photo{height:130px;border-radius:14px;background:linear-gradient(135deg,#1a1a22,#12121a);border:1px dashed #33333a;display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--gr);font-size:13px;margin-top:14px;gap:6px}
 .modebox{font-size:12.5px;padding:13px 15px;border-radius:12px;margin-top:12px;line-height:1.5}
 .foot{text-align:center;color:#444;font-size:10px;margin-top:26px;letter-spacing:2px}
 a{color:var(--gold);text-decoration:none} .link-btn{display:block}
 #reader{border-radius:16px;overflow:hidden;border:2px solid var(--gold)}
 @keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
 @keyframes glow{0%,100%{box-shadow:0 0 0 0 rgba(111,160,122,.5)}50%{box-shadow:0 0 34px 8px rgba(111,160,122,.5)}}
 @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}
 @keyframes slideup{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
 .blink{animation:blink 1s infinite} .active{animation:glow 1.4s infinite;border-color:var(--grn)!important}
 .pulse{animation:pulse 1.5s infinite} .anim{animation:slideup .4s ease}
 .notif{background:linear-gradient(160deg,#14211a,#0f1712);border:1px solid var(--grn);border-radius:18px;padding:22px;text-align:center;animation:glow 1.4s infinite}
 .ring{width:96px;height:96px;border-radius:50%;border:3px solid #1e1e24;border-top-color:var(--gold);margin:0 auto 8px;animation:spin 1s linear infinite}
 @keyframes spin{to{transform:rotate(360deg)}}
 @keyframes shake{0%,100%{transform:rotate(0)}20%{transform:rotate(-18deg)}40%{transform:rotate(15deg)}60%{transform:rotate(-12deg)}80%{transform:rotate(8deg)}}
 .shake{animation:shake .6s ease-in-out infinite;transform-origin:top center}
</style>"""

def shell(role, body, js=""):
    return f"""{CSS}<div class='phone'>
    <div class='nav'><div class='l'><span class='dotL'></span><div><div class='logo'>WALLAET</div><div class='role'>{role}</div></div></div><span id='pill' class='pill'></span></div>
    <div class='body'>{body}<div class='foot'>SECURED DELIVERY RECEPTION</div></div></div>
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
    <div id='s0' class='card gold anim' style='text-align:center'>
      <div class='hero'><div class='em pulse'>📍</div><div class='t'>At the delivery address</div><div class='s'>Tap when you reach the customer's door</div></div>
      <button class='b-gold' onclick='reached()'>📍  Reached location</button>
    </div>
    <div id='s1' class='card gold anim' style='display:none;text-align:center'>
      <div class='hero'><div id='qricon' class='em'>🔳</div><div class='t'>Find the box</div><div class='s' id='scanhint'>Scan the Wallaet QR sticker on the box</div></div>
      <div id='reader' style='width:100%;display:none;margin-bottom:10px'></div>
      <button class='b-gold' onclick='scan()'>📷  Scan box QR</button>
      <button class='b-dark' onclick='manualScan()'>Enter code manually</button>
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
    async function otpYes(){await fetch('/courier/confirm',{method:'POST'});}
    async function otpNo(){await fetch('/courier/mismatch',{method:'POST'});}
    let cLast='';
    async function tick(){let s=await(await fetch('/state')).json();let el=document.getElementById('stt');
      if(s.status===cLast && s.status=='otp_sent'){return;}   // otp_sent: ek hi baar render (button tap safe)
      cLast=s.status;
      if(s.status=='requested'){dots(2);el.innerHTML=s.mode=='flex'?"<span class='em'>🔎</span>"+s.platform+" is verifying the order…":"<span class='em'>⏳</span>Owner approve kar raha — OTP bhej raha…";}
      else if(s.status=='otp_sent'){dots(2);el.innerHTML="<div style='font-size:13px;color:var(--gr);margin-bottom:10px'>Owner ne ye OTP bheja. Apne order ke OTP se milao:</div><div class='big' style='letter-spacing:8px;margin-bottom:14px'>"+s.otp+"</div><button class='b-grn' onclick='otpYes()'>✓ Match — box kholo</button><button class='b-red' onclick='otpNo()'>✗ Match nahi hua</button>";}
      else if(s.status=='approved'){dots(3);el.innerHTML="<span class='em'>✅</span>Verified! Box unlocking…";}
      else if(s.status=='unlocked'){dots(3);el.innerHTML="<span class='em'>🔓</span><b>Flap is OPEN</b><br>Drop the parcel now";}
      else if(s.status=='delivered'){dots(5);el.innerHTML="<span class='em'>📦</span><b>Delivered!</b><br>Thank you.<br><span class='muted'>Resetting…</span>";clearInterval(poll);setTimeout(()=>location.reload(),7000);}}"""
    return shell("Courier", "<script src='https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'></script>"+body, js)

@app.route("/owner")
def owner():
    body="""<div id='enable' class='card gold' style='text-align:center'>
      <div class='hero'><div class='em'>🔔</div><div class='t'>Enable alerts</div><div class='s'>Tap once so Wallaet can ring &amp; vibrate for deliveries</div></div>
      <button class='b-gold' onclick='enable()'>🔔  Enable sound &amp; vibration</button>
    </div>
    <div id='c'></div>"""
    js="""let last=null;let ac;let soundOn=false;
    function enable(){try{ac=new(window.AudioContext||window.webkitAudioContext)();let o=ac.createOscillator(),g=ac.createGain();o.connect(g);g.connect(ac.destination);g.gain.setValueAtTime(0.15,ac.currentTime);o.frequency.value=880;o.start();o.stop(ac.currentTime+0.15);}catch(e){}
      if(navigator.vibrate)navigator.vibrate(120);soundOn=true;document.getElementById('enable').style.display='none';}
    let ringTimer=null;
    function tone(seq){if(!soundOn||!ac)return;try{seq.forEach((n)=>{let o=ac.createOscillator(),g=ac.createGain();o.connect(g);g.connect(ac.destination);
      let t=ac.currentTime+n[2];o.frequency.setValueAtTime(n[0],t);g.gain.setValueAtTime(0.001,t);g.gain.exponentialRampToValueAtTime(0.5,t+0.02);g.gain.exponentialRampToValueAtTime(0.001,t+n[1]);o.start(t);o.stop(t+n[1]+0.03);});}catch(e){}}
    function bell(){tone([[880,0.14,0],[1320,0.3,0.14]]);}
    function success(){tone([[660,0.16,0],[880,0.16,0.16],[1320,0.4,0.32]]);}
    function ringHard(){bell();if(navigator.vibrate)navigator.vibrate([400,150,400]);}
    function startRing(){if(ringTimer)return;ringHard();ringTimer=setInterval(ringHard,1600);}
    function stopRing(){if(ringTimer){clearInterval(ringTimer);ringTimer=null;}}
    function plist(s){if(!s.parcels||!s.parcels.length)return"";let rows=s.parcels.map((p,i)=>"<div style='display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #1e1e24'><span>📦 "+(i+1)+" · "+p.platform+"<br><span class='muted' style='font-size:11px'>🕐 "+(p.t||"")+" · "+p.pid+"</span></span><span style='display:flex;align-items:center;gap:9px'>"+((p.photo_ids&&p.photo_ids.length)?"<span style='display:flex;gap:4px'>"+p.photo_ids.map(id=>"<img src='/box/photo/"+id+"' style='width:34px;height:34px;object-fit:cover;border-radius:7px;border:1px solid #2a2a30' onclick='window.open(this.src)'>").join("")+"</span>":(p.photo_id?"<img src='/box/photo/"+p.photo_id+"' style='width:34px;height:34px;object-fit:cover;border-radius:7px;border:1px solid #2a2a30' onclick='window.open(this.src)'>":""))+"<b style='color:var(--gold)'>"+p.w+" g</b></span></div>").join("");
      let full=s.full?"<div class='modebox' style='background:#2a1414;color:#e88;text-align:center;font-weight:700'>⚠️ BOX FULL — "+s.parcels.length+"/"+s.cap+" parcels. Please empty it.</div>":"";
      return "<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><b>📥 Box contents</b><span class='badge'>"+s.parcels.length+"/"+s.cap+" parcels</span></div>"+full+"<div style='margin-top:10px'>"+rows+"</div><div style='display:flex;justify-content:space-between;margin-top:14px'><span class='muted'>TOTAL WEIGHT</span><b class='big' style='font-size:30px'>"+s.total+" <span style='font-size:15px;color:var(--gr)'>g</span></b></div><button class='b-red' onclick='empty()'>🔓 Empty box (I collected)</button></div>";}
    function render(s){let c=document.getElementById('c');
      if(s.status=='idle'){
        if(s.parcels&&s.parcels.length)c.innerHTML="<div class='card'><div class='st'><span class='em'>✅</span><b>All delivered & secured</b><br><span class='muted'>Waiting for next courier…</span></div></div>"+plist(s);
        else c.innerHTML="<div class='card'><div class='st'><span class='em'>🏠</span><b>All quiet</b><br><span class='muted'>Waiting for a delivery…</span></div></div>";}
      else if(s.status=='reached')c.innerHTML="<div class='card'><div class='notif'><div style='font-size:40px'>📍🔔</div><b style='font-size:18px;color:var(--grn)'>Courier reached your address</b><br><span class='blink' style='color:var(--grn);font-weight:700'>● WALLAET ACTIVE</span><br><span class='muted'>Get ready — a delivery is starting</span></div></div>";
      else if(s.status=='scanned')c.innerHTML="<div class='card'><div class='st'><span class='em'>🔳</span><b>Courier at your box</b><br><span class='muted'>W-304 · identifying delivery…</span></div></div>";
      else if(s.status=='requested'){
        if(s.mode=='flex')c.innerHTML="<div class='card'><div class='st'><div class='ring'></div><b>"+s.platform+" delivery incoming</b><br><span class='muted'>Auto-verified by "+s.platform+" — no action needed</span></div></div>";
        else c.innerHTML="<div class='card' style='border:1px solid var(--gold);animation:glow 1s infinite'><div style='text-align:center'><span class='shake' style='font-size:56px;display:inline-block'>🔔</span><br><b style='font-size:20px;color:var(--gold)'>Delivery request!</b><br><span class='muted'>SMS wala OTP daal ke approve karo</span></div><div style='margin-top:16px;text-align:center'><span class='badge'>🛍️ "+s.platform+"</span><span class='badge'>🪪 "+s.partner_id+"</span></div>"+(s.mismatch?"<div class='modebox' style='background:#2a1414;color:#e88;text-align:center;margin-top:12px'>⚠️ Code mismatch — sahi OTP daalein</div>":"")+"<input id='otpIn' type='tel' maxlength='6' placeholder='SMS wala OTP' style='text-align:center;letter-spacing:5px;font-size:19px;margin-top:12px'><button class='b-grn' onclick='ok()'>✓ Approve & send OTP</button><button class='b-dark' onclick='ringHard()'>🔔 Ring again</button></div>";}
      else if(s.status=='otp_sent')c.innerHTML="<div class='card'><div class='st'><div class='ring'></div><b>OTP courier ko bhej diya</b><br><span class='muted'>Code <b style='color:var(--gold);letter-spacing:3px'>"+s.otp+"</b> · courier match confirm kar raha…</span></div></div>";
      else if(s.status=='approved'||s.status=='unlocked')c.innerHTML="<div class='card'><div class='st'><span class='em'>🔓</span><b>Approved</b><br><span class='muted'>Delivery in progress…</span></div></div>";
      else if(s.status=='delivered')c.innerHTML="<div class='card'><div class='dcard'><div style='display:flex;justify-content:space-between;align-items:center'><b style='color:var(--grn);font-size:16px'>📦 DELIVERED</b><span style='color:var(--grn);font-size:22px'>✓</span></div><div style='margin-top:12px'><span class='badge'>🛍️ "+s.platform+"</span><span class='badge'>🪪 "+s.partner_id+"</span></div><div style='margin-top:16px'><span class='muted'>THIS PARCEL</span><div class='big'>"+s.weight+" <span style='font-size:20px;color:var(--gr)'>g</span></div></div>"+((s.last_photo_ids&&s.last_photo_ids.length)?"<div class='lbl' style='margin-top:14px'>Delivery proof · "+s.last_photo_ids.length+" shots</div><div style='display:flex;gap:8px;overflow-x:auto;padding-bottom:4px'>"+s.last_photo_ids.map(id=>"<img src='/box/photo/"+id+"' style='height:170px;flex:0 0 auto;border-radius:12px;border:1px solid #2a2a30;object-fit:cover' onclick='window.open(this.src)'>").join("")+"</div>":(s.photo?"<div class='photo'><span style='font-size:30px'>📸</span>Delivery photo captured</div>":""))+"<div style='display:flex;justify-content:space-between;margin-top:14px;padding-top:12px;border-top:1px solid #1e1e24'><span class='muted'>Box now holds "+s.parcels.length+" parcel"+(s.parcels.length>1?"s":"")+"</span><b style='color:var(--gold)'>total "+s.total+" g</b></div></div></div>";}
    async function tick(){let s=await(await fetch('/state')).json();
      let key=s.status+'|'+s.partner_id+'|'+(s.parcels?s.parcels.length:0)+'|'+(s.last_photo_ids?s.last_photo_ids.length:0);
      if(key===last){return;}                  // nothing changed -> no redraw (kills flicker)
      let statusChanged = !last || last.split('|')[0]!==s.status;
      stopRing();                              // any change stops the ring loop
      if(statusChanged){
        if(s.status=='reached'){bell();if(navigator.vibrate)navigator.vibrate(250);}
        if(s.status=='requested'&&s.mode=='mvp')startRing();   // ring until approve
        if(s.status=='delivered'){success();setTimeout(()=>{fetch('/next');},5000);}
      }
      last=key;render(s);}
    async function ok(){stopRing();let el=document.getElementById('otpIn');let otp=el?(el.value||'').trim():'';if(!otp){alert('SMS wala OTP daalein');return;}let r=await(await fetch('/owner/approve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({otp:otp})})).json();if(!r.ok)alert(r.err||'OTP daalein');}
    async function empty(){await fetch('/reset');last='';}
    tick();setInterval(tick,1000);"""
    return shell("Owner · Flat 304", body, js)

@app.route("/box")
def box():
    body="""
    <div class='card gold'><div id='s' class='st'>&hellip;</div></div>
    <div class='card'><div class='lbl'>Box contents</div>
      <div style='display:flex;justify-content:space-between;align-items:center'><span class='muted'>Parcels inside</span><b id='cnt' style='color:var(--gold)'>0</b></div>
      <div style='display:flex;justify-content:space-between;align-items:center;margin-top:6px'><span class='muted'>Total weight</span><b id='tot' class='big' style='font-size:30px'>0 <span style='font-size:14px;color:var(--gr)'>g</span></b></div>
    </div>
    <div class='card'><div class='lbl'>Simulate a parcel drop</div>
      <button class='b-gold' onclick='drop(300)'>📦  Small parcel · 300 g</button>
      <button class='b-gold' onclick='drop(700)'>📦  Medium parcel · 700 g</button>
      <button class='b-gold' onclick='drop(1400)'>📦  Large parcel · 1400 g</button>
      <div class='muted' style='margin-top:10px'>Flap unlocks automatically once verified. Pick a size to simulate the parcel landing — weight adds to the box total.</div></div>"""
    js="""async function tick(){let s=await(await fetch('/state')).json();let el=document.getElementById('s');if(s.status!='reached')el.className='st';
      document.getElementById('cnt').textContent=s.parcels?s.parcels.length:0;
      document.getElementById('tot').innerHTML=(s.total||0)+" <span style='font-size:14px;color:var(--gr)'>g</span>";
      if(s.status=='idle')el.innerHTML="<span class='em'>🔒</span><b>STANDBY</b><br><span class='muted'>Box locked · monitoring</span>";
      else if(s.status=='reached'){el.className='st active';el.innerHTML="<span class='em blink'>🟢</span><b class='blink' style='color:var(--grn)'>WALLAET ACTIVE</b><br><span class='muted'>Light blinking · ready for courier</span>";}
      else if(s.status=='scanned')el.innerHTML="<span class='em'>🔦</span><b>IDENTIFIED · W-304</b><br><span class='muted'>Beep + light ON</span>";
      else if(s.status=='requested')el.innerHTML="<div class='ring'></div><b>VERIFYING…</b>";
      else if(s.status=='approved'){el.innerHTML="<span class='em'>🔓</span>UNLOCK received — opening flap";await fetch('/box/unlocked',{method:'POST'});}
      else if(s.status=='unlocked')el.innerHTML="<span class='em pulse'>🔓</span><b style='color:var(--grn)'>FLAP OPEN</b><br><span class='muted'>Waiting for parcel drop</span>";
      else if(s.status=='delivered')el.innerHTML="<span class='em'>✅</span><b style='color:var(--grn)'>DELIVERED</b><br><span class='muted'>"+s.weight+"g added · total "+s.total+"g · locked</span>";}
    async function drop(w){await fetch('/box/delivered',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({weight:w,photo:true})});}
    tick();setInterval(tick,1000);"""
    return shell("Box simulator", body, js)

@app.route("/state")
def state():
    d=dict(S); d["full"]=isfull(); d["cap"]=CAP_COUNT; return jsonify(d)
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
def aok():
    # MVP: owner SMS wala OTP type kare -> courier ko bheja jata (status=otp_sent),
    # courier match confirm kare tabhi approved. (firmware ke OTP flow jaisa)
    d=request.get_json() or {}
    otp="".join(ch for ch in str(d.get("otp","")) if ch.isdigit())[:6]
    if not otp:
        return jsonify(ok=False, err="SMS wala OTP daalein")
    S["otp"]=otp; S["mismatch"]=False
    setst("otp_sent")
    return jsonify(ok=True, otp=otp)
@app.route("/courier/confirm",methods=["POST"])
def cconfirm():
    # courier: OTP apne order se MATCH -> approved -> Pi unlock karega
    if S["status"]=="otp_sent": setst("approved")
    return jsonify(ok=True)
@app.route("/courier/mismatch",methods=["POST"])
def cmismatch():
    # courier: OTP match nahi -> owner ko wapas (sahi OTP bheje)
    S["otp"]=""; S["mismatch"]=True
    if S["status"]=="otp_sent": setst("requested")
    return jsonify(ok=True)
@app.route("/box/poll")
def bpoll(): return jsonify(command=("unlock" if S["status"]=="approved" else "none"),status=S["status"],mode=S["mode"])
@app.route("/box/unlocked",methods=["POST"])
def bunl():
    if S["status"]=="approved": setst("unlocked")
    S["last_photo_ids"]=[]; S["last_photo_id"]=None   # naya session -> purani session photos clear
    return jsonify(ok=True)
@app.route("/box/delivered",methods=["POST"])
def bdel():
    global _photo_seq
    import base64
    d=request.get_json() or {}; w=int(d.get("weight",0)); S["weight"]=w
    imgs=d.get("photos") or ([d["photo_b64"]] if d.get("photo_b64") else [])   # backward: POST me photos bheji ho
    for im in imgs:
        try:
            b64=im.split(",",1)[1] if im.startswith("data:") else im
            _photo_seq+=1; PHOTOS[_photo_seq]=("image/jpeg", base64.b64decode(b64))
            S.setdefault("last_photo_ids",[]).append(_photo_seq)
        except Exception:
            pass
    ids=list(S.get("last_photo_ids",[]))              # jo photos ab tak aayi (photo_add background se)
    S["photo"]=bool(ids) or bool(d.get("photo",False))
    S["last_photo_id"]=ids[-1] if ids else None
    S["parcels"].append({"platform":S["platform"],"pid":S["partner_id"],"w":w,"t":datetime.now().strftime("%I:%M %p"),"photo_id":(ids[-1] if ids else None),"photo_ids":ids})
    S["total"]=sum(p["w"] for p in S["parcels"])
    setst("delivered")
    return jsonify(ok=True, total=S["total"], count=len(S["parcels"]), full=isfull())
@app.route("/box/photo_add",methods=["POST"])
def bphotoadd():
    # v67: delivery ke dauraan ek-ek photo background me aati - store + current session/parcel se jodo
    global _photo_seq
    import base64
    d=request.get_json() or {}; im=d.get("img") or ""
    if not im: return jsonify(ok=False)
    try:
        b64=im.split(",",1)[1] if im.startswith("data:") else im
        _photo_seq+=1; PHOTOS[_photo_seq]=("image/jpeg", base64.b64decode(b64))
        S.setdefault("last_photo_ids",[]).append(_photo_seq)
        S["last_photo_id"]=_photo_seq; S["photo"]=True
        if S["parcels"]:
            S["parcels"][-1].setdefault("photo_ids",[]).append(_photo_seq)
            S["parcels"][-1]["photo_id"]=_photo_seq
        return jsonify(ok=True, id=_photo_seq)
    except Exception:
        return jsonify(ok=False)
@app.route("/box/photo/<int:pid>")
def bphoto(pid):
    p=PHOTOS.get(pid)
    if not p: return ("",404)
    return app.response_class(p[1], mimetype=p[0], headers={"Cache-Control":"max-age=86400"})
def isfull():
    return len(S["parcels"])>=CAP_COUNT or S["total"]>=CAP_WEIGHT
@app.route("/full")
def full(): return jsonify(full=isfull(), count=len(S["parcels"]), cap=CAP_COUNT, total=S["total"], capw=CAP_WEIGHT)
@app.route("/next")
def nxt():
    # ready for the next courier — keep parcels, clear only the current transaction
    S["status"]="idle"; S["partner_id"]=""; S["platform"]=""; S["weight"]=0; S["photo"]=False; S["last_photo_id"]=None; S["last_photo_ids"]=[]; S["otp"]=""; S["mismatch"]=False; S["mode"]="mvp"; S["last"]=time.time()
    return jsonify(ok=True)
@app.route("/reset")
def reset(): S.update(fresh()); PHOTOS.clear(); return jsonify(ok=True)

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
