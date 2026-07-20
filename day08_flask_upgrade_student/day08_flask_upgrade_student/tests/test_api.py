import sys
from pathlib import Path
# 把项目根目录加入Python搜索路径
sys.path.append(str(Path(__file__).parent.parent))

import json
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

# 测试1：/health 返回200
def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["ok"] is True

# 测试2：未登录访问 /api/metrics 被拦截302跳转登录
def test_metrics_no_login(client):
    resp = client.get("/api/metrics")
    assert resp.status_code == 302

# 测试3：登录后访问指标接口正常返回ok与metrics
def test_metrics_login(client):
    # 先登录
    client.post("/login", data={"username":"student","password":"day07"})
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["ok"] is True
    assert "metrics" in data

# 测试4：Fashion筛选接口返回过滤数据
def test_category_fashion(client):
    client.post("/login", data={"username":"student","password":"day07"})
    resp = client.get("/api/categories?category=Fashion")
    data = json.loads(resp.data)
    assert data["category"] == "Fashion"
    assert len(data["rows"]) == 1