import sys
from testrail import *

def logInfo(message):
    print("[INFO] " + message)
    sys.stdout.flush()

client = APIClient('')
client.user = ''
client.password = ''

PROJECT_ID = ''
SOURCE_SUITE_ID = ''
DESTINATION_SUITE_ID = ''

def get_all_testrail_cases(paths, suite_id, project_id):
    cases = list()
    offset = 0
    while True:
        result = client.send_get('get_cases/{0}&suite_id={1}&offset={2}'.format(project_id, suite_id, offset))
        if result.get('size') > 0:
            for case in result.get('cases'):
                case_section = next(x for x in paths if x.get('id') == case.get('section_id'))
                cases.append({"case": case, "path": case_section.get('path') + '/{}'.format(case.get('title'))})
            offset = offset + 250
        else:
            break
    return cases

def get_all_suite_sections(suite_id, project_id):
    sections = list()
    offset = 0
    while True:
        result = client.send_get('get_sections/{0}&suite_id={1}&offset={2}'.format(project_id, suite_id, offset))
        if result.get('size') > 0:
            for section in result.get('sections'):
                sections.append(section)
            offset = offset + 250
        else:
            break
    return sections

def get_sections_paths(sections):
    sections_paths = list()
    for section in sections:
        path = list()
        section_raw = section
        while True:
            path.insert(0, section_raw.get('name'))
            if section_raw.get('depth') !=0:
                section_raw = next(x for x in sections if x.get('id') == section_raw.get('parent_id'))
            else:
                break
        sections_paths.append({"id": section.get('id'), "path": '/'.join(path)})
    return sections_paths

def merge_cases(source_cases, dest_cases, dest_branch_sections_paths, suite_id):
    exist_cases = list()
    new_cases = list()
    for source_case in source_cases:
        for dest_case in dest_cases:
            if source_case.get('path') == dest_case.get('path'):
                exist_cases.append(source_case)
                update_case(dest_case.get('case'), source_case.get('case'))
                logInfo('Content for TestCase with id {0} updated from TestCase with id: {1}.'.format(dest_case.get('case').get('id'), source_case.get('case').get('id')))
                break
        if (source_case not in exist_cases):
            new_cases.append(source_case)
    for new_case in new_cases:
        exist_id = 0
        path_parts = new_case.get('path').split('/')
        path_part = ''
        for i in range(1, len(path_parts) + 1):
            path_part = ('/').join(path_parts[0:i])
            if any(d['path'] == path_part for d in dest_branch_sections_paths):
                exist_id = next(x for x in dest_branch_sections_paths if x.get('path') == path_part).get('id')
                continue
            else:
                arr = path_parts[i - 1:]
                section_id = exist_id
                new_section_root = path_part.split('/')[0:len(path_part.split('/')) - 1]
                if (len(arr) > 1):
                    for j in range(0, len(arr) - 1):
                        section_id = create_section(arr[j], suite_id, section_id)
                        new_section_root.append(arr[j])
                        dest_branch_sections_paths.append({"id": section_id, "path": '/'.join(new_section_root)})
                move_case(section_id, suite_id, new_case.get('case').get('id'))
                logInfo('TestCase with id: {0} moved'.format(new_case.get('case').get('id')))
                break

def create_section(section_name, suite_id, parent_id, project_id):
    if parent_id != 0:
        body = {
            'suite_id': suite_id,
            'parent_id': parent_id,
            'name': section_name
        }
        resp = client.send_post('add_section/{}'.format(project_id), body)
        return resp.get('id')
    else:
        body = {
            'suite_id': suite_id,
            'name': section_name
        }
        resp = client.send_post('add_section/{}'.format(project_id), body)
        return resp.get('id')

def move_case(section_id, suite_id, case_id):
    body = {
        'section_id': section_id,
        'suite_id': suite_id,
        'case_ids': [case_id]
    }
    client.send_post('move_cases_to_section/{0}'.format(section_id), body)

def update_case(case_dest, case_source):
    body = {
        'custom_steps_separated': case_source.get('custom_steps_separated')
    }
    client.send_post('update_case/{0}'.format(case_dest.get('id')), body)

source_branch_sections = get_all_suite_sections(SOURCE_SUITE_ID, PROJECT_ID)
source_branch_sections_paths = get_sections_paths(source_branch_sections)
source_branch_cases = get_all_testrail_cases(source_branch_sections_paths, SOURCE_SUITE_ID, PROJECT_ID)

dest_branch_sections = get_all_suite_sections(DESTINATION_SUITE_ID, PROJECT_ID)
dest_branch_sections_paths = get_sections_paths(dest_branch_sections)
dest_branch_cases = get_all_testrail_cases(dest_branch_sections_paths, DESTINATION_SUITE_ID, PROJECT_ID)

merge_cases(source_branch_cases, dest_branch_cases, dest_branch_sections_paths, DESTINATION_SUITE_ID)