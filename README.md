# Useful Tetrail utils for autotests

- [Check test cases ids from Testrail with autotests](#check-test-cases-ids-from-testrail-with-autotests)
- [Merge test cases between suites](#merge-test-cases-between-suites)

## Check test cases ids from Testrail with autotests

### Problem
When developing autotests with subsequent integration with TMS, at some point, problems begin with creating an autotest -> test case connection. The more autotests we have, the higher the probability of error. As a result, situations arise when autotests refer to the same test case or test cases have an incorrect automation status within the TMS.

### Solution
The script check_testrail_ids allows you to check the autotests and test cases inside the TMS, as well as the correctness of their links. What exactly is checked:
- Find autotests that have not exists in testrail (by ids)
- Find testcases that have automated tests but have incorrect automation_status in Testrail (by ids)
- Find Testrail ids used in several autotests
- Find testcases marked as automated in Testrail but no autotests exist

### Example of usage
Before execute script you need to specify some vars:
- SUITE_ID - master suite ID from Testrail
- PROJECT_ID - project ID from Testrail
- client.user - username to connect to Testrail via API
- client.password - password to connect to Testrail via API
- Testrail API URL - API URL for conntect to Testrail

`python check_testrail_ids.py /path/to/folder/with/autotests/files`

### Limitations
This script was developed for autotests with Java. Each atutotest must have annotion: `@TestRailId` if you have another name - change it at 94 row of the entire script.

## Merge test cases between suites

### Problem
Often projects use test case review approach. Changes are living in different suites until the review success. After that, all test cases must be merged to master suite. In Testrail UI it is very time-consuming operation and high risk of human error.

### Solution
The script merge_cases.py allows you to merge test cases between two suites. All new test cases will be moved. Any already exist test case will be updated in destination suite. Existence of test case checked by full name and path equality

### Example of usage
Before execute script you need to specify some vars:
- SOURCE_SUITE_ID - the source suite ID from Testrail (test cases will be moved FROM this suite)
- DESTINATION_SUITE_ID - the destination suite ID from Testrail (test cases will be moved INTO this suite)
- PROJECT_ID - project ID from Testrail
- client.user - username to connect to Testrail via API
- client.password - password to connect to Testrail via API
- Testrail API URL - API URL for conntect to Testrail

`python merge_cases.py`

### Limitations
After script execution, the source suite won't delete. When check the existence of test case, the algorithm compare full path with case sensitive. 