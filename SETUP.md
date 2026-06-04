# Streamlit + Supabase 연동 설정 가이드

이 문서는 CSV 데이터를 Supabase에 업로드하고 Streamlit 대시보드에서 실시간으로 표시하는 전체 과정을 기록합니다.

## 목차
1. [Supabase 설정](#supabase-설정)
2. [Streamlit 앱 수정](#streamlit-앱-수정)
3. [Secrets 설정](#secrets-설정)
4. [실행 및 테스트](#실행-및-테스트)
5. [주의사항](#주의사항)

---

## Supabase 설정

### 1단계: CSV 파일 준비

```
C:\test\data\sales.csv
```

CSV 구조:
```csv
date,category,product,broadcast_time,sales,orders,host
2026-04-01,패션,럭셔리 핸드백,21:35,21915253,283,신정호
```

### 2단계: Supabase에서 테이블 생성

**프로젝트 정보:**
- URL: `https://akpyanfpcpkxgubxoitl.supabase.co`
- Project ID: `akpyanfpcpkxgubxoitl`

**테이블 생성 SQL:**

```sql
CREATE TABLE sales (
  id BIGSERIAL PRIMARY KEY,
  date DATE NOT NULL,
  category TEXT NOT NULL,
  product TEXT NOT NULL,
  broadcast_time TIME NOT NULL,
  sales BIGINT NOT NULL,
  orders BIGINT NOT NULL,
  host TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);
```

### 3단계: 데이터 삽입

CSV의 모든 행을 INSERT 문으로 Supabase에 삽입합니다.
(150개 행의 매출 데이터)

**확인 방법:**
```bash
# SQL Editor에서 실행
SELECT COUNT(*) FROM sales;  -- 결과: 150
```

---

## Streamlit 앱 수정

### 현재 코드 구조

**`app.py`의 주요 변경사항:**

#### 1. Supabase REST API 사용

이전에는 supabase 라이브러리를 사용하려 했지만, 윈도우에서 컴파일 오류가 발생하므로 **REST API를 직접 사용**합니다.

```python
import requests

@st.cache_data(ttl=0)  # ttl=0: 캐시 비활성화
def load_data():
    supabase_url, supabase_key = get_supabase_config()
    
    url = f"{supabase_url}/rest/v1/sales"
    headers = {
        "apikey": supabase_key,
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df
```

#### 2. 설정 함수

```python
def get_supabase_config():
    # secrets.toml에서 Supabase 설정 읽기
    supabase_url = st.secrets.get("supabase_url") or \
                   st.secrets.get("supabase", {}).get("url")
    supabase_key = st.secrets.get("supabase_key") or \
                   st.secrets.get("supabase", {}).get("key")
    
    if not supabase_url or not supabase_key:
        st.error("Supabase 설정이 없습니다.")
        st.stop()
    
    return supabase_url, supabase_key
```

---

## Secrets 설정

### 파일 위치

```
C:\test\.streamlit\secrets.toml
```

### 내용 (절대 Git에 커밋하지 말 것!)

```toml
# Supabase 연결 설정 (방법 1: 구조화된 형식)
[supabase]
url = "https://akpyanfpcpkxgubxoitl.supabase.co"
key = "sb_publishable_Hbapm89Bu3s5RxFJYvrhfw_lqB1pAK7"

# 또는 방법 2: 직접 참조 (둘 다 지원)
supabase_url = "https://akpyanfpcpkxgubxoitl.supabase.co"
supabase_key = "sb_publishable_Hbapm89Bu3s5RxFJYvrhfw_lqB1pAK7"
```

### 보안 - .gitignore

```
# .gitignore에 추가
.streamlit/secrets.toml
.streamlit/secrets.local.toml
.env
.env.local
```

이렇게 하면 secrets.toml이 Git에 업로드되지 않습니다.

---

## 실행 및 테스트

### 1단계: 필수 패키지 설치

```bash
cd c:\test
pip install -r requirements.txt
```

**requirements.txt 내용:**
```
streamlit>=1.28.0
pandas>=2.0.0
matplotlib>=3.8.0
requests>=2.31.0
```

### 2단계: Streamlit 실행

```bash
cd c:\test
streamlit run app.py
```

**출력:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 3단계: 브라우저에서 확인

```
http://localhost:8501
```

표시되는 항목:
- ✅ 오늘 매출 (latest_date의 총 sales)
- ✅ 어제 매출 (previous_date의 총 sales)
- ✅ 어제 대비 증감률
- ✅ 일별 매출 추이 (차트)
- ✅ 카테고리별 매출 비중 (원형차트)
- ✅ 총 매출액, 총 주문수, 일평균 매출

### 4단계: 데이터 수정 후 변경 확인

Supabase에서 데이터를 수정하면, **브라우저를 새로고침**하면 즉시 반영됩니다.

**예: 처음 5개 행의 금액을 2배로 수정**

SQL:
```sql
UPDATE sales 
SET sales = sales * 2 
WHERE id IN (1, 2, 3, 4, 5);
```

결과: Streamlit 대시보드의 모든 수치가 2배로 증가 (캐시 비활성화 시)

---

## 주의사항

### 1. 캐시 문제

Streamlit의 `@st.cache_data` 데코레이터는 기본적으로 데이터를 캐시합니다.

**해결책:**
```python
@st.cache_data(ttl=0)  # ttl=0: 캐시 비활성화
def load_data():
    ...
```

또는 특정 시간만 캐시:
```python
@st.cache_data(ttl=300)  # 300초 = 5분
def load_data():
    ...
```

### 2. API Key 보안

- ❌ secrets.toml을 Git에 커밋하지 말 것
- ✅ .gitignore에 `.streamlit/secrets.toml` 추가
- ✅ 환경 변수로 관리 (프로덕션 환경)

### 3. Supabase API Key 종류

- **anonPublic**: 공개 데이터 읽기 (RLS로 보호)
- **sb_publishable_...**: 최신 형식의 공개 키
- **serviceRole**: 관리자 권한 (절대 공개하지 말 것)

현재 사용: `sb_publishable_...` (공개 키)

### 4. 윈도우 환경 특이사항

- supabase 라이브러리 설치 실패 (C++ 컴파일 필요)
- 대신 requests 라이브러리로 REST API 직접 호출
- PowerShell의 heredoc 문법 다름 (백슬래시 대신 백틱)

---

## 문제 해결

### 문제: "ModuleNotFoundError: supabase"

**원인:** supabase 라이브러리 컴파일 오류

**해결:**
1. requirements.txt에서 supabase 제거
2. REST API 사용으로 변경
3. requests 라이브러리만 사용

### 문제: Streamlit에서 숫자가 안 바뀜

**원인:** 캐시된 데이터 사용

**해결:**
1. `@st.cache_data(ttl=0)` 설정
2. Streamlit 프로세스 종료 후 재시작
3. 브라우저 새로고침

### 문제: Supabase 403 에러

**원인:** API Key 오류 또는 권한 부족

**확인:**
```bash
# API Key 테스트
curl -H "apikey: YOUR_KEY" \
  https://YOUR_PROJECT.supabase.co/rest/v1/sales?limit=1
```

---

## Git 커밋 내역

```bash
git log --oneline -5
```

```
ce13cf5 Add Supabase integration with REST API and Streamlit secrets configuration
0bc4056 Fix font compatibility for Streamlit Cloud deployment
c9e4cd2 Add requirements.txt with necessary dependencies
f1832c4 Add Streamlit dashboard
```

**최신 커밋 (ce13cf5)의 변경사항:**
- ✅ app.py: Supabase REST API 연동
- ✅ requirements.txt: requests 추가
- ✅ data/sales.csv: 최신 데이터
- ✅ .gitignore: 보안 설정

---

## 다음 단계 (선택사항)

### 1. Streamlit Cloud 배포

```bash
# GitHub에 푸시됨
git push origin master
```

Streamlit Cloud (https://streamlit.io/cloud) 에서 자동 배포 가능

### 2. 자동 새로고침 추가

```python
import time
while True:
    st.rerun()
    time.sleep(60)  # 60초마다 새로고침
```

### 3. 데이터베이스 쿼리 최적화

```python
# 필요한 컬럼만 선택
url = f"{supabase_url}/rest/v1/sales?select=date,category,sales,orders"
```

### 4. 에러 처리 개선

```python
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    st.error(f"네트워크 오류: {str(e)}")
```

---

## 참고 링크

- [Supabase 문서](https://supabase.com/docs)
- [Streamlit 문서](https://docs.streamlit.io)
- [Supabase REST API](https://supabase.com/docs/reference/api/rest)
- [Streamlit Secrets](https://docs.streamlit.io/develop/concepts/connections/secrets-management)

---

**마지막 업데이트:** 2026-06-04
**작성자:** Claude Code
**상태:** ✅ 완료 및 테스트 완료
