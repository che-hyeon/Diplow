from datetime import datetime
from project.celery import app
from status.models import Nation
from .models import MovementData
import os, environ
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR,'.env'))
NATION_DATA_KEY_3 = env('NATION_DATA_KEY_3')

import logging

logger = logging.getLogger(__name__)

@app.task()
def load_movement_data_task():
    base_urls = [
        "/15052910/v1/uddi:edb0eae9-b88f-41e2-b86f-ce76377a404a",
        "/15052910/v1/uddi:3775853b-2279-4ddd-982f-e224f2ea4796",
        "/15052910/v1/uddi:372bebb0-0672-41c3-95dd-a48058fe28c1",
        "/15052910/v1/uddi:c48345b3-9368-42a4-8c59-ff9f0d8bc0ab",
        "/15052910/v1/uddi:a77218eb-01a9-4d84-8505-80c5ab87bc20",
        "/15052910/v1/uddi:c4d6575d-8c0a-443c-977f-b45f0cfa98eb",
        "/15052910/v1/uddi:3ca52d9d-ffa8-4bbc-a77c-cfd9b42dbcf4",
        "/15052910/v1/uddi:6538b438-7343-46c4-93d9-c13287208b1f",
        "/15052910/v1/uddi:120094ff-86b3-4bc6-ae0e-a9cceb34716f",
        "/15052910/v1/uddi:69ea1707-6d56-4d3b-88fd-a8b52aefcb75",
        "/15052910/v1/uddi:a7cf85a0-9c47-4a6f-9c22-9fd20d8e6371",
        "/15052910/v1/uddi:26560bc8-9ae7-4b26-ae68-954d2c786c89",
        "/15052910/v1/uddi:9b61ed70-d55f-4b02-8af3-eefa63e8f0b0",
        "/15052910/v1/uddi:228e1a48-f9f7-4ee3-bb37-f03d38262cd9",
        "/15052910/v1/uddi:55c3eba4-3f6d-4621-9a12-fca370103adc",
        "/15052910/v1/uddi:eee52c10-dbc2-405c-88b2-aef8eec9cc26",
        "/15052910/v1/uddi:3cd8d4ec-dc01-4af6-8b26-d66920f6abe1",
        "/15052910/v1/uddi:faf6e7e5-49de-4687-9ed2-ec4dfec5f94b",
        "/15052910/v1/uddi:6fac7a01-2324-49a9-b6e7-82b1443decda",
        "/15052910/v1/uddi:9b28bd0a-a0df-4c73-917a-92c0cc518504",
        "/15052910/v1/uddi:a1dd9b9a-48af-4f5f-a821-e4d59e12033f",
        "/15052910/v1/uddi:792a64d9-3e98-4e87-b8aa-cf3984dd2549",
        "/15052910/v1/uddi:44c8f5cc-2188-44b6-9b69-c26d4a8d20cc",
        "/15052910/v1/uddi:f1655578-28ef-4109-a8d0-f4ebeb711b51",
        "/15052910/v1/uddi:2fe7831f-c478-4326-9ef6-fe7ae96b0686",
        "/15052910/v1/uddi:967aa882-6ce6-49b1-b950-d94876c11c80",
        "/15052910/v1/uddi:ee4e3d3f-a86f-4a6d-a13e-b535e3794b84",
        "/15052910/v1/uddi:939c5ca1-f1f4-411f-b6e7-d76043933615",
        "/15052910/v1/uddi:c3d847c2-7c66-4507-ad96-f8e3d51ff9ad",
        "/15052910/v1/uddi:801f1b3b-794b-46a1-ba31-bca714c67b53",
        "/15052910/v1/uddi:c4d1dfa6-e930-4749-97ec-eb18912f8423",
        "/15052910/v1/uddi:e43273cf-a573-4542-871e-fba567347db9",
        "/15052910/v1/uddi:4aba0e0e-c850-4f88-a014-e1aa1f3e9480",
        "/15052910/v1/uddi:27468ccd-d38e-4898-a45e-f9b397337dd0",
        "/15052910/v1/uddi:26ec9120-fb8c-45a9-9e92-a8d7dc82bdfb",
        "/15052910/v1/uddi:daea05bd-c847-4c82-8191-fd7f0595964b",
        "/15052910/v1/uddi:83e5c97d-5c77-4f9b-bd37-a603b3dfe482",
        "/15052910/v1/uddi:77cb9100-b33e-49cd-89f2-e5b9bd72eed4",
        "/15052910/v1/uddi:20a6314b-6afb-4898-8ed1-f4bd1b2adbae",
        "/15052910/v1/uddi:a03a071c-b8f7-4a1f-886d-fe24e68dd582",
        "/15052910/v1/uddi:2aeef0a4-3b77-41f0-a666-b9ba186e4b8f",
        "/15052910/v1/uddi:843b9e85-8535-41db-a2d1-edd6d6e70f77",
        "/15052910/v1/uddi:699b3590-160f-4b84-be2f-f4bb38fb675b",
        "/15052910/v1/uddi:10ff0fb5-e1c6-4bc9-a90f-9adec2f7980f",
        "/15052910/v1/uddi:8034dfe2-86b4-4eef-86fa-b7a689206918",
        "/15052910/v1/uddi:1b70bbdd-084d-4b11-886d-f5b5f2a38c9e",
        "/15052910/v1/uddi:f0f80470-da29-4c15-81d9-f9e2912bec5a",
        "/15052910/v1/uddi:b11acb27-82f6-4b05-9dd3-9f5ea92bcbbf",
        "/15052910/v1/uddi:eff7fd98-dc31-4cbe-af6a-b108110a4067",
        "/15052910/v1/uddi:17ee3405-4807-4aa7-b233-ddc3c55f6c66",
        "/15052910/v1/uddi:c2981b2b-0e69-4319-a111-f8ed7a0c7fb7",
        "/15052910/v1/uddi:c490f93a-5af7-4bff-af34-c3be2b859326",
        "/15052910/v1/uddi:92c50f94-ad82-4b4a-b129-c8480669eab4",
        "/15052910/v1/uddi:a0c00070-5fb8-4cfe-b91d-e083b6d81588",
        "/15052910/v1/uddi:d5582a6a-031d-468c-9ee7-c5554c3ce938",
        "/15052910/v1/uddi:59c6389c-8119-477d-a053-ae02fba32d9a",
        "/15052910/v1/uddi:3aa9def5-6553-477b-8dee-af0a1b93b878",
        "/15052910/v1/uddi:09e546c2-6211-40fc-a020-cff839985968",
        "/15052910/v1/uddi:6b12b861-8acc-48cf-8fbd-8cc37d2f33e1",
        "/15052910/v1/uddi:c665ce09-3a5c-473e-97c7-fc5eae104656"
    ]
    service_key = NATION_DATA_KEY_3
    per_page = 100
    page = 1

    saved = []
    failed = []

    nations = Nation.objects.all()
    logger.info("이동 데이터 로딩 시작")
    for base_url in base_urls:
        try:
            count_url = f"https://api.odcloud.kr/api{base_url}?page=1&perPage=1&returnType=json&serviceKey={service_key}"
            try:
                count_response = requests.get(count_url, timeout=10)
                count_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                failed.append({"url": count_url, "reason": f"페이지 수 요청 실패: {str(e)}"})
                continue

            total_count = count_response.json().get("totalCount", 0)
            total_pages = (total_count // per_page) + (1 if total_count % per_page else 0)

            for page in range(1, total_pages + 1):
                url = f"https://api.odcloud.kr/api{base_url}?page={page}&perPage={per_page}&returnType=json&serviceKey={service_key}"
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    failed.append({"url": url, "page": page, "reason": f"요청 실패: {str(e)}"})
                    continue

                raw_data = response.json().get("data", [])
                for idx, item in enumerate(raw_data, start=1):
                    try:
                        nation_name_raw = item.get("국가명")
                        if not nation_name_raw:
                            failed.append({"page": page, "index": idx, "reason": "국가명 없음", "item": item})
                            continue

                        nation_name = nation_name_raw.strip()
                        matched_nation = None
                        for nation in nations:
                            if nation.nation_name and nation.nation_name in nation_name:
                                matched_nation = nation
                                break

                        if not matched_nation:
                            failed.append({"page": page, "index": idx, "reason": "국가 매칭 실패", "item": item})
                            continue

                        nation_type_raw = (item.get("구분") or "").strip()
                        if nation_type_raw == "공여국":
                            nation_type = "donor"
                        elif nation_type_raw == "수원국":
                            nation_type = "recipient"
                        else:
                            nation_type = "etc"

                        content_kr = "\n".join([(item.get(f"본문{i}") or "") for i in range(1, 6)]).strip()
                        content_en = "\n".join([(item.get(f"영문본문{i}") or "") for i in range(1, 6)]).strip()

                        date_str = (item.get("날짜") or "").strip()
                        try:
                            pub_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except ValueError:
                            failed.append({"page": page, "index": idx, "reason": f"날짜 형식 오류: {date_str}", "item": item})
                            continue

                        existing = MovementData.objects.filter(
                            nation=matched_nation,
                            category=(item.get("분야") or "").strip(),
                            title_kr=(item.get("제목") or "").strip(),
                            nation_type=nation_type,
                            pub_date=pub_date
                        ).first()

                        if existing:
                            continue  # 이미 존재

                        obj, created = MovementData.objects.update_or_create(
                            nation=matched_nation,
                            category=(item.get("분야") or "").strip(),
                            title_kr=(item.get("제목") or "").strip(),
                            nation_type=nation_type,
                            pub_date=pub_date,
                            defaults={
                                "title_en": (item.get("영문제목") or "").strip(),
                                "content_kr": content_kr,
                                "content_en": content_en,
                            }
                        )
                        saved.append({"page": page, "index": idx, "id": obj.id, "created": created})

                    except Exception as e:
                        failed.append({"page": page, "index": idx, "reason": str(e), "item": item})

        except Exception as e:
            failed.append({"url": base_url, "reason": f"기본 URL 반복 에러: {str(e)}"})
    logger.info("이동 데이터 로딩 종료")

