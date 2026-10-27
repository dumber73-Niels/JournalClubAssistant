# 라이선스 등급 조사 (Crossref)

논문 DOI와 그 참고문헌(DOI가 있는 것)의 라이선스를 Crossref로 조회해 F(CC 라이선스) / L(그 외) / unknown으로 나눈다. 로드맵 1.8절의 판정 규칙 중 Crossref 부분만 구현한 조사용 스크립트이며, 실제 판정 모듈은 PMC·Europe PMC·Unpaywall도 함께 조회해야 한다.

```
python3 grade.py "10.1002/JPER.24-0082,10.1111/clr.14435"   # 쉼표로 구분한 DOI 목록 → grades.json
```

- 출력 `grades.json`은 DOI별로 본인 등급, 참고문헌 수, 참고문헌 등급 목록과 연도를 담는다. 저장소에는 넣지 않는다.
- Crossref에 `tdm_license`(Wiley 자체 텍스트마이닝 라이선스)만 있는 경우는 F가 아니다. CC URL이 있고 `content-version`이 `vor` 또는 `unspecified`인 것만 F로 센다.
- 일시 오류(요청 제한)가 있어 재시도와 캐시를 넣었다. 예의를 위해 `User-Agent`에 연락처를 넣는다.
