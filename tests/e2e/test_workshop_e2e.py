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
    
    expect(page).to_have_url(re.compile(r"/cars/\d+$"), timeout=15000)
    expect(page.get_by_role("heading", name="Honda Civic")).to_be_visible(timeout=15000)
    
    # 2. 点击 Edit car 链接
    page.get_by_role("link", name="Edit car").click()
    
    # 3. 更改 Model 和 Year
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")
    page.get_by_role("button", name="Save changes").click()
    
    # 4. 等待页面跳转，然后强制刷新页面，确保读到最新数据
    page.wait_for_url(re.compile(r"/cars/\d+$"), timeout=15000)
    page.reload()
    page.wait_for_timeout(3000) # 强制等待 3 秒让云端渲染
    
    # 5. 重新断言
    expect(page.locator("#car-model")).to_have_text("Accord", timeout=15000)
    expect(page.locator("#car-year")).to_have_text("2023", timeout=15000)
    
    # 6. 再次刷新并断言（检查改动是否持久化）
    page.reload()
    page.wait_for_timeout(3000)
    expect(page.locator("#car-model")).to_have_text("Accord", timeout=15000)
    expect(page.locator("#car-year")).to_have_text("2023", timeout=15000)