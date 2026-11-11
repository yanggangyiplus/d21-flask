# Flask 도구들: 앱, 양식 채우기, 주소 뒤의 ?값 읽기
import os
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
# 우리가 만든 도구들: CSV 읽기 · 후기 DB · 후기 검증
import data
import db
import validate

# .env 파일의 값(SECRET_KEY 등)을 환경변수로 읽어 온다
load_dotenv()

# 우리 가게(앱)를 하나 만든다
app = Flask(__name__)
# 세션(찜)과 flash 를 잠그는 열쇠. 코드에 적지 않고 .env(배포에서는 환경 변수)에서 읽는다. 없으면 KeyError 로 멈춘다
app.secret_key = os.environ["SECRET_KEY"]


# 주소 "/" → 홈. 전체 개수와 카테고리 버튼을 보여 준다
@app.route("/")
def home():
    # 전체 클래스 목록 (한 번만 읽는다)
    rows = data.load_classes()
    # 양식에 전체 개수, 카테고리 목록, '지금 할인중' 클래스(최대 10개)를 넘긴다
    return render_template(
        "home.html",
        total=len(rows),
        categories=data.categories(),
        sales=[r for r in rows if r["discounted"]][:10],
    )


# 주소 "/classes" → 클래스 목록. 예: /classes?category=공예&sort=price
@app.route("/classes")
def classes():
    # ?category= 값 (없으면 빈 글자 = 전체)
    category = request.args.get("category", "")
    # ?sort= 값 (없으면 빈 글자 = CSV 순서)
    sort = request.args.get("sort", "")
    # 거르고 정렬한 결과와, 선택 상자를 다시 채울 값들을 양식에 넘긴다
    return render_template(
        "classes.html",
        items=data.search(category, sort),
        categories=data.categories(),
        category=category,
        sort=sort,
    )


# 주소 "/class/번호" → 상세 화면. <int:class_id> 는 숫자만 받는다 (글자면 자동으로 404)
# GET = 보기, POST = 후기 남기기 (같은 주소)
@app.route("/class/<int:class_id>", methods=["GET", "POST"])
def detail(class_id):
    # 번호로 클래스를 찾는다
    item = data.get_class(class_id)
    # 없으면 진짜 404 상태 코드로 중단한다 (POST 여도 마찬가지)
    if item is None:
        abort(404)
    form, errors, status = {}, {}, 200
    if request.method == "POST":
        form = request.form
        clean, errors = validate.check_review(form)
        if not errors:
            db.add_review(class_id, clean["nickname"], clean["rating"], clean["content"])
            flash("후기가 저장됐어요.")
            # PRG: 저장 뒤엔 redirect 로 GET 화면을 다시 보여 줘서 새로고침해도 중복 저장이 없다
            return redirect(url_for("detail", class_id=class_id))
        # 검증 실패: redirect 하지 않고 입력값을 남긴 채 400 으로 다시 보여 준다
        status = 400
    return render_template(
        "class.html", c=item, reviews=db.reviews_of(class_id),
        form=form, errors=errors, wished=class_id in session.get("wish", []),
    ), status


# 찜하기/취소: 값을 바꾸는 일이라 POST 만 받는다. 찜은 브라우저(세션)마다 따로
@app.route("/wish/<int:class_id>", methods=["POST"])
def wish(class_id):
    if data.get_class(class_id) is None:
        abort(404)
    ids = session.get("wish", [])
    ids = [i for i in ids if i != class_id] if class_id in ids else ids + [class_id]
    session["wish"] = ids
    return redirect(url_for("detail", class_id=class_id))


@app.route("/wishlist")
def wishlist():
    ids = session.get("wish", [])
    return render_template("wishlist.html", items=[c for c in map(data.get_class, ids) if c])


# 메뉴의 '찜 목록 (개수)' 를 모든 화면에서 쓰게 한다
@app.context_processor
def wish_count():
    return {"wish_count": len(session.get("wish", []))}


# 404 오류가 나면 이 함수가 화면을 만든다. 뒤의 404 가 '상태 코드'다 (이게 없으면 200이 돼 버린다)
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


# 서버 코드가 터졌을 때 보여 줄 친절한 화면 (상태 코드 500)
@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


# 주소 "/about" → 소개 화면
@app.route("/about")
def about():
    return render_template("about.html")


# 주소 "/hello/이름" → 인사 화면
@app.route("/hello/<name>")
def hello(name):
    return render_template("hello.html", name=name)


# 이 파일을 직접 실행했을 때만 가게 문을 연다
if __name__ == "__main__":
    # debug 는 내 컴퓨터에서 직접 켤 때만. 배포(gunicorn)에서는 이 줄이 실행되지 않는다
    app.run(debug=True)
