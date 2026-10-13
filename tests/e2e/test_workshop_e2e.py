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
    page.get_by_label("Color", exact=False).fill("Red")
    page.get_by_role("button", name="Create car").click()
    
    # 断言成功创建并跳转
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    expect(page.get_by_role("heading", name="Honda Civic")).to_be_visible()
    
    # 2. 点击 Edit car 链接
    page.get_by_role("link", name="Edit car").click()
    
    # 3. 更改 Model 和 Year
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")
    
    # ⭐ 关键修复 1：强制触发 input 事件，让前端 JS 同步状态（防止无头浏览器竞态条件）
    page.get_by_label("Model", exact=True).dispatch_event("input")
    page.get_by_label("Year", exact=True).dispatch_event("input")
    
    # ⭐ 关键修复 2：给前端一点反应时间
    page.wait_for_timeout(500)
    
    page.get_by_role("button", name="Save changes").click()
    
    # 等待跳转回详情页
    page.wait_for_url(re.compile(r"/cars/\d+$"))
    
    # 使用 PDF 提示的 #car-model 和 #car-year 断言
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")
    
    # 4. 刷新页面，验证数据是否真的持久化到了数据库
    page.reload()
    
    # 5. 再次断言 ID 元素的值
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")