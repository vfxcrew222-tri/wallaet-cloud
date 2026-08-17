from flask import Flask, request, jsonify, render_template_string
import time, os

app = Flask(__name__)

# ---- simple in-memory state (ek delivery session) ----
state = {
    "status": "idle",        # idle -> requested -> approved -> unlocked -> delivered
    "courier": "",
    "partner_id": "",
    "platform": "",
    "otp_needed": False,
    "photo": "",
    "weight": 0,
    "last_update": time.time(),
}

def set_status(s):
    state["status"] = s
    state["last_update"] = time.time()

# ============ COURIER PAGE ============
COURIER_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wallaet Courier</title></head>
<body style="font-family:sans-serif;background:#0b0b0c;color:#f4f1ea;text-align:center;padding:20px;max-width:420px;margin:auto">
<h2 style="color:#c9a24b">WALLAET</h2>
<p style="color:#9a968c">Courier Delivery</p>
<div id="box" style="background:#16161a;border:1px solid #c9a24b;border-radius:10px;padding:20px;margin:16px 0">
  <div id="step1">
    <p>Delivery Partner ID (required):</p>
    <input id="pid" style="padding:10px;width:80%;border-radius:6px;border:none" placeholder="e.g. AMZ-DEL-48213">
    <br><br>
    <button onclick="requestOtp()" style="background:#c9a24b;color:#0b0b0c;border:none;padding:12px 24px;border-radius:6px;font-weight:bold">Request Delivery</button>
  </div>
  <div id="status" style="margin-top:16px;color:#c9a24b"></div>
</div>
<script>
async function requestOtp(){
  let pid=document.getElementById('pid').value;
  if(pid.length<2){alert('Enter Partner ID');return;}
  let r=await fetch('/courier/request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({partner_id:pid})});
  document.getElementById('step1').style.display='none';
  poll();
}
async function poll(){
  let r=await fetch('/state'); let s=await r.json();
  let el=document.getElementById('status');
  if(s.status=='requested') el.innerHTML='⏳ Waiting for owner approval...';
  else if(s.status=='approved') el.innerHTML='✅ Approved! Box unlocking...';
  else if(s.status=='unlocked') el.innerHTML='🔓 Flap OPEN — drop the parcel now';
  else if(s.status=='delivered') el.innerHTML='📦 Delivered! Thank you. ✓';
  if(s.status!='delivered') setTimeout(poll,1500);
}
</script>
</body></html>
"""

# ============ OWNER PAGE ============
OWNER_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wallaet Owner</title></head>
<body style="font-family:sans-serif;background:#0b0b0c;color:#f4f1ea;text-align:center;padding:20px;max-width:420px;margin:auto">
<h2 style="color:#c9a24b">WALLAET</h2>
<p style="color:#9a968c">Owner App</p>
<div id="box" style="background:#16161a;border:1px solid #c9a24b;border-radius:10px;padding:20px;margin:16px 0;min-height:120px">
  <div id="content" style="color:#9a968c">Waiting for delivery...</div>
</div>
<script>
async function poll(){
  let r=await fetch('/state'); let s=await r.json();
  let c=document.getElementById('content');
  if(s.status=='idle') c.innerHTML='<span style="color:#9a968c">Waiting for delivery...</span>';
  else if(s.status=='requested') c.innerHTML='🔔 <b>Courier at your box!</b><br>Partner ID: '+s.partner_id+'<br><br><button onclick="approve()" style="background:#6fa07a;color:#fff;border:none;padding:12px 28px;border-radius:6px;font-weight:bold">APPROVE</button>';
  else if(s.status=='approved'||s.status=='unlocked') c.innerHTML='✅ Approved — delivery in progress...';
  else if(s.status=='delivered') c.innerHTML='📦 <b>Delivered!</b><br>Partner ID: '+s.partner_id+'<br>Weight: '+s.weight+'g'+(s.photo?'<br>📸 Photo captured':'');
  setTimeout(poll,1500);
}
async function approve(){ await fetch('/owner/approve',{method:'POST'}); }
poll();
</script>
</body></html>
"""

@app.route("/")
def home():
    return '<body style="font-family:sans-serif;background:#0b0b0c;color:#c9a24b;text-align:center;padding:50px"><h1>WALLAET CLOUD ✅</h1><p style="color:#f4f1ea"><a href="/courier" style="color:#c9a24b">Courier page</a> &nbsp;|&nbsp; <a href="/owner" style="color:#c9a24b">Owner page</a></p></body>'

@app.route("/courier")
def courier(): return render_template_string(COURIER_HTML)

@app.route("/owner")
def owner(): return render_template_string(OWNER_HTML)

@app.route("/state")
def get_state(): return jsonify(state)

# courier requests delivery
@app.route("/courier/request", methods=["POST"])
def courier_request():
    d = request.get_json() or {}
    state["partner_id"] = d.get("partner_id","")
    set_status("requested")
    return jsonify(ok=True)

# owner approves
@app.route("/owner/approve", methods=["POST"])
def owner_approve():
    set_status("approved")
    return jsonify(ok=True)

# ============ BOX / PI endpoints ============
# Pi polls this to get command
@app.route("/box/poll")
def box_poll():
    # tell Pi what to do
    cmd = "none"
    if state["status"] == "approved":
        cmd = "unlock"
    return jsonify(command=cmd, status=state["status"])

# Pi confirms it unlocked
@app.route("/box/unlocked", methods=["POST"])
def box_unlocked():
    set_status("unlocked")
    return jsonify(ok=True)

# Pi reports delivery (weight detected + photo)
@app.route("/box/delivered", methods=["POST"])
def box_delivered():
    d = request.get_json() or {}
    state["weight"] = d.get("weight", 0)
    state["photo"] = d.get("photo", "captured")
    set_status("delivered")
    return jsonify(ok=True)

# reset for next demo
@app.route("/reset")
def reset():
    for k in ["status","courier","partner_id","platform","photo"]:
        state[k] = "" if k!="status" else "idle"
    state["weight"]=0; state["otp_needed"]=False
    set_status("idle")
    return jsonify(ok=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
