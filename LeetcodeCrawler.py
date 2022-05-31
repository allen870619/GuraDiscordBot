import requests

def dailyProblem():
    data = {"query": "\nquery questionOfToday {\nactiveDailyCodingChallengeQuestion {\ndate\nlink\nquestion {\nacRate\ndifficulty\nfrontendQuestionId: questionFrontendId\ntitle\n\n}\n}\n}\n"}
    response = requests.post("https://leetcode.com/graphql/",
                             json=data).json()["data"]["activeDailyCodingChallengeQuestion"]

    result = ("%s\n%s. %s  (%s, AC %.2f%%)\nhttps://leetcode.com%s"%(response["date"],
    response["question"]["frontendQuestionId"],
    response["question"]["title"],
    response["question"]["difficulty"],
    response["question"]["acRate"],
    response["link"]))
    return result

def dailyProblemAC():
    data = {"query": "\nquery questionOfToday {\nactiveDailyCodingChallengeQuestion {\ndate\nlink\nquestion {\nacRate\ndifficulty\nfrontendQuestionId: questionFrontendId\ntitle\n\n}\n}\n}\n"}
    raw = requests.post("https://leetcode.com/graphql/",
                             json=data).json()

    response = raw["data"]["activeDailyCodingChallengeQuestion"]
    result = ("%s\n%s. %s  \n(AC %.2f%%)"%(response["date"],
    response["question"]["frontendQuestionId"],
    response["question"]["title"],
    response["question"]["acRate"]))
    return result

def randProblem():
    # get title
    data = {"query":"\n    query randomQuestion($categorySlug: String, $filters: QuestionListFilterInput) {\n  randomQuestion(categorySlug: $categorySlug, filters: $filters) {\n    titleSlug\n  }\n}\n    ","variables":{"categorySlug":"","filters":{}}}
    response = requests.post("https://leetcode.com/graphql/",json=data).json()
    problem = response["data"]["randomQuestion"]["titleSlug"]

    # get info
    data = {"operationName":"questionData","variables":{"titleSlug":problem},"query":"query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n questionFrontendId\n    title\n  titleSlug\n  isPaidOnly\n   difficulty\n   acRate\n}\n}\n"}
    response = requests.post("https://leetcode.com/graphql/",json=data).json()["data"]
    result = ("%s. %s  (%s, AC %.2f%%)\nhttps://leetcode.com/problems/%s"%(response["question"]["questionFrontendId"],
    response["question"]["title"],
    response["question"]["difficulty"],
    response["question"]["acRate"],
    response["question"]["titleSlug"]))
    return result