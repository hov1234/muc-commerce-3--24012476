from functools import wraps
from pathlib import Path
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from services.data_service import load_dashboard_data
from services.qa_service import answer_question

# 全局路径与应用初始化
BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"
# 接口中文正常展示，关闭unicode转义
app.config["JSON_AS_ASCII"] = False

# 登录鉴权装饰器
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

# 首页路由
@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))

# 登录页面
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

# 退出登录
@app.route("/logout")
def logout():
    session.clear()
    flash("你已安全退出。", "success")
    return redirect(url_for("login"))

# 数据看板页面
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

# 问答页面
@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html", username=session["username"])

# 问答接口 POST 仅接收JSON
@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True)
    # 任务3：非JSON请求触发400错误处理器
    if payload is None:
        return jsonify({"ok": False, "error": "请求格式不正确。"}), 400
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "error": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})

# 健康检测接口（免登录）
@app.route("/health")
def health():
    return jsonify({"ok": True, "service": "day08-flask-api"}), 200

# TODO 8-1 任务1：指标API GET
@app.route("/api/metrics", methods=["GET"])
@login_required
def api_metrics():
    data = load_dashboard_data(BASE_DIR, selected_category="全部")
    # 任务4规范：只传普通Python列表字典，不传DataFrame
    metric_list = data["metrics"]
    return jsonify({
        "ok": True,
        "metrics": metric_list
    })

# TODO 8-2 任务2：品类筛选API GET
@app.route("/api/categories", methods=["GET"])
@login_required
def api_categories():
    select_cat = request.args.get("category", "全部")
    dash_data = load_dashboard_data(BASE_DIR, selected_category=select_cat)
    # 任务4规范：只传处理好的普通列表，不直接返回df
    table_rows = dash_data["category_rows"]
    return jsonify({
        "ok": True,
        "category": select_cat,
        "rows": table_rows
    })

# TODO 8-3 任务3：全局400错误统一响应
@app.errorhandler(400)
def bad_request(_error):
    # 固定结构 ok:false + error，状态码400，不用200伪装失败
    return jsonify({"ok": False, "error": "请求格式不正确。"}), 400

# 拓展：405方法不允许错误统一JSON返回
@app.errorhandler(405)
def method_not_allow(_error):
    return jsonify({"ok": False, "error": "当前URL不支持该请求方法"}), 405

# 404页面不存在
@app.errorhandler(404)
def page_not_found(_error):
    return jsonify({"ok": False, "error": "访问的接口地址不存在"}), 404

# 服务启动
if __name__ == "__main__":
    app.run(debug=False, port=5500)
    