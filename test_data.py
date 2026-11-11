# 실행: python test_data.py (Flask 없이도 돌아간다). 통과하면 아무것도 안 나오고 OK만 찍힌다
import data

rows = data.load_classes()
assert len(rows) == 60

# 할인가가 있으면 할인가, 없으면 정가
assert data.search()[1]["price"] == 31200 and data.search()[1]["discounted"]
assert data.search()[0]["price"] == 25000 and not data.search()[0]["discounted"]

# 빈칸은 0이나 nan이 아니라 None
assert any(r["price"] is None for r in rows) and any(r["rating"] is None for r in rows)
assert all(r["price"] != 0 and r["rating"] != 0 for r in rows)

# 가격 싼 순: 가격 문의(None)는 맨 뒤
prices = [r["price"] for r in data.search(sort="price")]
known = [p for p in prices if p is not None]
assert known == sorted(known) and prices[len(known):] == [None] * (len(prices) - len(known))

# 평점 높은 순: 평점 없음은 맨 뒤
ratings = [r["rating"] for r in data.search(sort="rating")]
known = [x for x in ratings if x is not None]
assert known == sorted(known, reverse=True) and ratings[len(known):] == [None] * (len(ratings) - len(known))

# 카테고리 거르기, 없는 카테고리는 0개
assert {r["category"] for r in data.search("공예")} == {"공예"}
assert data.search("없는카테고리") == []
print("OK")
