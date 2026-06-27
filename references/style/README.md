# Style Guides

이 폴더는 안전교육 영상 하네스가 재사용할 수 있는 시각 스타일 카탈로그다.
프로젝트별 일회성 레퍼런스는 `projects/<slug>/ref/approved/`에 두고, 여러 프로젝트에서
반복 사용하고 싶은 그림체와 렌더링 규칙은 이곳에 스타일별 폴더로 보관한다.

## 사용 규칙

1. 좋은 이미지 스타일이 나오면 `style-guides/<style-id>/` 폴더를 만든다.
2. `STYLE_GUIDE.md`에 스타일 DNA, 프롬프트 블록, 금지 요소, QA 기준을 적는다.
3. 참고 이미지는 `references/` 아래에 복사하고 원본 생성물은 삭제하지 않는다.
4. 프로젝트의 `project_config.json`에서 `style_guide_id`를 선택한다.
5. `generate_images.py`와 `generate_seedance.py`는 선택된 스타일 가이드를 프롬프트에 자동 주입한다.

## 현재 인터뷰 선택지

- `korean-industrial-webtoon`: 현대 한국 웹툰풍 안전교육 이미지
- `clean-instructional-3d`: 깔끔한 3D 안전교육 렌더
- `flat-vector-safety`: 단순 벡터/픽토그램형 안전교육
- `semi-realistic-industrial`: 준실사 산업현장 교육 장면
- `minimal-pictogram-training`: 최소 정보 중심 픽토그램/표지판형 교육

운영 인터뷰에서는 먼저 레퍼런스 보유 여부를 묻고, 다음 질문에서 위 5가지 스타일을
보여준 뒤 선택하게 한다.
