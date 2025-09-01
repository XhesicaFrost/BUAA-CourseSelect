from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
import time
import os


def switch_to_login_iframe(driver, timeout=10):
    """等待并切换到包含登录表单的 iframe"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "loginIframe"))
        )
        return True
    except TimeoutException:
        # 兜底：遍历所有 iframe，找到包含输入框的那个
        driver.switch_to.default_content()
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        for f in frames:
            driver.switch_to.frame(f)
            if driver.find_elements(By.ID, "unPassword") or driver.find_elements(By.NAME, "username"):
                return True
            driver.switch_to.default_content()
        return False
    
def getNameInput(driver):
    # 先尝试按 ID 查找可见元素，超时则继续按 NAME 查找；都找不到返回 None
    try:
        return WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "unPassword"))
        )
    except TimeoutException:
        pass

    try:
        return WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
    except TimeoutException:
        return None
    
def login(username,password,login_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(login_url)
    wait=WebDriverWait(driver,10)
    time.sleep(2)
    switch_to_login_iframe(driver)
    try:
        username_input=getNameInput(driver)
        try:
            username_input.clear()
        except Exception:
            pass
        username_input.send_keys(username)
    except:
        print("未能找到用户名输入")
        return None
    try:
        password_input=WebDriverWait(driver,5).until(
            EC.visibility_of_element_located((By.ID,"pwPassword"))
        )
        try:
            password_input.clear()
        except Exception:
            pass
        password_input.send_keys(password)
    except:
        print("未能找到密码输入")
        return None
    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.submit-btn[value='登录']"))
        )
        login_btn.click()
    except Exception:
        print("未能找到登录按钮")
        return None
    print("登录第一阶段成功")

    # 新增：列出所有button供调试
    time.sleep(2)  # 等待页面加载
    try:
        js = """
        var btns = document.querySelectorAll('button.el-button--primary');
        for (var i=0; i<btns.length; i++) {
            if (btns[i].innerText.replace(/\\s/g,'') === '确定') {
                btns[i].click();
                return true;
            }
        }
        return false;
        """
        result = driver.execute_script(js)
        print(f"JS点击结果: {result}")
    except Exception as e:
        print(f"JS点击也失败: {e}")
    try:
        js = """
        var btns = document.querySelectorAll('button.el-button--primary');
        for (var i=0; i<btns.length; i++) {
            if (btns[i].innerText.replace(/\\s/g,'') === '选课') {
                btns[i].click();
                return true;
            }
        }
        return false;
        """
        result = driver.execute_script(js)
        print(f"JS点击结果: {result}")
    except Exception as e:
        print(f"JS点击也失败: {e}")
    return driver