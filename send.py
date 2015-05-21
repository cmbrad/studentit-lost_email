#!/usr/bin/env python3
# Import smtplib for the actual sending function
import smtplib
import os,sys

# Import the email modules we'll need
from email.mime.text import MIMEText

from directory import get_from_directory

TEMPLATES_DIR = "templates/"

USERNAME = ""
PASSWORD = ""

def validate_input(num_input, max_val):
    try:
        num = int(num_input)
        if num in range(1,max_val + 1):
            return True
    except Exception:
        pass
    return False

def print_template_options(templates):
    option = 1
    for template in templates:
        print("[{}] {}".format(option,template.split('.')[0].title()))
        option += 1

def get_template_index(max_val):
    return input("Select a library template! Enter the corresponding number [1-{}]: ".format(max_val))

def read_template(filename):
    template_p = open(TEMPLATES_DIR + filename, 'r')
    template_data = template_p.read()
    template_p.close()
    return template_data

def do_replace(template, rep_dict):
    for rep in rep_dict:
        template = template.replace(rep, rep_dict[rep])
    return template

def get_student_data():
    name = input("Enter the student's name: ")
    item = input("What have they lost? ")
    form_of_id = input("What form of ID do they need? ")
    
    replace = {'[Student Name]' : name,
               '[item]' : item,
               '[student card]' : form_of_id
    }
    return replace

def get_email_text():
    # Choose a template.
    templates = os.listdir(TEMPLATES_DIR)
    print_template_options(templates)

    # Get index of template user selects
    template = get_template_index(len(templates))
    while validate_input(template, len(templates)) == False:
        template = get_template_index(len(templates))

    # Convert it to an integer. Earlier validation means this is safe
    template = int(template)
   
    # Read in template data. -1 since we're starting selection index from 1
    template_data = read_template(templates[template - 1])

    student_data = {}
    final_text = ""
    success = False
    while not success:
        # Request student specific data
        student_data = get_student_data()
        
        # Replace given locations with data for student
        final_text = do_replace(template_data, student_data)

        print(str(final_text))
        success = True if input("Is this okay? (y/n)").lower() == "y" else False

    return (student_data, final_text)
    
(student_data, email_text) = get_email_text()

# Lookup student in directory
students = get_from_directory(student_data['[Student Name]'])
students_cnt = len(students)
print("Found {} matching students.".format(students_cnt))

student_email = ""
if students_cnt == 0:
    student_email = input("No students found. Please enter an email address.")
elif students_cnt == 1:
    print("Selected {} ({}).".format(students[0]["name"], students[0]["email"]))
    student_email = students[0]["email"]
else:
    print("Multiple students found. Choose the best one.")
    stu = 1
    for student in students:
        print("[{}] {} - {}".format(stu, student["name"], student["email"]))
        stu = stu + 1

# Create a text/plain message
msg = MIMEText(email_text)

me = 'chris.bradley@unimelb.edu.au'
you = student_email
reply_to = 'student-it@unimelb.edu.au'

msg['Subject'] = 'Lost {} in {} Library'.format(student_data['[item]'], "a")
msg['From'] = me
msg['To'] = you
msg['Reply-To'] = reply_to

print("Sending email...")

# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP('smtp.unimelb.edu.au',587)
s.ehlo()
s.starttls()
s.ehlo()
s.login(USERNAME, PASSWORD)
s.sendmail(me, [you], msg.as_string())
s.quit()

print("Sent.")
