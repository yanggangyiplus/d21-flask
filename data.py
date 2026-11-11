# CSV 파일을 읽는 도구(파이썬 기본 제공)를 가져온다
import csv
# 파일 위치를 편하게 다루는 도구를 가져온다
from pathlib import Path

# 이 파일 옆의 data/classes.csv (레포 안에 있어야 배포 서버도 읽는다)
CSV_PATH = Path(__file__).resolve().parent / "data" / "classes.csv"


# 글자를 숫자로 바꾼다. 빈칸이면 0이 아니라 None(값 없음)을 돌려준다
def _num(text):
    # 앞뒤 공백을 지운다
    text = text.strip()
    # 글자가 있으면 숫자로, 없으면 None
    return float(text) if text else None


# CSV를 읽어서 클래스 목록(딕셔너리의 리스트)을 만든다
def load_classes():
    # 결과를 담을 빈 상자
    rows = []
    # utf-8-sig: 엑셀이 파일 맨 앞에 붙이는 보이지 않는 표시(BOM)를 없애 준다
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        # 한 줄씩 읽는다. 첫 줄(제목)이 칸 이름이 된다
        for r in csv.DictReader(f):
            # 정가: 빈칸이면 None
            list_price = _num(r["정가"])
            # 할인가: 빈칸이면 None
            sale = _num(r["할인가"])
            # 평점: 빈칸이면 None
            rating = _num(r["평점"])
            # 상자에 필요한 값만 정리해서 넣는다
            rows.append({
                # 번호: 상세 화면 주소(/class/번호)에 쓴다
                "id": int(r["id"]),
                "category": r["카테고리"],
                "region": r["지역"],
                "name": r["클래스명"],
                # 정가는 취소선으로 보여 줄 때 쓴다
                "list_price": list_price,
                # 판매가: 할인가가 있으면 할인가, 없으면 정가, 둘 다 없으면 None (0원도 None 취급)
                "price": (sale or list_price) or None,
                # 할인 중: 할인가와 정가가 둘 다 있을 때만 True
                "discounted": bool(sale and list_price),
                # 평점이 비었거나 0이면 None → 화면에 '아직 리뷰가 없어요'
                "rating": rating or None,
                # 리뷰 수는 정수로
                "reviews": int(r["리뷰수"]),
            })
    # 다 모은 목록을 돌려준다
    return rows


# 번호로 클래스 하나를 찾는다. 없는 번호면 None
def get_class(class_id):
    # 목록을 처음부터 훑어서 번호가 같은 첫 항목을 돌려준다 (없으면 None)
    return next((r for r in load_classes() if r["id"] == class_id), None)


# 카테고리 이름만 중복 없이, 가나다순으로 모은다 (선택 상자와 버튼에 쓴다)
def categories():
    return sorted({r["category"] for r in load_classes()})


# 카테고리로 거르고 정렬해서 돌려준다
def search(category="", sort=""):
    # 전체 목록
    rows = load_classes()
    # 카테고리가 정해졌으면 그것만 남긴다
    if category:
        rows = [r for r in rows if r["category"] == category]
    # 싼 순: (가격 없음이면 True → 뒤로, 가격 오름차순)
    if sort == "price":
        rows.sort(key=lambda r: (r["price"] is None, r["price"] or 0))
    # 평점 높은 순: (평점 없음이면 True → 뒤로, 큰 숫자가 앞으로 오게 마이너스)
    elif sort == "rating":
        rows.sort(key=lambda r: (r["rating"] is None, -(r["rating"] or 0)))
    # sort 가 이상한 값이면 아무것도 안 하고 CSV 순서 그대로
    return rows
