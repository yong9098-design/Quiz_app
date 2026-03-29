# 🎉 현용이의 퀴즈 마을

실시간 WebSocket(Socket.io) 기반 단체 퀴즈 시스템

---

## 📁 프로젝트 구조

```
quiz_village/
├── app.py                  ← Flask 서버 (Socket.io 포함)
└── templates/
    └── index.html          ← 클라이언트 단일 페이지 앱
```

---

## ⚙️ 설치 및 실행

### 1. 패키지 설치

```bash
pip install flask flask-socketio qrcode[pil]
```

### 2. 서버 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

---

## 🔑 접속 방법

| 역할 | URL | 설명 |
|------|-----|------|
| 관리자 | `http://localhost:5000/admin` | 방 생성 · 게임 시작 |
| 플레이어 | `http://localhost:5000` | 방 코드 입력 후 입장 |
| 직접 입장 | `http://localhost:5000/join/<방코드>` | QR 코드 스캔 시 자동 이동 |

---

## 🎮 게임 흐름

1. 관리자가 `/admin` 접속 → **방 생성** → QR 코드 및 입장 URL 표시
2. 참가자가 URL/QR로 접속 → **실명 입력** → 대기실 입장
3. 관리자가 **주제 · 난이도 선택** 후 게임 시작
4. **문제(5초) → 정답+랭킹(5초)** 자동 반복 × 10문제
5. 전체 종료 후 3초 카운트다운 → **TOP 3 시상대 발표**
6. 20초 후 자동으로 대기실 복귀

---

## 🛡️ 보안 기능

- XSS 방지: 서버에서 `html.escape()` 처리
- 중복 제출 방지: 소켓 세션당 문제당 1회 수락
- 관리자 이벤트 보호: `session['is_admin']` + `admin_sid` 이중 검증
- 방 격리: Socket.io `room` 기능으로 세션 격리

---

## ⚡ 채점 방식

- 정답 시 기본 **100점** + 빠를수록 최대 **+20점** 보너스
- 오답 또는 무응답은 **0점**
- 보너스 계산식: `bonus = 20 × (남은시간 / 제한시간)`

---

## 🔧 설정값 변경 (app.py 상단)

```python
QUESTION_TIME    = 5    # 문제 풀이 제한 시간 (초)
RANKING_TIME     = 5    # 정답+랭킹 노출 시간 (초)
FINAL_WAIT_TIME  = 20   # 최종 결과 후 대기실 복귀 시간 (초)
COUNTDOWN_TIME   = 3    # TOP3 발표 전 카운트다운 시간 (초)
BASE_SCORE       = 100  # 정답 기본 점수
BONUS_MAX        = 20   # 빠른 정답 최대 보너스 점수
```

---

## 📚 문제 은행 구조

`app.py` 상단의 `QUIZ_BANK` 딕셔너리를 수정해 문제를 추가/변경할 수 있습니다.

```python
QUIZ_BANK = {
    "상식": {
        "상": [
            {"q": "문제 텍스트", "options": ["①", "②", "③", "④"], "a": 0},
            # a는 정답 인덱스 (0~3)
        ],
        "하": [ ... ]
    },
    "역사": {
        "상": [ ... ],
        "하": [ ... ]
    }
}
```
