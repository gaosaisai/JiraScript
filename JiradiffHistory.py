# -*- coding: utf-8 -*-

# This script shows how to use the client in anonymous mode
# against jira.atlassian.com.
##from jira import JIRA
from jira_login import jira
import re
import difflib
import datetime
import dateutil
from dateutil import parser
from dateutil import tz

### Get all projects viewable by anonymous users.
# projects = jira.projects()
#
# # Sort available project keys, then return the second, third, and fourth keys.
# keys = sorted([project.key for project in projects])
#
# print keys

### get one issue
#oneIssue = jira.issue('FORDSYNC3-35457', expand='changelog')
filter='project = Ford_Sync_3 AND type = bug AND (labels is EMPTY OR labels not in (Luxoft_Issue, HMI_Feedback))\
AND resolution = Unresolved AND (labels is EMPTY OR labels not in (Pre-Triage_Done, Pre-Triage_Skipped))\
AND (affectedVersion is EMPTY OR affectedVersion not in versionMatch("^SYNC_IVI_GT.*"))\
AND labels in (Pre-Triage_Ongoing) ORDER BY key ASC, updated DESC'
##filter='reporter = currentUser() ORDER BY updated DESC , createdDate DESC'
issues = jira.search_issues(jql_str=filter, maxResults=50, expand='changelog')
postfix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
with open("diffHistory_"+postfix+".html",'w') as file:#生成新文件
    print ("history diff html created.")
    theDaysBefore = 1
    startday = (datetime.datetime.now()-datetime.timedelta(days = theDaysBefore)).strftime('%Y-%m-%d')
    print ("filtering the date from "+startday)
    num = 0
    for oneIssue in issues:
        changelog = oneIssue.changelog
        localtz = tz.tzlocal()
        comment_lines=[]
        change_lines=[]
        lastChecklistAuthor=""
        lastChecklistComments=""
        for eachComment in jira.comments(oneIssue):
            localCommentDate = dateutil.parser.parse(eachComment.created).astimezone(localtz)
            formattedComment = eachComment.body
            if ('Pre-Triage Suggested Rating' in formattedComment):
                lastChecklistAuthor=eachComment.author.displayName
                lastChecklistComments=formattedComment
            if(localCommentDate.strftime("%Y-%m-%d")>=startday):#只存Pre-Triage checklist 以外的comments
                if('Pre-Triage Suggested Rating' not in formattedComment):
                    comment_lines.append('<span style="background:#FFD700">Author: '+eachComment.author.displayName+'</span>' +' Date: '\
                                         +str(localCommentDate)+'</span><br>')
                    comment_lines.append(formattedComment+"<br>")            
        for history in changelog.histories:
            localHistoryDate = dateutil.parser.parse(history.created).astimezone(localtz)
            dateStr = localHistoryDate.strftime("%Y-%m-%d")
            for item in history.items:
                if(not lastChecklistAuthor and item.field == 'labels' and 'Pre-Triage_Ongoing' in item.toString):
                    lastChecklistAuthor=history.author.displayName
                ###查询description有变化且日期大于给定日期
                if(item.field == 'description' or item.field == 'environment') and dateStr>=startday:
                    # print ('Date:',history.created,' From:',item.fromString, 'To:',item.toString, ' By: ',history.author)
                    from_lines = item.fromString.splitlines()
                    to_lines = item.toString.splitlines()
                    d = difflib.HtmlDiff()
                    change_lines.append('<span style="background:#FFD700">Author: '+history.author.displayName+'</span>'+' Date: '\
                                        +str(localHistoryDate)+'</span>')
                    change_lines.append(d.make_file(from_lines, to_lines, context=True, numlines=1))
        if(comment_lines or change_lines):
            num+=1
            file.write('<span style="background:#FFD700">ID: ' + oneIssue.key+'</span><br>')
            if(lastChecklistAuthor):
                file.write('<span style="background:#FFD700">Reviewer: ' + lastChecklistAuthor+'</span><br>')
            if(lastChecklistComments):
                failedItems=[]
                allItems=re.split('\|\s+\d+\s+\|', lastChecklistComments)
                for item in allItems:
                    if("(x)" in item):
                        failedItems.append('<span style="background:#FFD700">FailedItem:  </span>' + item +'<br>')
                if(failedItems):
                    file.writelines(failedItems)
            file.writelines(comment_lines)
            file.write("-"*150+"<br>")
            file.writelines(change_lines)
            file.write("<br>")
    print ("finish data writing.")
    print ("issues changed number: "+ str(num))

# print oneIssue.fields.project.key
# print oneIssue.fields.issuetype.name
# print oneIssue.fields.reporter.displayName
# print oneIssue.fields.summary
# print oneIssue.fields.project.id

###使用JQL进行查询
#issues = jira.search_issues('project=FORDSYNC3')

###检索第一个标题中含有‘issue’的issue的所有comment
#issues = jira.search_issues(jql_str='project = FORDSYNC3 AND summary ~"Voice output"', maxResults=2,fields='comment')

###检索issue的全部fields
# issues = jira.search_issues(jql_str='project = FORDSYNC3 AND summary ~"Voice output"', maxResults=1)
#
# #查看summary
# print issues[0].fields.summary


#Change in v3: Adding failed itmes in checklst and the author who made the comments/description chages.
