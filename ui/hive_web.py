"""Hive Web Interface
FastAPI application exposing dialogue & manual trade endpoints.
Non-intrusive: does not stop autonomous engine.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any
import re

from config.enhanced_task_config import get_enhanced_task_config, TradeParameters
from config.narration_logger import get_narration_logger
from foundation.rick_charter import RickCharter
from execution.order_router import ManualTrade, place_trade

PIN = "841921"
app = FastAPI(title="RICK ↔ Hive Web Interface", version="1.0")

cfg = get_enhanced_task_config()
logger = get_narration_logger()

# ----------------- Models -----------------
class DialogueRequest(BaseModel):
    message: str
    override: bool = False
    apply_suggestions: bool = True
    pin: str | None = None

class DialogueResponse(BaseModel):
    parsed: Dict[str, Any]
    plan: str | None
    charter_ok: bool
    charter_reason: str
    suggestions: Dict[str, Any]
    executed: bool = False

# ----------------- Helpers -----------------
execute_pattern = re.compile(r"^(place trade|make position|execute trade).*841921", re.I)

def looks_execute(msg: str) -> bool:
    return bool(execute_pattern.search(msg.strip()))

def extract_parameters_text(msg: str) -> str:
    if "841921" in msg:
        return msg[: msg.lower().rfind("841921")].strip()
    return msg

# Charter validation (same logic as terminal, simplified)

def charter_validate(parsed: Dict) -> tuple[bool, str, Dict]:
    suggestions = {}
    qty = float(parsed.get("quantity", 10000) or 0)
    ep = parsed.get("entry_price")
    stop = parsed.get("stop_loss")
    tp = parsed.get("take_profit")
    direction = parsed.get("direction","buy").lower()
    notional_price = ep if ep else 1.0
    notional = qty * notional_price

    if qty <= 0:
        suggestions["quantity"] = 10000
        return False, "Quantity must be > 0", suggestions

    if notional < RickCharter.MIN_NOTIONAL_USD:
        needed = int((RickCharter.MIN_NOTIONAL_USD / notional_price) + 0.5)
        suggestions["quantity"] = needed
        suggestions["reason_notional"] = f"Increase quantity to {needed}" \
            f" for notional >= ${RickCharter.MIN_NOTIONAL_USD}."

    if ep and stop and tp:
        try:
            entry = float(ep); sl = float(stop); target = float(tp)
            if direction == "buy":
                risk = entry - sl; reward = target - entry
            else:
                risk = sl - entry; reward = entry - target
            if risk > 0:
                rr = reward / risk
                if rr < RickCharter.MIN_RISK_REWARD_RATIO:
                    needed_reward = RickCharter.MIN_RISK_REWARD_RATIO * risk
                    if direction == "buy":
                        suggested_tp = round(entry + needed_reward, 5)
                    else:
                        suggested_tp = round(entry - needed_reward, 5)
                    suggestions["take_profit"] = suggested_tp
                    suggestions["reason_rr"] = f"Adjust TP to {suggested_tp} for RR >= {RickCharter.MIN_RISK_REWARD_RATIO}."
        except Exception:
            pass

    failures = any(k.startswith("reason_") for k in suggestions.keys())
    if failures:
        return False, "; ".join(v for k,v in suggestions.items() if k.startswith("reason_")), suggestions
    return True, "Charter compliance satisfied", suggestions

# ----------------- API Endpoints -----------------
@app.post("/api/dialogue", response_model=DialogueResponse)
async def dialogue(req: DialogueRequest):
    raw = req.message.strip()
    parsed = cfg.manual_trade_input(raw)
    parsed["raw_text"] = raw
    plan = cfg.submit_manual_trade(TradeParameters(**{
        "symbol": parsed.get("symbol", "EURUSD"),
        "direction": parsed.get("direction", "buy"),
        "quantity": parsed.get("quantity", 10000),
        "entry_price": parsed.get("entry_price"),
        "stop_loss": parsed.get("stop_loss"),
        "take_profit": parsed.get("take_profit"),
        "risk_percent": parsed.get("risk_percent", 2.0),
        "broker": parsed.get("broker", "oanda")
    }))

    charter_ok, charter_reason, suggestions = charter_validate(parsed)
    executed = False

    if looks_execute(raw):
        # Need PIN and charter compliance or override
        if not req.pin or req.pin != PIN:
            charter_ok = False
            charter_reason = "PIN missing or invalid for execution"
        else:
            if not charter_ok and not req.override:
                charter_reason += " | Provide override=true to force or adjust suggested params."
            else:
                # Apply suggestions if not ok and override requested (configurable)
                if not charter_ok and req.override and req.apply_suggestions:
                    for k,v in suggestions.items():
                        if k.startswith("reason_"): continue
                        parsed[k] = v
                    charter_ok2, charter_reason2, suggestions2 = charter_validate(parsed)
                    charter_ok = charter_ok2; charter_reason = charter_reason2; suggestions = suggestions2
                if charter_ok or req.override:
                    tp = TradeParameters(
                        symbol=parsed.get("symbol", "EURUSD"),
                        direction=parsed.get("direction", "buy"),
                        quantity=parsed.get("quantity", 10000),
                        entry_price=parsed.get("entry_price"),
                        stop_loss=parsed.get("stop_loss"),
                        take_profit=parsed.get("take_profit"),
                        risk_percent=parsed.get("risk_percent", 2.0),
                        broker=parsed.get("broker", "oanda"),
                    )
                    mt = ManualTrade(
                        symbol=tp.symbol,
                        direction=tp.direction,
                        quantity=float(tp.quantity or 0),
                        broker=tp.broker,
                        entry_price=(float(tp.entry_price) if tp.entry_price is not None else None),
                        stop_loss=(float(tp.stop_loss) if tp.stop_loss is not None else None),
                        take_profit=(float(tp.take_profit) if tp.take_profit is not None else None),
                        order_type="market",
                    )
                    res = place_trade(pin=int(PIN), trade=mt)
                    if res.get("success"):
                        price = res.get("price") or tp.entry_price or 0
                        logger.narrate_trade_executed(tp.symbol, tp.direction, tp.quantity, float(price), tp.broker)
                        executed = True
                    else:
                        logger.narrate_error("MANUAL_EXECUTION", res.get("error", "unknown error"))

    return DialogueResponse(
        parsed=parsed,
        plan=plan,
        charter_ok=charter_ok,
        charter_reason=charter_reason,
        suggestions=suggestions,
        executed=executed
    )

# Simple websocket to stream narration tail updates
clients = set()
@app.websocket("/ws/narration")
async def narration_socket(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        await ws.send_text("Connected to narration stream.")
        import asyncio, os
        last_size = 0
        log_path = logger.log_file
        while True:
            if log_path.exists():
                size = log_path.stat().st_size
                if size != last_size:
                    with open(log_path, 'r') as f:
                        lines = f.readlines()[-10:]
                    await ws.send_text("\n".join(line.strip() for line in lines))
                    last_size = size
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        clients.discard(ws)

# ----------------- Static HTML -----------------
INDEX_HTML = """<!DOCTYPE html><html><head><title>RICK ↔ Hive Web</title>
<style>body{font-family:Arial;background:#111;color:#eee;margin:20px;}textarea{width:100%;height:120px;background:#222;color:#eee;padding:8px;border:1px solid #444;}button{padding:8px 14px;margin-top:8px;}pre{background:#222;padding:10px;border:1px solid #333;white-space:pre-wrap;}#stream{height:180px;overflow:auto;background:#000;padding:8px;font-size:12px;border:1px solid #333;}</style></head><body>
<h1>RICK ↔ Hive Web Interface</h1>
<p>Enter dialogue or trade suggestion. Append 'place trade 841921' to execute.</p>
<textarea id="msg" placeholder="e.g. Buy 20000 EURUSD at 1.1050 stop 1.1000 target 1.1150 then place trade 841921"></textarea>
<div><label>PIN: <input id="pin" value="841921" style="width:100px"/></label> <label>Override <input type="checkbox" id="override"/></label></div>
<button onclick="sendMsg()">Send</button>
<h3>Response</h3>
<pre id="resp"></pre>
<h3>Narration Stream</h3>
<div id="stream"></div>
<script>
async function sendMsg(){
 const msg=document.getElementById('msg').value;
 const pin=document.getElementById('pin').value.trim();
 const override=document.getElementById('override').checked;
 const payload={message:msg, pin:pin, override:override};
 const r=await fetch('/api/dialogue',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 const j=await r.json();
 document.getElementById('resp').textContent=JSON.stringify(j,null,2);
}
const ws=new WebSocket((location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/ws/narration');
ws.onmessage=e=>{const div=document.getElementById('stream');div.textContent=e.data;div.scrollTop=div.scrollHeight;};
</script>
</body></html>"""

@app.get("/")
async def index():
    return INDEX_HTML

# Uvicorn entry point helper
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ui.hive_web:app", host="0.0.0.0", port=8700, reload=False)
