# pip install flask flask-socketio qrcode[pil]
"""
현용이의 퀴즈 마을 - 실시간 단체 퀴즈 시스템
서버: app.py
"""

import html
import io
import base64
import time
import threading
import uuid
import random

from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import qrcode

# ──────────────────────────────────────────────────────────────────────────────
# ★ 설정값 변수 (게임 밸런스 조정 시 이 값만 수정하세요)
# ──────────────────────────────────────────────────────────────────────────────
ADMIN_NAME      = "이현용"  # 이 이름으로 입장 시 관리자 권한 부여
QUESTION_TIME   = 5    # 문제 풀이 제한 시간 (초)
RANKING_TIME    = 5    # 정답+랭킹 노출 시간 (초)
FINAL_WAIT_TIME = 20   # 최종 결과 후 대기실 복귀 시간 (초)
COUNTDOWN_TIME  = 3    # TOP3 발표 전 카운트다운 시간 (초)
BASE_SCORE      = 100  # 정답 기본 점수
BONUS_MAX       = 20   # 빠른 정답 최대 보너스 점수

# ──────────────────────────────────────────────────────────────────────────────
# ★ 문제 은행 (주제별 / 난이도별 10문제씩)
# ──────────────────────────────────────────────────────────────────────────────
QUIZ_BANK = {
    "상식": {
        "상": [
            {"q": "세계에서 가장 긴 강은?",
             "options": ["나일강", "아마존강", "양쯔강", "미시시피강"], "a": 0},
            {"q": "인간의 뇌 무게는 평균 약 몇 kg인가?",
             "options": ["1.0 kg", "1.4 kg", "2.0 kg", "0.8 kg"], "a": 1},
            {"q": "빛의 속도는 약 초속 몇 km인가?",
             "options": ["100,000 km", "200,000 km", "300,000 km", "400,000 km"], "a": 2},
            {"q": "원소기호 'Au'는 무슨 원소인가?",
             "options": ["은(Ag)", "알루미늄(Al)", "금(Au)", "구리(Cu)"], "a": 2},
            {"q": "태양계에서 가장 큰 행성은?",
             "options": ["토성", "천왕성", "목성", "해왕성"], "a": 2},
            {"q": "인체에서 가장 긴 뼈는?",
             "options": ["척추", "대퇴골(넓적다리뼈)", "상완골", "경골"], "a": 1},
            {"q": "DNA 이중나선 구조가 처음 발표된 해는?",
             "options": ["1943년", "1953년", "1963년", "1973년"], "a": 1},
            {"q": "지구에서 달까지의 평균 거리는?",
             "options": ["약 28만 km", "약 38만 km", "약 48만 km", "약 58만 km"], "a": 1},
            {"q": "물의 끓는점은 1기압에서 몇 도인가?",
             "options": ["90°C", "95°C", "100°C", "105°C"], "a": 2},
            {"q": "주기율표에서 원자번호 1번 원소는?",
             "options": ["헬륨(He)", "리튬(Li)", "수소(H)", "탄소(C)"], "a": 2},
        ],
        "하": [
            {"q": "대한민국의 수도는?",
             "options": ["부산", "서울", "인천", "대구"], "a": 1},
            {"q": "무지개는 몇 가지 색으로 이루어져 있는가?",
             "options": ["5가지", "6가지", "7가지", "8가지"], "a": 2},
            {"q": "물의 화학식은?",
             "options": ["CO₂", "O₂", "H₂O", "NaCl"], "a": 2},
            {"q": "하루는 몇 시간인가?",
             "options": ["12시간", "24시간", "36시간", "48시간"], "a": 1},
            {"q": "지구는 태양계에서 몇 번째 행성인가?",
             "options": ["1번째", "2번째", "3번째", "4번째"], "a": 2},
            {"q": "사람의 눈은 몇 개인가?",
             "options": ["1개", "2개", "3개", "4개"], "a": 1},
            {"q": "태양은 어느 방향에서 뜨는가?",
             "options": ["서쪽", "남쪽", "동쪽", "북쪽"], "a": 2},
            {"q": "1년은 몇 개월인가?",
             "options": ["10개월", "11개월", "12개월", "13개월"], "a": 2},
            {"q": "사람의 손가락은 총 몇 개인가?",
             "options": ["8개", "9개", "10개", "12개"], "a": 2},
            {"q": "한국의 국기 이름은?",
             "options": ["일장기", "성조기", "태극기", "삼색기"], "a": 2},
        ],
    },
    "역사": {
        "상": [
            {"q": "조선을 건국한 인물은?",
             "options": ["이성계", "왕건", "견훤", "궁예"], "a": 0},
            {"q": "임진왜란이 시작된 해는?",
             "options": ["1382년", "1492년", "1592년", "1692년"], "a": 2},
            {"q": "세종대왕이 훈민정음을 반포한 해는?",
             "options": ["1343년", "1443년", "1446년", "1543년"], "a": 2},
            {"q": "프랑스 혁명이 일어난 해는?",
             "options": ["1769년", "1779년", "1789년", "1799년"], "a": 2},
            {"q": "제1차 세계대전이 시작된 해는?",
             "options": ["1904년", "1914년", "1924년", "1934년"], "a": 1},
            {"q": "3·1 운동이 일어난 해는?",
             "options": ["1909년", "1919년", "1929년", "1939년"], "a": 1},
            {"q": "거북선을 만든 장군은?",
             "options": ["강감찬", "을지문덕", "이순신", "권율"], "a": 2},
            {"q": "고구려를 세운 인물은?",
             "options": ["박혁거세", "주몽", "온조", "김수로"], "a": 1},
            {"q": "조선의 마지막 왕은?",
             "options": ["고종", "순종", "철종", "헌종"], "a": 1},
            {"q": "한국의 광복절은 몇 월 며칠인가?",
             "options": ["7월 15일", "8월 15일", "9월 15일", "10월 15일"], "a": 1},
        ],
        "하": [
            {"q": "대한민국의 첫 번째 대통령은?",
             "options": ["박정희", "이승만", "윤보선", "최규하"], "a": 1},
            {"q": "한국전쟁이 시작된 해는?",
             "options": ["1945년", "1948년", "1950년", "1953년"], "a": 2},
            {"q": "세종대왕이 만든 우리나라 고유 문자는?",
             "options": ["한자", "가나", "한글", "한문"], "a": 2},
            {"q": "고조선을 세운 인물은?",
             "options": ["단군왕검", "주몽", "이성계", "왕건"], "a": 0},
            {"q": "신라의 수도는?",
             "options": ["평양", "한성", "경주", "개성"], "a": 2},
            {"q": "고려를 세운 인물은?",
             "options": ["이성계", "왕건", "궁예", "견훤"], "a": 1},
            {"q": "한국의 국경일인 '개천절'은 몇 월 며칠인가?",
             "options": ["10월 1일", "10월 3일", "10월 5일", "10월 9일"], "a": 1},
            {"q": "일제강점기에서 해방된 연도는?",
             "options": ["1943년", "1944년", "1945년", "1946년"], "a": 2},
            {"q": "조선시대 최상위 신분 계급은?",
             "options": ["중인", "상민", "양반", "천민"], "a": 2},
            {"q": "삼국시대에 속하지 않는 나라는?",
             "options": ["고구려", "백제", "신라", "발해"], "a": 3},
        ],
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# Flask 앱 초기화
# ──────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "hyeonjun-quiz-secret-key-change-in-production"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ──────────────────────────────────────────────────────────────────────────────
# 게임 룸 상태 저장소  { room_id → room_data }
# ──────────────────────────────────────────────────────────────────────────────
rooms       = {}
room_lock   = threading.Lock()
sid_to_room = {}   # { socket_sid: room_id } — session 대신 사용 (WebSocket 환경에서 session 수정 미지속 문제 해결)


# ──────────────────────────────────────────────────────────────────────────────
# 유틸리티 함수
# ──────────────────────────────────────────────────────────────────────────────
def generate_room_id() -> str:
    """짧고 입력하기 쉬운 6자리 방 ID 생성"""
    return str(uuid.uuid4())[:6].upper()


def generate_qr_code(url: str) -> str:
    """URL을 QR 코드 이미지로 변환 후 base64 문자열로 반환"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a2e", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def get_ranking(room: dict) -> list:
    """현재 점수 기준 내림차순 랭킹 리스트 반환"""
    return sorted(
        [{"name": p["name"], "score": p["score"]} for p in room["players"].values()],
        key=lambda x: x["score"],
        reverse=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# HTTP 라우트
# ──────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """메인 페이지 (이름 기반 관리자 판별 — index1.html 사용)"""
    return render_template("index1.html")


@app.route("/join/<room_id>")
def join_game_link(room_id):
    """플레이어 초대 링크 — 방코드 클라이언트에 노출 없이 그냥 메인 화면으로 이동"""
    return render_template("index1.html")


# ──────────────────────────────────────────────────────────────────────────────
# Socket.io 이벤트 핸들러
# ──────────────────────────────────────────────────────────────────────────────
@socketio.on("connect")
def handle_connect():
    """클라이언트 연결 확인"""
    print(f"[INFO] 클라이언트 연결: {request.sid}")


@socketio.on("create_room")
def handle_create_room():
    """관리자 전용: 새 게임 방 생성 및 QR 코드 발급"""
    if not session.get("is_admin"):
        emit("error", {"message": "관리자만 방을 생성할 수 있습니다."})
        return

    room_id = generate_room_id()
    with room_lock:
        rooms[room_id] = {
            "players":            {},     # { sid: { name, score, answered } }
            "status":             "waiting",  # waiting | playing | finished
            "current_question":   -1,
            "questions":          [],
            "answers_received":   set(),
            "question_start_time": None,
            "phase":              0,     # 타이머 레이스 컨디션 방지용 버전 카운터
            "topic":              "상식",
            "difficulty":         "하",
            "admin_sid":          request.sid,
        }

    sid_to_room[request.sid] = room_id
    join_room(room_id)

    host = request.host
    join_url = f"http://{host}/join/{room_id}"
    qr_data = generate_qr_code(join_url)

    emit("room_created", {
        "room_id":  room_id,
        "join_url": join_url,
        "qr_code":  qr_data,
    })


@socketio.on("join_game")
def handle_join_game(data):
    """이름 기반 입장 처리 — ADMIN_NAME 입력 시 관리자 권한 부여"""
    room_id  = str(data.get("room_id", "")).upper().strip()
    raw_name = str(data.get("name", "")).strip()
    name     = html.escape(raw_name)          # XSS 방지
    is_admin = (raw_name == ADMIN_NAME)        # 원본 이름으로 비교

    # ── 이름 검증 ─────────────────────────────────────────────────
    if not name:
        emit("join_error", {"message": "이름을 입력해주세요."})
        return
    if len(name) > 20:
        emit("join_error", {"message": "이름은 20자 이하여야 합니다."})
        return

    # ── room_id 결정 ──────────────────────────────────────────────
    error_msg = None   # lock 안에서 에러 메시지 수집 → lock 밖에서 emit

    if not room_id:
        with room_lock:
            waiting = [rid for rid, r in rooms.items() if r["status"] == "waiting"]
            if waiting:
                room_id = waiting[0]
            elif is_admin:
                # 관리자가 처음 입장: 방 자동 생성
                room_id = generate_room_id()
                rooms[room_id] = {
                    "players":             {},
                    "status":              "waiting",
                    "current_question":    -1,
                    "questions":           [],
                    "answers_received":    set(),
                    "question_start_time": None,
                    "phase":               0,
                    "topic":               "상식",
                    "difficulty":          "하",
                    "admin_sid":           request.sid,
                }
            else:
                error_msg = f"아직 방이 없습니다. '{ADMIN_NAME}'님의 입장을 기다려주세요."

    if error_msg:
        emit("join_error", {"message": error_msg})
        return

    # ── 방 상태 검증 및 플레이어 등록 (lock 안) ──────────────────
    with room_lock:
        if room_id not in rooms:
            error_msg = "존재하지 않는 방입니다."
        else:
            room = rooms[room_id]
            if room["status"] != "waiting":
                error_msg = "게임이 이미 진행 중입니다."
            else:
                for p in room["players"].values():
                    if p["name"] == name:
                        error_msg = "이미 사용 중인 이름입니다."
                        break
                if not error_msg:
                    room["players"][request.sid] = {
                        "name":     name,
                        "score":    0,
                        "answered": False,
                        "is_admin": is_admin,
                    }
                    if is_admin:
                        room["admin_sid"] = request.sid   # 관리자 SID 갱신

    # ── lock 밖에서 에러 emit ────────────────────────────────────
    if error_msg:
        emit("join_error", {"message": error_msg})
        return

    # ── join_room & sid_to_room 등록 (lock 밖) ───────────────────
    sid_to_room[request.sid] = room_id
    join_room(room_id)

    # 관리자에게만 QR 코드 생성 (라이브러리 미설치 시 graceful fallback)
    qr_data  = None
    join_url = None
    if is_admin:
        host     = request.host
        join_url = f"http://{host}/join/{room_id}"
        try:
            qr_data = generate_qr_code(join_url)
        except Exception as e:
            print(f"[WARN] QR 코드 생성 실패 (qrcode 라이브러리 확인): {e}")
            qr_data = None

    players_list = [p["name"] for p in rooms[room_id]["players"].values()]
    emit("join_success", {
        "name":     name,
        "room_id":  room_id,
        "is_admin": is_admin,
        "join_url": join_url,
        "qr_code":  qr_data,
    })
    emit("player_list_update", {"players": players_list}, to=room_id)


@socketio.on("start_game")
def handle_start_game(data):
    """관리자 전용: 게임 시작 — 이름 기반 권한 검증"""
    room_id = sid_to_room.get(request.sid)
    if not room_id or room_id not in rooms:
        return

    room   = rooms[room_id]
    sid    = request.sid
    player = room["players"].get(sid, {})

    # ── 이중 보안: admin_sid 일치 + is_admin 플래그 확인 ─────────
    if room.get("admin_sid") != sid or not player.get("is_admin"):
        return   # 관리자가 아닌 사용자 emit 무시

    if room["status"] != "waiting":
        emit("error", {"message": "이미 게임이 시작되었습니다."})
        return

    topic      = str(data.get("topic",      "상식"))
    difficulty = str(data.get("difficulty", "하"))

    if topic not in QUIZ_BANK or difficulty not in QUIZ_BANK.get(topic, {}):
        emit("error", {"message": "잘못된 주제 또는 난이도입니다."})
        return

    with room_lock:
        room["topic"]            = topic
        room["difficulty"]       = difficulty
        room["questions"]        = random.sample(
            QUIZ_BANK[topic][difficulty],
            len(QUIZ_BANK[topic][difficulty])
        )
        room["status"]           = "playing"
        room["current_question"] = -1
        room["phase"]            = 0

        # 모든 플레이어 점수 초기화
        for sid in room["players"]:
            room["players"][sid]["score"]    = 0
            room["players"][sid]["answered"] = False

    socketio.emit("game_starting", {
        "topic":           topic,
        "difficulty":      difficulty,
        "total_questions": len(room["questions"]),
    }, to=room_id)

    def delayed_start():
        time.sleep(2)
        _next_question(room_id, 0)

    threading.Thread(target=delayed_start, daemon=True).start()


@socketio.on("submit_answer")
def handle_submit_answer(data):
    """플레이어 답변 제출 (소켓 세션당 문제당 1회만 수락)"""
    room_id = sid_to_room.get(request.sid)
    if not room_id or room_id not in rooms:
        return

    room = rooms[room_id]
    sid  = request.sid

    if room["status"] != "playing":
        return
    if sid not in room["players"]:
        return

    # ── 중복 제출 방지 ────────────────────────────────────────────
    if sid in room["answers_received"]:
        return

    q_index = data.get("question_index", -1)
    if q_index != room["current_question"]:
        return   # 이전·이후 문제의 응답 무시

    answer = data.get("answer")
    if answer is None:
        return

    room["answers_received"].add(sid)

    question   = room["questions"][q_index]
    is_correct = (int(answer) == question["a"])

    if is_correct:
        elapsed   = time.time() - room["question_start_time"]
        remaining = max(0.0, QUESTION_TIME - elapsed)
        bonus     = int(BONUS_MAX * (remaining / QUESTION_TIME))
        gained    = BASE_SCORE + bonus
        room["players"][sid]["score"] += gained
        emit("answer_result", {
            "correct":       True,
            "score_gained":  gained,
            "correct_index": question["a"],
        })
    else:
        emit("answer_result", {
            "correct":       False,
            "score_gained":  0,
            "correct_index": question["a"],
        })


@socketio.on("disconnect")
def handle_disconnect():
    """연결 해제 시 플레이어 목록에서 제거"""
    sid     = request.sid
    room_id = sid_to_room.pop(sid, None)   # sid_to_room에서 제거 + room_id 회수
    if not room_id or room_id not in rooms:
        return

    room = rooms[room_id]

    if sid in room["players"]:
        with room_lock:
            room["players"].pop(sid, None)
            room["answers_received"].discard(sid)

        players_list = [p["name"] for p in room["players"].values()]
        socketio.emit("player_list_update", {"players": players_list}, to=room_id)


# ──────────────────────────────────────────────────────────────────────────────
# 내부 게임 흐름 함수 (백그라운드 스레드에서 호출)
# ──────────────────────────────────────────────────────────────────────────────
def _next_question(room_id: str, expected_phase: int):
    """다음 문제로 진행하거나 게임 종료를 처리"""
    if room_id not in rooms:
        return

    room = rooms[room_id]
    if room["phase"] != expected_phase:
        return   # 오래된(stale) 타이머 스레드 무시

    room["current_question"] += 1
    q_index = room["current_question"]

    if q_index >= len(room["questions"]):
        _show_final_countdown(room_id, expected_phase)
        return

    question = room["questions"][q_index]

    # 이번 문제 답변 상태 초기화
    room["answers_received"]   = set()
    room["question_start_time"] = time.time()

    socketio.emit("show_question", {
        "question_number": q_index + 1,
        "total_questions": len(room["questions"]),
        "question":        question["q"],
        "options":         question["options"],
        "time_limit":      QUESTION_TIME,
        "question_index":  q_index,
    }, to=room_id)

    # QUESTION_TIME 초 후 자동으로 정답+랭킹 표시
    def auto_show_answer():
        time.sleep(QUESTION_TIME)
        _show_answer(room_id, q_index, expected_phase)

    threading.Thread(target=auto_show_answer, daemon=True).start()


def _show_answer(room_id: str, q_index: int, expected_phase: int):
    """정답과 실시간 랭킹 표시 (RANKING_TIME 초 후 다음 문제로 자동 전환)"""
    if room_id not in rooms:
        return

    room = rooms[room_id]
    if room["phase"] != expected_phase:
        return
    if room["current_question"] != q_index:
        return

    question = room["questions"][q_index]
    ranking  = get_ranking(room)

    socketio.emit("show_answer", {
        "correct_index": question["a"],
        "correct_text":  question["options"][question["a"]],
        "ranking":       ranking[:10],
        "time_limit":    RANKING_TIME,
    }, to=room_id)

    def auto_next():
        time.sleep(RANKING_TIME)
        _next_question(room_id, expected_phase)

    threading.Thread(target=auto_next, daemon=True).start()


def _show_final_countdown(room_id: str, expected_phase: int):
    """TOP3 발표 전 긴장감 넘치는 카운트다운 → 최종 결과 표시"""
    if room_id not in rooms:
        return

    room = rooms[room_id]
    if room["phase"] != expected_phase:
        return

    room["status"] = "finished"
    socketio.emit("final_countdown_start", {"countdown": COUNTDOWN_TIME}, to=room_id)

    def reveal_results():
        time.sleep(COUNTDOWN_TIME)
        if room_id not in rooms:
            return

        ranking = get_ranking(rooms[room_id])
        socketio.emit("show_final_results", {
            "ranking":   ranking,
            "wait_time": FINAL_WAIT_TIME,
        }, to=room_id)

        def auto_reset():
            time.sleep(FINAL_WAIT_TIME)
            if room_id not in rooms:
                return
            # 방 초기화 (재사용 가능하도록)
            with room_lock:
                rooms[room_id]["status"]           = "waiting"
                rooms[room_id]["current_question"] = -1
                rooms[room_id]["questions"]        = []
                rooms[room_id]["phase"]            += 1
            socketio.emit("redirect_to_lobby", {}, to=room_id)

        threading.Thread(target=auto_reset, daemon=True).start()

    threading.Thread(target=reveal_results, daemon=True).start()


# ──────────────────────────────────────────────────────────────────────────────
# 서버 실행
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=5000,
        allow_unsafe_werkzeug=True,
    )
