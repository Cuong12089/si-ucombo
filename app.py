"""
Free Fire: Combo và Độ nhạy - bản Streamlit.

Cách chạy:
    pip install streamlit anthropic
    export ANTHROPIC_API_KEY="khóa-api-của-bạn"   # Windows PowerShell: $env:ANTHROPIC_API_KEY="AQ.Ab8RN6KNdbCWRNI3NNYyFEzMvIIBy0XqdF2YuMmUsJ7WvORPYg"
    streamlit run streamlit_app.py

Hoặc đặt khóa trong file .streamlit/secrets.toml:
    ANTHROPIC_API_KEY = "khóa-api-của-bạn"

Không dán khóa vào file này và không đưa file chứa khóa lên GitHub.
Đổi model bằng biến môi trường ANTHROPIC_MODEL nếu cần.
"""
import json
import os

import anthropic
import streamlit as st

st.set_page_config(page_title="Free Fire: Combo và Độ nhạy", page_icon="🔥")

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
st.title("🔥 Free Fire: Combo và Độ nhạy")
st.caption("Chọn combo hợp lối chơi, chỉnh độ nhạy theo đúng máy của bạn.")
tab1, tab2, tab3 = st.tabs(["Combo nhân vật", "Độ nhạy", "Trợ lý AI"])

with tab1:
    pick = st.radio("Lối chơi", list(FILTERS), horizontal=True)
    for c in COMBOS:
        if FILTERS[pick] and c["t"] != FILTERS[pick]:
            continue
        with st.container(border=True):
            st.subheader(c["n"])
            st.caption("Hợp với: " + c["m"])
            cols = st.columns(2)
            for i, ch in enumerate(c["c"]):
                skill, desc = CHARS[ch]
                role = "Chủ động" if i == 0 else "Bị động"
                cols[i % 2].markdown(f"**{ch}** · {role} · *{skill}*  \n{desc}")
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
    cols = st.columns(3)
    for i, (name, v) in enumerate(zip(NAMES, values)):
        with cols[i % 3]:
            st.metric(name, v)
            st.progress(v / 100)
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
