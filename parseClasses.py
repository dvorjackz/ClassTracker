from lxml import html
import requests
from selenium import webdriver
import time
from selenium.common.exceptions import WebDriverException

chrome_path = r"chromedriver"
driver = webdriver.Chrome(chrome_path)

classURL = input('Class URL: ')
page = requests.get(classURL)
# tree = html.fromstring(page.content)
reps = int(input('No. pages: '))
driver.get(classURL)

i = 0
subjectCode = ""
while i < len(classURL):
    if classURL[i:i+5] == 'subj=':
        j = i+5
        while j < len(classURL):
            if classURL[j] == '&':
                break
            if classURL[j:j+3] == "%26":
                j += 3
            elif classURL[j] != '+':
                subjectCode += classURL[j]
                j += 1
            else:
                j += 1
        break
    i += 1
print("Subject code:", subjectCode)

# Output files
# TODO: Merge this all into one excel sheet
with open('class_codes.txt', 'w') as f:
    f.write("")
with open('class_names.txt', 'w') as f:
    f.write("")
with open('instructor_names.txt', 'w') as f:
    f.write("")
with open('units.txt', 'w') as f:
    f.write("")
with open('ge_categories.txt', 'w') as f:
    f.write("")
with open('finals.txt', 'w') as f:
    f.write("")
with open('writing_req.txt', 'w') as f:
    f.write("") 

pageNo = 1
while pageNo <= reps:

    print("--------------- Page " + str(pageNo) + " Scrape ---------------")

    if pageNo > 1:
        page_button = driver.find_elements_by_xpath("//a[@style='color: rgb(0, 85, 166); background-color: rgb(255, 255, 255);' and text()='" + str(pageNo) + "']")
        page_button[0].click()
        time.sleep(5)

    # class_titles = tree.xpath('//a[@href="javascript:void(0)"]/text()')
    class_titles = driver.find_elements_by_xpath("//div[@id='divClassNames']/div[@class='results']/div[@id='resultsTitle']/div/h3/a")
        
    for class_title in class_titles:
        print(class_title.text)

#     i = 0
#     while i < len(class_titles):
#         if class_titles[i].text[:1] == '\r':
#             del class_titles[i]
#         else:
#             i += 1

    class_codes = []
    for word in class_titles:
        j = 0
        for char in word.text:
            if char == ' ':
                class_codes.append(word.text[:j])
                break
            j += 1

    for code in class_codes:
        print(code)

    class_names = []
    for word in class_titles:
        j = 0
        for char in word.text:
            if char == '-':
                class_names.append(word.text[j+2:])
                break
            j += 1

    for name in class_names:
        print(name)

    with open('class_codes.txt', 'a') as f:
        for item in class_codes:
            f.write("%s\n" % item)

    with open('class_names.txt', 'a') as f:
        for item in class_names:
            f.write("%s\n" % item)

    expand_all_link = driver.find_element_by_xpath("//a[@id='expandAll']")
    try:
        expand_all_link.click()
    except WebDriverException as exception:
        print("Unable to expand all classes.")

#     class_links_xpath = "//a[contains(@id, '-title') and contains(@id, '" + subjectCode + "')]"
#     class_links = driver.find_elements_by_xpath(class_links_xpath)

#     for item in class_links:
#         print(item.text)

#     driver.execute_script("window.scrollTo(0, 720)") 
#     for item in class_links:
#         try:
#             item.click()
#         except WebDriverException as exception:
#             print("Webdriver Misclick")
#         driver.execute_script("window.scrollTo(0, scrollY + 300)")

    time.sleep(10)

    instructors = driver.find_elements_by_class_name("instructorColumn")
    instructor_list = []

    for instructor in instructors:
        if '\n' in instructor.text:
            temp = instructor.text.split('\n')
            instructor_list.append(temp[0])
        else:
            instructor_list.append(instructor.text)

    i = 0
    while i < len(instructor_list):
        if instructor_list[i] == 'Instructor(s)':
            del instructor_list[i]
            i += 1
        else:
            del instructor_list[i]

    for instructor in instructor_list:
        print(instructor)

    with open('instructor_names.txt', 'a') as f:
        for instructor in instructor_list:
            f.write("%s\n" % instructor)

    units = driver.find_elements_by_class_name("unitsColumn")
    units_list = []

    for unit in units:
        units_list.append(unit.text)

    i = 0
    while i < len(units_list):
        if units_list[i] == 'Units':
            del units_list[i]
            i += 1
        else:
            del units_list[i]

    for unit in units_list:
        print(unit)

    with open('units.txt', 'a') as f:
        for units in units_list:
            f.write("%s\n" % units)

    # gather the links for to access the GE, Writing, and Final information for each class
    searchString = "//div[@class='primarySection']/div[contains(@id, '" + subjectCode + "') and contains(@id, '-children')]/child::div[1]/div[@class='sectionColumn']/div[contains(@class, 'click_info')]/p/a"
    ge_links = driver.find_elements_by_xpath(searchString)

