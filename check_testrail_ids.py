import sys, os, re
from testrail import *

def logCritical(message):
    print("[CRITICAL] " + message)
    sys.stdout.flush()

def logWarning(message):
    print("[WARNING] " + message)
    sys.stdout.flush()

def logInfo(message):
    print("[INFO] " + message)
    sys.stdout.flush()

def logInfoInLine(message):
    print("[INFO] " + message, end = " ")
    sys.stdout.flush()

# Specify your Master suite ID here
SUITE_ID = ''

# Specify your Project ID here
PROJECT_ID = ''

# Specify your testrai URL here
client = APIClient('')

# Username, that has access to testrail
client.user = ''

# API key of the specifyed user
client.password = ''

def get_all_testrail_cases():
    """
    Get all test cases form suite with SUITE_ID

    Returns:
        A list of test cases
    """
    cases = list()
    offset = 0
    while True:
        result = client.send_get('get_cases/{0}&suite_id={1}&offset={2}'.format(PROJECT_ID, SUITE_ID, offset))
        if result.get('size') > 0:
            for case in result.get('cases'):
                cases.append(case)
            offset = offset + 250
        else:
            break
    return cases

# List of test cases
testrail_cases = list()
# List of test cases ids
testrail_cases_ids = list()

logInfo('Get all ids from master suite testrail')
result = get_all_testrail_cases()
logInfo('Get all ids from master suite testrail - COMPLETE')

# Collect test cases and test cases ids
for testrail_case in result:
    testrail_cases.append({'id': testrail_case.get('id'), 'automation_status': testrail_case.get('custom_automation_status')})
    testrail_cases_ids.append(testrail_case.get('id'))

# Collect only autommated test cases
testrail_automated_cases = [tc for tc in testrail_cases if tc.get('automation_status') == 1]

# Path for autotests folder
tests_path = sys.argv[1]
test_pattern = ".java"
java_tests = list()

for path, dirs, files in os.walk(tests_path):
    for file in files:
        if test_pattern in file:
            java_tests.append(os.path.join(path, file))

testrail_id_pattern = re.compile('(\\d+)')

java_tests_ids = list()
empty_java_tests_ids = list()
duplicate_ids = list()

# Collect automated tests by ids
for test_file in java_tests:
    result = False
    file = open(test_file)
    lines = file.readlines()
    last = lines[-1]
    for line in lines:
        if "@TestRailId" in line:
            id = testrail_id_pattern.search(line).group(0)
            if id in java_tests_ids:
                logWarning("TestId used in several tests: " + id)
                duplicate_ids.append(id)
            java_tests_ids.append(id)
            result = True
    if result == False:
        empty_java_tests_ids.append(test_file)

# Compare autotests with ids in testrail
errors_ids = list()
errors_status = list()
for id in java_tests_ids:
    if int(id) not in testrail_cases_ids:
        errors_ids.append(id)
    else:
        for testrail_case in testrail_cases:
            if int(id) == testrail_case.get('id'):
                if testrail_case.get('automation_status') != 1:
                    errors_status.append(id)
                break

errors_testrail_ids = list()
for testrail_automated_case in testrail_automated_cases:
    if str(testrail_automated_case.get('id')) not in java_tests_ids:
        errors_testrail_ids.append(testrail_automated_case.get('id'))

if len(errors_ids) > 0 or len(errors_status) > 0 or len(duplicate_ids) > 0 or len(errors_testrail_ids) > 0:
    logCritical("Automated tests that have not exists in testrail ids: {}".format(errors_ids))
    logCritical("Testcases that have automated tests but have incorrect automation_status in testrail: {}".format(errors_status))
    logCritical("This ids used in several automate tests: {}".format(duplicate_ids))
    logCritical("This testcases marked as automated but no tests exist: {}".format(errors_testrail_ids))
    sys.stdout.flush()
    sys.exit(1)

logInfo("Check complete, everything is fine")
logInfo("Autotests with ids count: {}".format(len(java_tests_ids)))
logInfo("TestCases in master count: {}".format(len(testrail_cases)))
logInfo("Total coverage of suite: {}".format(len(java_tests_ids) / len(testrail_cases) * 100))

sys.stdout.flush()