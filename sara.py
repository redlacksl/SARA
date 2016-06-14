# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 16:18:41 2015

@author: sredlack

SARA: Stephen's Automated Response Assistant
SARA will take a list of tasks in a text file and randomly select a sample for
 today's todos.
The task list can be a text copy/paste from Outlook or Evernote or any other
 task management program that allows you to copy data into a text file.
Things that are tagged "D:" are considered Dailies and will bubble to the top
 of the list.
Tasks can be tagged "Px" where x=2 to 6 to give it more priority in the gueue.
A higher priority will not guarentee it showing up in the selected task list,
 but it does make it appear more frequently in the selection deck, thereby
 increasing its probablity of showing up in the final list.
SARA assumes the input file will have a header and will ignore the first line.
"""

"""
TODO: test email function for possible Evernote integration
"""

import smtplib
import csv
import random
import sys
import os

HEADER_TEXT = "Selected Tasks"

def send_mail(task_list, mail_server, mail_to):
    sender = 'abc@def.gh'
    receivers = [mail_to]
    
    message = '''
From: SARA@def.gh
Subject: Today's Task List

'''
    message = message + '\r\n'.join(task_list)
    
    smtpObj = smtplib.SMTP(mail_server)
    smtpObj.sendmail(sender, receivers, message)
    print ("Successfully sent email")
    smtpObj.quit()
    return

def print_and_log( output, journal ):
    print(output)
    journal.write(str(output) + '\n')
    return

sa = sys.argv
lsa = len(sys.argv)
if lsa < 3:
    print ("Usage: [ python ] sara.py file_name cycle_rate")
    print ("Example: [ python ] sara.py tasks.txt 4 mail_server_name me@somewhere.com")
    print ("The program assumes the task list has a header row and will ignore it")
    sa.append(input("Filename:"))
    sa.append(input("Cycle rate:"))
    sa.append(input("Mail server:"))
    sa.append(input("Mail to:"))

os.chdir(os.path.dirname(sa[1]))
journal_path = "selected_tasks.txt"
cycle_rate = int(sa[2])

journal = open(journal_path, 'w')

try:
    with open(sa[1]) as f:
        reader = csv.reader(f, delimiter='\t')
        raw_tasks = list(reader)
    
        # Remove the header row
        del raw_tasks[0]
    
    # Expand list based on Priority tags
    tasks = []
    for raw_task in raw_tasks:
        taskname = raw_task[0]
        if taskname.startswith("P2:"):
            for i in range(2):tasks.append(taskname)
        elif taskname.startswith("P3:"):
            for i in range(3):tasks.append(taskname)
        elif taskname.startswith("P4:"):
            for i in range(4):tasks.append(taskname)
        elif taskname.startswith("P5:"):
            for i in range(5):tasks.append(taskname)
        elif taskname.startswith("P6:"):
            for i in range(6):tasks.append(taskname)
        else:
            tasks.append(taskname)

    final_tasks = []
    
    # Randomize the task list
    random.shuffle(tasks)
    
    # Remove all duplicates from the deck, so only the 1st instance is kept
    for task in tasks:
        if (task not in final_tasks): final_tasks.append(task)
    
    selected_tasks = []
    
    # Select all the daily tasks
    for task in final_tasks:
        if task.startswith("D:"):
            selected_tasks.append(task)
    
    # Remove all selected daily tasks from the draw pile
    for task in selected_tasks:
        final_tasks.remove(task)
    
    # Selext x more tasks for today, where x is the number of tasks / cycle rate
    for i in range (int(len(final_tasks)/cycle_rate)):
        selected_tasks.append(final_tasks[i])

    # Write the selected tasks to the output file
    selected_tasks.insert(0, HEADER_TEXT)
    for task in selected_tasks:
        print_and_log (task, journal)
    
    # Send the task list to me
    if lsa == 5: send_mail(selected_tasks, sa[3], sa[4])
except Exception as error:
    print_and_log (error, journal)
finally:
    journal.close()
    input("All done. Hit Enter to exit")

