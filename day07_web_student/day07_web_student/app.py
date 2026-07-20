from functools import wraps
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from services.data_service import load_dashboard_data
from services.qa_service import answer_question


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "student" and password == "day07":
            session["username"] = username
            flash("登录成功，欢迎进入电商用户分析系统。", "success")
            return redirect(url_for("dashboard"))
        flash("账号或密码错误。演示账号：student / day07", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("你已安全退出。", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    category = request.args.get("category", "全部")
    dashboard_data = load_dashboard_data(BASE_DIR, category)
    return render_template(
        "dashboard.html",
        username=session["username"],
        selected_category=category,
        **dashboard_data,
    )


@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html", username=session["username"])


@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "answer": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404

@app.route("/segments")
@login_required
def segments():
    from services.data_service import _read_csv
    import pandas as pd
    seg_df = _read_csv(BASE_DIR / "data" / "segment_analysis.csv")
    seg_df["流失率展示"] = seg_df["流失率"].apply(lambda x: f"{x:.1%}")
    seg_list = seg_df.to_dict("records")

    max_risk = seg_df.loc[seg_df["流失率"].idxmax()]
    insight_text = (
        f"新用户阶段流失风险最高，流失率 {max_risk['流失率']:.1%}，"
        f"该阶段用户 {max_risk['用户数']} 人，流失 {max_risk['流失人数']} 人；"
        "随着用户使用周期变长，流失率持续下降，24个月以上用户无流失。"
    )
    return render_template("segments.html", seg_rows=seg_list, insight=insight_text)
if __name__ == "__main__":
    app.run(debug=False, port=5000)