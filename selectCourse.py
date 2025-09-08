from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

def selectCourseType(driver, type_text):
    try:
        # 等待菜单栏加载
        menu_ul = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.teachingClassTypeMenu"))
        )
        # 查找所有菜单项
        menu_items = menu_ul.find_elements(By.CSS_SELECTOR, "li.el-menu-item")
        for item in menu_items:
            span = item.find_element(By.TAG_NAME, "span")
            text = span.text.strip()
            print(f"菜单项: {text}")
            if text == type_text:
                item.click()
                print(f"已点击课程种类: {type_text}")
                return driver
        print(f"未找到课程种类: {type_text}")
        return None
    except Exception as e:
        print(f"选择课程种类失败: {e}")
        return None


def closeGuideImage(driver):
    try:
        # 等待图片容器出现且可见
        guide_div = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.ID, "popContainer"))
        )
        # 检查是否显示
        if guide_div.is_displayed():
            guide_div.click()
            print("已关闭覆盖图片")
        else:
            print("覆盖图片未显示，无需处理")
    except Exception:
        print("未检测到覆盖图片，无需处理")
    return driver  
def filterCourse(driver, coursename):
    try:
        # 查找课程搜索输入框
        search_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input.el-input__inner[placeholder='请输入课程代码/课程名称']"))
        )
        search_input.clear()
        search_input.send_keys(coursename)
        print(f"已输入课程名称/代码: {coursename}")
        return driver
    except Exception as e:
        print(f"未能找到课程搜索输入框: {e}")
        return None
def finalSelect(driver, teachername):
    attempt = 0
    while True:
        try:
            # 每次循环都重新查找课程列表和目标行
            course_rows = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.el-table__row"))
            )
            print(f"第{attempt+1}次尝试，共找到{len(course_rows)}条课程记录")
            target_row = None
            if teachername:
                for row in course_rows:
                    tds = row.find_elements(By.TAG_NAME, "td")
                    for td in tds:
                        if teachername in td.text:
                            target_row = row
                            break
                    if target_row:
                        break
            else:
                target_row = course_rows[0] if course_rows else None

            if not target_row:
                print("未找到对应教师的课程")
                time.sleep(0.2)
                attempt += 1
                continue

            # 每次循环都重新查找按钮
            select_btns = target_row.find_elements(By.CSS_SELECTOR, "button")
            found = False
            for btn in select_btns:
                btn_text = btn.text.replace(" ", "").replace("\n", "")
                if "退选" in btn_text:
                    print("已是退选状态，选课成功！")
                    return True
                if "选择" in btn_text:
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"已选择课程(教师：{teachername if teachername else '第一条'})(JS点击)")
                    found = True
                    # 二次确认
                    try:
                        confirm_btns = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.el-button--primary"))
                        )
                        clicked = False
                        for cbtn in confirm_btns:
                            cbtn_text = cbtn.text.replace(" ", "").replace("\n", "")
                            if cbtn_text == "确定" or cbtn_text == "确 定":
                                driver.execute_script("arguments[0].click();", cbtn)
                                print("已点击二次确认“确 定”按钮(JS点击)")
                                clicked = True
                                break
                        if not clicked:
                            print("未找到文本为“确 定”的主按钮")
                    except Exception:
                        print("未找到或未能点击二次确认“确 定”按钮")
                    break
            if not found:
                print("未找到选课按钮，等待后重试")
                time.sleep(0.2)
                attempt += 1
                continue

            # 再次检查是否已变为退选，每次都重新查找
            time.sleep(0.2)
            course_rows = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.el-table__row"))
            )
            target_row = None
            if teachername:
                for row in course_rows:
                    tds = row.find_elements(By.TAG_NAME, "td")
                    for td in tds:
                        if teachername in td.text:
                            target_row = row
                            break
                    if target_row:
                        break
            else:
                target_row = course_rows[0] if course_rows else None

            if target_row:
                select_btns = target_row.find_elements(By.CSS_SELECTOR, "button")
                for btn in select_btns:
                    btn_text = btn.text.replace(" ", "").replace("\n", "")
                    if "退选" in btn_text:
                        print("选课已成功(已变为退选按钮)")
                        return True
            print("选课未成功，准备重试")
            time.sleep(0.2)
            attempt += 1
        except Exception as e:
            print(f"选课失败: {e}，准备重试")
            time.sleep(0.2)
            attempt += 1

# 示例调用
def selectCourse(driver):
    # 先处理覆盖图片
    driver=closeGuideImage(driver)
    # 选择课程种类
    courseType = input("请输入想选择课程种类")
    if (driver := selectCourseType(driver, courseType)) is None:
        print("课程种类选择失败")
        return None
    coursename=input("请输入想选择的课程名称/课程代码")+'\n'
    driver=filterCourse(driver,coursename)
    teachername=input("请输入想选择的教师名称,留空则选择搜索结果第一条")
    teachername=teachername.strip()
    finalSelect(driver,teachername)
    print("选课流程结束")
