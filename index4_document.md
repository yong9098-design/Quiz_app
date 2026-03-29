# 현용이의 퀴즈 마을 — index4.html 완전 문서

> **파일명**: `index4.html`  
> **버전**: 로컬 버전 v4  
> **최종 수정일**: 2026-03-19  
> **방식**: 서버 없는 순수 HTML + CSS + JavaScript (BroadcastChannel API)

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [개발 히스토리](#2-개발-히스토리)
3. [시스템 구조](#3-시스템-구조)
4. [메시지 프로토콜](#4-메시지-프로토콜)
5. [퀴즈 은행](#5-퀴즈-은행)
6. [점수 계산 공식](#6-점수-계산-공식)
7. [타이머 설정](#7-타이머-설정)
8. [모바일 반응형](#8-모바일-반응형)
9. [배포 관련 분석](#9-배포-관련-분석)
10. [사용 방법](#10-사용-방법)
11. [소스 코드](#11-소스-코드)

---

## 1. 프로젝트 개요

**현용이의 퀴즈 마을**은 서버 없이 브라우저만으로 실시간 그룹 퀴즈를 진행할 수 있는 웹 애플리케이션입니다.

| 항목 | 내용 |
|---|---|
| 동작 방식 | BroadcastChannel API (같은 브라우저 탭 간 실시간 통신) |
| 서버 의존성 | 없음 (100% 클라이언트 사이드) |
| 외부 리소스 | Google Fonts CDN (Jua, Noto Sans KR) |
| 지원 브라우저 | Chrome, Edge, Firefox 최신 버전 |
| 파일 구성 | 단일 HTML 파일 (CSS + JS 내장) |

---

## 2. 개발 히스토리

### v3 → v4 최초 변환 (index3.html 기반)

| 기능 | 내용 |
|---|---|
| 난이도별 타이머 | 상(어려움) 기본 10초, 하(쉬움) 기본 3초 |
| timeLimit 메시지 포함 | `g_question`에 `timeLimit` 필드 추가, 모든 탭이 동기화된 시간 사용 |
| urgent 스타일 | 제한시간 5초 이하 시 타이머 원이 빨간색으로 강조 |
| 연습 게임 주제 추가 | 상/하 각 3문제씩 추가 |
| 채널 분리 | BroadcastChannel 이름 `quiz-village-v4` (v3과 충돌 방지) |

### 기능 추가 1 — 관리자 타이머 직접 설정

- 관리자 설정창에 상/하 난이도 타이머를 숫자로 직접 입력하는 UI 추가
- `S.qtimeMap = { '상': 10, '하': 3 }` — 게임 중 변경 가능한 mutable 타이머 맵
- `getQTime()`이 `S.qtimeMap`을 우선 참조하도록 수정
- 입력 즉시 드롭다운 옵션 텍스트 및 미리보기 숫자 실시간 갱신
- 입력 범위: 1~99초 (자동 클램프)

### 기능 추가 2 — 모바일 반응형 강화

기존 미디어쿼리 `@media(max-width:500px)` 1개에서 3단계 체계로 확장:

| 브레이크포인트 | 대상 기기 | 주요 변경 |
|---|---|---|
| 768px 이하 | 태블릿 / 대형 폰 | 카드 패딩 축소, 관리자 패널 여백 조정 |
| 480px 이하 | 갤럭시·아이폰 표준 | 보기 2열→1열, 게임 헤더 2줄 재배치, 타이머 우상단 이동 |
| 360px 이하 | 소형 스마트폰 | 버튼·카드 추가 축소, 관리자 타이머 설정 세로 배치 |

추가 터치 UX 개선:
- `-webkit-tap-highlight-color: transparent` — 탭 시 파란 하이라이트 제거
- `touch-action: manipulation` — 300ms 탭 지연 제거

### 배포 가능 여부 분석 결과

| 항목 | 상태 | 설명 |
|---|---|---|
| 정적 파일 구조 | ✅ 완전 구현 | 서버 의존성 0, 지연시간 최소 |
| 모바일 반응형 | ✅ 개선 완료 | 3단계 미디어쿼리, 터치 UX |
| localStorage | ❌ 미반영 | 의도적 제외 (사용자 요청) |
| GitHub 저장 | ✅ 가능 | 단일 정적 파일 |
| Cloudflare Pages 배포 | ✅ 가능 (단, 제약 있음) | 배포는 가능하나 BroadcastChannel 특성상 **같은 브라우저·같은 기기** 내 탭끼리만 통신 가능. 다른 기기 간 멀티플레이 불가 |

---

## 3. 시스템 구조

```
브라우저 탭 A (관리자: 이현용)
    ├── adminJoin()          → 게임 방 생성, 로비 표시
    ├── adminStartGame()     → 주제/난이도/타이머 설정 후 게임 시작
    ├── adminNextQuestion()  → 문제 BroadcastChannel 전송
    ├── adminShowAnswer()    → 정답 공개 + 실시간 랭킹
    ├── adminFinish()        → 카운트다운 → 최종 결과
    └── adminReset()         → 대기실 초기화

브라우저 탭 B, C, D ... (참가자)
    ├── joinGame()           → p_join 브로드캐스트
    ├── submitAnswer()       → p_answer 브로드캐스트
    └── handleGameMsg()      → g_* 수신 → UI 갱신
```

### 화면 전환 흐름

```
view-main (이름 입력)
    ↓ joinGame()
view-lobby (대기실)
    ↓ adminStartGame()
view-game (문제 화면)
    ↓ 타이머 만료 or 전원 답변
view-answer (정답 + 랭킹)
    ↓ 다음 문제 or 마지막 문제
view-countdown (3·2·1 카운트다운)
    ↓
view-final (TOP3 시상대 + 전체 순위)
    ↓ 20초 후 자동
view-lobby (대기실 초기화)
```

---

## 4. 메시지 프로토콜

### 플레이어 → 관리자 (`p_` 접두사)

| 메시지 | 데이터 | 설명 |
|---|---|---|
| `p_join` | `{ name }` | 입장 요청 |
| `p_answer` | `{ answer, qIdx }` | 답변 제출 |

### 관리자 → 전체 (`g_` 접두사)

| 메시지 | 주요 데이터 | 설명 |
|---|---|---|
| `g_join_success` | `{ name }` | 입장 승인 |
| `g_join_error` | `{ message }` | 입장 거부 (게임 중, 중복 이름 등) |
| `g_player_list` | `{ players[] }` | 참가자 목록 갱신 |
| `g_starting` | `{ topic, difficulty, timeLimit, total }` | 게임 시작 알림 |
| `g_question` | `{ qIdx, qNum, total, q, options, timeLimit }` | 문제 전송 |
| `g_answer_result` | `{ correct, scoreGained, correctIndex }` | 채점 결과 (개인) |
| `g_show_answer` | `{ correctText, ranking, timeLimit }` | 정답 공개 + 순위 |
| `g_countdown` | `{ countdown }` | 최종 발표 카운트다운 |
| `g_final_results` | `{ ranking, waitTime }` | 최종 순위 |
| `g_lobby_reset` | `{}` | 대기실 초기화 |

### 메시지 라우팅 규칙

- `msg.from === MY_ID` → 자신이 보낸 메시지 무시
- `msg.to && msg.to !== MY_ID` → 다른 탭 대상 메시지 무시
- `g_*` 접두사 → 참가자 탭의 `handleGameMsg()` 처리
- `p_*` 접두사 → 관리자 탭의 `handlePlayerMsg()` 처리

---

## 5. 퀴즈 은행

```
QUIZ_BANK
├── 상식
│   ├── 상 (10문제) — 세계에서 가장 긴 강, 빛의 속도, DNA 등
│   └── 하 (10문제) — 대한민국 수도, 무지개 색 수, 물의 화학식 등
├── 역사
│   ├── 상 (10문제) — 임진왜란, 세종대왕, 프랑스 혁명 등
│   └── 하 (10문제) — 초대 대통령, 한국전쟁, 한글 창제 등
└── 연습 게임
    ├── 상 (3문제) — 피보나치 수열, RGB 3원색, 바다 면적
    └── 하 (3문제) — 국화, 1주일, 여름
```

문제는 게임 시작 시 Fisher-Yates 셔플로 무작위 정렬됩니다.

---

## 6. 점수 계산 공식

```
정답 시 획득 점수 = BASE_SCORE + BONUS

BASE_SCORE = 100점 (고정)
BONUS = BONUS_MAX(50점) × (남은시간 / 제한시간)

최대 점수 = 150점 / 문제
최소 점수 (정답, 시간 초과 직전) = 100점
오답 = 0점
```

빠르게 정답을 맞힐수록 보너스 점수가 높습니다.

---

## 7. 타이머 설정

관리자 설정창에서 게임 시작 전에 자유롭게 변경 가능합니다.

| 난이도 | 기본값 | 변경 범위 | 타이머 스타일 |
|---|---|---|---|
| 상 (어려움) | 10초 | 1 ~ 99초 | 노란색 원형 |
| 하 (쉬움) | 3초 | 1 ~ 99초 | 빨간색 원형 (5초 이하 시) |

- 입력값 변경 즉시 드롭다운 옵션 텍스트와 미리보기 숫자 실시간 갱신
- `S.qtimeMap`에 저장되어 게임 중 `getQTime()`이 참조

---

## 8. 모바일 반응형

### 3단계 미디어쿼리

**768px 이하 (태블릿 / 대형 폰)**
- 카드 패딩: 32px → 24px 18px
- 관리자 패널 여백 축소
- 포디움 블록 크기 축소

**480px 이하 (갤럭시·아이폰 표준 — 375~430px)**
- 보기 버튼: 2열 → 1열 전환
- 게임 헤더: 3요소 → 2줄 재배치 (문제번호+점수 / 배지)
- 타이머: 우하단(`bottom:24px`) → 우상단(`top:52px`) 이동으로 버튼 가림 방지
- 게임 화면 상단 여백 120px 확보 (타이머와 콘텐츠 겹침 방지)
- 버튼·카드 패딩 추가 축소

**360px 이하 (소형 스마트폰)**
- 타이머 52px로 추가 축소
- 관리자 타이머 설정: 가로 배치 → 세로 배치
- 카드·버튼 최소 크기 적용

### 터치 UX 개선

```css
a, button, input, select, .option-btn, .btn {
  -webkit-tap-highlight-color: transparent;  /* 탭 하이라이트 제거 */
  touch-action: manipulation;                /* 300ms 지연 제거 */
}
```

---

## 9. 배포 관련 분석

### GitHub 저장 — ✅ 가능
단일 정적 파일로 구성되어 있어 그대로 저장소에 올릴 수 있습니다. 빌드 도구 불필요.

### Cloudflare Pages 배포 — ✅ 기술적으로 가능 (단, 제약 있음)

배포 자체는 `index4.html` 파일 하나로 즉시 가능합니다.

**핵심 제약**: BroadcastChannel API는 **같은 브라우저 인스턴스 내 탭 간**에서만 동작합니다.

| 시나리오 | 동작 여부 |
|---|---|
| 같은 PC, 같은 Chrome에서 여러 탭 | ✅ 정상 동작 |
| A의 PC ↔ B의 PC | ❌ 통신 불가 |
| PC Chrome ↔ 모바일 Chrome | ❌ 통신 불가 |
| 같은 PC, Chrome ↔ Firefox | ❌ 통신 불가 |

**실제 멀티플레이가 필요한 경우 선택지**:

- **옵션 A**: 기존 `app.py` (Flask + WebSocket)를 Railway, Render 등 무료 서버에 배포
- **옵션 B**: Firebase Realtime DB 또는 Supabase Realtime으로 BroadcastChannel 부분 교체 → Cloudflare Pages 그대로 유지

---

## 10. 사용 방법

1. 브라우저에서 `index4.html` 파일 열기
2. **관리자**: `이현용` 이름으로 입장 → 게임 방 자동 생성
3. **참가자**: 새 탭(`Ctrl+T`)에서 같은 파일 열기 → 이름 입력 후 입장
4. 관리자가 주제 / 난이도 선택, 필요 시 타이머 직접 설정
5. **게임 시작** 클릭 → 카운트다운 후 문제 출제
6. 제한시간 내 빠르게 보기 선택 → 빠를수록 보너스 점수
7. 모든 문제 완료 후 최종 시상대 발표

> ※ 같은 브라우저의 여러 탭에서만 동작합니다 (BroadcastChannel API 제약)

---

## 11. 소스 코드

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>현용이의 퀴즈 마을 🎉 (로컬 버전 v4)</title>
  <link href="https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet" />
  <style>
    /* ═══════════════════════════════ 기본 / 배경 ═══════════════════════════════ */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    /* 모바일 터치 탭 지연 제거 */
    a, button, input, select, .option-btn, .btn {
      -webkit-tap-highlight-color: transparent;
      touch-action: manipulation;
    }

    :root {
      --c1:#ff6b6b; --c2:#feca57; --c3:#48dbfb; --c4:#ff9ff3;
      --c5:#54a0ff; --c6:#5f27cd;
      --dark:#1a1a2e; --card:rgba(255,255,255,0.10);
      --radius:20px; --shadow:0 8px 32px rgba(0,0,0,0.35);
    }
    body {
      font-family:'Noto Sans KR',sans-serif;
      background:linear-gradient(135deg,#1a1a2e 0%,#16213e 25%,#0f3460 50%,#533483 75%,#1a1a2e 100%);
      background-size:400% 400%; animation:bgShift 12s ease infinite;
      min-height:100vh; color:#fff; overflow-x:hidden;
    }
    @keyframes bgShift {
      0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}
    }
    .bg-shapes{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
    .bg-shapes span{position:absolute;display:block;border-radius:50%;opacity:0.07;animation:floatUp linear infinite;}
    .bg-shapes span:nth-child(1){width:80px;height:80px;left:10%;background:var(--c1);animation-duration:18s;}
    .bg-shapes span:nth-child(2){width:40px;height:40px;left:25%;background:var(--c2);animation-duration:12s;animation-delay:2s;}
    .bg-shapes span:nth-child(3){width:100px;height:100px;left:40%;background:var(--c3);animation-duration:22s;animation-delay:4s;}
    .bg-shapes span:nth-child(4){width:60px;height:60px;left:55%;background:var(--c4);animation-duration:15s;animation-delay:1s;}
    .bg-shapes span:nth-child(5){width:120px;height:120px;left:70%;background:var(--c5);animation-duration:20s;animation-delay:3s;}
    .bg-shapes span:nth-child(6){width:50px;height:50px;left:85%;background:var(--c1);animation-duration:14s;animation-delay:6s;}
    .bg-shapes span:nth-child(7){width:90px;height:90px;left:5%;background:var(--c6);animation-duration:25s;animation-delay:5s;}
    .bg-shapes span:nth-child(8){width:35px;height:35px;left:60%;background:var(--c2);animation-duration:11s;animation-delay:8s;}
    @keyframes floatUp{
      0%{transform:translateY(110vh) rotate(0deg);opacity:0;}
      10%{opacity:0.07;} 90%{opacity:0.07;}
      100%{transform:translateY(-10vh) rotate(360deg);opacity:0;}
    }

    /* ── 모드 배지 (우상단 고정) ─────────────────────────── */
    #mode-badge{
      position:fixed;top:14px;right:16px;z-index:200;
      display:flex;align-items:center;gap:6px;
      background:rgba(0,0,0,.45);backdrop-filter:blur(8px);
      border:1px solid rgba(255,255,255,.12);border-radius:50px;
      padding:5px 12px;font-size:.72rem;color:rgba(255,255,255,.6);
    }
    #mode-badge span{
      display:inline-block;width:8px;height:8px;border-radius:50%;
      background:var(--c3);box-shadow:0 0 8px var(--c3);
    }

    /* ═══════════════════════════════ 공통 컴포넌트 ══════════════════════════════ */
    .view{
      position:relative;z-index:1;display:none;flex-direction:column;
      align-items:center;justify-content:center;
      min-height:100vh;padding:24px 16px;
    }
    .view.active{display:flex;}
    .fade-in{animation:fadeIn .45s ease both;}
    @keyframes fadeIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

    .title{
      font-family:'Jua',cursive;font-size:clamp(2.4rem,8vw,5rem);text-align:center;
      background:linear-gradient(90deg,var(--c2) 0%,var(--c1) 40%,var(--c4) 70%,var(--c3) 100%);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
      filter:drop-shadow(0 0 20px rgba(255,202,87,.5));line-height:1.2;margin-bottom:8px;
    }
    .subtitle{font-size:1rem;color:rgba(255,255,255,.6);margin-bottom:32px;text-align:center;}
    .card{
      background:var(--card);backdrop-filter:blur(16px);
      border:1px solid rgba(255,255,255,.15);border-radius:var(--radius);
      padding:32px;box-shadow:var(--shadow);width:100%;max-width:520px;
    }
    .btn{
      display:inline-flex;align-items:center;justify-content:center;gap:8px;
      padding:14px 32px;border:none;border-radius:50px;
      font-family:'Jua',cursive;font-size:1.1rem;cursor:pointer;
      transition:transform .15s,box-shadow .15s,filter .15s;
      box-shadow:0 4px 15px rgba(0,0,0,.3);
    }
    .btn:hover:not(:disabled){transform:translateY(-2px);filter:brightness(1.1);box-shadow:0 8px 25px rgba(0,0,0,.4);}
    .btn:active:not(:disabled){transform:translateY(0);}
    .btn:disabled{opacity:.5;cursor:not-allowed;}
    .btn-primary{background:linear-gradient(135deg,var(--c1),#ee5a24);color:#fff;}
    .btn-success{background:linear-gradient(135deg,#00d2d3,#009432);color:#fff;}
    .btn-warning{background:linear-gradient(135deg,var(--c2),#f39c12);color:#1a1a2e;}
    .btn-lg     {padding:18px 48px;font-size:1.3rem;}
    .btn-full   {width:100%;margin-top:12px;}
    .btn-sm     {padding:8px 20px;font-size:.9rem;}

    .input-group{display:flex;flex-direction:column;gap:8px;margin-bottom:16px;}
    .input-group label{font-size:.85rem;color:rgba(255,255,255,.7);font-weight:700;}
    .input-group input,.input-group select{
      background:rgba(255,255,255,.12);border:1.5px solid rgba(255,255,255,.25);
      border-radius:12px;padding:12px 16px;color:#fff;
      font-size:1rem;font-family:'Noto Sans KR',sans-serif;outline:none;width:100%;
      transition:border-color .2s;
    }
    .input-group input::placeholder{color:rgba(255,255,255,.4);}
    .input-group input:focus,.input-group select:focus{border-color:var(--c3);background:rgba(255,255,255,.18);}
    .input-group select option{background:#1a1a2e;color:#fff;}

    .error-msg{
      background:rgba(255,107,107,.25);border:1px solid var(--c1);
      border-radius:10px;padding:10px 16px;font-size:.9rem;color:#ffcccc;
      margin-top:8px;display:none;
    }
    .badge{display:inline-block;padding:4px 12px;border-radius:50px;font-size:.75rem;font-weight:700;letter-spacing:.5px;}
    .badge-topic{background:linear-gradient(135deg,var(--c5),var(--c6));}
    .badge-diff {background:linear-gradient(135deg,var(--c2),var(--c1));color:#1a1a2e;}
    /* 연습 게임 주제 배지 색 */
    .badge-topic.practice{background:linear-gradient(135deg,#00d2d3,#009432);}

    .toast{
      position:fixed;top:24px;left:50%;transform:translateX(-50%);
      background:rgba(0,0,0,.88);color:#fff;padding:12px 28px;
      border-radius:50px;font-family:'Jua',cursive;font-size:1rem;
      z-index:999;display:none;box-shadow:0 4px 20px rgba(0,0,0,.4);
    }
    .toast.show{display:block;animation:toastIn .3s ease;}
    @keyframes toastIn{from{opacity:0;top:0}to{opacity:1;top:24px}}

    /* ═══════════════════════════════ VIEW 1 : 메인 ═══════════════════════════════ */
    .emoji-banner{font-size:3rem;margin-bottom:12px;animation:bounce 1.5s ease infinite;}
    @keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}

    .how-to-box{
      background:rgba(72,219,251,.08);border:1px solid rgba(72,219,251,.25);
      border-radius:14px;padding:14px 18px;margin-bottom:18px;font-size:.82rem;
      color:rgba(255,255,255,.65);line-height:1.7;
    }
    .how-to-box strong{color:var(--c3);}

    /* ═══════════════════════════════ VIEW 2 : 로비 ═══════════════════════════════ */
    .player-count{font-size:.85rem;color:rgba(255,255,255,.5);text-align:center;margin-bottom:8px;}
    .player-grid{
      display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));
      gap:10px;max-height:260px;overflow-y:auto;padding:4px;
    }
    .player-chip{
      background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.06));
      border:1px solid rgba(255,255,255,.2);border-radius:12px;
      padding:8px 12px;text-align:center;font-size:.88rem;font-weight:700;
      animation:popIn .3s ease;word-break:break-all;
    }
    @keyframes popIn{0%{transform:scale(.5);opacity:0}70%{transform:scale(1.1)}100%{transform:scale(1);opacity:1}}

    #admin-panel{
      background:rgba(255,202,87,.1);border:1px solid rgba(255,202,87,.3);
      border-radius:var(--radius);padding:22px;margin-top:16px;width:100%;max-width:540px;
    }
    #admin-panel h3{font-family:'Jua',cursive;font-size:1.1rem;color:var(--c2);margin-bottom:14px;}
    .admin-controls{display:flex;gap:12px;flex-wrap:wrap;}
    .admin-controls .input-group{flex:1;min-width:140px;}

    /* 관리자: 타이머 직접 설정 */
    .timer-custom-wrap{
      background:rgba(255,255,255,.06);border-radius:10px;
      padding:12px 16px;margin:10px 0 4px;
    }
    .timer-custom-wrap .tc-label{
      font-size:.78rem;color:rgba(255,255,255,.55);margin-bottom:10px;display:block;
    }
    .tc-row{display:flex;align-items:center;gap:18px;flex-wrap:wrap;}
    .tc-item{display:flex;align-items:center;gap:7px;font-size:.88rem;color:rgba(255,255,255,.75);}
    .tc-badge{font-size:.75rem;padding:3px 10px;border-radius:20px;font-weight:700;white-space:nowrap;}
    .tc-badge.hard{background:linear-gradient(135deg,var(--c1),#ee5a24);color:#fff;}
    .tc-badge.easy{background:linear-gradient(135deg,#00d2d3,#009432);color:#fff;}
    .tc-item input[type=number]{
      width:58px;background:rgba(255,255,255,.15);
      border:1.5px solid rgba(255,255,255,.3);border-radius:8px;
      padding:6px 6px;color:#fff;font-size:1rem;
      font-family:'Jua',cursive;text-align:center;outline:none;
      transition:border-color .2s;
    }
    .tc-item input[type=number]:focus{border-color:var(--c3);background:rgba(255,255,255,.2);}
    .tc-item input[type=number]::-webkit-inner-spin-button,
    .tc-item input[type=number]::-webkit-outer-spin-button{opacity:1;}
    .tc-sec{font-size:.82rem;color:rgba(255,255,255,.5);}

    /* 난이도 타이머 미리보기 */
    #timer-preview{
      display:flex;align-items:center;justify-content:center;gap:8px;
      background:rgba(255,255,255,.06);border-radius:10px;
      padding:8px 16px;margin:10px 0;font-size:.85rem;color:rgba(255,255,255,.7);
    }
    #timer-preview .t-num{
      font-family:'Jua',cursive;font-size:1.4rem;
      color:var(--c2);text-shadow:0 0 12px rgba(254,202,87,.5);
    }

    /* 공유 링크 섹션 (admin 로비) */
    #share-section{
      background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);
      border-radius:var(--radius);padding:20px;margin-bottom:16px;
      text-align:center;width:100%;max-width:540px;
    }
    #share-section h4{font-family:'Jua',cursive;font-size:1rem;color:var(--c3);margin-bottom:10px;}
    .share-steps{text-align:left;font-size:.82rem;color:rgba(255,255,255,.6);line-height:2;margin-bottom:12px;}
    .share-steps span{color:var(--c2);font-weight:700;}
    #share-url-box{
      background:rgba(255,255,255,.08);border:1px dashed rgba(255,255,255,.25);
      border-radius:8px;padding:8px 14px;font-size:.82rem;word-break:break-all;
      color:var(--c3);margin:6px 0;cursor:pointer;transition:background .2s;
    }
    #share-url-box:hover{background:rgba(255,255,255,.13);}

    /* ═══════════════════════════════ VIEW 3 : 게임 ═══════════════════════════════ */
    /* 480px 이하에서 타이머(우상단)와 콘텐츠가 겹치지 않도록 여백 확보 */
    #view-game{justify-content:flex-start;padding-top:24px;}
    @media(max-width:480px){
      #view-game{ padding-top:120px; }
    }
    @media(max-width:360px){
      #view-game{ padding-top:110px; }
    }
    .game-header{
      display:flex;align-items:center;justify-content:space-between;
      width:100%;max-width:700px;margin-bottom:16px;
    }
    .q-progress{font-family:'Jua',cursive;font-size:1rem;color:rgba(255,255,255,.7);}
    .score-display{
      font-family:'Jua',cursive;
      background:linear-gradient(135deg,var(--c2),var(--c1));
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
      font-size:1.1rem;
    }
    .progress-bar-wrap{
      width:100%;max-width:700px;height:6px;
      background:rgba(255,255,255,.15);border-radius:10px;margin-bottom:18px;overflow:hidden;
    }
    .progress-bar-fill{height:100%;background:linear-gradient(90deg,var(--c3),var(--c5));border-radius:10px;transition:width .4s ease;}

    .question-card{
      background:rgba(255,255,255,.10);backdrop-filter:blur(20px);
      border:1px solid rgba(255,255,255,.2);border-radius:24px;
      padding:32px;width:100%;max-width:700px;
      box-shadow:0 16px 48px rgba(0,0,0,.4);position:relative;
    }
    .question-text{
      font-family:'Jua',cursive;font-size:clamp(1.3rem,4vw,1.9rem);
      text-align:center;line-height:1.5;margin-bottom:28px;
    }
    .options-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
    .option-btn{
      background:rgba(255,255,255,.10);border:2px solid rgba(255,255,255,.2);
      border-radius:16px;padding:18px 14px;color:#fff;
      font-family:'Noto Sans KR',sans-serif;font-size:1rem;font-weight:700;
      cursor:pointer;transition:all .2s;text-align:center;line-height:1.4;
      position:relative;overflow:hidden;
    }
    .option-btn:hover:not(:disabled){
      background:rgba(255,255,255,.22);border-color:var(--c3);
      transform:translateY(-2px);box-shadow:0 6px 20px rgba(72,219,251,.3);
    }
    .option-btn:disabled{cursor:not-allowed;}
    .option-label{
      display:inline-flex;align-items:center;justify-content:center;
      width:28px;height:28px;border-radius:50%;
      background:rgba(255,255,255,.15);font-size:.85rem;margin-right:6px;flex-shrink:0;
    }
    .option-btn.selected{border-color:var(--c5);background:rgba(84,160,255,.25);}
    .option-btn.correct {border-color:#00d2d3;background:rgba(0,210,211,.30);animation:flashOk .4s ease;}
    .option-btn.wrong   {border-color:var(--c1);background:rgba(255,107,107,.25);}
    @keyframes flashOk{0%,100%{transform:scale(1)}50%{transform:scale(1.03)}}

    .timer-wrap{position:fixed;bottom:24px;right:24px;width:88px;height:88px;z-index:10;}
    .timer-circle{
      width:88px;height:88px;border-radius:50%;
      background:conic-gradient(var(--c2) var(--pct,360deg),rgba(255,255,255,.1) 0);
      display:flex;align-items:center;justify-content:center;
      box-shadow:0 0 24px rgba(254,202,87,.5),inset 0 0 0 6px rgba(0,0,0,.3);
    }
    /* 3초 모드: 타이머를 빨간색으로 강조 */
    .timer-circle.urgent{
      background:conic-gradient(var(--c1) var(--pct,360deg),rgba(255,255,255,.1) 0);
      box-shadow:0 0 28px rgba(255,107,107,.7),inset 0 0 0 6px rgba(0,0,0,.3);
    }
    .timer-num{font-family:'Jua',cursive;font-size:2.2rem;color:#fff;text-shadow:0 2px 8px rgba(0,0,0,.5);}
    .timer-num.pulse{animation:tPulse .4s cubic-bezier(.36,.07,.19,.97);}
    @keyframes tPulse{0%{transform:scale(1)}40%{transform:scale(1.35);color:var(--c1)}100%{transform:scale(1)}}

    .answer-overlay{
      position:absolute;inset:0;border-radius:24px;
      display:none;flex-direction:column;align-items:center;justify-content:center;
      font-family:'Jua',cursive;font-size:1.6rem;z-index:5;
    }
    .answer-overlay.show{display:flex;}
    .answer-overlay.correct-overlay{background:rgba(0,210,211,.25);border:3px solid #00d2d3;}
    .answer-overlay.wrong-overlay  {background:rgba(255,107,107,.25);border:3px solid var(--c1);}
    .overlay-icon {font-size:3rem;margin-bottom:8px;animation:bounce .6s;}
    .overlay-score{font-size:1.2rem;color:var(--c2);}

    /* ═══════════════════════════════ VIEW 4 : 정답+랭킹 ════════════════════════ */
    .correct-answer-reveal{text-align:center;margin-bottom:20px;}
    .correct-answer-reveal .label{font-size:.85rem;color:rgba(255,255,255,.5);margin-bottom:6px;}
    .answer-text{
      font-family:'Jua',cursive;font-size:1.8rem;color:var(--c2);
      text-shadow:0 0 20px rgba(254,202,87,.6);animation:scaleIn .4s ease;
    }
    @keyframes scaleIn{0%{transform:scale(.6);opacity:0}70%{transform:scale(1.08)}100%{transform:scale(1);opacity:1}}
    .ranking-list{display:flex;flex-direction:column;gap:8px;}
    .rank-item{
      display:flex;align-items:center;gap:12px;
      background:rgba(255,255,255,.07);border-radius:12px;padding:10px 14px;
      border-left:4px solid transparent;animation:slideIn .3s ease both;
    }
    .rank-item:nth-child(1){border-left-color:#ffd700;}
    .rank-item:nth-child(2){border-left-color:#c0c0c0;}
    .rank-item:nth-child(3){border-left-color:#cd7f32;}
    @keyframes slideIn{from{transform:translateX(-20px);opacity:0}to{transform:translateX(0);opacity:1}}
    .rank-medal{font-size:1.4rem;width:32px;text-align:center;}
    .rank-name {flex:1;font-weight:700;}
    .rank-score{font-family:'Jua',cursive;font-size:1.1rem;color:var(--c2);}
    .next-bar-wrap{margin-top:14px;height:4px;background:rgba(255,255,255,.15);border-radius:10px;overflow:hidden;}
    .next-bar-fill{height:100%;background:linear-gradient(90deg,var(--c1),var(--c2));border-radius:10px;transition:width 1s linear;}

    /* ═══════════════════════════════ VIEW 5 : 카운트다운 ══════════════════════ */
    #view-countdown{background:radial-gradient(circle at center,rgba(95,39,205,.4) 0%,transparent 70%);}
    .countdown-label{
      font-family:'Jua',cursive;font-size:1.5rem;color:rgba(255,255,255,.7);margin-bottom:20px;
      animation:flicker 1s ease infinite alternate;
    }
    @keyframes flicker{from{opacity:.6}to{opacity:1;text-shadow:0 0 20px var(--c4)}}
    .countdown-num{
      font-family:'Jua',cursive;font-size:clamp(8rem,20vw,14rem);line-height:1;
      background:linear-gradient(135deg,var(--c4),var(--c1),var(--c2));
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
      filter:drop-shadow(0 0 30px rgba(255,159,243,.6));
    }
    .count-pop{animation:countPop .6s cubic-bezier(.34,1.56,.64,1);}
    @keyframes countPop{0%{transform:scale(2.5) rotate(-10deg);opacity:0}100%{transform:scale(1) rotate(0);opacity:1}}

    /* ═══════════════════════════════ VIEW 6 : 최종 결과 ═══════════════════════ */
    #view-final{text-align:center;}
    .final-title{
      font-family:'Jua',cursive;font-size:clamp(2rem,7vw,3.5rem);
      background:linear-gradient(90deg,var(--c2),var(--c1),var(--c4));
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
      margin-bottom:32px;animation:shimmer 2s linear infinite;background-size:200%;
    }
    @keyframes shimmer{0%{background-position:-200%}100%{background-position:200%}}
    .podium{display:flex;align-items:flex-end;justify-content:center;gap:12px;margin-bottom:32px;}
    .podium-item{display:flex;flex-direction:column;align-items:center;animation:riseUp .7s ease both;}
    .podium-item:nth-child(1){animation-delay:.4s;}
    .podium-item:nth-child(2){animation-delay:0s;}
    .podium-item:nth-child(3){animation-delay:.8s;}
    @keyframes riseUp{from{transform:translateY(60px);opacity:0}to{transform:translateY(0);opacity:1}}
    .podium-avatar{font-size:3rem;margin-bottom:6px;animation:bounce 1.5s ease infinite;}
    .podium-name{font-family:'Jua',cursive;font-size:1rem;max-width:90px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:4px;}
    .podium-score{font-family:'Jua',cursive;font-size:.9rem;color:var(--c2);margin-bottom:6px;}
    .podium-block{border-radius:12px 12px 0 0;width:88px;display:flex;align-items:flex-start;justify-content:center;padding-top:10px;font-family:'Jua',cursive;font-size:2rem;}
    .podium-block.gold  {height:120px;background:linear-gradient(180deg,#ffd700,#f9ca24);}
    .podium-block.silver{height:88px; background:linear-gradient(180deg,#bdc3c7,#95a5a6);}
    .podium-block.bronze{height:68px; background:linear-gradient(180deg,#cd7f32,#a0522d);}
    .redirect-notice{font-size:.9rem;color:rgba(255,255,255,.5);margin-top:12px;}
    #redirect-count{color:var(--c3);font-weight:700;}

    ::-webkit-scrollbar{width:6px;}
    ::-webkit-scrollbar-track{background:rgba(255,255,255,.05);border-radius:3px;}
    ::-webkit-scrollbar-thumb{background:rgba(255,255,255,.2);border-radius:3px;}

    /* ═══════════════ 반응형 — 태블릿 (768px 이하) ═══════════════ */
    @media(max-width:768px){
      .card{ padding:24px 18px; }
      .question-card{ padding:24px 16px; }
      #admin-panel{ padding:16px 14px; }
      .admin-controls .input-group{ min-width:120px; }
      .podium-block{ width:76px; } .podium-name{ max-width:76px; }
      .how-to-box{ font-size:.78rem; }
    }

    /* ═══════════════ 반응형 — 스마트폰 (480px 이하) ══════════════ */
    @media(max-width:480px){
      /* 보기 버튼: 2열 → 1열 */
      .options-grid{ grid-template-columns:1fr; gap:10px; }

      /* 문제 카드 여백 · 글씨 */
      .question-card{ padding:18px 12px; }
      .question-text{ margin-bottom:14px; font-size:clamp(1.05rem,4.5vw,1.45rem); }
      .option-btn{ padding:14px 12px; font-size:.95rem; }

      /* 게임 헤더: 3요소 → 2줄로 재배치
         1줄: [문제 n/n]  [내 점수]
         2줄: [주제배지 · 난이도배지] 중앙 */
      .game-header{ flex-wrap:wrap; gap:4px; }
      .game-header > div{ order:3; width:100%; text-align:center; margin-top:2px; }
      .q-progress{ font-size:.85rem; }
      .score-display{ font-size:.88rem; }

      /* 타이머: 우하단 → 우상단(모드배지 바로 아래)으로 이동, 크기 축소
         모드배지가 top:14px + 약 28px 높이 → top:52px 에 배치 */
      .timer-wrap{ bottom:auto; top:52px; right:10px; width:62px; height:62px; }
      .timer-circle{ width:62px; height:62px;
        box-shadow:0 0 16px rgba(254,202,87,.5),inset 0 0 0 5px rgba(0,0,0,.3); }
      .timer-circle.urgent{
        box-shadow:0 0 20px rgba(255,107,107,.7),inset 0 0 0 5px rgba(0,0,0,.3); }
      .timer-num{ font-size:1.5rem; }

      /* 카드 · 버튼 */
      .card{ padding:20px 14px; }
      .btn-lg{ padding:14px 24px; font-size:1.1rem; }
      .btn-full{ margin-top:10px; }

      /* 로비 */
      .player-grid{ grid-template-columns:repeat(auto-fill,minmax(88px,1fr)); gap:8px; }

      /* 정답 오버레이 */
      .answer-overlay{ font-size:1.25rem; }
      .overlay-icon{ font-size:2.2rem; }

      /* 포디움 */
      .podium-block{ width:72px; } .podium-name{ max-width:72px; }
      .podium{ gap:8px; }

      /* 공유 링크 */
      #share-section{ padding:14px; }
      .share-steps{ font-size:.78rem; line-height:1.8; }

      /* 타이머 직접 설정 */
      .tc-row{ gap:12px; }
      .tc-item input[type=number]{ width:52px; }
    }

    /* ═══════════════ 반응형 — 소형 스마트폰 (360px 이하) ══════════ */
    @media(max-width:360px){
      .option-btn{ padding:12px 10px; font-size:.88rem; }
      .options-grid{ gap:8px; }

      .timer-wrap{ width:52px; height:52px; top:48px; }
      .timer-circle{ width:52px; height:52px;
        box-shadow:0 0 12px rgba(254,202,87,.5),inset 0 0 0 4px rgba(0,0,0,.3); }
      .timer-circle.urgent{
        box-shadow:0 0 16px rgba(255,107,107,.7),inset 0 0 0 4px rgba(0,0,0,.3); }
      .timer-num{ font-size:1.2rem; }

      .podium{ gap:4px; }
      .podium-block{ width:62px; font-size:1.6rem; } .podium-name{ max-width:62px; font-size:.88rem; }

      .btn-lg{ padding:12px 18px; font-size:.98rem; }
      #admin-panel{ padding:12px 10px; }
      .tc-row{ flex-direction:column; gap:8px; }
      .tc-item input[type=number]{ width:60px; }

      .card{ padding:16px 12px; }
      .question-card{ padding:14px 10px; }
    }
  </style>
</head>

<body>
  <div class="bg-shapes">
    <span></span><span></span><span></span><span></span>
    <span></span><span></span><span></span><span></span>
  </div>
  <div class="toast" id="toast"></div>

  <!-- 모드 표시 배지 -->
  <div id="mode-badge">
    <span></span>
    <span id="mode-text">로컬 멀티탭 모드</span>
  </div>

  <!-- ══════════════════════════════════════════════════════
       VIEW 1 : 메인 — 이름 입력
  ══════════════════════════════════════════════════════ -->
  <div class="view active fade-in" id="view-main">
    <div class="emoji-banner">🎉🎊🎉</div>
    <h1 class="title">현용이의 퀴즈 마을</h1>
    <p class="subtitle">두뇌를 깨워라! 빠를수록 점수가 올라간다! ⚡</p>

    <div class="card">
      <div class="how-to-box">
        🖥️ <strong>서버 없는 로컬 버전 v4</strong><br>
        관리자: <strong>이현용</strong> 이름으로 입장 → 게임 방 생성<br>
        참가자: 다른 탭에서 이 페이지를 열고 이름 입력 후 입장<br>
        <small style="color:rgba(255,255,255,.4);">※ 같은 브라우저의 여러 탭에서 동시 플레이 가능</small>
      </div>

      <div class="input-group">
        <label for="input-name">실명 입력 (최대 20자)</label>
        <input type="text" id="input-name" maxlength="20" placeholder="ex) 홍길동"
               onkeydown="if(event.key==='Enter') joinGame()" autocomplete="off" />
      </div>
      <div class="error-msg" id="join-error"></div>
      <button class="btn btn-primary btn-full btn-lg" id="btn-join" onclick="joinGame()">
        🎯 입장하기!
      </button>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════════════
       VIEW 2 : 로비 — 대기실
  ══════════════════════════════════════════════════════ -->
  <div class="view fade-in" id="view-lobby">
    <h1 class="title" style="font-size:clamp(1.8rem,6vw,3rem);margin-bottom:4px;">🏠 대기실</h1>
    <p class="subtitle" id="lobby-sub"></p>

    <!-- 관리자 전용: 공유 링크 안내 -->
    <div id="share-section" style="display:none;">
      <h4>📋 참가 방법 안내 (관리자 전용)</h4>
      <div class="share-steps">
        <span>①</span> 아래 주소를 복사하세요<br>
        <span>②</span> 새 탭(Ctrl+T)을 열고 붙여넣기 후 접속<br>
        <span>③</span> 이름을 입력하고 입장하기 클릭
      </div>
      <div id="share-url-box" onclick="copyUrl()" title="클릭하여 복사"></div>
      <button class="btn btn-sm btn-primary" style="margin-top:8px;" onclick="copyUrl()">🔗 링크 복사</button>
    </div>

    <!-- 참가자 목록 -->
    <div class="card" style="max-width:600px;margin-top:8px;">
      <p class="player-count" id="player-count-text">참가자 0명 입장 중</p>
      <div class="player-grid" id="player-grid"></div>
    </div>

    <!-- 관리자 전용: 게임 설정 + 시작 -->
    <div id="admin-panel" style="display:none;">
      <h3>⚙️ 게임 설정</h3>
      <div class="admin-controls">
        <div class="input-group">
          <label for="sel-topic">📚 주제</label>
          <select id="sel-topic" onchange="onTopicChange()">
            <option value="상식">상식</option>
            <option value="역사">역사</option>
            <option value="연습 게임">🎮 연습 게임 (3문제)</option>
          </select>
        </div>
        <div class="input-group">
          <label for="sel-diff">🎚 난이도 / 제한시간</label>
          <select id="sel-diff" onchange="onDiffChange()">
            <option value="상">상 (어려움) · ⏱ 10초</option>
            <option value="하">하 (쉬움) · ⏱ 3초</option>
          </select>
        </div>
      </div>

      <!-- ★ 관리자 타이머 직접 설정 -->
      <div class="timer-custom-wrap">
        <span class="tc-label">⏱ 타이머 직접 설정 (초 단위, 1~99초)</span>
        <div class="tc-row">
          <div class="tc-item">
            <span class="tc-badge hard">상 (어려움)</span>
            <input type="number" id="input-time-hard" min="1" max="99" value="10"
                   oninput="onTimerChange()" />
            <span class="tc-sec">초</span>
          </div>
          <div class="tc-item">
            <span class="tc-badge easy">하 (쉬움)</span>
            <input type="number" id="input-time-easy" min="1" max="99" value="3"
                   oninput="onTimerChange()" />
            <span class="tc-sec">초</span>
          </div>
        </div>
      </div>

      <!-- 난이도별 타이머 미리보기 -->
      <div id="timer-preview">
        <span>⏱ 문제당 제한시간:</span>
        <span class="t-num" id="preview-sec">10</span>
        <span>초</span>
      </div>

      <button class="btn btn-warning btn-full btn-lg" style="margin-top:14px;" onclick="adminStartGame()">
        ▶️ 게임 시작!
      </button>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════════════
       VIEW 3 : 게임 — 문제 화면
  ══════════════════════════════════════════════════════ -->
  <div class="view fade-in" id="view-game">
    <div class="game-header">
      <span class="q-progress" id="q-progress">문제 1 / 10</span>
      <div>
        <span class="badge badge-topic" id="badge-topic">상식</span>
        <span class="badge badge-diff"  id="badge-diff" style="margin-left:4px;">하</span>
      </div>
      <span class="score-display" id="my-score-display">내 점수: 0점</span>
    </div>
    <div class="progress-bar-wrap">
      <div class="progress-bar-fill" id="q-bar" style="width:10%;"></div>
    </div>
    <div class="question-card">
      <div class="answer-overlay" id="ans-overlay">
        <div class="overlay-icon"  id="ov-icon">✅</div>
        <div id="ov-msg">정답!</div>
        <div class="overlay-score" id="ov-score"></div>
      </div>
      <p class="question-text" id="question-text">로딩 중...</p>
      <div class="options-grid"  id="options-grid"></div>
    </div>
    <div class="timer-wrap" id="timer-wrap">
      <div class="timer-circle" id="timer-circle" style="--pct:360deg;">
        <span class="timer-num" id="timer-num">?</span>
      </div>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════════════
       VIEW 4 : 정답 + 랭킹
  ══════════════════════════════════════════════════════ -->
  <div class="view fade-in" id="view-answer">
    <h2 style="font-family:'Jua',cursive;font-size:1.5rem;margin-bottom:20px;color:var(--c3);">
      📊 정답 & 실시간 순위
    </h2>
    <div class="card" style="max-width:620px;">
      <div class="correct-answer-reveal">
        <div class="label">✅ 정답은...</div>
        <div class="answer-text" id="answer-reveal-text"></div>
      </div>
      <hr style="border:none;border-top:1px solid rgba(255,255,255,.12);margin-bottom:14px;" />
      <p style="font-family:'Jua',cursive;font-size:.9rem;margin-bottom:10px;color:rgba(255,255,255,.55);">
        🏆 누적 순위 TOP 10
      </p>
      <div class="ranking-list" id="ranking-list"></div>
      <div class="next-bar-wrap">
        <div class="next-bar-fill" id="next-bar" style="width:100%;"></div>
      </div>
      <p style="font-size:.75rem;color:rgba(255,255,255,.35);text-align:right;margin-top:4px;">
        잠시 후 다음 문제로 이동...
      </p>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════════════
       VIEW 5 : TOP3 발표 전 카운트다운
  ══════════════════════════════════════════════════════ -->
  <div class="view fade-in" id="view-countdown">
    <div style="text-align:center;">
      <div class="countdown-label">🎆 최종 결과 발표까지...</div>
      <div class="countdown-num" id="countdown-num">3</div>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════════════
       VIEW 6 : 최종 결과 — TOP 3 시상대
  ══════════════════════════════════════════════════════ -->
  <div class="view fade-in" id="view-final">
    <h1 class="final-title">🏆 최종 결과 발표!</h1>
    <div class="podium" id="podium"></div>
    <div class="ranking-list" id="rest-ranking"
         style="width:100%;max-width:420px;margin-bottom:20px;"></div>
    <p class="redirect-notice">
      <span id="redirect-count">20</span>초 후 대기실로 자동 이동합니다...
    </p>
    <button class="btn btn-primary btn-lg" style="margin-top:14px;" onclick="manualLobby()">
      🔄 지금 대기실로 이동
    </button>
  </div>

  <!-- ══════════════════════════════════════════════════════
       JavaScript — BroadcastChannel 기반 멀티탭 게임 엔진 v4
       ▶ 변경사항
         · 난이도별 문제 제한시간: 상=10초, 하=3초
         · g_question 메시지에 timeLimit 포함
         · 연습 게임 주제 추가 (상/하 각 3문제)
  ══════════════════════════════════════════════════════ -->
  <script>
  'use strict';

  /* ══════════════════════════════════════════════════════
     설정 상수
  ══════════════════════════════════════════════════════ */
  const ADMIN_NAME = "이현용";

  /* ★ 난이도별 제한시간 (초) */
  const Q_TIME_MAP = {
    '상': 10,   // 어려움 → 10초
    '하': 3,    // 쉬움   → 3초
  };

  const RANK_TIME = 5;   // 정답+랭킹 노출 시간
  const CD_TIME   = 3;   // 최종 카운트다운
  const FIN_TIME  = 20;  // 최종 결과 후 로비 복귀
  const BASE_SCORE = 100;
  const BONUS_MAX  = 50;

  /** 현재 게임의 문제 제한시간 반환 (관리자가 직접 설정한 값 우선) */
  function getQTime() {
    return S.qtimeMap[S.difficulty] || Q_TIME_MAP[S.difficulty] || 10;
  }

  /* ══════════════════════════════════════════════════════
     퀴즈 은행
     ★ 연습 게임 추가: 상/하 각 3문제
  ══════════════════════════════════════════════════════ */
  const QUIZ_BANK = {

    /* ─────────────────── 상식 (10문제) ─────────────────── */
    "상식": {
      "상": [
        {q:"세계에서 가장 긴 강은?",                    options:["나일강","아마존강","양쯔강","미시시피강"], a:0},
        {q:"인간의 뇌 무게는 평균 약 몇 kg인가?",        options:["1.0 kg","1.4 kg","2.0 kg","0.8 kg"],   a:1},
        {q:"빛의 속도는 약 초속 몇 km인가?",             options:["100,000 km","200,000 km","300,000 km","400,000 km"], a:2},
        {q:"원소기호 'Au'는 무슨 원소인가?",             options:["은(Ag)","알루미늄(Al)","금(Au)","구리(Cu)"], a:2},
        {q:"태양계에서 가장 큰 행성은?",                 options:["토성","천왕성","목성","해왕성"],         a:2},
        {q:"인체에서 가장 긴 뼈는?",                     options:["척추","대퇴골(넓적다리뼈)","상완골","경골"], a:1},
        {q:"DNA 이중나선 구조가 처음 발표된 해는?",      options:["1943년","1953년","1963년","1973년"],     a:1},
        {q:"지구에서 달까지의 평균 거리는?",              options:["약 28만 km","약 38만 km","약 48만 km","약 58만 km"], a:1},
        {q:"물의 끓는점은 1기압에서 몇 도인가?",         options:["90°C","95°C","100°C","105°C"],          a:2},
        {q:"주기율표에서 원자번호 1번 원소는?",           options:["헬륨(He)","리튬(Li)","수소(H)","탄소(C)"], a:2},
      ],
      "하": [
        {q:"대한민국의 수도는?",                          options:["부산","서울","인천","대구"],             a:1},
        {q:"무지개는 몇 가지 색으로 이루어져 있는가?",    options:["5가지","6가지","7가지","8가지"],         a:2},
        {q:"물의 화학식은?",                              options:["CO₂","O₂","H₂O","NaCl"],                a:2},
        {q:"하루는 몇 시간인가?",                         options:["12시간","24시간","36시간","48시간"],     a:1},
        {q:"지구는 태양계에서 몇 번째 행성인가?",         options:["1번째","2번째","3번째","4번째"],         a:2},
        {q:"사람의 눈은 몇 개인가?",                      options:["1개","2개","3개","4개"],                 a:1},
        {q:"태양은 어느 방향에서 뜨는가?",                options:["서쪽","남쪽","동쪽","북쪽"],             a:2},
        {q:"1년은 몇 개월인가?",                          options:["10개월","11개월","12개월","13개월"],     a:2},
        {q:"사람의 손가락은 총 몇 개인가?",               options:["8개","9개","10개","12개"],               a:2},
        {q:"한국의 국기 이름은?",                         options:["일장기","성조기","태극기","삼색기"],     a:2},
      ],
    },

    /* ─────────────────── 역사 (10문제) ─────────────────── */
    "역사": {
      "상": [
        {q:"조선을 건국한 인물은?",                       options:["이성계","왕건","견훤","궁예"],           a:0},
        {q:"임진왜란이 시작된 해는?",                     options:["1382년","1492년","1592년","1692년"],     a:2},
        {q:"세종대왕이 훈민정음을 반포한 해는?",          options:["1343년","1443년","1446년","1543년"],     a:2},
        {q:"프랑스 혁명이 일어난 해는?",                  options:["1769년","1779년","1789년","1799년"],     a:2},
        {q:"제1차 세계대전이 시작된 해는?",               options:["1904년","1914년","1924년","1934년"],     a:1},
        {q:"3·1 운동이 일어난 해는?",                     options:["1909년","1919년","1929년","1939년"],     a:1},
        {q:"거북선을 만든 장군은?",                       options:["강감찬","을지문덕","이순신","권율"],     a:2},
        {q:"고구려를 세운 인물은?",                       options:["박혁거세","주몽","온조","김수로"],       a:1},
        {q:"조선의 마지막 왕은?",                         options:["고종","순종","철종","헌종"],             a:1},
        {q:"한국의 광복절은 몇 월 며칠인가?",             options:["7월 15일","8월 15일","9월 15일","10월 15일"], a:1},
      ],
      "하": [
        {q:"대한민국의 첫 번째 대통령은?",                options:["박정희","이승만","윤보선","최규하"],     a:1},
        {q:"한국전쟁이 시작된 해는?",                     options:["1945년","1948년","1950년","1953년"],     a:2},
        {q:"세종대왕이 만든 우리나라 고유 문자는?",       options:["한자","가나","한글","한문"],             a:2},
        {q:"고조선을 세운 인물은?",                       options:["단군왕검","주몽","이성계","왕건"],       a:0},
        {q:"신라의 수도는?",                              options:["평양","한성","경주","개성"],             a:2},
        {q:"고려를 세운 인물은?",                         options:["이성계","왕건","궁예","견훤"],           a:1},
        {q:"한국의 국경일인 '개천절'은 몇 월 며칠인가?",  options:["10월 1일","10월 3일","10월 5일","10월 9일"], a:1},
        {q:"일제강점기에서 해방된 연도는?",               options:["1943년","1944년","1945년","1946년"],     a:2},
        {q:"조선시대 최상위 신분 계급은?",                options:["중인","상민","양반","천민"],             a:2},
        {q:"삼국시대에 속하지 않는 나라는?",              options:["고구려","백제","신라","발해"],           a:3},
      ],
    },

    /* ─────────────────── ★ 연습 게임 (3문제씩) ─────────── */
    "연습 게임": {
      "상": [
        {
          q:"피보나치 수열 1, 1, 2, 3, 5, 8 다음 숫자는?",
          options:["11","12","13","15"],
          a:2,   // 13
        },
        {
          q:"빛의 3원색(RGB)을 모두 합치면 무슨 색이 되는가?",
          options:["검정","회색","흰색","노랑"],
          a:2,   // 흰색
        },
        {
          q:"지구 표면의 약 몇 %가 바다로 덮여 있는가?",
          options:["약 51%","약 61%","약 71%","약 81%"],
          a:2,   // 약 71%
        },
      ],
      "하": [
        {
          q:"대한민국의 국화(나라꽃)는?",
          options:["장미","무궁화","벚꽃","해바라기"],
          a:1,   // 무궁화
        },
        {
          q:"1주일은 며칠인가?",
          options:["5일","6일","7일","8일"],
          a:2,   // 7일
        },
        {
          q:"한국의 사계절 중 가장 더운 계절은?",
          options:["봄","여름","가을","겨울"],
          a:1,   // 여름
        },
      ],
    },
  };

  /* ══════════════════════════════════════════════════════
     탭 고유 ID & BroadcastChannel
  ══════════════════════════════════════════════════════ */
  const MY_ID = 'p_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 6);
  const ch    = window.BroadcastChannel ? new BroadcastChannel('quiz-village-v4') : null;

  /* ══════════════════════════════════════════════════════
     전역 상태
  ══════════════════════════════════════════════════════ */
  const S = {
    isAdmin:    false,
    myName:     '',
    myScore:    0,
    qIdx:       -1,
    answered:   false,
    timerH:     null,
    redirectIv: null,
    joinTimer:  null,

    /* Admin 전용 */
    players:    {},
    status:     'idle',   // idle | waiting | playing | finished
    questions:  [],
    curQ:       -1,
    answersIn:  new Set(),
    qStartTime: 0,
    qTimerH:    null,
    difficulty: '상',     // 현재 선택된 난이도 (getQTime() 참조용)

    /* ★ 관리자가 직접 설정하는 난이도별 타이머 (초) */
    qtimeMap:   { '상': 10, '하': 3 },
  };

  /* ══════════════════════════════════════════════════════
     브로드캐스트 헬퍼
  ══════════════════════════════════════════════════════ */

  function bcast(type, data = {}, to = null) {
    if (!ch) return;
    ch.postMessage({ type, data, from: MY_ID, to, ts: Date.now() });
  }

  /** 관리자: 모든 탭에 보내고 자신도 즉시 처리 */
  function emitAll(type, data = {}) {
    bcast(type, data, null);
    handleGameMsg(type, data, Date.now());
  }

  /** 관리자: 특정 탭에만 전송 (자신이면 로컬 처리) */
  function emitTo(targetId, type, data = {}) {
    if (targetId === MY_ID) {
      handleGameMsg(type, data, Date.now());
    } else {
      bcast(type, data, targetId);
    }
  }

  /* ══════════════════════════════════════════════════════
     채널 수신 라우터
  ══════════════════════════════════════════════════════ */
  if (ch) {
    ch.onmessage = ({ data: msg }) => {
      if (msg.from === MY_ID) return;
      if (msg.to && msg.to !== MY_ID) return;

      if (msg.type.startsWith('g_')) {
        if (!S.isAdmin) handleGameMsg(msg.type, msg.data, msg.ts);
      } else if (msg.type.startsWith('p_') && S.isAdmin) {
        handlePlayerMsg(msg.type, msg.data, msg.from, msg.ts);
      }
    };
  }

  /* ══════════════════════════════════════════════════════
     플레이어 메시지 처리 (관리자 탭 전용)
  ══════════════════════════════════════════════════════ */
  function handlePlayerMsg(type, data, from, ts) {
    switch (type) {

      case 'p_join': {
        if (S.status !== 'waiting') {
          emitTo(from, 'g_join_error', { message: '게임이 이미 진행 중입니다.' });
          return;
        }
        if (data.name === ADMIN_NAME) {
          emitTo(from, 'g_join_error', { message: `'${ADMIN_NAME}' 이름은 관리자 전용입니다.` });
          return;
        }
        if (Object.values(S.players).some(p => p.name === data.name)) {
          emitTo(from, 'g_join_error', { message: '이미 사용 중인 이름입니다.' });
          return;
        }
        S.players[from] = { name: data.name, score: 0 };
        emitTo(from, 'g_join_success', { name: data.name });
        broadcastPlayerList();
        break;
      }

      case 'p_answer': {
        if (S.status !== 'playing') return;
        if (S.answersIn.has(from)) return;
        if (data.qIdx !== S.curQ) return;

        S.answersIn.add(from);
        const q  = S.questions[S.curQ];
        const ok = (parseInt(data.answer) === q.a);
        let gained = 0;
        if (ok) {
          const elapsed = (Date.now() - S.qStartTime) / 1000;
          const rem     = Math.max(0, getQTime() - elapsed);
          const bonus   = Math.round(BONUS_MAX * rem / getQTime());
          gained        = BASE_SCORE + bonus;
          S.players[from].score += gained;
        }
        emitTo(from, 'g_answer_result', {
          correct:      ok,
          scoreGained:  gained,
          correctIndex: q.a,
        });
        break;
      }
    }
  }

  /* ══════════════════════════════════════════════════════
     게임 메시지 처리 (모든 탭 공통)
  ══════════════════════════════════════════════════════ */
  function handleGameMsg(type, data, ts = Date.now()) {
    switch (type) {

      case 'g_join_success': {
        clearTimeout(S.joinTimer); S.joinTimer = null;
        S.myName  = data.name;
        S.myScore = 0;
        _el('lobby-sub').textContent =
          `🎮 ${data.name}님 환영합니다! 관리자가 게임을 시작할 때까지 기다려주세요.`;
        showView('view-lobby');
        break;
      }

      case 'g_join_error': {
        clearTimeout(S.joinTimer); S.joinTimer = null;
        setError('⚠️ ' + (data.message || '입장 실패'));
        resetJoinBtn();
        break;
      }

      case 'g_player_list': {
        updatePlayerList(data.players);
        break;
      }

      case 'g_starting': {
        _el('badge-topic').textContent = data.topic;
        _el('badge-diff').textContent  = data.difficulty + ' · ' + data.timeLimit + '초';
        // 연습 게임이면 배지 색 변경
        const bt = _el('badge-topic');
        bt.classList.toggle('practice', data.topic === '연습 게임');
        toast(`🎮 게임 시작! ${data.topic} | ${data.difficulty} (${data.timeLimit}초)`, 2200);
        break;
      }

      case 'g_question': {
        stopTimer();
        S.qIdx     = data.qIdx;
        S.answered = false;

        _el('my-score-display').textContent = `내 점수: ${S.myScore.toLocaleString()}점`;
        _el('q-progress').textContent       = `문제 ${data.qNum} / ${data.total}`;
        _el('q-bar').style.width            = (data.qNum / data.total * 100) + '%';
        _el('question-text').textContent    = data.q;
        _el('ans-overlay').className        = 'answer-overlay';

        const grid = _el('options-grid');
        grid.innerHTML = '';
        ['①','②','③','④'].forEach((lbl, i) => {
          const b = document.createElement('button');
          b.className = 'option-btn';
          b.innerHTML = `<span class="option-label">${lbl}</span>${esc(data.options[i])}`;
          b.onclick   = () => submitAnswer(i);
          grid.appendChild(b);
        });

        _el('timer-wrap').style.display = 'block';

        // ★ 3초 모드(하)이면 타이머를 빨간색(urgent)으로 강조
        const cirEl = _el('timer-circle');
        if (data.timeLimit <= 5) {
          cirEl.classList.add('urgent');
        } else {
          cirEl.classList.remove('urgent');
        }

        showView('view-game');

        // ★ data.timeLimit 사용 (난이도별 동적 시간)
        const elapsed   = Math.max(0, (Date.now() - ts) / 1000);
        const remaining = Math.max(1, data.timeLimit - elapsed);
        startTimer(remaining, data.timeLimit);
        break;
      }

      case 'g_answer_result': {
        stopTimer();
        document.querySelectorAll('.option-btn').forEach((b, i) => {
          b.disabled = true;
          if (i === data.correctIndex)               b.classList.add('correct');
          else if (b.classList.contains('selected')) b.classList.add('wrong');
        });
        if (data.correct) S.myScore += data.scoreGained;
        _el('my-score-display').textContent = `내 점수: ${S.myScore.toLocaleString()}점`;

        const ov = _el('ans-overlay');
        ov.className = 'answer-overlay show ' + (data.correct ? 'correct-overlay' : 'wrong-overlay');
        _el('ov-icon').textContent  = data.correct ? '✅' : '❌';
        _el('ov-msg').textContent   = data.correct ? '정답!' : '오답...';
        _el('ov-score').textContent = data.correct
          ? `+${data.scoreGained}점 획득!` : '아쉽지만 다음 기회에!';
        break;
      }

      case 'g_show_answer': {
        stopTimer();
        _el('timer-wrap').style.display = 'none';
        _el('answer-reveal-text').textContent = data.correctText;
        renderRanking('ranking-list', data.ranking);
        animNextBar(data.timeLimit);
        showView('view-answer');
        break;
      }

      case 'g_countdown': {
        stopTimer();
        showView('view-countdown');
        let n = data.countdown;
        const el = _el('countdown-num');
        (function tick() {
          if (!el) return;
          el.textContent = n;
          el.classList.remove('count-pop'); void el.offsetWidth; el.classList.add('count-pop');
          if (n > 0) { n--; setTimeout(tick, 1000); }
        })();
        break;
      }

      case 'g_final_results': {
        const { ranking, waitTime } = data;
        const podium = _el('podium');
        const rest   = _el('rest-ranking');
        podium.innerHTML = rest.innerHTML = '';

        [1, 0, 2].forEach(idx => {
          const item = ranking[idx];
          if (!item) return;
          const div = document.createElement('div');
          div.className = 'podium-item';
          div.innerHTML =
            `<div class="podium-avatar">${['🥇','🥈','🥉'][idx]}</div>` +
            `<div class="podium-name">${esc(item.name)}</div>` +
            `<div class="podium-score">${item.score.toLocaleString()}점</div>` +
            `<div class="podium-block ${'gold silver bronze'.split(' ')[idx]}">${idx+1}위</div>`;
          podium.appendChild(div);
        });

        ranking.slice(3).forEach((item, i) => {
          const d = document.createElement('div');
          d.className = 'rank-item';
          d.style.animationDelay = (i * 0.1) + 's';
          d.innerHTML =
            `<span class="rank-medal">${4+i}위</span>` +
            `<span class="rank-name">${esc(item.name)}</span>` +
            `<span class="rank-score">${item.score.toLocaleString()}점</span>`;
          rest.appendChild(d);
        });

        showView('view-final');
        startRedirectCD(waitTime);
        break;
      }

      case 'g_lobby_reset': {
        clearInterval(S.redirectIv);
        S.myScore = 0; S.answered = false; S.qIdx = -1;
        stopTimer();
        showView('view-lobby');
        break;
      }
    }
  }

  /* ══════════════════════════════════════════════════════
     관리자 게임 로직
  ══════════════════════════════════════════════════════ */

  function adminJoin(name) {
    S.isAdmin = true;
    S.myName  = name;
    S.status  = 'waiting';
    S.players[MY_ID] = { name, score: 0 };

    _el('lobby-sub').textContent =
      `👑 관리자 모드 | 다른 탭에서 이 페이지를 열어 참가자를 모으세요!`;
    _el('admin-panel').style.display   = 'block';
    _el('share-section').style.display = 'block';
    _el('share-url-box').textContent   = window.location.href;

    updatePlayerList([name]);
    updateTimerPreview();
    showView('view-lobby');
  }

  /** 게임 시작 */
  function adminStartGame() {
    if (S.status !== 'waiting') return;

    const topic = _el('sel-topic').value;
    const diff  = _el('sel-diff').value;
    S.topic      = topic;
    S.difficulty = diff;
    S.questions  = shuffle([...QUIZ_BANK[topic][diff]]);
    S.status     = 'playing';
    S.curQ       = -1;

    for (const id in S.players) S.players[id].score = 0;
    S.myScore = 0;

    emitAll('g_starting', {
      topic,
      difficulty: diff,
      timeLimit:  getQTime(),
      total:      S.questions.length,
    });
    setTimeout(() => adminNextQuestion(), 2000);
  }

  /** 다음 문제 진행 */
  function adminNextQuestion() {
    if (S.status !== 'playing') return;
    S.curQ++;

    if (S.curQ >= S.questions.length) {
      adminFinish();
      return;
    }

    S.answersIn  = new Set();
    S.qStartTime = Date.now();
    const q     = S.questions[S.curQ];
    const qTime = getQTime();   // ★ 난이도별 시간

    emitAll('g_question', {
      qIdx:      S.curQ,
      qNum:      S.curQ + 1,
      total:     S.questions.length,
      q:         q.q,
      options:   q.options,
      timeLimit: qTime,         // ★ 핵심: 각 문제마다 제한시간 전달
    });

    clearTimeout(S.qTimerH);
    S.qTimerH = setTimeout(() => adminShowAnswer(S.curQ), qTime * 1000);
  }

  /** 정답+랭킹 표시 */
  function adminShowAnswer(qIdx) {
    if (S.curQ !== qIdx || S.status !== 'playing') return;
    clearTimeout(S.qTimerH); S.qTimerH = null;

    const q       = S.questions[qIdx];
    const ranking = adminGetRanking();

    emitAll('g_show_answer', {
      correctIndex: q.a,
      correctText:  q.options[q.a],
      ranking:      ranking.slice(0, 10),
      timeLimit:    RANK_TIME,
    });

    setTimeout(() => adminNextQuestion(), RANK_TIME * 1000);
  }

  /** 모든 문제 완료 → 최종 결과 흐름 */
  function adminFinish() {
    S.status = 'finished';
    emitAll('g_countdown', { countdown: CD_TIME });

    setTimeout(() => {
      const ranking = adminGetRanking();
      emitAll('g_final_results', { ranking, waitTime: FIN_TIME });
      setTimeout(() => adminReset(), FIN_TIME * 1000);
    }, (CD_TIME + 1) * 1000);
  }

  /** 방 초기화 */
  function adminReset() {
    S.status    = 'waiting';
    S.curQ      = -1;
    S.questions = [];
    emitAll('g_lobby_reset', {});
    broadcastPlayerList();
  }

  function adminGetRanking() {
    return Object.values(S.players)
      .map(p => ({ name: p.name, score: p.score }))
      .sort((a, b) => b.score - a.score);
  }

  function broadcastPlayerList() {
    const names = Object.values(S.players).map(p => p.name);
    emitAll('g_player_list', { players: names });
  }

  /* ══════════════════════════════════════════════════════
     입장 로직
  ══════════════════════════════════════════════════════ */

  function joinGame() {
    if (!ch) {
      setError('⚠️ BroadcastChannel 미지원 브라우저입니다. Chrome / Edge / Firefox 최신 버전을 사용해주세요.');
      return;
    }

    const input = _el('input-name');
    const name  = input.value.trim();
    setError('');

    if (!name)           { setError('⚠️ 이름을 입력해주세요.'); input.focus(); return; }
    if (name.length > 20) { setError('⚠️ 이름은 20자 이하여야 합니다.'); return; }

    const btn = _el('btn-join');
    btn.disabled = true;
    btn.innerHTML = '⏳ 연결 중...';

    if (name === ADMIN_NAME) {
      adminJoin(name);
      return;
    }

    S.joinTimer = setTimeout(() => {
      resetJoinBtn();
      setError(`⚠️ 관리자(${ADMIN_NAME})가 없습니다. 관리자가 먼저 입장해야 합니다.`);
    }, 10000);

    bcast('p_join', { name });
  }

  /** 답변 제출 */
  function submitAnswer(idx) {
    if (S.answered) return;
    S.answered = true;
    document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);
    document.querySelectorAll('.option-btn')[idx].classList.add('selected');

    if (S.isAdmin) {
      handlePlayerMsg('p_answer', { answer: idx, qIdx: S.qIdx }, MY_ID, Date.now());
    } else {
      bcast('p_answer', { answer: idx, qIdx: S.qIdx });
    }
  }

  /* ══════════════════════════════════════════════════════
     관리자 패널 UI 핸들러
  ══════════════════════════════════════════════════════ */

  /** 난이도 변경 시: 타이머 미리보기 갱신 & S.difficulty 업데이트 */
  function onDiffChange() {
    S.difficulty = _el('sel-diff').value;
    updateTimerPreview();
  }

  /** 주제 변경 시: 문제 수 힌트 표시 (연습 게임은 3문제임을 강조) */
  function onTopicChange() {
    updateTimerPreview();
  }

  /** ★ 관리자가 타이머 입력값을 직접 변경했을 때 */
  function onTimerChange() {
    const hardEl = _el('input-time-hard');
    const easyEl = _el('input-time-easy');
    if (!hardEl || !easyEl) return;

    // 1~99 범위로 클램프
    const hard = Math.max(1, Math.min(99, parseInt(hardEl.value) || 10));
    const easy = Math.max(1, Math.min(99, parseInt(easyEl.value) || 3));

    S.qtimeMap['상'] = hard;
    S.qtimeMap['하'] = easy;

    // sel-diff 옵션 텍스트에 변경된 시간 반영
    updateDiffOptions();
    // 미리보기 업데이트
    updateTimerPreview();
  }

  /** sel-diff 드롭다운 옵션 텍스트를 현재 qtimeMap 기준으로 갱신 */
  function updateDiffOptions() {
    const sel = _el('sel-diff');
    if (!sel) return;
    sel.options[0].text = `상 (어려움) · ⏱ ${S.qtimeMap['상']}초`;
    sel.options[1].text = `하 (쉬움) · ⏱ ${S.qtimeMap['하']}초`;
  }

  /** 타이머 미리보기 숫자 갱신 */
  function updateTimerPreview() {
    const diff = _el('sel-diff') ? _el('sel-diff').value : S.difficulty;
    S.difficulty = diff;
    const sec = S.qtimeMap[diff] || 10;
    const el  = _el('preview-sec');
    if (el) {
      el.textContent = sec;
      el.style.color = sec <= 5 ? 'var(--c1)' : 'var(--c2)';
    }
  }

  /* ══════════════════════════════════════════════════════
     UI 유틸리티
  ══════════════════════════════════════════════════════ */

  function showView(id) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const el = document.getElementById(id);
    if (!el) { console.error('[showView] 없는 뷰:', id); return; }
    el.classList.add('active');
    el.classList.remove('fade-in'); void el.offsetWidth; el.classList.add('fade-in');
  }

  function toast(msg, ms = 2600) {
    const t = _el('toast');
    t.textContent = msg; t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), ms);
  }

  function setError(msg) {
    const el = _el('join-error');
    if (!el) return;
    if (msg) { el.textContent = msg; el.style.display = 'block'; }
    else      { el.style.display = 'none'; }
  }

  function resetJoinBtn() {
    clearTimeout(S.joinTimer); S.joinTimer = null;
    const btn = _el('btn-join');
    if (btn) { btn.disabled = false; btn.innerHTML = '🎯 입장하기!'; }
  }

  function esc(t) {
    return String(t).replace(/[&<>"']/g, m =>
      ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[m]));
  }

  function _el(id) { return document.getElementById(id); }

  function updatePlayerList(players) {
    const grid = _el('player-grid');
    const cnt  = _el('player-count-text');
    if (!grid) return;
    grid.innerHTML = '';
    players.forEach((n, i) => {
      const c = document.createElement('div');
      c.className = 'player-chip';
      c.textContent = n;
      c.style.animationDelay = (i * 0.05) + 's';
      grid.appendChild(c);
    });
    if (cnt) cnt.textContent = `참가자 ${players.length}명 입장 중`;
  }

  function renderRanking(elId, list, max = 10) {
    const el = _el(elId);
    if (!el) return;
    el.innerHTML = '';
    list.slice(0, max).forEach((item, i) => {
      const d = document.createElement('div');
      d.className = 'rank-item';
      d.style.animationDelay = (i * 0.08) + 's';
      d.innerHTML =
        `<span class="rank-medal">${['🥇','🥈','🥉'][i] || (i+1)+'위'}</span>` +
        `<span class="rank-name">${esc(item.name)}</span>` +
        `<span class="rank-score">${item.score.toLocaleString()}점</span>`;
      el.appendChild(d);
    });
  }

  /* ── 비주얼 타이머 ────────────────────────────────── */
  function startTimer(secs, total) {
    stopTimer();
    let rem = Math.ceil(secs);
    const numEl = _el('timer-num');
    const cirEl = _el('timer-circle');

    (function tick() {
      const pct = (rem / total) * 360;
      if (cirEl) cirEl.style.setProperty('--pct', pct + 'deg');
      if (numEl) {
        numEl.textContent = rem;
        numEl.classList.remove('pulse'); void numEl.offsetWidth; numEl.classList.add('pulse');
      }
      if (rem <= 0) {
        stopTimer();
        document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);
        return;
      }
      rem--;
      S.timerH = setTimeout(tick, 1000);
    })();
  }

  function stopTimer() {
    clearTimeout(S.timerH); S.timerH = null;
  }

  function animNextBar(secs) {
    const bar = _el('next-bar');
    if (!bar) return;
    bar.style.transition = 'none'; bar.style.width = '100%';
    void bar.offsetWidth;
    bar.style.transition = `width ${secs}s linear`; bar.style.width = '0%';
  }

  function startRedirectCD(secs) {
    clearInterval(S.redirectIv);
    let n = secs;
    const el = _el('redirect-count');
    if (el) el.textContent = n;
    S.redirectIv = setInterval(() => {
      n--;
      if (el) el.textContent = Math.max(0, n);
      if (n <= 0) clearInterval(S.redirectIv);
    }, 1000);
  }

  function manualLobby() {
    clearInterval(S.redirectIv);
    S.myScore = 0; S.answered = false; S.qIdx = -1;
    stopTimer();
    showView('view-lobby');
  }

  function copyUrl() {
    const url = _el('share-url-box').textContent;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => toast('🔗 링크 복사 완료!'));
    } else {
      const ta = document.createElement('textarea');
      ta.value = url; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
      toast('🔗 링크 복사 완료!');
    }
  }

  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  /* ══════════════════════════════════════════════════════
     초기화
  ══════════════════════════════════════════════════════ */
  (function init() {
    if (!window.BroadcastChannel) {
      const e = _el('join-error');
      e.textContent = '⚠️ BroadcastChannel API 미지원 브라우저입니다. Chrome / Edge / Firefox 최신 버전을 사용해주세요.';
      e.style.display = 'block';
      _el('btn-join').disabled = true;
      return;
    }
    _el('input-name').focus();
    _el('mode-text').textContent = '로컬 멀티탭 v4 · 서버 없음';
  })();
  </script>
</body>
</html>
```
