import re
    

import settings

def main():
    try:
        from github import Github
        from github.GithubException import BadCredentialsException
    except ImportError:
        print('No github module found, try running pip install pygithub')
        return
    g = Github(settings.ACCESS_TOKEN)
    try:
        org = g.get_organization(settings.ORGANIZATION_NAME)
    except BadCredentialsException:
        print('Bad credentials. Go to https://github.com/settings/tokens ,')
        print('generate new token there and put in local_settings.py ACCESS_TOKEN')
        return
    for repo in org.get_repos():
        in_scope = repo.name in settings.PROJECT_REPOS
        if settings.PROJECT_REPOS and not in_scope:
            continue 
        for pull in repo.get_pulls():
            print('[%s]' % repo.name, pull.title, pull.html_url)
            mistakes = check(pull)
            if not mistakes:
                print('\t', green('OK'))
            for m in mistakes:
                print('\t-', red(m))
        #import bpython; bpython.embed(locals())
        #return


def check(pull):
    mistakes = []
    if settings.JIRA_PROJECT not in pull.title: # TODO check for numbers
        mistakes.append('There are no issue mentioned in title')
    if len(pull.body) < 20:
        mistakes.append('Description of changes made in PR should be present')
    if not pull.mergeable:
        mistakes.append('Has merge conflicts')
    if reviews_approved(pull) < 1:
        mistakes.append('PR should be reviewed and approved by at least one team member')

    if not last_commit_built_successfully(pull):
        mistakes.append('There are unsuccessfull travis checks in last PR commit')

    if not has_test_confirmation(pull):
        mistakes.append('Should have comment "Tested [when] on build #[number]"')

    return mistakes

def last_commit_built_successfully(pull):
    last_commit = list(pull.get_commits())[-1]
    status = last_commit.get_combined_status()
    return status.state == 'success'

def reviews_approved(pull):
    approvals = 0
    for review in pull.get_reviews():
        if review.state == 'APPROVED':
            approvals += 1
    return approvals


def has_test_confirmation(pull):
    return True # TODO: implement this somehow
    for c in pull.get_comments():
        text = c.body
        # if 'Tested' in text and 'on build #' in text:
        if 'tested' in text or 'Tested' in text:
            return True
    return False


NONE_COLOR = "\033[0m"
RED_COLOR = "\033[31m"
GREEN_COLOR = "\033[92m"

def red(s):
    return RED_COLOR + s + NONE_COLOR

def green(s):
    return GREEN_COLOR + s + NONE_COLOR

if __name__ == '__main__':
    main()
