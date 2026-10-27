# 로컬 모델 추출 시험 (방법 정보 찾기 + 원문 인용 + 부재 판정)

소형 로컬 모델이 논문 섹션에서 방법 정보를 찾아 **원문 그대로 인용**하는지, 그리고 원문에 없는 정보를 "없음"으로 판정하는지 확인하는 시험이다. 로드맵 1.3절 4항, 1.8절 참고.

- 입력 논문 3편은 모두 오픈 액세스(CC BY-NC)이고, `make_inputs.py`가 PMC에서 받아 변환한다. 논문 본문 텍스트와 모델 출력은 저장소에 넣지 않는다(`.gitignore`).
- 문항 10개: 찾기 6개(S1-S3, K1, K2, C2), 부재 판정 4개(S4, K3, K4, C1). 부재 문항은 비슷해 보이는 글이 원문에 있는 함정을 포함한다. 정답 기준은 `score.py`의 `TRUTH`.

## 실행

```
cd eval/local_model_extraction
python3 make_inputs.py                      # *_full.txt, *_methods.txt 생성, 해시 출력
python3 run_test.py http://localhost:11434/v1 <모델명> results.jsonl
python3 score.py results.jsonl
```

- Ollama를 쓸 때는 컨텍스트(`num_ctx`)를 24576 이상으로 설정한다. 기본값 4096에서는 입력이 조용히 잘린다. 결과의 `prompt_tokens`로 잘림을 확인한다.
- 입력 해시(2026-10-27 기준): chew_full 74f5613254c63bc5, kaji_full 82c0396c9ea58016, song_full e10dd854c386cfba, chew_methods bd8b49ef3b3c4cd6, kaji_methods 48e69e3eb6487fb6, song_methods 050e85af46ce7544.

## 한계

문항이 한 문장 안에서 답이 나오는 literal 질문이고, 입력이 PMC XML에서 뽑은 깨끗한 텍스트다. PDF 추출 텍스트, 스캔본 OCR, 표현을 바꾼 질문, 여러 문장을 종합하는 질문은 아직 포함하지 않았다.
