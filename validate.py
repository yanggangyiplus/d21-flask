# 후기 검증 규칙. 브라우저 검사(required · maxlength)는 F12로 지울 수 있어서, 진짜 검사는 여기(서버)에서 한다
def check_review(form):
    """(깨끗한 값, 칸별 오류) 를 돌려준다. 오류가 비어 있어야 저장한다."""
    nickname = form.get("nickname", "").strip()
    rating = form.get("rating", "").strip()
    content = form.get("content", "").strip()
    errors = {}
    if not 1 <= len(nickname) <= 20:
        errors["nickname"] = "닉네임이 비었거나 20자를 넘었어요. 공백 말고 1~20자로 적어 주세요."
    # isdigit: '4.5' · '다섯' · '-1' 모두 걸러진다
    if not (rating.isascii() and rating.isdigit() and 1 <= int(rating) <= 5):
        errors["rating"] = "별점은 1~5 중 정수 하나예요. 목록에서 골라 주세요."
    if not 1 <= len(content) <= 200:
        errors["content"] = "후기가 비었거나 200자를 넘었어요. 1~200자로 적어 주세요."
    clean = {"nickname": nickname, "rating": int(rating) if "rating" not in errors else None, "content": content}
    return clean, errors
