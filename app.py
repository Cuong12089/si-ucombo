"""
Free Fire: Combo va Do nhay - ung dung web mot file.

Cach chay:
    pip install flask anthropic
    export ANTHROPIC_API_KEY="khoa-api-cua-ban"     # Windows PowerShell: $env:ANTHROPIC_API_KEY="khoa-api-cua-ban"
    python app.py
Sau do mo http://localhost:5000

Luu y: khoa API chi dat trong bien moi truong tren may chu, khong dan vao file nay
va khong gui len GitHub. Doi model bang bien ANTHROPIC_MODEL neu can.
"""
import os
import time
from collections import defaultdict, deque

import anthropic
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
MAX_PER_MINUTE = 10  # gioi han so cau hoi moi phut cho moi dia chi IP
_hits = defaultdict(deque)

SYSTEM = (
    "Bạn là trợ lý của trang Free Fire: Combo và Độ nhạy. "
    "Trả lời bằng tiếng Việt, ngắn gọn, thân thiện. "
    "Chỉ nói về Free Fire: combo nhân vật, độ nhạy, cách chơi. "
    "Không bịa số liệu cụ thể của kỹ năng; nếu không chắc thì nói rõ và nhắc người chơi "
    "xem mô tả trong game vì kỹ năng hay được cân bằng lại. "
    "Bộ số độ nhạy chỉ là điểm khởi đầu, không phải con số chuẩn."
)

