import re

def format_comment_by_expr(text, expresion, replace, commitInfo):
    task_regex_group = re.search(expresion, text)
    comment = re.sub(expresion, '', text)
    comment = comment + '\n'
    comment = comment + '****************************************************************\n'
    comment = comment + '****************************************************************\n'
    comment = comment + 'Git Commiter Info: '+'\n' 
    comment = comment +"Autor: " +commitInfo['author']['name']+'\n' 
    comment = comment + "E-mail: "+commitInfo['author']['email']+'\n' 
    comment = comment + "Username: "+commitInfo['author']['username']+'\n' 
    comment = comment + '****************************************************************\n'
    comment = comment + '****************************************************************\n'
    comment = comment + 'Commit Info:'+'\n' 
    comment = comment + '--> '+commitInfo['url']
    return {'message':comment, 'artifact_id':task_regex_group.group(1)}