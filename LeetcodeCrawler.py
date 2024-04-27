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

def fetch_random_problem():
    # get title
    data = {"query":"query randomQuestion($categorySlug: String, $filters: QuestionListFilterInput) { randomQuestion(categorySlug: $categorySlug, filters: $filters) { titleSlug } }","variables":{"categorySlug":"","filters":{}}}
    response = requests.post("https://leetcode.com/graphql/",json=data).json()
    problem = response["data"]["randomQuestion"]["titleSlug"]

    # get info
    data = {"operationName":"questionData","variables":{"titleSlug":problem},"query":"query questionData($titleSlug: String!) { question(titleSlug: $titleSlug) { questionFrontendId title titleSlug isPaidOnly difficulty acRate}}"}
    response = requests.post("https://leetcode.com/graphql/",json=data).json()["data"]
    result = ("%s. %s  (%s, AC %.2f%%)\nhttps://leetcode.com/problems/%s"%(response["question"]["questionFrontendId"],
    response["question"]["title"],
    response["question"]["difficulty"],
    response["question"]["acRate"],
    response["question"]["titleSlug"]))
    return result


# print(dailyProblemAC())

print(dailyProblem())