PAGE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Free Fire: Combo và Độ nhạy</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600&family=Chakra+Petch:wght@600;700&display=swap">
<style>
:root{--bg:#e8edf1;--panel:#fff;--text:#121c26;--muted:#56687a;--a1:#e89a00;--a2:#d63a1a;--line:#ccd5dd;--chip:#fff1cf;--hero:#0b1620;
--hf:"Chakra Petch","Be Vietnam Pro",system-ui,sans-serif;--bf:"Be Vietnam Pro",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
--cut:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,14px 100%,0 calc(100% - 14px));
box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0e1a26;--panel:#16283a;--text:#eaf0f5;--muted:#8da1b4;--a1:#ffb400;--a2:#ff5a36;--line:#2a4058;--chip:#3a3015}}
:root[data-theme="dark"]{--bg:#0e1a26;--panel:#16283a;--text:#eaf0f5;--muted:#8da1b4;--a1:#ffb400;--a2:#ff5a36;--line:#2a4058;--chip:#3a3015}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--bf);line-height:1.6}
.hero{background:var(--hero);color:#eaf0f5;padding:30px 18px 64px;position:relative;overflow:hidden}
.hero-in{max-width:780px;margin:0 auto;position:relative}
.hero h1{margin:0;font-family:var(--hf);font-size:clamp(2.4rem,9vw,3.8rem);line-height:1;font-weight:700;letter-spacing:.5px}
.hero h1 span{display:block;color:#ffb400;font-size:.52em;margin-top:8px;font-weight:600}
.hero p{margin:14px 0 0;max-width:30ch;color:#9fb3c6}
.xh{position:absolute;right:-30px;top:-18px;width:190px;height:190px;opacity:.9;animation:lock .9s cubic-bezier(.2,.8,.2,1) both}
@keyframes lock{from{transform:scale(1.6) rotate(-40deg);opacity:0}to{transform:none;opacity:.9}}
.wrap{max-width:780px;margin:-34px auto 0;padding:0 14px 48px;position:relative}
.tabs{display:grid;grid-template-columns:repeat(3,1fr);background:var(--panel);clip-path:var(--cut);margin-bottom:16px}
.tab{padding:14px;border:0;background:transparent;color:var(--muted);font:700 1rem var(--hf);cursor:pointer;border-bottom:4px solid transparent}
.tab.on{color:var(--text);border-bottom-color:var(--a1);background:var(--chip)}
.card{background:var(--panel);clip-path:var(--cut);padding:18px 18px 18px 20px;margin-bottom:14px}
.card h3{margin:0 0 8px;font:700 1.2rem var(--hf)}
.cc{border-left:5px solid var(--a1)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.chip{display:flex;align-items:center;gap:8px;background:var(--bg);padding:4px 12px 4px 4px;font:600 .9rem var(--hf)}
.chip b{width:26px;height:26px;background:var(--a1);color:#0b1620;display:grid;place-items:center;font-size:.85rem}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.f{padding:8px 14px;border:0;background:var(--panel);color:var(--muted);cursor:pointer;font:600 .9rem var(--hf);border-bottom:3px solid transparent}
.f.on{color:var(--text);border-bottom-color:var(--a2)}
.note{font-size:.85rem;color:var(--muted);border-left:3px solid var(--a1);padding:4px 10px;margin:12px 0}
.fld{margin:12px 0}
.fld label{display:block;font-weight:600;font-size:.9rem;margin-bottom:6px}
.in{width:100%;padding:12px;border:0;border-bottom:2px solid var(--line);background:var(--bg);color:var(--text);font:1rem var(--bf)}
.in:focus{outline:none;border-bottom-color:var(--a1)}
.res{margin-top:8px;font-size:.9rem;color:var(--muted)}
.res.ok{color:var(--a1);font-weight:700}
.tiles{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
@media(min-width:560px){.tiles{grid-template-columns:repeat(3,1fr)}}
.tile{background:var(--bg);padding:12px;clip-path:var(--cut)}
.tile small{color:var(--muted);font-weight:600}
.tile .n{font:700 2.6rem/1.1 var(--hf);color:var(--a1)}
.bar{height:8px;margin-top:6px;background:repeating-linear-gradient(90deg,var(--line) 0 2px,transparent 2px 8px)}
.bar i{display:block;height:100%;background:repeating-linear-gradient(90deg,var(--a1) 0 2px,transparent 2px 8px)}
input[type=range]{width:100%;accent-color:var(--a1)}
.btn{width:100%;padding:14px;border:0;background:var(--a1);color:#0b1620;font:700 1.05rem var(--hf);cursor:pointer;margin-top:14px;clip-path:var(--cut)}
.hide{display:none}
.msg{padding:10px 12px;margin:8px 0;white-space:pre-wrap;font-size:.95rem;clip-path:var(--cut)}
.msg.u{background:var(--chip)}
.msg.a{background:var(--bg)}
textarea.in{resize:vertical}
ol{padding-left:20px;margin:8px 0}
button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--a2);outline-offset:2px}
@media(prefers-reduced-motion:reduce){.xh{animation:none}}
.mode{color:var(--muted);font-size:.85rem;margin-bottom:8px}
.roster{display:grid;gap:8px;margin:10px 0}
@media(min-width:560px){.roster{grid-template-columns:1fr 1fr}}
.ch{display:flex;gap:10px;background:var(--bg);padding:8px 10px;align-items:flex-start}
.ch b{flex:none;width:30px;height:30px;background:var(--a1);color:#0b1620;display:grid;place-items:center;font:700 .95rem var(--hf)}
.ch strong{font-family:var(--hf)}
.ch em{font-style:normal;color:var(--a1);font-size:.8rem;font-weight:600}
.ch span{display:block;font-size:.85rem;color:var(--muted)}
details{margin-top:8px;border-top:1px solid var(--line);padding-top:8px}
summary{cursor:pointer;font:700 .95rem var(--hf);color:var(--a1)}
details p{margin:8px 0;font-size:.92rem}
</style>
</head>
<body>
<div class="hero"><div class="hero-in"><svg class="xh" viewBox="0 0 200 200" fill="none" stroke="#ffb400" stroke-width="3" aria-hidden="true"><circle cx="100" cy="100" r="62"/><circle cx="100" cy="100" r="8" fill="#ff5a36" stroke="none"/><path d="M100 10v52M100 138v52M10 100h52M138 100h52"/></svg><h1>Free Fire<span>Combo và độ nhạy</span></h1><p>Chọn combo hợp lối chơi, chỉnh độ nhạy theo đúng máy của bạn.</p></div></div>
<div class="wrap">
<div class="tabs"><button class="tab on" data-t="combo">Combo nhân vật</button><button class="tab" data-t="sens">Độ nhạy</button><button class="tab" data-t="ai">Trợ lý AI</button></div>

<section id="combo">
<div class="filters" id="cf"></div>
<div id="clist"></div>
<div class="note">Các bộ combo lấy từ nhiều trang hướng dẫn, không phải từ nhà phát hành, và kỹ năng thường được cân bằng lại theo từng bản cập nhật. Bạn đọc lại mô tả kỹ năng trong game trước khi dùng, vì mình không ghi con số cụ thể do các nguồn ghi khác nhau.</div>
</section>

<section id="sens" class="hide">
<div class="card">
<h3>📱 Máy của bạn</h3>
<div class="fld"><label for="q">Gõ tên máy (ví dụ: iPhone 14, Galaxy S23, Redmi Note 12)</label>
<input class="in" id="q" list="dl" placeholder="Gõ tên máy..." autocomplete="off"><datalist id="dl"></datalist>
<div class="res" id="res">Chưa nhập tên máy.</div></div>
<div class="fld"><label for="dev">Hoặc chọn nhóm máy</label><select class="in" id="dev"></select></div>
<div class="fld"><label for="hz">Tần số quét màn hình (bạn xem trong cài đặt máy)</label><select class="in" id="hz"></select></div>
<div class="note" id="tot"></div>
</div>

<div class="card">
<div class="filters" id="sf"></div>
<div class="tiles" id="tiles"></div>
<div style="margin-top:16px"><b>Chỉnh tay: <span id="off">0</span></b><input type="range" id="slider" min="-10" max="10" value="0"></div>
<button class="btn" id="copy">Sao chép bộ độ nhạy</button>
</div>

<div class="card">
<h3>Cách chỉnh cho hợp tay</h3>
<ol>
<li>Vào phòng tập hoặc Custom Room, dùng bộ số gợi ý trước.</li>
<li>Tâm bay quá đà, văng khỏi đầu địch: <b>giảm 3-5</b> điểm.</li>
<li>Kéo tâm không kịp, xoay chậm: <b>tăng 3-5</b> điểm.</li>
<li>Chỉ đổi <b>một nhóm</b> mỗi lần, thử vài trận rồi mới đổi tiếp.</li>
<li>Màn hình nhỏ thường cần số cao hơn, màn lớn hoặc máy tính bảng cần số thấp hơn, máy lag thì nên giảm bớt.</li>
</ol>
</div>
<div class="note">Đây là bộ số khởi đầu phổ biến, không phải con số chuẩn cho mọi người. Mình xếp máy vào nhóm theo kích thước màn hình và độ mượt, chưa dựa trên thông số chính thức từng máy. Độ nhạy hợp nhất vẫn tùy tay bạn.</div>
</section>
<section id="ai" class="hide">
<div class="card">
<h3>Trợ lý AI</h3>
<div class="note" id="aist">Hỏi về combo nhân vật hoặc độ nhạy. Trợ lý biết bạn đang chọn máy và bộ số nào ở tab Độ nhạy.</div>
<div class="filters" id="sg"></div>
<div id="msgs"></div>
<div class="fld"><textarea class="in" id="ask" rows="2" placeholder="Nhập câu hỏi của bạn..."></textarea></div>
<button class="btn" id="send">Gửi câu hỏi</button>
</div>
</section>
</div>

<script>
var $=function(i){return document.getElementById(i)};
var chars={
Alok:["Drop the Beat","Tạo vùng hồi máu và tăng tốc độ di chuyển cho bạn và đồng đội."],
Chrono:["Time Turner","Dựng khiên chắn sát thương phía trước và giúp di chuyển nhanh hơn."],
Wukong:["Camouflage","Hóa thành bụi cây để ẩn mình và áp sát hoặc quan sát."],
Skyler:["Riot Buster","Phát sóng âm phá tường gloo của địch."],
Dimitri:["Healing Heartbeat","Tạo vùng hồi phục cho đội khi cố thủ."],
Jota:["Sustained Raids","Hồi máu khi hạ gục địch bằng súng tiểu liên hoặc shotgun."],
Hayato:["Bushido","Tăng xuyên giáp khi máu của bạn càng thấp."],
Kelly:["Dash","Tăng tốc độ chạy nước rút."],
Moco:["Hacker's Eye","Đánh dấu địch bị bạn bắn trúng để cả đội nhìn thấy."],
"D-Bee":["Bullet Beats","Giúp di chuyển và bắn ổn định hơn trong giao tranh."],
Luqueta:["Hat Trick","Tăng máu tối đa mỗi khi hạ gục địch."],
Maxim:["Gluttony","Dùng vật phẩm hồi máu nhanh hơn."],
Joseph:["Nutty Movement","Tăng tốc độ di chuyển."],
Iris:["Dimension","Hỗ trợ đối phó tường gloo."]
};
var combos=[
{n:"Xung phong áp sát",t:"rush",m:"Xếp hạng, Đấu đội",c:["Chrono","Jota","Hayato","Kelly"],how:"Dựng khiên Chrono rồi chạy vào bằng Kelly. Giữ súng tiểu liên hoặc shotgun để Jota hồi máu sau mỗi lần hạ gục. Khi máu thấp, Hayato giúp bạn vẫn gây sát thương tốt.",good:"Vừa chắc vừa nhanh, hợp giao tranh gần và đẩy nhà.",bad:"Phụ thuộc vào việc bạn chủ động hạ gục. Đứng xa và bắn tỉa sẽ lãng phí cả bộ.",alt:"Thay Kelly bằng Moco nếu muốn thêm thông tin vị trí địch."},
{n:"Cân bằng, dễ dùng nhất",t:"rank",m:"Xếp hạng, Solo",c:["Alok","Jota","Hayato","Kelly"],how:"Bật Alok khi vào giao tranh hoặc khi cần đổi vị trí để vừa hồi máu vừa chạy nhanh. Jota và Hayato lo phần đánh gần, Kelly giúp xoay vòng khi bo thu hẹp.",good:"Dùng được ở hầu hết tình huống, phù hợp người mới.",bad:"Không có khiên như Chrono, dễ thiệt khi bị đánh úp từ xa.",alt:"Thay Hayato bằng Moco để biết địch ở đâu, hoặc bằng Maxim để hồi máu nhanh hơn."},
{n:"Do thám và đánh gần",t:"rush",m:"Xếp hạng",c:["Alok","Hayato","Kelly","Moco"],how:"Bắn trúng một phát để Moco đánh dấu địch, cả đội sẽ thấy vị trí. Sau đó vào bằng tốc độ của Alok và Kelly, Hayato lo phần xuyên giáp khi máu tụt.",good:"Có thông tin và có tốc độ, hợp đội phối hợp qua mic.",bad:"Không có nhiều hồi máu khi hạ gục như Jota, nên cần dùng vật phẩm thường xuyên.",alt:"Thay Hayato bằng Jota nếu muốn hồi máu khi đánh."},
{n:"Bắn tỉa, đánh xa",t:"snipe",m:"Xếp hạng, Solo",c:["Wukong","Moco","Jota","Kelly"],how:"Dùng Wukong để lén đổi vị trí hoặc quan sát từ bụi cây. Moco đánh dấu địch sau phát bắn đầu, Kelly giúp rút nhanh sau khi bắn.",good:"Giữ khoảng cách, ít phải lộ mặt.",bad:"Hạ gục từ xa ít khi kích hoạt Jota, nên hồi máu yếu.",alt:"Thay Jota bằng Laura nếu bạn chủ yếu dùng súng bắn tỉa."},
{n:"Phá tường gloo",t:"gloo",m:"Đấu đội",c:["Skyler","D-Bee","Moco","Luqueta"],how:"Skyler phá tường gloo, Moco đánh dấu địch lộ diện, D-Bee giúp bạn di chuyển và bắn ổn định khi giao tranh gần. Luqueta tăng máu tối đa sau mỗi lần hạ gục.",good:"Khắc chế đội hay dựng tường gloo và cố thủ.",bad:"Ít tác dụng khi địch không dùng tường, tốc độ chạy không nổi bật.",alt:"Thay Luqueta bằng Iris để thêm khả năng đối phó tường gloo."},
{n:"Cố thủ, giữ vị trí",t:"def",m:"Xếp hạng, Đấu đội",c:["Alok","Dimitri","Luqueta","Maxim"],how:"Chọn điểm cao hoặc nhà chắc. Đặt Alok hoặc Dimitri tạo vùng hồi phục cho đội, Maxim giúp dùng hộp cứu thương nhanh, Luqueta giúp trụ lâu khi có hạ gục.",good:"Đội rất khó bị hạ khi cố thủ trong vòng cuối.",bad:"Di chuyển chậm và ít chủ động, không hợp đẩy giao tranh.",alt:"Thay Maxim bằng Kelly để có thêm tốc độ khi cần rút."},
{n:"Tốc độ tối đa",t:"speed",m:"Đấu đội, xoay vòng",c:["Kelly","Joseph","Alok","Iris"],how:"Dùng khi phải chạy bo xa hoặc muốn áp sát nhanh. Alok tăng tốc thêm và hồi máu, Iris hỗ trợ khi địch cản bằng tường gloo.",good:"Di chuyển nhanh nhất trong các bộ gợi ý, hợp đổi vị trí liên tục.",bad:"Sát thương và khả năng trụ khi bị bắn thấp hơn các bộ khác.",alt:"Thay Iris bằng Jota để hồi máu khi hạ gục."}
];
var cf=[["all","Tất cả"],["rush","Xung phong"],["rank","Cân bằng"],["snipe","Bắn tỉa"],["gloo","Phá gloo"],["def","Cố thủ"],["speed","Tốc độ"]],ft="all";
function drawC(){
 $("cf").innerHTML=cf.map(function(x){return '<button class="f '+(x[0]==ft?'on':'')+'" data-f="'+x[0]+'">'+x[1]+'</button>'}).join("");
 $("clist").innerHTML=combos.filter(function(c){return ft=="all"||c.t==ft}).map(function(c){
  var r=c.c.map(function(x,i){var a=chars[x];return '<div class="ch"><b>'+x[0]+'</b><div><strong>'+x+'</strong> <em>'+(i==0?"Chủ động":"Bị động")+' · '+a[0]+'</em><span>'+a[1]+'</span></div></div>'}).join("");
  return '<div class="card cc"><h3>'+c.n+'</h3><div class="mode">Hợp với: '+c.m+'</div><div class="roster">'+r+'</div><details><summary>Cách chơi chi tiết</summary><p><b>Cách chơi:</b> '+c.how+'</p><p><b>Điểm mạnh:</b> '+c.good+'</p><p><b>Điểm yếu:</b> '+c.bad+'</p><p><b>Thay thế:</b> '+c.alt+'</p></details></div>'}).join("");
}
$("cf").onclick=function(e){if(e.target.dataset.f){ft=e.target.dataset.f;drawC()}};

var devs=[
{n:"Chưa chọn (bỏ qua)",o:0,d:"Dùng bộ số gốc."},
{n:"iPhone nhỏ (mini, SE)",o:4,d:"Màn nhỏ, ít chỗ vuốt nên tăng độ nhạy."},
{n:"iPhone thường (khoảng 6.1 inch)",o:1,d:"Gần bộ số gốc."},
{n:"iPhone Plus / Pro Max (khoảng 6.7 inch)",o:-2,d:"Màn lớn, vuốt rộng nên giảm nhẹ."},
{n:"iPad / máy tính bảng",o:-7,d:"Màn rất lớn, cần giảm nhiều để không bay tâm."},
{n:"Samsung Galaxy S / Ultra",o:-1,d:"Màn lớn, thường mượt. Giảm nhẹ."},
{n:"Samsung A, Xiaomi, Redmi, Realme, Oppo, Vivo",o:0,d:"Tầm trung, giữ bộ số gốc rồi tinh chỉnh."},
{n:"Máy gaming (ROG, Red Magic...)",o:-2,d:"Phản hồi cảm ứng nhanh nên có thể giảm nhẹ."},
{n:"Máy cũ hoặc cấu hình yếu",o:-3,d:"Dễ giật lag, giảm để dễ kiểm soát."}
];
var hzs=[["60 Hz",0],["90 Hz",-1],["120 Hz",-2],["144 Hz trở lên",-3]];
var db=[];
function A(a,i){a.forEach(function(n){db.push([n,i])})}
function R(p,a,s,i){a.forEach(function(k){s.forEach(function(x){db.push([p+k+x,i])})})}
R("iPhone ",[11,12,13,14,15,16],["",  " Pro"],2);
R("iPhone ",[11,12,13,14,15,16],[" Pro Max"],3);
R("iPhone ",[14,15,16],[" Plus"],3);
A(["iPhone SE","iPhone 12 mini","iPhone 13 mini"],1);
A(["iPhone 6","iPhone 7","iPhone 8","Redmi 9A","Galaxy J7"],8);
A(["iPad","iPad Air","iPad Pro","iPad mini"],4);
R("Galaxy S",[20,21,22,23,24,25],["","+"," Ultra"],5);
R("Galaxy A",[12,13,14,15,23,24,25,32,33,34,35,52,53,54,55,56],[""],6);
R("Redmi Note ",[10,11,12,13,14],[""],6);
A(["POCO X5","POCO X6","POCO X7","POCO F5","POCO F6","Realme 8","Realme 9","Realme 10","Realme 11","Realme 12","Realme 13","Oppo Reno 8","Oppo Reno 10","Oppo Reno 11","Oppo Reno 12","Oppo A57","Oppo A58","Oppo A78","Vivo Y21","Vivo Y27","Vivo V25","Vivo V27","Vivo V29"],6);
R("ROG Phone ",[6,7,8,9],[""],7);
A(["Red Magic 8 Pro","Red Magic 9 Pro","Red Magic 10 Pro"],7);
$("dl").innerHTML=db.map(function(m){return '<option value="'+m[0]+'">'}).join("");
$("dev").innerHTML=devs.map(function(d,i){return '<option value="'+i+'">'+d.n+'</option>'}).join("");
$("hz").innerHTML=hzs.map(function(h,i){return '<option value="'+i+'"'+(i==1?" selected":"")+'>'+h[0]+'</option>'}).join("");
var nm=function(s){return s.toLowerCase().replace(/\s+/g,"")};

var names=["Tổng quát","Red Dot","Ống ngắm 2x","Ống ngắm 4x","AWM","Nhìn tự do"];
var presets={drag:{l:"Kéo tâm mạnh",v:[95,92,88,84,60,68]},bal:{l:"Cân bằng",v:[88,85,80,75,55,62]},far:{l:"Bắn xa, chắc tay",v:[80,76,72,66,48,56]}};
var sp="bal",off=0,dv=0,hv=1;
function tot(){return off+devs[dv].o+hzs[hv][1]}
function sg(n){return (n>0?"+":"")+n}
function cl(n){return Math.max(0,Math.min(100,n))}
function drawS(){
 $("sf").innerHTML=Object.keys(presets).map(function(k){return '<button class="f '+(k==sp?'on':'')+'" data-p="'+k+'">'+presets[k].l+'</button>'}).join("");
 $("tiles").innerHTML=presets[sp].v.map(function(v,i){var x=cl(v+tot());return '<div class="tile"><small>'+names[i]+'</small><div class="n">'+x+'</div><div class="bar"><i style="width:'+x+'%"></i></div></div>'}).join("");
 $("off").textContent=sg(off);
 $("tot").textContent=devs[dv].d+" Tổng điều chỉnh: "+sg(tot())+" điểm (máy "+sg(devs[dv].o)+", tần số quét "+sg(hzs[hv][1])+", chỉnh tay "+sg(off)+").";
}
$("sf").onclick=function(e){if(e.target.dataset.p){sp=e.target.dataset.p;drawS()}};
$("slider").oninput=function(e){off=+e.target.value;drawS()};
$("dev").onchange=function(e){dv=+e.target.value;drawS()};
$("hz").onchange=function(e){hv=+e.target.value;drawS()};
$("q").oninput=function(e){
 var q=nm(e.target.value),r=$("res");
 if(!q){r.className="res";r.textContent="Chưa nhập tên máy.";return}
 var m=db.filter(function(x){return nm(x[0])==q})[0]||db.filter(function(x){return nm(x[0]).indexOf(q)==0})[0];
 if(m){dv=m[1];$("dev").value=dv;r.className="res ok";r.textContent="Nhận diện: "+m[0]+" → nhóm "+devs[dv].n}
 else{r.className="res";r.textContent="Chưa có máy này trong danh sách. Bạn chọn nhóm gần nhất ở ô bên dưới."}
 drawS();
};
$("copy").onclick=function(){
 var t=presets[sp].v.map(function(v,i){return names[i]+": "+cl(v+tot())}).join("\n"),b=$("copy");
 function ok(){b.textContent="Đã sao chép";setTimeout(function(){b.textContent="Sao chép bộ độ nhạy"},1500)}
 try{navigator.clipboard.writeText(t).then(ok,function(){b.textContent="Không sao chép được"})}catch(x){b.textContent="Không sao chép được"}
};

var hist=[],busy=false;
var sugg=["Combo nào hợp cho người mới?","Khác nhau giữa Alok và Chrono?","Mình nên chỉnh độ nhạy thế nào nếu tâm hay bay quá đầu?"];
$("sg").innerHTML=sugg.map(function(x){return '<button class="f" data-q="'+x+'">'+x+'</button>'}).join("");
$("sg").onclick=function(e){if(e.target.dataset.q){$("ask").value=e.target.dataset.q;ask()}};
function pageData(){
 return JSON.stringify({combo:combos.map(function(c){return {ten:c.n,nhanVat:c.c,hopVoi:c.m}}),doNhay:{kieu:presets[sp].l,dongMay:devs[dv].n,tanSoQuet:hzs[hv][0],so:presets[sp].v.map(function(v,i){return names[i]+": "+cl(v+tot())})}});
}
function add(r,t){var d=document.createElement("div");d.className="msg "+r;d.textContent=t;$("msgs").appendChild(d);return d}
function ask(){
 var q=$("ask").value.trim();
 if(!q||busy)return;
 $("ask").value="";add("u",q);hist.push({r:"user",t:q});busy=true;$("send").textContent="Đang trả lời...";
 var msgs=hist.slice(-9).map(function(m){return {role:m.r,content:m.t}});
 var b=add("a","...");
 fetch("/api/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({messages:msgs,data:pageData()})})
 .then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j}})})
 .then(function(o){if(!o.ok)throw o.j;b.textContent=o.j.text;hist.push({r:"assistant",t:o.j.text})})
 .catch(function(e){hist.pop();b.textContent=(e&&e.error)||"Không kết nối được máy chủ. Bạn kiểm tra app.py còn chạy không."})
 .then(function(){busy=false;$("send").textContent="Gửi câu hỏi"});
}
$("send").onclick=ask;
document.querySelector(".tabs").onclick=function(e){
 var t=e.target.dataset.t;if(!t)return;
 document.querySelectorAll(".tab").forEach(function(b){b.classList.toggle("on",b.dataset.t==t)});
 $("combo").classList.toggle("hide",t!="combo");$("sens").classList.toggle("hide",t!="sens");$("ai").classList.toggle("hide",t!="ai");
};
drawC();drawS();
</script>
</body>
</html>
"""


def too_many(ip):
    now = time.time()
    q = _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= MAX_PER_MINUTE:
        return True
    q.append(now)
    return False


@app.get("/")
def index():
    return Response(PAGE, mimetype="text/html")


@app.post("/api/ask")
def ask():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return jsonify(error="Máy chủ chưa có ANTHROPIC_API_KEY. Hãy đặt biến môi trường rồi chạy lại app.py."), 503
    if too_many(request.remote_addr or "?"):
        return jsonify(error="Bạn hỏi hơi nhanh, đợi một chút rồi thử lại nhé."), 429

    body = request.get_json(silent=True) or {}
    raw = body.get("messages")
    if not isinstance(raw, list):
        return jsonify(error="Yêu cầu không hợp lệ."), 400

    msgs = []
    for m in raw[-9:]:
        if not isinstance(m, dict):
            continue
        role, content = m.get("role"), m.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            msgs.append({"role": role, "content": content[:1000]})
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    if not msgs or msgs[-1]["role"] != "user":
        return jsonify(error="Yêu cầu không hợp lệ."), 400

    data = body.get("data")
    data = data[:4000] if isinstance(data, str) else ""
    system = SYSTEM + "\n\nDữ liệu trên trang: " + data

    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(model=MODEL, max_tokens=700, system=system, messages=msgs)
    except anthropic.RateLimitError:
        return jsonify(error="API đang bị giới hạn tốc độ, bạn thử lại sau ít phút."), 429
    except anthropic.AuthenticationError:
        return jsonify(error="Khóa API không đúng hoặc đã hết hạn."), 401
    except anthropic.APIError:
        return jsonify(error="Không gọi được trợ lý lúc này, bạn thử lại sau."), 502

    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    return jsonify(text=text or "Mình chưa có câu trả lời, bạn hỏi lại thử nhé.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
