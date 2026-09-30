"""
Free Fire: Combo và Độ nhạy - bản Streamlit.

Cách chạy:
    pip install streamlit anthropic
    export ANTHROPIC_API_KEY="khóa-api-của-bạn"   # Windows PowerShell: $env:ANTHROPIC_API_KEY="khóa-api-của-bạn"
    streamlit run streamlit_app.py

Hoặc đặt khóa trong file .streamlit/secrets.toml:
    ANTHROPIC_API_KEY = "khóa-api-của-bạn"

Không dán khóa vào file này và không đưa file chứa khóa lên GitHub.
Đổi model bằng biến môi trường ANTHROPIC_MODEL nếu cần.
Để đủ màu giao diện, giữ file .streamlit/config.toml cạnh file này.
"""
import json
import os

import anthropic
import html as _html

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Free Fire: Combo và Độ nhạy", page_icon="🔥")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=Be+Vietnam+Pro:wght@400;600&display=swap');
.stApp{font-family:'Be Vietnam Pro',sans-serif;background:radial-gradient(900px 420px at 15% -5%,rgba(255,40,20,.35),transparent 60%),radial-gradient(800px 400px at 90% 0%,rgba(255,170,0,.18),transparent 60%),#08080a}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:860px;padding-top:1rem}
h1,h2,h3,[data-testid="stMetricValue"]{font-family:'Chakra Petch',sans-serif!important}
.ff-hero{position:relative;overflow:hidden;text-align:center;padding:34px 14px 26px;margin-bottom:16px;border:1px solid #6a1414;background:linear-gradient(180deg,rgba(90,10,10,.6),rgba(12,8,9,.92));clip-path:polygon(0 0,calc(100% - 26px) 0,100% 26px,100% 100%,26px 100%,0 calc(100% - 26px));box-shadow:0 0 50px rgba(255,50,20,.25) inset}
.ff-hero .horns{font-size:2.2rem;letter-spacing:6px;animation:flick 2.4s infinite}
.ff-hero h1{font-size:clamp(2.8rem,12vw,5.2rem);margin:4px 0 0;line-height:1;font-weight:700;letter-spacing:3px;background:linear-gradient(180deg,#fff2a8 0%,#ffd000 30%,#ff7a00 62%,#ff1a1a 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 16px rgba(255,60,20,.6))}
.ff-hero .tag{margin:10px 0 0;color:#ffb3a8;font:600 1.05rem 'Chakra Petch',sans-serif}
.ff-badges{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:16px}
.ff-badges span{border:1px solid #ff3b1c;background:rgba(255,59,28,.14);color:#ffd9a0;padding:6px 16px;font:700 .85rem 'Chakra Petch',sans-serif;clip-path:polygon(8px 0,100% 0,calc(100% - 8px) 100%,0 100%)}
.ff-hero i{position:absolute;bottom:-10px;width:6px;height:6px;border-radius:50%;background:#ffb000;box-shadow:0 0 8px #ff4b00;opacity:0;animation:rise 4s linear infinite}
@keyframes rise{0%{transform:translateY(0) scale(1);opacity:0}15%{opacity:.9}100%{transform:translateY(-240px) translateX(18px) scale(.3);opacity:0}}
@keyframes flick{0%,100%{opacity:1}45%{opacity:.75}50%{opacity:1}55%{opacity:.6}}
.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:2px solid #3a0d0d}
.stTabs [data-baseweb="tab"]{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:1.08rem;background:#1a0b0d;border-radius:0;clip-path:polygon(12px 0,100% 0,calc(100% - 12px) 100%,0 100%);padding:11px 24px}
.stTabs [aria-selected="true"]{background:linear-gradient(180deg,#ff3b1c,#a30d0d)!important;color:#fff!important;box-shadow:0 0 18px rgba(255,59,28,.5)}
.stTabs [data-baseweb="tab-highlight"]{background:#ffd000!important}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid #5a1212!important;border-left:5px solid #ff3b1c!important;background:linear-gradient(180deg,#170a0b,#0e0708);box-shadow:0 0 22px rgba(255,40,20,.2);border-radius:2px!important}
[data-baseweb="select"]>div{background:#1a0b0d!important;border:1px solid #5a1212!important}
div[role="radiogroup"] label{background:#1a0b0d;border:1px solid #4a1010;padding:4px 12px;margin-right:6px}
[data-testid="stExpander"]{border:1px solid #5a1212;background:#120708}
[data-testid="stExpander"] summary{font-family:'Chakra Petch',sans-serif;font-weight:700;color:#ffb000}
[data-testid="stChatMessage"]{background:#170a0c;border:1px solid #4a1010}
pre{background:#120708!important;border:1px dashed #6a1414}
.roster{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin:8px 0 4px}
.ch{display:flex;gap:10px;padding:10px;background:linear-gradient(135deg,#1d0c0e,#120809);border:1px solid #4a1010;border-left:3px solid #ff3b1c}
.ch.act{border-left-color:#ffd000;box-shadow:0 0 14px rgba(255,208,0,.2)}
.ch b{flex:none;width:38px;height:38px;display:grid;place-items:center;font:700 1.2rem 'Chakra Petch',sans-serif;color:#140606;background:linear-gradient(135deg,#ffd000,#ff6a00)}
.ch .r{font:700 .72rem 'Chakra Petch',sans-serif;color:#ff8a70}
.ch.act .r{color:#ffd000}
.ch strong{font-family:'Chakra Petch',sans-serif;font-size:1.05rem;display:block}
.ch em{font-style:normal;color:#ffb98f;font-size:.82rem}
.ch span{display:block;font-size:.83rem;color:#c9b6b0;margin-top:2px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:10px 0}
.tile{padding:12px 14px;background:linear-gradient(160deg,#1f0b0d,#0f0708);border:1px solid #5a1212;clip-path:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,14px 100%,0 calc(100% - 14px))}
.tile small{color:#ff9a8a;font-weight:600}
.tile .n{font:700 2.8rem/1.05 'Chakra Petch',sans-serif;background:linear-gradient(180deg,#ffe066,#ff6a00);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 10px rgba(255,100,0,.5))}
.bar{height:8px;margin-top:6px;background:repeating-linear-gradient(90deg,#3a1414 0 3px,transparent 3px 8px)}
.bar i{display:block;height:100%;background:repeating-linear-gradient(90deg,#ffb000 0 3px,transparent 3px 8px)}
@media(prefers-reduced-motion:reduce){.ff-hero .horns,.ff-hero i{animation:none}}
</style>
"""
HERO = """
<div class="ff-hero">{embers}<div class="horns">😈🔥💀🔥😈</div>
<h1>FREE FIRE</h1>
<div class="tag">Combo hiểm · Độ nhạy chuẩn · Kéo tâm như quỷ</div>
<div class="ff-badges"><span>{nc} combo</span><span>{nm} dòng máy</span><span>Trợ lý AI</span></div></div>
"""
EMBERS = "".join(
    f'<i style="left:{l}%;animation-delay:{d}s;animation-duration:{t}s"></i>'
    for l, d, t in [(6, 0, 4), (16, 1.2, 3.6), (28, 2.4, 4.4), (40, .6, 3.8), (52, 1.8, 4.2),
                    (64, 3, 3.6), (76, .3, 4.6), (88, 2.1, 4), (95, 1.5, 3.4)]
)
ICONS = {"rush": "🔥", "rank": "⚔️", "snipe": "🎯", "gloo": "🧱", "def": "🛡️", "speed": "⚡"}

# Nhạc chiến tự soạn, tạo bằng Web Audio ngay trong trình duyệt (không dùng nhạc có bản quyền).
MUSIC = """
<style>
body{margin:0;font-family:system-ui,sans-serif;color:#ffd9a0}
.p{display:flex;align-items:center;gap:12px;padding:10px 14px;background:linear-gradient(90deg,#2a0909,#120708);border:1px solid #6a1414;border-left:5px solid #ff3b1c}
button{cursor:pointer;border:0;padding:10px 18px;font-weight:700;color:#140606;background:linear-gradient(135deg,#ffd000,#ff6a00)}
input{accent-color:#ff3b1c;flex:1}
span{font-size:.85rem;white-space:nowrap}
</style>
<div class="p"><button id="b">🔊 Bật nhạc chiến</button><input id="v" type="range" min="0" max="100" value="45"><span id="s">Đang tắt</span></div>
<script>
var ctx,master,timer,on=false,step=0,next=0,bpm=140,spb=60/140/4,roots=[45,43,41,40];
var bp=[1,0,0,1,0,1,0,0,1,0,0,1,0,1,1,0],arp=[0,3,7,12,7,3,0,3];
function f(m){return 440*Math.pow(2,(m-69)/12)}
function tone(t,m,ty,g,d){var o=ctx.createOscillator(),v=ctx.createGain();o.type=ty;o.frequency.value=f(m);v.gain.setValueAtTime(g,t);v.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(v);v.connect(master);o.start(t);o.stop(t+d+.02)}
function kick(t){var o=ctx.createOscillator(),v=ctx.createGain();o.frequency.setValueAtTime(150,t);o.frequency.exponentialRampToValueAtTime(40,t+.12);v.gain.setValueAtTime(.9,t);v.gain.exponentialRampToValueAtTime(.0001,t+.2);o.connect(v);v.connect(master);o.start(t);o.stop(t+.22)}
function noise(t,g,d,hp){var n=ctx.sampleRate*d,b=ctx.createBuffer(1,n,ctx.sampleRate),a=b.getChannelData(0);for(var i=0;i<n;i++)a[i]=Math.random()*2-1;var s=ctx.createBufferSource(),fl=ctx.createBiquadFilter(),v=ctx.createGain();s.buffer=b;fl.type="highpass";fl.frequency.value=hp;v.gain.setValueAtTime(g,t);v.gain.exponentialRampToValueAtTime(.0001,t+d);s.connect(fl);fl.connect(v);v.connect(master);s.start(t)}
function play(i,t){var bar=Math.floor(i/16)%4,k=i%16,r=roots[bar];
 if(k%4==0)kick(t);
 if(k==4||k==12)noise(t,.5,.15,1500);
 if(k%2==1)noise(t,.12,.04,7000);
 if(bp[k])tone(t,r,"sawtooth",.28,spb*1.8);
 if(k%2==0)tone(t,r+24+arp[(k/2)%8],"square",.07,spb*1.6);
 if(k==0&&bar%2==0)tone(t,r+36,"triangle",.1,spb*10)}
function sched(){while(next<ctx.currentTime+.25){play(step,next);next+=spb;step=(step+1)%64}}
document.getElementById("b").onclick=function(){
 if(!ctx){ctx=new (window.AudioContext||window.webkitAudioContext)();master=ctx.createGain();master.gain.value=.45*.5;master.connect(ctx.destination)}
 on=!on;
 if(on){ctx.resume();next=ctx.currentTime+.05;step=0;timer=setInterval(sched,50);this.textContent="⏸ Tắt nhạc";document.getElementById("s").textContent="Đang phát"}
 else{clearInterval(timer);ctx.suspend();this.textContent="🔊 Bật nhạc chiến";document.getElementById("s").textContent="Đang tắt"}};
document.getElementById("v").oninput=function(){if(master)master.gain.value=this.value/100*.5};
</script>
"""

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
MAX_QUESTIONS = 30  # số câu hỏi tối đa cho mỗi phiên, tránh tốn tiền API

SYSTEM = (
    "Bạn là trợ lý của trang Free Fire: Combo và Độ nhạy. "
    "Trả lời bằng tiếng Việt, ngắn gọn, thân thiện. "
    "Chỉ nói về Free Fire: combo nhân vật, độ nhạy, cách chơi. "
    "Không bịa số liệu cụ thể của kỹ năng; nếu không chắc thì nói rõ và nhắc người chơi "
    "xem mô tả trong game vì kỹ năng hay được cân bằng lại. "
    "Bộ số độ nhạy chỉ là điểm khởi đầu, không phải con số chuẩn."
)

# ---------------------------------------------------------------- Dữ liệu
CHARS = {
    "Alok": ("Drop the Beat", "Tạo vùng hồi máu và tăng tốc độ di chuyển cho bạn và đồng đội."),
    "Chrono": ("Time Turner", "Dựng khiên chắn sát thương phía trước và giúp di chuyển nhanh hơn."),
    "Wukong": ("Camouflage", "Hóa thành bụi cây để ẩn mình và áp sát hoặc quan sát."),
    "Skyler": ("Riot Buster", "Phát sóng âm phá tường gloo của địch."),
    "Dimitri": ("Healing Heartbeat", "Tạo vùng hồi phục cho đội khi cố thủ."),
    "Jota": ("Sustained Raids", "Hồi máu khi hạ gục địch bằng súng tiểu liên hoặc shotgun."),
    "Hayato": ("Bushido", "Tăng xuyên giáp khi máu của bạn càng thấp."),
    "Kelly": ("Dash", "Tăng tốc độ chạy nước rút."),
    "Moco": ("Hacker's Eye", "Đánh dấu địch bị bạn bắn trúng để cả đội nhìn thấy."),
    "D-Bee": ("Bullet Beats", "Giúp di chuyển và bắn ổn định hơn trong giao tranh."),
    "Luqueta": ("Hat Trick", "Tăng máu tối đa mỗi khi hạ gục địch."),
    "Maxim": ("Gluttony", "Dùng vật phẩm hồi máu nhanh hơn."),
    "Joseph": ("Nutty Movement", "Tăng tốc độ di chuyển."),
    "Iris": ("Dimension", "Hỗ trợ đối phó tường gloo."),
}

COMBOS = [
    dict(n="Xung phong áp sát", t="rush", m="Xếp hạng, Đấu đội", c=["Chrono", "Jota", "Hayato", "Kelly"],
         how="Dựng khiên Chrono rồi chạy vào bằng Kelly. Giữ súng tiểu liên hoặc shotgun để Jota hồi máu sau mỗi lần hạ gục. Khi máu thấp, Hayato giúp bạn vẫn gây sát thương tốt.",
         good="Vừa chắc vừa nhanh, hợp giao tranh gần và đẩy nhà.",
         bad="Phụ thuộc vào việc bạn chủ động hạ gục. Đứng xa và bắn tỉa sẽ lãng phí cả bộ.",
         alt="Thay Kelly bằng Moco nếu muốn thêm thông tin vị trí địch."),
    dict(n="Cân bằng, dễ dùng nhất", t="rank", m="Xếp hạng, Solo", c=["Alok", "Jota", "Hayato", "Kelly"],
         how="Bật Alok khi vào giao tranh hoặc khi cần đổi vị trí để vừa hồi máu vừa chạy nhanh. Jota và Hayato lo phần đánh gần, Kelly giúp xoay vòng khi bo thu hẹp.",
         good="Dùng được ở hầu hết tình huống, phù hợp người mới.",
         bad="Không có khiên như Chrono, dễ thiệt khi bị đánh úp từ xa.",
         alt="Thay Hayato bằng Moco để biết địch ở đâu, hoặc bằng Maxim để hồi máu nhanh hơn."),
    dict(n="Do thám và đánh gần", t="rush", m="Xếp hạng", c=["Alok", "Hayato", "Kelly", "Moco"],
         how="Bắn trúng một phát để Moco đánh dấu địch, cả đội sẽ thấy vị trí. Sau đó vào bằng tốc độ của Alok và Kelly, Hayato lo phần xuyên giáp khi máu tụt.",
         good="Có thông tin và có tốc độ, hợp đội phối hợp qua mic.",
         bad="Không có nhiều hồi máu khi hạ gục như Jota, nên cần dùng vật phẩm thường xuyên.",
         alt="Thay Hayato bằng Jota nếu muốn hồi máu khi đánh."),
    dict(n="Bắn tỉa, đánh xa", t="snipe", m="Xếp hạng, Solo", c=["Wukong", "Moco", "Jota", "Kelly"],
         how="Dùng Wukong để lén đổi vị trí hoặc quan sát từ bụi cây. Moco đánh dấu địch sau phát bắn đầu, Kelly giúp rút nhanh sau khi bắn.",
         good="Giữ khoảng cách, ít phải lộ mặt.",
         bad="Hạ gục từ xa ít khi kích hoạt Jota, nên hồi máu yếu.",
         alt="Thay Jota bằng Laura nếu bạn chủ yếu dùng súng bắn tỉa."),
    dict(n="Phá tường gloo", t="gloo", m="Đấu đội", c=["Skyler", "D-Bee", "Moco", "Luqueta"],
         how="Skyler phá tường gloo, Moco đánh dấu địch lộ diện, D-Bee giúp bạn di chuyển và bắn ổn định khi giao tranh gần. Luqueta tăng máu tối đa sau mỗi lần hạ gục.",
         good="Khắc chế đội hay dựng tường gloo và cố thủ.",
         bad="Ít tác dụng khi địch không dùng tường, tốc độ chạy không nổi bật.",
         alt="Thay Luqueta bằng Iris để thêm khả năng đối phó tường gloo."),
    dict(n="Cố thủ, giữ vị trí", t="def", m="Xếp hạng, Đấu đội", c=["Alok", "Dimitri", "Luqueta", "Maxim"],
         how="Chọn điểm cao hoặc nhà chắc. Đặt Alok hoặc Dimitri tạo vùng hồi phục cho đội, Maxim giúp dùng hộp cứu thương nhanh, Luqueta giúp trụ lâu khi có hạ gục.",
         good="Đội rất khó bị hạ khi cố thủ trong vòng cuối.",
         bad="Di chuyển chậm và ít chủ động, không hợp đẩy giao tranh.",
         alt="Thay Maxim bằng Kelly để có thêm tốc độ khi cần rút."),
    dict(n="Tốc độ tối đa", t="speed", m="Đấu đội, xoay vòng", c=["Kelly", "Joseph", "Alok", "Iris"],
         how="Dùng khi phải chạy bo xa hoặc muốn áp sát nhanh. Alok tăng tốc thêm và hồi máu, Iris hỗ trợ khi địch cản bằng tường gloo.",
         good="Di chuyển nhanh nhất trong các bộ gợi ý, hợp đổi vị trí liên tục.",
         bad="Sát thương và khả năng trụ khi bị bắn thấp hơn các bộ khác.",
         alt="Thay Iris bằng Jota để hồi máu khi hạ gục."),
]
FILTERS = {"Tất cả": None, "Xung phong": "rush", "Cân bằng": "rank", "Bắn tỉa": "snipe",
           "Phá gloo": "gloo", "Cố thủ": "def", "Tốc độ": "speed"}

DEVS = [  # (tên nhóm, điểm cộng trừ, mô tả)
    ("Chưa chọn (bỏ qua)", 0, "Dùng bộ số gốc."),
    ("iPhone nhỏ (mini, SE)", 4, "Màn nhỏ, ít chỗ vuốt nên tăng độ nhạy."),
    ("iPhone thường (khoảng 6.1 inch)", 1, "Gần bộ số gốc."),
    ("iPhone Plus / Pro Max (khoảng 6.7 inch)", -2, "Màn lớn, vuốt rộng nên giảm nhẹ."),
    ("iPad / máy tính bảng", -7, "Màn rất lớn, cần giảm nhiều để không bay tâm."),
    ("Samsung Galaxy S / Ultra", -1, "Màn lớn, thường mượt. Giảm nhẹ."),
    ("Samsung A, Xiaomi, Redmi, Realme, Oppo, Vivo", 0, "Tầm trung, giữ bộ số gốc rồi tinh chỉnh."),
    ("Máy gaming (ROG, Red Magic...)", -2, "Phản hồi cảm ứng nhanh nên có thể giảm nhẹ."),
    ("Máy cũ hoặc cấu hình yếu", -3, "Dễ giật lag, giảm để dễ kiểm soát."),
]
HZS = [("60 Hz", 0), ("90 Hz", -1), ("120 Hz", -2), ("144 Hz trở lên", -3)]
NAMES = ["Tổng quát", "Red Dot", "Ống ngắm 2x", "Ống ngắm 4x", "AWM", "Nhìn tự do"]
PRESETS = {"Kéo tâm mạnh": [95, 92, 88, 84, 60, 68],
           "Cân bằng": [88, 85, 80, 75, 55, 62],
           "Bắn xa, chắc tay": [80, 76, 72, 66, 48, 56]}

MODELS = {}  # tên máy -> chỉ số nhóm trong DEVS


def add(names, grp):
    for n in names:
        MODELS[n] = grp


def gen(prefix, nums, sufs, grp):
    for k in nums:
        for s in sufs:
            MODELS[f"{prefix}{k}{s}"] = grp


gen("iPhone ", [11, 12, 13, 14, 15, 16], ["", " Pro"], 2)
gen("iPhone ", [11, 12, 13, 14, 15, 16], [" Pro Max"], 3)
gen("iPhone ", [14, 15, 16], [" Plus"], 3)
add(["iPhone SE", "iPhone 12 mini", "iPhone 13 mini"], 1)
add(["iPhone 6", "iPhone 7", "iPhone 8", "Redmi 9A", "Galaxy J7"], 8)
add(["iPad", "iPad Air", "iPad Pro", "iPad mini"], 4)
gen("Galaxy S", [20, 21, 22, 23, 24, 25], ["", "+", " Ultra"], 5)
gen("Galaxy A", [12, 13, 14, 15, 23, 24, 25, 32, 33, 34, 35, 52, 53, 54, 55, 56], [""], 6)
gen("Redmi Note ", [10, 11, 12, 13, 14], [""], 6)
add(["POCO X5", "POCO X6", "POCO X7", "POCO F5", "POCO F6", "Realme 8", "Realme 9", "Realme 10",
     "Realme 11", "Realme 12", "Realme 13", "Oppo Reno 8", "Oppo Reno 10", "Oppo Reno 11",
     "Oppo Reno 12", "Oppo A57", "Oppo A58", "Oppo A78", "Vivo Y21", "Vivo Y27", "Vivo V25",
     "Vivo V27", "Vivo V29"], 6)
gen("ROG Phone ", [6, 7, 8, 9], [""], 7)
add(["Red Magic 8 Pro", "Red Magic 9 Pro", "Red Magic 10 Pro"], 7)

st.session_state.setdefault("dev", 0)
st.session_state.setdefault("msgs", [])


def on_model():
    name = st.session_state.get("model_pick")
    if name:
        st.session_state.dev = MODELS[name]
        st.session_state.model_msg = f"Nhận diện: {name} → nhóm {DEVS[MODELS[name]][0]}"
    else:
        st.session_state.model_msg = ""


def get_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None


def stream_answer(msgs, system, key):
    client = anthropic.Anthropic(api_key=key)
    with client.messages.stream(model=MODEL, max_tokens=700, system=system, messages=msgs) as s:
        yield from s.text_stream


# ---------------------------------------------------------------- Giao diện
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HERO.format(embers=EMBERS, nc=len(COMBOS), nm=len(MODELS)), unsafe_allow_html=True)
components.html(MUSIC, height=64)
with st.expander("🎵 Dùng nhạc của bạn"):
    st.caption("Nhạc chính thức của Free Fire thuộc bản quyền Garena nên app không kèm sẵn. "
               "Bạn có thể tải lên file nhạc mà bạn có quyền sử dụng, đặc biệt nếu đưa app lên mạng.")
    up = st.file_uploader("Chọn file nhạc (mp3, wav, ogg)", type=["mp3", "wav", "ogg"])
    if up:
        try:
            st.audio(up, loop=True)
        except TypeError:
            st.audio(up)
tab1, tab2, tab3 = st.tabs(["😈 Combo quỷ", "🎯 Độ nhạy", "🤖 Trợ lý AI"])

with tab1:
    pick = st.radio("Lối chơi", list(FILTERS), horizontal=True)
    for c in COMBOS:
        if FILTERS[pick] and c["t"] != FILTERS[pick]:
            continue
        with st.container(border=True):
            st.subheader(f'{ICONS[c["t"]]} {c["n"]}')
            st.caption("Hợp với: " + c["m"])
            tiles = ""
            for i, ch in enumerate(c["c"]):
                skill, desc = CHARS[ch]
                role = "CHỦ ĐỘNG" if i == 0 else "Bị động"
                tiles += (f'<div class="ch{" act" if i == 0 else ""}"><b>{_html.escape(ch[0])}</b><div>'
                          f'<div class="r">{role}</div><strong>{_html.escape(ch)}</strong>'
                          f'<em>{_html.escape(skill)}</em><span>{_html.escape(desc)}</span></div></div>')
            st.markdown(f'<div class="roster">{tiles}</div>', unsafe_allow_html=True)
            with st.expander("Cách chơi chi tiết"):
                st.markdown(f"**Cách chơi:** {c['how']}")
                st.markdown(f"**Điểm mạnh:** {c['good']}")
                st.markdown(f"**Điểm yếu:** {c['bad']}")
                st.markdown(f"**Thay thế:** {c['alt']}")
    st.caption("Các bộ combo lấy từ nhiều trang hướng dẫn, không phải từ nhà phát hành, và kỹ năng "
               "thường được cân bằng lại theo từng bản cập nhật. Bạn đọc lại mô tả kỹ năng trong game "
               "trước khi dùng. App không ghi con số cụ thể vì các nguồn ghi khác nhau.")

with tab2:
    st.selectbox("Tên máy (bấm vào và gõ để tìm)", sorted(MODELS), index=None,
                 placeholder="Ví dụ: iPhone 14, Galaxy S23, Redmi Note 12",
                 key="model_pick", on_change=on_model)
    if st.session_state.get("model_msg"):
        st.success(st.session_state.model_msg)
    dev = st.selectbox("Hoặc chọn nhóm máy", range(len(DEVS)), format_func=lambda i: DEVS[i][0], key="dev")
    hz = st.selectbox("Tần số quét màn hình (xem trong cài đặt máy)", range(len(HZS)), index=1,
                      format_func=lambda i: HZS[i][0])
    style = st.radio("Kiểu chơi", list(PRESETS), index=1, horizontal=True)
    manual = st.slider("Chỉnh tay (tăng/giảm toàn bộ)", -10, 10, 0)

    total = manual + DEVS[dev][1] + HZS[hz][1]
    st.info(f"{DEVS[dev][2]} Tổng điều chỉnh: {total:+d} điểm "
            f"(máy {DEVS[dev][1]:+d}, tần số quét {HZS[hz][1]:+d}, chỉnh tay {manual:+d}).")

    values = [max(0, min(100, v + total)) for v in PRESETS[style]]
    st.markdown('<div class="tiles">' + "".join(
        f'<div class="tile"><small>{n}</small><div class="n">{v}</div>'
        f'<div class="bar"><i style="width:{v}%"></i></div></div>'
        for n, v in zip(NAMES, values)) + '</div>', unsafe_allow_html=True)
    st.caption("Bấm biểu tượng sao chép ở góc khung bên dưới để lấy bộ số:")
    st.code("\n".join(f"{n}: {v}" for n, v in zip(NAMES, values)), language=None)

    st.markdown("**Cách chỉnh cho hợp tay**")
    st.markdown(
        "1. Vào phòng tập hoặc Custom Room, dùng bộ số gợi ý trước.\n"
        "2. Tâm bay quá đà, văng khỏi đầu địch: **giảm 3-5** điểm.\n"
        "3. Kéo tâm không kịp, xoay chậm: **tăng 3-5** điểm.\n"
        "4. Chỉ đổi **một nhóm** mỗi lần, thử vài trận rồi mới đổi tiếp.\n"
        "5. Màn hình nhỏ thường cần số cao hơn, màn lớn hoặc máy tính bảng cần số thấp hơn, "
        "máy lag thì nên giảm bớt."
    )
    st.caption("Đây là bộ số khởi đầu phổ biến, không phải con số chuẩn cho mọi người. Máy được xếp "
               "nhóm theo kích thước màn hình và độ mượt, chưa dựa trên thông số chính thức từng máy.")

with tab3:
    key = get_key()
    if not key:
        st.info("Chưa có ANTHROPIC_API_KEY. Đặt biến môi trường hoặc file .streamlit/secrets.toml "
                "(xem hướng dẫn ở đầu file) rồi chạy lại.")
    st.caption("Hỏi về combo hoặc độ nhạy. Trợ lý biết bạn đang chọn máy và bộ số nào ở tab Độ nhạy.")
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input("Nhập câu hỏi của bạn...", disabled=not key)
    if q:
        asked = sum(1 for m in st.session_state.msgs if m["role"] == "user")
        if asked >= MAX_QUESTIONS:
            st.warning("Bạn đã hỏi đủ số câu tối đa của phiên này. Tải lại trang để hỏi tiếp.")
        else:
            st.session_state.msgs.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)
            data = json.dumps({
                "combo": [{"ten": c["n"], "nhanVat": c["c"], "hopVoi": c["m"]} for c in COMBOS],
                "doNhay": {"kieu": style, "dongMay": DEVS[dev][0], "tanSoQuet": HZS[hz][0],
                            "so": [f"{n}: {v}" for n, v in zip(NAMES, values)]},
            }, ensure_ascii=False)
            msgs = [{"role": m["role"], "content": m["content"][:1000]} for m in st.session_state.msgs[-9:]]
            while msgs and msgs[0]["role"] != "user":
                msgs.pop(0)
            with st.chat_message("assistant"):
                try:
                    reply = st.write_stream(stream_answer(msgs, SYSTEM + "\n\nDữ liệu trên trang: " + data, key))
                    st.session_state.msgs.append({"role": "assistant", "content": reply})
                except anthropic.RateLimitError:
                    st.session_state.msgs.pop()
                    st.error("API đang bị giới hạn tốc độ, bạn thử lại sau ít phút.")
                except anthropic.AuthenticationError:
                    st.session_state.msgs.pop()
                    st.error("Khóa API không đúng hoặc đã hết hạn.")
                except anthropic.APIError:
                    st.session_state.msgs.pop()
                    st.error("Không gọi được trợ lý lúc này, bạn thử lại sau.")