#     i = 0
#     while i < len(ge_links):
#         if ge_links[i].text[-1] != '1':
#             del ge_links[i]
#         else:
#             i += 1

    driver.execute_script("window.scrollTo(0, 720)")
    i = 0
    while i < len(ge_links):
        try:
            ge_links[i].click()
            i += 1 
        except WebDriverException as exception:
            driver.execute_script("window.scrollTo(0, scrollY + 200)") # if a misclick occurs, keeps scrolling until the desired link appears on the screen
        
    ge_cat_list = []
    writing_req_list = []
    finals_list = []

    # Writing requirement
    for course in class_codes:
        if course[-1] == 'W':
            writing_req_list.append("Yes")
        else:
            writing_req_list.append("No")

    i = len(ge_links)
    while i > 0:
        driver.switch_to.window(driver.window_handles[i])
        
        # GE Categories
        if (len(driver.find_elements_by_xpath("//p[text() = 'This class does not satisfy any GE requirements.']")) > 0):
            ge_cat_list.append("No")
        else:
            ge_cats = []
            if len(driver.find_elements_by_xpath("//p[text() = 'Foundations of Arts and Humanities -Literary and Cultural Analysis ']")) > 0 or len(driver.find_elements_by_xpath("//p[text() = 'Foundations of Arts and Humanities -Philosophical and Linguistic Analysis ']")) > 0 or len(driver.find_elements_by_xpath("//p[text() = 'Foundations of Arts and Humanities -Visual and Performance Arts Analysis and Practice ']")) > 0:
                ge_cats.append("Foundations of Arts and Humanities")
            if len(driver.find_elements_by_xpath("//p[text() = 'Foundations of Society and Culture -Historical Analysis ']")) > 0 or len(driver.find_elements_by_xpath("//p[text() = 'Foundations of Society and Culture -Social Analysis ']")) > 0:
                ge_cats.append("Foundations of Society and Culture")
            if len(driver.find_elements_by_xpath("//p[text() = 'Foundations of Scientific Inquiry -Life Sciences ']")) > 0 or len(driver.find_elements_by_xpath("//p[text() = 'Foundations of Scientific Inquiry -Physical Sciences ']")) > 0:
                ge_cats.append("Foundations of Scientific Inquiry")
            ge_cat_list.append(", ".join(str(x) for x in ge_cats))

        # Final exams existences
        if len(driver.find_elements_by_xpath("//p[text() = 'None listed']")) > 0:
            finals_list.append("No")
        else:
            finals_list.append("Yes")

        # update counter
        i -= 1

    for if_ge in ge_cat_list:
        print(if_ge)

    print("Lengths of each major column (code, names, instructors, units, categories, finals, writing) thus far: " + str(len(class_codes)) + ", " + str(len(class_names)) + ", " + str(len(instructor_list)) + ", " + str(len(units_list)) + ", " + str(len(ge_cat_list)) + ", " + str(len(finals_list)) + ", " + str(len(writing_req_list)))

    with open('ge_categories.txt', 'a') as f:
        for ge_cat in ge_cat_list:
            f.write("%s\n" % ge_cat)

    with open('finals.txt', 'a') as f:
        for final in finals_list:
            f.write("%s\n" % final)

    with open('writing_req.txt', 'a') as f:
        for writing_req in writing_req_list:
            f.write("%s\n" % writing_req)

    print ('Class codes: ', class_codes)
    print ('Class names: ', class_names)
    print("Instructors:", instructor_list) 
    print("Units:", units_list)
    print("GE Categories:", ge_cat_list)
    print("Finals:", finals_list)
    print("Writing reqs:", writing_req_list)

    driver.switch_to.window(driver.window_handles[0])
    driver.execute_script("window.scrollTo(0, 0)")
    pageNo += 1
