import tkinter as tk
from tkinter import *
import json
import speech_recognition as sr
import smtplib
from email.message import EmailMessage
from tkinter import simpledialog
import warnings  
from transformers import BartForConditionalGeneration, BartTokenizer

warnings.filterwarnings("ignore")

window = tk.Tk()
window.geometry("1000x500")

def load_solutions():
    try:
        with open('solutions.json', 'r') as file:
            solutions = json.load(file)
    except FileNotFoundError:
        solutions = {}
    return {key: value for key, value in solutions.items() if key != 'user_system_interaction'}

def main():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Please explain the problem with your home product")
        audio = r.listen(source)
        print("Recognizing Now .... ")
        try:
            s = r.recognize_google(audio)
            print("You have said:\n" + s)
            print("Audio Recorded Successfully\n")
            return s
        except Exception as e:
            print("Error: " + str(e))

def summarize_text(text):
    tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
    model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    inputs = tokenizer([text], max_length=1024, return_tensors="pt", truncation=True)
    summary_ids = model.generate(inputs.input_ids, num_beams=4, max_length=300, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def SendMailToCustomer(email_content, customer_email):
    msg = EmailMessage()
    msg['Subject'] = 'Solution to Your Problem'
    msg['From'] = 'sriram2003chandu@gmail.com'  
    msg['To'] = customer_email.strip()  
    msg.set_content(email_content)

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'sriram2003chandu@gmail.com'  
    smtp_password = 'aenstmwfkxjabimm'  

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            print("Email sent successfully to the customer.")
    except Exception as e:
        print("Error occurred while sending email to the customer:", str(e))

def update_problem_options(selected_product):
    global var_problem_type
    for widget in window.winfo_children():
        if isinstance(widget, Checkbutton):
            widget.pack_forget()
    var_problem_type = []
    for problem in solutions[selected_product]:
        var = IntVar(window)
        var_problem_type.append(var)
        tk.Checkbutton(window, text=problem, variable=var).pack()

def Print_input():
    selected_product = var_home_product.get()

    if not selected_product:
        print("Please select a product.")
        return

    if not var_problem_type:
        print("Please select at least one problem.")
        return

    selected_problems = [problem for i, problem in enumerate(solutions[selected_product]) if var_problem_type[i].get() == 1]

    if not selected_problems:
        print("Please select at least one problem.")
        return

    problem_description = simpledialog.askstring("Input", f"Please explain the problem with your {selected_product}")

    if not problem_description:
        print("Please provide a problem description.")
        return

    # Summarize the problem description using BART
    summarized_description = summarize_text(problem_description)

    selected_solutions = [solutions[selected_product][problem] for problem in selected_problems]

    combined_solution_steps = []
    for solution in selected_solutions:
        solution_steps = solution.split(". ")
        combined_solution_steps.extend(solution_steps)

    overall_problems_description = ", ".join(selected_problems)

    email_content = ""  # Initialize email_content here

    # Append the problem descriptions to the email content
    for problem in selected_problems:
        email_content += f"- {problem}\n"

    email_content += f"Here is a summary of the problem you provided:\n{summarized_description}\n\n"
    email_content += f"To address these issues, our experts have outlined the following solutions:\n"
    for i, step in enumerate(combined_solution_steps, start=1):
        email_content += f"{i}. {step}\n"
    email_content += "\n"
    email_content += "Service Person Details:- \n"
    email_content+="Name: 'Service Person name'\n"
    email_content+="Contact Number: 'Service Person Contact Number'"

    SendMailToCustomer(email_content, inputtxt1.get('1.0', 'end-1c'))

solutions = load_solutions()

tk.Label(text="Enter Name").pack()
inputtxt = tk.Text(window, height=1, width=15)
inputtxt.pack()

tk.Label(text="Enter Phone number").pack()
inputtxt2 = tk.Text(window, height=1, width=15)
inputtxt2.pack()

tk.Label(text="Enter Email").pack()
inputtxt1 = tk.Text(window, height=1, width=15)
inputtxt1.pack()

tk.Label(text="Type of Home Product").pack()
home_product_options = list(solutions.keys())
var_home_product = tk.StringVar(window)
var_home_product.set(home_product_options[0])  
dropdown_home_product = tk.OptionMenu(window, var_home_product, *home_product_options, command=update_problem_options)
dropdown_home_product.pack()

var_problem_type = []

b1 = tk.Button(text="Next", command=Print_input)
b1.pack()

window.mainloop()
