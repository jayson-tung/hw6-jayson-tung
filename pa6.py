'''webscraping Course Catalog'''
import re
import bs4
import requests
import pandas as pd

html = open("coursecatalog.html").read()
soup = bs4.BeautifulSoup(html)
links = soup.find_all("a")


for link in links:
    if "href" in link.attrs.keys():
        if "programsofstudy" in link.attrs["href"]:
            PRG_STUDY = str(requests.get(link.attrs["href"]).content)

soup1 = bs4.BeautifulSoup(PRG_STUDY)
links1 = soup1.find_all("a")

majors = []
for link in links1:
    if "href" in link.attrs.keys():
        if "thecollege" in link.attrs["href"] and "contacts" not in link.attrs["href"]:
            majors.append(bs4.BeautifulSoup(str(requests.get("http://collegecatalog.uchicago.edu" + link.attrs["href"]).content)))


def get_classes(major):
    '''grabs the information of all classes of a single department'''
    mains = major.find_all("div", class_="courseblock main")
    subs = major.find_all("div", class_="courseblock subsequence")
    classes = []
    descriptions = []
    terms_offered = []
    equiv_courses = []
    prereqs = []
    instructors = []
    for a_class in mains:
        details = a_class.find("p", class_="courseblockdetail")
        if details is not None:
            classes.append(a_class.text.replace("\\n", "").replace("\\xc2\\xa0", " ").replace("\xa0", " ")[:10])
            descriptions.append(a_class.find("p", class_="courseblockdesc").text.replace("\\n", "").replace("\\", ""))
            terms_offered.append(re.findall(r"Terms Offered: ([A-Za-z\s]+)",
                                            details.text))
            equiv_courses.append(re.findall(r"Equivalent Course\(s\): ([\w\s,]+)",
                                            details.text))
            prereqs.append(re.findall(r"Prerequisite\(s\): ([\w\s,]+)",
                                      details.text))
            instructors.append(re.findall(r"Instructor\(s\): ([\w\s.,-]+)",
                                          details.text))

    for a_class in subs:
        details = a_class.find("p", class_="courseblockdetail")
        classes.append(a_class.text.replace("\\n", "").replace("\\xc2\\xa0", " ").replace("\xa0", " ")[:10])
        descriptions.append(a_class.find("p", class_="courseblockdesc").text.replace("\\n", "").replace("\\", ""))
        terms_offered.append(re.findall(r"Terms Offered: ([A-Za-z\s]+)",
                                        details.text))
        equiv_courses.append(re.findall(r"Equivalent Course\(s\): ([\w\s,]+)",
                                        details.text))
        prereqs.append(re.findall(r"Prerequisite\(s\): ([\w\s,]+)",
                                  details.text))
        instructors.append(re.findall(r"Instructor\(s\): ([\w\s.,-]+)",
                                      details.text))
    return {"courses": classes, "descriptions": descriptions,
            "terms_offered": terms_offered, "equivalent_courses": equiv_courses,
            "prerequisites": prereqs, "instructors": instructors}


course_dfs = [pd.DataFrame(get_classes(major),
                           index=range(len(get_classes(major)["courses"]
                                           ))) for major in majors]
course_dfs = [course for course in course_dfs if course.size != 0]

# Question 1: How many classes total?
total_classes = sum([len(course["courses"]) for course in course_dfs])
# returns 4902

# Question 2: Which department offers the most classes?
dept_most_classes = max([(len(course["courses"]),course.iloc[0,0][:4]) for course in course_dfs])[1]
# returns ECON

# Question 3: Is there a difference in classes offered between quarters?
all_dfs = pd.concat(course_dfs)


def list_to_string(lst):
    '''turns list of strings into single string'''
    return "".join(lst)


all_dfs["terms_offered"] = all_dfs["terms_offered"].apply(list_to_string)
AUTUMN = "Autumn: " + str(len(all_dfs.query("'Autumn' in terms_offered")["courses"]))
WINTER = "Winter: " + str(len(all_dfs.query("'Winter' in terms_offered")["courses"]))
SPRING = "Spring: " + str(len(all_dfs.query("'Spring' in terms_offered")["courses"]))
SUMMER = "Summer: " + str(len(all_dfs.query("'Summer' in terms_offered")["courses"]))
print(", ".join([AUTUMN, WINTER, SPRING, SUMMER]))
# prints "Autumn: 1414, Winter: 1285, Spring: 1291, Summer: 58"

# Export all_dfs to csv
all_dfs.to_csv("hw6_data.csv", index=False)
