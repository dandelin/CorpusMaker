# CorpusMaker

Extract Web Community's Corpus

## 사용법

### 설치

현재 package로는 제공되지 않음  

1. git clone https://github.com/dandelin/CorpusMaker.git  
2. CorpusMaker 모듈을 파이썬 외부 모듈 경로에 복사  

#### 의존성

requests (http://docs.python-requests.org/en/latest/)  
regex (https://pypi.python.org/pypi/regex)  
lxml (http://lxml.de/)  
libextract.api (https://github.com/datalib/libextract)  

### 사용 예

```python
from CorpusMaker import cr, utils

spider = cr.Spider("http://wonjaekim.com", "wonjaekim.com", "cr.db")
spider.nstep(20)
utils.combine("cr.db")
```
