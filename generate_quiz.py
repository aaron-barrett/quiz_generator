# This generates quizzes from a set of 100 predetermined questions, choosing 1 problem between 1-10, 11-20, ..., 91-100, and inputs them in the quiz_outline.tex
# by inputting them at the end of every \item detected. The newly generated tex file and pdf are saved in created subdirectory of this project.
# This takes just one command line argument which determines how many randomly generated exams are created.
# If two command line arguments are given, then this script also creates solutions. 
# Aaron Barrett
# Last Updated 8/27/22

import numpy as np
import re
import os
import sys


# Bare bones argparser that isn't argparser.
number_of_command_line_arguments = len(sys.argv)
if number_of_command_line_arguments == 1: 
    number_of_exams = 1
    compile_type = "quiz"
elif number_of_command_line_arguments == 2:
    number_of_exams = int(sys.argv[1])
    compile_type = "quiz"
elif number_of_command_line_arguments == 3:
    number_of_exams = int(sys.argv[1])
    # TODO create an actual argparser for solution generation and also rubric generation. 
    # compile_type = sys.argv[2]
    compile_type = "solution"
else:
    print("Error with command line arguments")
    exit(0) 
    
# This assumes that we want 10 questions, so one question from each set of 10.
number_of_questions = 10
problem_directory = "problems"
solution_directory = "solutions"
save_directory = "quizzes"
source_tex = "quiz_outline.tex"
problem_anchor = "item"
# Quick hack to allow multiple consecutive runs of this script.
try:
    os.mkdir(save_directory)
    print("Directory" , save_directory ,  "Created")
except FileExistsError:
    print("Directory" , save_directory ,  "already exists")
    old_save_directory = save_directory + "_" + str(np.random.randint(0,100))
    print("Directory", save_directory, "renaming as", old_save_directory)
    os.rename(save_directory, old_save_directory)
    print("Directory" , save_directory ,  "Created")
    os.mkdir(save_directory)

for version in range(1, number_of_exams + 1):
    array_of_question_numbers = np.empty(0)
    for i in range(number_of_questions):
        starting_question_number = i*10 + 1
        ending_question_number = starting_question_number + 10
        array_of_question_numbers = np.append(array_of_question_numbers, np.random.randint(starting_question_number, ending_question_number))
    array_of_question_numbers = array_of_question_numbers.astype(int)
    # Saves exam skeleton as string.
    exam_outline = ""
    with open(source_tex) as header:
        exam_outline = header.read()
    # Obtain all 10 item instances to input exam questions
    question_inputs = [m.start() for m in re.finditer(problem_anchor, exam_outline)]
    # Obtains character after "item" to input gateway problem stored in data
    question_inputs = [ m + 4  for m in question_inputs]
    # These detected indices shift afer we add each problem. This keeps track of that.
    offset_counter = 0
    for i in range(number_of_questions) :
        problem_data = ""
        solution_data =""
        # Note this is windows file path name using "\"
        problem_filename = problem_directory + "\p" + str(array_of_question_numbers[i])  + ".tex"
        solution_filename = solution_directory + "\p" + str(array_of_question_numbers[i])  + "_solution.tex"
        # Obtains all lines in an individual exam problems as string.
        with open(problem_filename) as problem:
            problem_data = problem.read()
        problem_data += "\n Problem " + str(array_of_question_numbers[i]) + "\n"
        with open(solution_filename) as solution:
            solution_data = r"\ifbool{sol}{\\ \textcolor{NavyBlue}{Solution: \newline " + solution.read() +  r"\newline Gateway Problem " + str(array_of_question_numbers[i]) + "\n" + "}}"
        exam_outline = exam_outline[0: (question_inputs[i]+offset_counter) ] + problem_data + solution_data + exam_outline[(question_inputs[i]+offset_counter):]
        # Count how many characters the new data offsets the original start of "item"
        offset_counter += (len(problem_data) + len(solution_data))
    # Windows or linux, pdflatex likes linux style paths. Huh.
    exam_name = "quiz_version_" + str(version)
    text_file = open(os.path.join(save_directory, exam_name + ".tex"), "wt")
    text_file.write(exam_outline)
    text_file.close()
    print("Generating Version", version)
    if compile_type == "solution":
        file = open ("flags.tex", "w")
        file.writelines(["\setbool{sol}{true}"])
        file.close()
        os.system("pdflatex -output-directory="+ save_directory + " " + exam_name + ".tex" + ">nul")
        quiz_directory = os.path.join(save_directory, exam_name + ".pdf")
        quiz_solution_directory = os.path.join(save_directory, exam_name + "_solution.pdf")
        os.rename(quiz_directory, quiz_solution_directory)
        file = open ("flags.tex", "w")
        file.writelines(["\setbool{sol}{false}"])
        file.close()
        os.system("pdflatex -output-directory="+ save_directory + " " + exam_name + ".tex" + ">nul")
    elif compile_type == "quiz": 
        file = open ("flags.tex", "w")
        file.writelines(["\setbool{sol}{false}"])
        file.close()
        os.system("pdflatex -output-directory=" + save_directory + " " + exam_name  + ".tex" + ">nul" )

# Deletes pdflatex generated build files. 
# This is written with \ for windows paths, so it needs to be / for linux.
os.system("del " + save_directory + "\*.aux >nul")
os.system("del " + save_directory + "\*.log >nul")
# Delete transient files created in this script. Might as well delete.
os.system("del flags.tex >nul")
# Files somehow created by pdflatex by using gateway_outline.tex 
os.system("del *.aux")
os.system("del *.fdb_latexmk")
os.system("del *.fls")
os.system("del *.log")
os.system("del *.synctex.gz")
# Misc cleanup files that sometimes appear from pdflatex
# os.system("del " + save_directory + "\*.fdb_latexmk >nul")
# os.system("del " + save_directory + "\*.fls>nul >nul")
# os.system("del " + save_directory + "\*.synctex.gz >nul")
# I delete the source tex for now. Otherwise uncomment this.
os.system("del " + save_directory + "\*.tex")

# Notes from generating solutions 
# look at question 13 is it supposed to be x^3/4 or x^{3/4}