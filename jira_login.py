# -*- coding: utf-8 -*-

# This script shows how to use the client in anonymous mode
# against jira.atlassian.com.
from jira import JIRA

options = {'server': 'https://jira.elektrobit.com'}
jira = JIRA(options,basic_auth=('saga270448', '11qaz2wsx&UJM'))


