import re
from playwright.sync_api import expect

def test_user_creates_car_in_browser(page, live_server):
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Toyota")
    page.get_by_label("Model", exact=True).fill("Yaris")
    page.get_by_label("Year", exact=True).fill("2020")
    page.get_by_label("Color", exact=False).fill("Blue")
    page.get_by_role("button", name="Create car").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    expect(page.get_by_role("heading", name="Toyota Yaris")).to_be_visible()

def test_user_edits_car_and_change_survives_reload(page, live_server):
    # 1. 创建 Honda Civic
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Honda")
    page.get_by_label("Model", exact=True).fill("Civic")
    page.get_by_label("Year", exact=True).fill("2022")
    page.get_by_role("button", name="Create car").click()
    
    # 断言创建成功，等待详情页渲染
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    expect(page.locator("#car-detail")).to_be_visible()
    
    # 2. 点击 Edit car，进入编辑页
    page.get_by_role("link", name="Edit car").click()
    
    # ⭐ 核心：等待编辑表单加载完成，且默认值是 Civic（解决云端竞态问题）
    expect(page.get_by_label("Model", exact=True)).to_have_value("Civic")
    
    # 3. 更改 Model 和 Year 并保存
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")
    page.get_by_role("button", name="Save changes").click()
    
    # 4. 断言页面标题变成了 Honda Accord
    expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible()
    
    # 5. 刷新页面并验证持久化
    page.reload()
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")