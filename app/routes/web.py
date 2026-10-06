"""Trang Jinja chỉ cung cấp layout; dữ liệu tri thức được tải qua API."""
from flask import Blueprint, current_app, render_template

web = Blueprint("web", __name__)


@web.get("/")
def dashboard():
    return render_template("dashboard.html", page="dashboard", title="Tổng quan")


@web.get("/shapes")
def shapes():
    return render_template("shapes.html", page="shapes", title="Các loại tứ giác")


@web.get("/shapes/<shape_id>")
def detail(shape_id):
    # API xác thực ID và trả 400/404; trang vẫn có layout để hiển thị lỗi.
    return render_template("detail.html", page="detail", title="Chi tiết loại hình", shape_id=shape_id)


@web.get("/graph")
def graph():
    return render_template("graph.html", page="graph", title="Khám phá Graph")


@web.get("/queries")
def queries():
    # Chỉ metadata mã nguồn của whitelist, không chạy query hoặc đưa kết quả tĩnh vào HTML.
    # Jinja tojson escape an toàn; không mở API nhận Cypher tự do.
    codes = current_app.extensions["services"]["queries"].demos
    return render_template("queries.html", page="queries", title="Truy vấn Neo4j", query_sources=codes)


@web.get("/about")
def about():
    return render_template("about.html", page="about", title="Giới thiệu dự án")
