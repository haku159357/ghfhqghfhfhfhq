import os
import base64
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="맞춤형 여행 캐리어 패킹 리스트",
    page_icon="🧳",
    layout="centered"
)

# 결과 카드에 옅은 테두리 + 그림자를 입히는 스타일
st.markdown(
    """
    <style>
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 1. 상단 타이틀 및 설명
st.title("🧳 맞춤형 여행 캐리어 패킹 리스트")
st.caption("설레는 여행, 짐 싸기 고민은 그만! 몇 가지 옵션만 선택하면 나만의 맞춤형 체크리스트와 여행 꿀팁을 만들어 드려요.")

st.divider()

# 2. 입력 옵션 선택 폼
st.subheader("✈️ 여행 정보 선택하기")

# 여행 기간 (라디오 버튼)
period = st.radio(
    "1. 여행 기간을 선택해 주세요",
    ["당일/1박 2일", "2박~3박", "4박~6박", "1주일 이상"],
    horizontal=True
)

# 여행 날씨/계절 (드롭다운)
weather = st.selectbox(
    "2. 여행지 날씨/계절을 선택해 주세요",
    ["무더운 여름/휴양지", "선선한 봄/가을", "쌀쌀한 겨울", "일교차 큼"]
)

# 여행 목적/스타일 (드롭다운)
style = st.selectbox(
    "3. 여행 목적 및 스타일을 선택해 주세요",
    ["힐링 & 휴양", "도시 탐방 & 맛집", "캠핑 & 액티비티", "비즈니스 & 출장"]
)

# 동행인 (라디오 버튼)
companion = st.radio(
    "4. 누구와 함께 떠나시나요?",
    ["나 혼자", "연인/친구", "아이와 함께", "부모님과 함께"],
    horizontal=True
)

st.divider()

# 3. 결과 보기 버튼
if st.button("📋 결과 보기", use_container_width=True, type="primary"):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 작성 후 API 키를 설정해 주세요.")
    else:
        client = OpenAI(api_key=api_key)

        prompt = f"""
다음 여행 조건에 맞는 맞춤형 캐리어 패킹 리스트(체크리스트)와 실용적인 여행 꿀팁 3가지를 추천해줘.

[여행 조건]
- 여행 기간: {period}
- 날씨/계절: {weather}
- 여행 목적/스타일: {style}
- 동행인: {companion}

[요청 사항]
1. 카테고리별 체크리스트(필수 소지품, 의류/잡화, 뷰티/위생, 전자기기/기타)를 깔끔한 불릿 포인트로 작성해줘.
2. 해당 여행 조건에서 꼭 챙겨야 할 팩폭/실용 꿀팁 3가지를 번호를 붙여 작성해줘.
3. 친근하고 설레는 톤앤매너로 작성해줘.
"""

        result_text = None
        with st.spinner("✈️ 고객님의 여행 조건에 맞춰 패킹 리스트를 생성하는 중입니다..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 여행 준비를 도와주는 친절하고 스마트한 여행 패킹 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                result_text = response.choices[0].message.content

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

        image_prompt = f"""
A clean, minimal flat-lay illustration of a travel packing scene for a "{period}" trip.
Weather/season: {weather}. Travel style: {style}. Traveling with: {companion}.
Show a stylish carry-on suitcase neatly packed with items that match this trip's weather and style,
along with a few essentials laid out beside it.
Mood: cheerful, witty, practical, clean, smart (설렘, 위트있는, 실용적인, 깔끔함, 스마트한).
Color palette: sky blue (#00A8FF) as the main tone, vivid yellow (#FFD100) as an accent color,
light gray/ivory (#F8F9FA) background.
Flat vector illustration style, no text, no letters, no watermark.
"""

        image_bytes = None
        with st.spinner("🎨 여행 분위기에 맞는 이미지를 생성하는 중입니다..."):
            try:
                image_response = client.images.generate(
                    model="gpt-image-1",
                    prompt=image_prompt,
                    size="1024x1024",
                    n=1
                )
                image_bytes = base64.b64decode(image_response.data[0].b64_json)

            except Exception as e:
                st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")

        # 텍스트/이미지/브랜드 요소를 하나의 결과 카드로 통합 출력
        if result_text:
            with st.container(border=True):
                st.subheader("📋 나만의 맞춤 패킹 리스트")

                if image_bytes:
                    st.image(image_bytes, use_container_width=True)

                st.markdown(result_text)

                st.divider()

                st.markdown(
                    """
                    <div style="
                        background-color:#FFF6D9;
                        border:1px dashed #FFD100;
                        border-radius:10px;
                        padding:14px 16px;
                        font-size:0.95rem;
                        line-height:1.6;
                    ">
                        🎁 짐 싸기 완료! 여행 필수용품 & 트래블 키트 15% 할인 쿠폰<br>
                        쿠폰코드:
                        <code style="background-color:#FFD100; padding:2px 8px; border-radius:6px;">
                            TRAVEL2026
                        </code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.info("💬 같이 가는 친구에게 패킹 리스트 공유하고 같이 체크하기 ✈️")

                st.markdown(
                    """
                    <div style="color:#00A8FF; font-size:0.9rem; margin-top:4px;">
                        #설렘 #위트있는 #실용적인 #깔끔함 #스마트한
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write("")
                save_col, share_col = st.columns(2)

                with save_col:
                    if image_bytes:
                        st.download_button(
                            label="🖼️ 이미지로 저장",
                            data=image_bytes,
                            file_name="my_packing_list.png",
                            mime="image/png",
                            use_container_width=True
                        )

                with share_col:
                    with st.popover("📤 SNS 공유하기", use_container_width=True):
                        st.caption("아래 문구를 복사해서 SNS나 단톡방에 붙여넣어 공유해 보세요.")
                        share_text = (
                            "✈️ 나만의 맞춤 여행 패킹 리스트 완성!\n"
                            "같이 가는 친구에게 공유하고 같이 체크하기 ✈️\n"
                            "#설렘 #위트있는 #실용적인 #깔끔함 #스마트한"
                        )
                        st.code(share_text, language=None)