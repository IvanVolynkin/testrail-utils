
# Check test cases ids from Testrail with autotests

## Problem
When developing autotests with subsequent integration with TMS, at some point, problems begin with creating an autotest -> test case connection. The more autotests we have, the higher the probability of error. As a result, situations arise when autotests refer to the same test case or test cases have an incorrect automation status within the TMS.

## Solution
The script check_testrail_ids allows you to check the autotests and test cases inside the TMS, as well as the correctness of their links. What exactly is checked:
- Find autotests that have not exists in testrail (by ids)
- Find testcases that have automated tests but have incorrect automation_status in Testrail (by ids)
- Find Testrail ids used in several autotests
- Find testcases marked as automated in Testrail but no autotests exist

## Example of usage
Before execute script you need to specify some vars:
- SUITE_ID - master suite ID from Testrail
- PROJECT_ID - project ID from Testrail
- client.user - username to connect to Testrail via API
- client.password - password to connect to Testrail via API
- Testrail API URL - API URL for conntect to Testrail

`python check_testrail_ids.py /path/to/folder/with/autotests/files`

## Limitations
This script was developed for autotests with Java. Each atutotest must have annotion: `@TestRailId` if you have another name - change it at 94 row of the entire script.