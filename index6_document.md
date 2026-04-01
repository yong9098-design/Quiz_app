# index6.html — 변경사항 문서

> **기반 파일**: `index5.html` (Supabase Realtime v5)  
> **버전**: v6  
> **작성일**: 2026-04-01

---

## 목차

1. [변경 개요](#1-변경-개요)
2. [수정 사항 상세](#2-수정-사항-상세)
   - [2-1. view-game: 즉시 정답/오답 표시 제거](#2-1-view-game-즉시-정답오답-표시-제거)
   - [2-2. view-game: 답 선택 후 타이머 계속 진행](#2-2-view-game-답-선택-후-타이머-계속-진행)
   - [2-3. view-answer: 이번 문제 순위만 표시](#2-3-view-answer-이번-문제-순위만-표시)
   - [2-4. view-final: 변경 없음](#2-4-view-final-변경-없음)
   - [2-5. 배경 화면 밝기 개선](#2-5-배경-화면-밝기-개선)
3. [사운드 추가](#3-사운드-추가)
   - [3-1. 배경 반복 멜로디](#3-1-배경-반복-멜로디)
   - [3-2. 카운트다운 틱 사운드](#3-2-카운트다운-틱-사운드)
   - [3-3. 최종 결과 축하 사운드](#3-3-최종-결과-축하-사운드)
4. [코드 변경 위치 요약](#4-코드-변경-위치-요약)
5. [게임 흐름 비교](#5-게임-흐름-비교)

---

## 1. 변경 개요

| 항목 | v5 (이전) | v6 (변경 후) |
|------|-----------|-------------|
| 답 선택 즉시 피드백 | 정답/오답 오버레이 즉시 표시 | **표시 안 함** (view-answer에서 공개) |
| 답 선택 후 타이머 | 즉시 정지 | **계속 진행** |
| view-answer 랭킹 | 누적 점수 기준 | **이번 문제 득점 기준** (TOP 10) |
| view-final | 변경 없음 | 변경 없음 |
| 배경 색상 | 매우 어두운 네이비 계열 | **약간 밝은 블루/퍼플 계열** |
| 사운드 | 없음 | **3종 추가** (배경음·틱·축하음) |

---

## 2. 수정 사항 상세

### 2-1. view-game: 즉시 정답/오답 표시 제거

**변경 전** (`g_answer_result` 핸들러)
```javascript
case 'g_answer_result': {
  stopTimer();
  document.querySelectorAll('.option-btn').forEach((b, i) => {
    b.disabled = true;
    if (i === data.correctIndex)               b.classList.add('correct');
    else if (b.classList.contains('selected')) b.classList.add('wrong');
  });
  if (data.correct) S.myScore += data.scoreGained;
  const ov = _el('ans-overlay');
  ov.className = 'answer-overlay show ' + (data.correct ? 'correct-overlay' : 'wrong-overlay');
  // ...오버레이 텍스트 설정...
  break;
}
```

**변경 후**
```javascript
case 'g_answer_result': {
  // 즉시 정답/오답 표시 안 함, 타이머 계속 진행
  if (data.correct) S.myScore += data.scoreGained;
  break;
}
```

- 오버레이(정답/오답 표시) 제거
- `stopTimer()` 호출 제거 → 타이머 계속 진행
- 버튼 `.correct` / `.wrong` 클래스 즉시 적용 제거
- 점수는 내부적으로만 업데이트 (view-answer에서 정답 공개)

### 2-2. view-game: 답 선택 후 타이머 계속 진행

**변경 전** (`submitAnswer`)
```javascript
function submitAnswer(idx) {
  if (S.answered) return;
  S.answered = true;
  document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);
  document.querySelectorAll('.option-btn')[idx].classList.add('selected');
  // ...
}
```

**변경 후**
```javascript
function submitAnswer(idx) {
  if (S.answered) return;
  S.answered = true;
  document.querySelectorAll('.option-btn').forEach((b, i) => {
    b.disabled = true;
    if (i === idx) b.classList.add('waiting'); // 대기 펄스 애니메이션
  });
  // ...
}
```

- 선택한 버튼에 `.waiting` 클래스 적용 → 파란 펄스 애니메이션으로 "대기 중" 상태 표시
- 타이머는 `g_answer_result`에서 `stopTimer()`를 제거했으므로 자연스럽게 계속 진행

**신규 CSS** (`.option-btn.waiting`)
```css
.option-btn.waiting {
  border-color: var(--c5);
  background: rgba(84,160,255,.20);
  animation: waitingPulse 1.2s ease infinite;
}
@keyframes waitingPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(84,160,255,.4); }
  50%      { box-shadow: 0 0 0 8px rgba(84,160,255,.0); }
}
```

### 2-3. view-answer: 이번 문제 순위만 표시

**변경 전**
- `adminShowAnswer()`가 누적 점수(`adminGetRanking()`) 기반 TOP 10 전송
- 제목: "🏆 누적 순위 TOP 10"

**변경 후**
- 신규 함수 `adminGetQRanking()` 추가 → 이번 문제에서 얻은 점수 기준 정렬
- `S.qScores` 객체에 문제별 득점 기록, 다음 문제 시작 시 초기화
- 제목: "🏆 이번 문제 순위 TOP 10"

```javascript
// S 상태에 추가
qScores: {},

// adminNextQuestion() 내 초기화
S.qScores = {};

// p_answer 처리 시 기록
S.qScores[from] = gained;

// 이번 문제 순위 계산 함수
function adminGetQRanking() {
  return Object.keys(S.players).map(id => ({
    name:  S.players[id].name,
    score: S.qScores[id] || 0,
  })).sort((a, b) => b.score - a.score);
}

// adminShowAnswer()에서 사용
ranking: adminGetQRanking().slice(0, 10),
```

> **최종 결과(view-final)**는 여전히 누적 점수(`adminGetRanking()`) 기준으로 표시됩니다.

### 2-4. view-final: 변경 없음

view-final (TOP3 시상대 + 전체 순위)의 소스코드는 원본 v5와 동일하게 유지됩니다.

### 2-5. 배경 화면 밝기 개선

**변경 전** (v5 — 모바일에서 너무 어둡게 보임)
```css
background: linear-gradient(135deg,
  #1a1a2e 0%, #16213e 25%, #0f3460 50%, #533483 75%, #1a1a2e 100%
);
```

**변경 후** (v6 — 약간 밝은 블루/퍼플 계열)
```css
background: linear-gradient(135deg,
  #2e2e52 0%, #263263 25%, #1e5496 50%, #6a42aa 75%, #2e2e52 100%
);
```

각 색상 값을 약 1.5~2배 밝게 조정하여 모바일 환경에서의 가독성 향상.

---

## 3. 사운드 추가

모든 사운드는 **Web Audio API**를 사용하여 외부 파일 없이 프로그래밍 방식으로 생성합니다.  
브라우저 자동재생 정책으로 인해 **사용자가 "입장하기" 버튼을 클릭할 때** AudioContext가 활성화됩니다.

### 3-1. 배경 반복 멜로디

- **시작 시점**: "입장하기" 버튼 클릭 시 (`joinGame()`)
- **종료 시점**: 게임 시작 시 (`g_starting` 수신)
- **방식**: 16음표 멜로디를 300ms 간격으로 무한 반복
- **음색**: 부드러운 사인파(sine), 볼륨 0.06 (귀에 거슬리지 않는 낮은 레벨)

```javascript
const melody = [523, 659, 784, 659, 523, 0, 392, 0, 523, 659, 784, 1047, 0, 784, 659, 0];
// C5  E5  G5  E5  C5  쉼 G4  쉼  C5  E5  G5  C6  쉼  G5  E5  쉼
```

### 3-2. 카운트다운 틱 사운드

- **시작 시점**: `g_countdown` 메시지 수신 (최종 결과 발표 전 카운트다운)
- **방식**: 카운트다운 숫자 표시마다 틱 사운드 재생
- **음색**: 사각파(square), 880Hz (일반 틱) / 1047Hz (마지막 틱)

```javascript
function playTick(isLast) {
  osc.frequency.value = isLast ? 1047 : 880;
  // 0.18초 짧은 소리
}
```

### 3-3. 최종 결과 축하 사운드

- **시작 시점**: `g_final_results` 수신 (view-final 진입 시)
- **방식**: 10개 음표를 0.12~0.18초 간격으로 순차 재생하는 팡파레
- **음색**: 사인파, C5→E5→G5→C6→G5→C6→E6→C6→E6→G6 상승 음계

```javascript
const sequence = [
  {f:523,t:0}, {f:659,t:0.12}, {f:784,t:0.24}, {f:1047,t:0.36},
  {f:784,t:0.52}, {f:1047,t:0.60}, {f:1319,t:0.72},
  {f:1047,t:0.90}, {f:1319,t:1.00}, {f:1568,t:1.12},
];
```

---

## 4. 코드 변경 위치 요약

| 위치 | 변경 내용 |
|------|-----------|
| `body` CSS | 배경 그라디언트 색상값 밝게 조정 |
| `.option-btn.waiting` CSS | 신규 추가 — 선택 후 대기 펄스 애니메이션 |
| `#view-answer` HTML | "누적 순위" → "이번 문제 순위" 텍스트 변경 |
| `S` 객체 | `qScores: {}` 필드 추가 |
| `handleGameMsg` — `g_answer_result` | 즉시 피드백 제거, `stopTimer()` 제거 |
| `handleGameMsg` — `g_starting` | `stopBgSound()` 호출 추가 |
| `handleGameMsg` — `g_countdown` | `playTick()` 호출 추가 |
| `handleGameMsg` — `g_final_results` | `playCelebration()` 호출 추가 |
| `adminNextQuestion()` | `S.qScores = {}` 초기화 추가 |
| `handlePlayerMsg` — `p_answer` | `S.qScores[from] = gained` 기록 추가 |
| `adminShowAnswer()` | `adminGetQRanking()` 사용으로 변경 |
| `adminGetQRanking()` | **신규 함수** — 이번 문제 득점 기준 랭킹 |
| `joinGame()` | `startBgSound()` 호출 추가 |
| `submitAnswer()` | `.waiting` 클래스 적용으로 변경 |
| Web Audio 함수들 | **신규** — `getAudioCtx`, `startBgSound`, `stopBgSound`, `playTick`, `playCelebration` |

---

## 5. 게임 흐름 비교

### v5 흐름 (이전)
```
문제 표시 → 답 선택 → [즉시 정답/오답 오버레이 표시 + 타이머 정지]
  → 시간 만료 → 정답+누적순위 화면 → 다음 문제
```

### v6 흐름 (변경 후)
```
문제 표시 → 답 선택 → [선택 버튼 대기 펄스 표시, 타이머 계속 진행]
  → 시간 만료 → 정답+이번문제순위 화면 → 다음 문제
```

- 참가자는 답을 선택해도 **시간이 다 될 때까지 정답 여부를 알 수 없음**
- **긴장감 유지**: 빠르게 정답을 골랐어도 타이머가 끝날 때까지 기다려야 함
- view-answer에서 정답과 함께 **이번 문제에서 얼마나 빨리 맞혔는지** 순위로 확인 가능
- 최종 결과는 **전체 누적 점수** 기준으로 시상
