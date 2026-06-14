# Korean Industrial Webtoon Safety

## 용도

산업안전 교육 영상을 현대 한국 웹툰풍으로 만들 때 사용한다. 현장 장비와 동선은
교육자료처럼 명확하게 보이되, 인물 표정과 장면 흐름은 웹툰 컷처럼 읽히게 한다.

## Visual DNA

- 현대 한국 웹툰풍, 네이버 웹툰에서 볼 법한 깔끔한 교육 만화 톤
- 얇고 선명한 외곽선, 과하지 않은 캐릭터화, 실제 작업자에 가까운 신체 비율
- 밝은 셀 셰이딩, 부드러운 하이라이트, 과도한 3D 플라스틱 질감 금지
- 안전모, 형광 조끼, 위험구역, 보행자 동선은 높은 가독성의 색상으로 강조
- 산업 현장은 단순화하되 BCT, 덤프트럭, 레미콘 플랜트, 보행로 같은 핵심 구조는 유지
- 인물 시선은 항상 보이는 위험, 신호수, 운전자, 거울, 모니터, 보행 동선 중 하나를 향해야 함
- 장면은 단독 포스터가 아니라 이전 컷과 다음 컷을 잇는 웹툰식 연속 컷처럼 구성

## Prompt Block

Use a modern Korean webtoon safety-training style: crisp clean line art, realistic adult worker proportions,
controlled cel shading, bright industrial safety colors, readable site geometry, and expressive but restrained
faces. Keep the scene educational and causal, like a sequence from a serious workplace safety webtoon.
Preserve PPE colors, vehicle shapes, road markings, hazard zones, and gaze motivation across every keyframe.

## Negative Constraints

- no chibi, no gag manga, no fantasy action, no superhero pose
- no photorealistic CCTV look, no dark gritty drama, no horror lighting
- no random bystanders, no unexplained person disappearance, no duplicate worker
- no visible company logo, no generated Korean or English text inside the image
- no collision impact, no injury, no gore, no unsafe behavior shown as successful

## QA Checklist

- 인물 비율이 성인 작업자처럼 보이는가
- 안전모/조끼/작업복 색상이 모든 컷에서 유지되는가
- 시선이 왜 그 방향을 보는지 화면 안에서 설명되는가
- 위험구역과 안전 동선이 웹툰풍 안에서도 명확히 읽히는가
- 이전/다음 컷과 이어지는 원인-행동-결과 흐름이 보이는가

## References

- `references/reference-001.png`: Codex imagegen으로 만든 레미콘 충돌 예방 웹툰풍 기준 이미지
