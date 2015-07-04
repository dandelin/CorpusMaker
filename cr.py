import requests, regex

def extract_multilingual(url):
    # requests로 url에서 raw html을 가져옴
    text = requests.get(url).text
    # lxml.html로 raw html을 etree로 파싱함
    body = html.fromstring(text)
    # etree의 모든 innertext를 가져옴
    texts = body.xpath("//*/text()")
    # [[a-zA-z0-9_]\s]+로만 이루어져있거나 한글이 포함된 구문만 담음
    texts = [text for text in texts if regex.search(ur'\p{Hangul}+', text) or regex.fullmatch(r'[\w\s]+', text)]
    # 각 구문에 대해 한글과 영단어만 추출
    texts = [regex.findall(ur'\p{Hangul}+\.?|\p{Latin}+\.?', text) for text in texts]
    # flatten list
    texts = [unicode(t) for text in texts for t in text]
    return texts