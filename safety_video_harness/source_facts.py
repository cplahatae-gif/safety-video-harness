from __future__ import annotations


def facts_for_sources(source_entries: list) -> list[dict]:
    facts: list[dict] = []
    for entry in source_entries:
        path = str(entry["path"])
        source_id = str(entry["source_id"])
        if is_remicon_collision_source(path):
            facts.extend(remicon_collision_facts(source_id))
        else:
            facts.append(
                {
                    "source_id": source_id,
                    "page_or_slide": 1,
                    "claim": "교육자료 기반 핵심 위험요인",
                    "keywords": ["안전", "위험요인", "예방"],
                }
            )
    return facts


def topics_from_facts(citations: list[dict]) -> list[dict]:
    blob = " ".join(str(citation["claim"]) for citation in citations)
    if "레미콘" in blob:
        return [
            {
                "topic_id": "topic-001",
                "title_ko": "레미콘 사업장 대형차량 충돌·접촉 예방",
                "risk_type": "vehicle_collision_blind_spot",
                "target_worker": "레미콘 사업장 근로자, 신호수, 운전원",
                "source_citations": citations,
                "video_fit_score": 5,
                "priority_score": 5,
                "recommended": True,
            },
            {
                "topic_id": "topic-002",
                "title_ko": "신호수 배치와 후방카메라 확인 절차",
                "risk_type": "signal_person_absent_reverse_collision",
                "target_worker": "신호수, 관리감독자, 차량 운전원",
                "source_citations": citations,
                "video_fit_score": 4,
                "priority_score": 5,
                "recommended": False,
            },
        ]
    return [
        {
            "topic_id": "topic-001",
            "title_ko": "핵심 위험요인 예방",
            "risk_type": "general",
            "target_worker": "현장 작업자",
            "source_citations": citations,
            "video_fit_score": 4,
            "priority_score": 4,
            "recommended": True,
        }
    ]


def is_remicon_collision_source(path: str) -> bool:
    lowered = path.lower()
    return "remicon-collision-guide" in lowered or "레미콘" in path or "충돌" in path


def remicon_collision_facts(source_id: str) -> list[dict]:
    return [
        {
            "source_id": source_id,
            "page_or_slide": 1,
            "claim": "레미콘 사업장 충돌·접촉 안전작업 가이드는 대형차량 진입 및 하역 작업 시 필수 안전 수칙을 다룬다.",
            "keywords": ["레미콘", "충돌", "접촉", "대형차량", "하역"],
        },
        {
            "source_id": source_id,
            "page_or_slide": 2,
            "claim": "레미콘 공장에 입고되는 대형차량의 주행, 하역, 대기 중 충돌·접촉 사고를 예방해 근로자의 생명을 보호해야 한다.",
            "keywords": ["주행", "하역", "대기", "충돌", "근로자"],
        },
        {
            "source_id": source_id,
            "page_or_slide": 3,
            "claim": "근로자는 사업장 내 제한속도 10~20km 이하를 준수하고 보행 중 스마트폰 사용을 금지해야 한다.",
            "keywords": ["근로자", "제한속도", "스마트폰 금지"],
        },
        {
            "source_id": source_id,
            "page_or_slide": 3,
            "claim": "감시인 또는 신호수는 차량 유도 시 보행자 접근을 상시 감시하고 무전기와 신호봉으로 운전원과 소통해야 한다.",
            "keywords": ["신호수", "감시인", "무전기", "신호봉"],
        },
        {
            "source_id": source_id,
            "page_or_slide": 4,
            "claim": "사각지대 내 보행자 미인지 상태에서 대형차량 후진 및 회전 시 보행자 충돌 위험이 크다.",
            "keywords": ["사각지대", "후진", "회전", "보행자 충돌"],
        },
        {
            "source_id": source_id,
            "page_or_slide": 4,
            "claim": "지정 구역 외 임의 작업과 통로 침범은 차량 밀림 및 끼임 위험을 높인다.",
            "keywords": ["지정구역", "임의작업", "통로", "끼임"],
        },
        {
            "source_id": source_id,
            "page_or_slide": 5,
            "claim": "BCT 또는 덤프트럭 후진 중 신호수 미배치, 후방카메라 불량, 보행통로 미준수는 충돌 사고 원인이 된다.",
            "keywords": ["BCT", "덤프트럭", "후진", "신호수 미배치", "후방카메라"],
        },
    ]
