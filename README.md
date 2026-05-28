# SafeMed

어르신 다약 복용 안전을 위한 다제 상호작용 위험 평가 서비스. 한국 식약처(MFDS) 공공 API 의약품 데이터를 구조화된 규칙·신호·관계 네트워크 점수와 결합하고, NVIDIA NIM 기반 LLM이 60세 이상 어르신께 쉬운 설명을 제공합니다.

## 구조

```
SafeMed/
  backend/   FastAPI · Python 3.12+
  frontend/  React 18 · Vite 5 · Tailwind 3
  data/      sample DUR CSVs, cache, processed data
  docs/      ARCHITECTURE / PHASES / SETUP
```

## Risk 평가 공식

```
Risk = α·Rule + β·PRR + γ·AE_Freq + δ·GCN
       α=0.45  β=0.30  γ=0.15  δ=0.10
```

- **Rule**: DUR 병용금기 / 노인주의 / 임부금기 / 효능군 중복
- **PRR**: 비례보고비 (Evans 2001, PRR ≥ 2 ∧ χ² ≥ 4 ∧ a ≥ 3)
- **AE_Freq**: 부작용 보고 빈도
- **GCN**: 동시복용 그래프 중심성 기반 증폭 인자

점수 대역: `0–30 🟢 안전` / `31–60 🟡 주의` / `61–100 🔴 위험`

## 로컬 실행

### 한 방에 (Docker Compose)

```bash
docker compose up --build
# backend  → http://localhost:8000
# frontend → http://localhost:5173
```

### 수동 실행

```bash
# 1) 백엔드
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload   # http://localhost:8000

# 2) 프론트엔드 (새 터미널)
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

### 환경 변수

`backend/.env` 설정:

```env
MFDS_SERVICE_KEY=...               # data.go.kr (URL-encoded 원본 키)
MFDS_KEY_IS_URL_ENCODED=true
LLM_PROVIDER=nim                   # nim | upstage | ollama | none
NIM_API_KEY=...                    # NVIDIA NIM 키 (build.nvidia.com)
NIM_MODEL=meta/llama-3.1-70b-instruct
```

`frontend/.env` 설정:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 테스트

```bash
cd backend
pytest                            # rules / signal / fetcher / analyze
```

## AI 학습 (선택)

SafeMed는 학습이 필요한 부분과 필요 없는 부분이 분리되어 있어요.

| 컴포넌트                         | 학습 필요? | 비고                                     |
| -------------------------------- | ---------- | ---------------------------------------- |
| **Module 1 — 규칙 엔진 (DUR)**   | ❌         | 식약처 CSV 매칭. 학습 개념 부적용.       |
| **Module 2 — PRR/ROR 통계 신호** | ❌         | EMA·FDA 표준 통계. 학습이 아니라 집계.   |
| **Module 2 — GCN 보조 검색**     | ✅ (선택)  | 학습 없으면 NetworkX 휴리스틱 폴백.      |
| **Module 3 — NIM LLM**           | ❌         | NVIDIA 사전학습 Llama-3.1-70B 추론 호출. |

### GCN 학습 (Phase B용, 진짜 데이터 들어오면 실행)

```bash
cd backend
pip install -e ".[ml]"            # torch + torch-geometric (~1GB)

# 1) 한국의약품안전관리원 "병용금기약물" CSV를 받아
#    data/raw/dur_combo.csv 로 저장

# 2) 학습 (CPU 7분 / CUDA 1분 수준)
python -m app.ml.train \
    --combo-csv ../data/raw/dur_combo.csv \
    --out ../data/processed/gcn_embeddings.pt \
    --epochs 200

# 3) 임베딩 품질 확인 (top-K 유사 성분)
python -m app.ml.evaluate \
    --emb ../data/processed/gcn_embeddings.pt \
    --query 와파린 --topk 10
```

임베딩 파일이 생기면 `app.signal.gcn`이 자동으로 감지해서 cosine 유사 성분에 위험 증폭 보너스를 얹어줘요. 파일이 없으면 그대로 NetworkX 휴리스틱으로 동작합니다 — 즉 데모 단계에서는 학습 없이도 분석 결과가 나옵니다.

## 주의

본 서비스는 **참고용**이며 의료적 진단·처방을 대체하지 않습니다. 약 복용 전에는 반드시 의사·약사 선생님과 상의하세요.

## 라이선스

MIT (see `LICENSE`).
