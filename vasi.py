from tkinter import *
from tkinter import ttk
import mysql.connector
import tkinter.messagebox as mb

# Connect to MySQL database (supports root with empty password or 'root')
bmi_calculator = None
for pwd in ["", "root"]:
    try:
        bmi_calculator = mysql.connector.connect(
            host="localhost",
            user="root",
            password=pwd,
            database="bmi"
        )
        break
    except Exception:
        continue

# Create database/table if not yet created
if bmi_calculator is None:
    for pwd in ["", "root"]:
        try:
            temp_conn = mysql.connector.connect(host="localhost", user="root", password=pwd)
            temp_cur = temp_conn.cursor()
            temp_cur.execute("CREATE DATABASE IF NOT EXISTS bmi")
            temp_conn.commit()
            temp_conn.close()
            bmi_calculator = mysql.connector.connect(
                host="localhost", user="root", password=pwd, database="bmi"
            )
            break
        except Exception:
            continue

class _DummyCursor:
    rowcount = 0
    def execute(self, *args, **kwargs): pass
    def fetchall(self): return []
    def close(self): pass

class _DummyDB:
    def cursor(self): return _DummyCursor()
    def commit(self): pass
    def close(self): pass

if bmi_calculator is not None:
    bc = bmi_calculator.cursor()
else:
    bmi_calculator = _DummyDB()
    bc = bmi_calculator.cursor()


calculate=Tk()
calculate.geometry('1020x1020')
calculate.title('BMI calculator 🦾')
calculate.resizable(True,True)


name_strvar=StringVar()
age_strvar=StringVar()
height_strvar=StringVar()
weight_strvar=StringVar()
gender_strvar=StringVar()
bmivalue=StringVar()

# FUNCTION TO CLEAR RECORDS IN GRID
def clear_records():
    global tree,name_strvar, age_strvar, height_strvar, gender_strvar, weight_strvar
    tree.delete(*tree.get_children())
    for i in ['name_strvar', 'age_strvar', 'height_strvar', 'gender_strvar', 'weight_strvar']:
       exec(f"{i}.set('')")

# FUNCTIONS TO DISPLAY RECORDS IN GRID
def display_records():
    tree.delete(*tree.get_children())
    bc.execute('SELECT * FROM bmi_calculator')
    data = bc.fetchall()
    for records in data:
       tree.insert('',END, values=records)

# FUNCTION TO BE ADDED IN DATABASE 
def database_connector():
          global name_strvar, age_strvar, height_strvar, gender_strvar, weight_strvar, bmivalue
          name=name_strvar.get()
          age=age_strvar.get()
          height=height_strvar.get()
          weight=weight_strvar.get()
          gender=gender_strvar.get()
          Bmi=bmivalue.get()
          sql="INSERT INTO bmi_calculator (Name,Age,Gender,Height,Weight,BMI) VALUES (%s,%s,%s,%s,%s,%s)"
          val=(name,age,gender,height,weight,Bmi)
          bc.execute(sql,val)
          bmi_calculator.commit()

          display_records()

# FUNCTION TO CALCULATE BMI 
def bmi_calculation():
    height=float(height_strvar.get())/ 100
    weight=float(weight_strvar.get())
    BMI = round(weight / (height ** 2), 2)
    bmivalue.set(BMI)
    name=name_strvar.get()
    age=age_strvar.get()
    height=height_strvar.get()
    weight=weight_strvar.get()
    gender=gender_strvar.get()
    Bmi=bmivalue.get() 

    if not name or not age or not height or not gender or not weight:
        mb.showerror('Error!', "Please fill all the missing fields!!")  

    else:
        if BMI<18.5:
            mb.showinfo("BMI",f'Your BMI is Under-Weight 🚶🏼‍♂')
        elif 18.5<=BMI<=25.9:
            mb.showinfo("BMI",f'Your BMI is Normal 🧍🏼‍♂')
        elif BMI>25.9:
            mb.showinfo("BMI",f'Your BMI is Over-Weight💃🏼')

    database_connector()
    bmi_calculator.commit()

    display_records()

# FUNCTION TO BE DETLETE IN BOTH DATABASE AND GRID 
def delete_record():
       current_item = tree.focus()
       values = tree.item(current_item)
       selection = values["values"]
       name2=selection[0]
       tree.delete(current_item)
       My_project = bmi_calculator.cursor()
       sql = ("Delete from bmi_calculator WHERE Name=%s", (name2,))
       bc.execute(*sql)

       bmi_calculator.commit()
       print(My_project.rowcount, "record(s) deleted")

       mb.showinfo('Done', 'The record you wanted to deleted was successfully deleted.')
       display_records()

# FUNCTION TO VIEW A RECORD 
def view_record():
    global name_strvar, age_strvar, height_strvar, gender_strvar, weight_strvar

    if not tree.selection():
       mb.showerror('Error!', 'Please select a record to update')
    else:
        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values["values"]
        name_strvar.set(selection[0]); height_strvar.set(selection[2])
        age_strvar.set(selection[1]); weight_strvar.set(selection[3])
        gender_strvar.set(selection[4])

    database_connector()

# FUNCTION TO EXIT THE PROJECT SCREEN 
def exit():
    calculate.destroy()
   
left_view=Frame(calculate,bg='#34b1eb')
left_view.place(x=0,y=0,relheight=1,relwidth=1)
left_view1=Frame(calculate,bg='#34b1eb')
left_view1.place(x=10,rely=0.1,relheight=0.5,relwidth=0.58)
lable_view=Frame(calculate,bg='yellow')
lable_view.place(relx=0.01,rely=0.8,relheight=0.129,relwidth=0.15)
lable_view1=Frame(calculate,bg='green')
lable_view1.place(relx=0.17,rely=0.8,relheight=0.129,relwidth=0.25)
lable_view2=Frame(calculate,bg='red')
lable_view2.place(relx=0.43,rely=0.8,relheight=0.129,relwidth=0.16)
lable_view3=Frame(calculate,bg='#34b1eb')
lable_view3.place(x=8,rely=0.65,relheight=0.12,relwidth=0.15)
left_view4=Frame(calculate,bg='#42f542')
left_view4.place(relx=0.17,rely=0.65,relheight=0.12,relwidth=0.41)
right_view=Frame(calculate,bg='skyblue')
right_view.place(relx=0.6,rely=0.0714,relheight=1,relwidth=0.5)


Label(left_view4,textvariable=bmivalue,font=('edwardian script itc',20,'bold'),bg='pink').place(relx=0,rely=0,relheight=1,relwidth=1)
Label(left_view,text='BMI calculator 💪🏼',font=('Colonna MT',36,'bold'),bg='#5934eb').pack(fill=X,side=TOP)
Label(lable_view,text='Under-\nWeight',font=('edwardian script itc',26,'bold'),bg='yellow').place(relx=0,rely=0)
Label(lable_view,text='<18.5',font=('algerian',15,'bold'),bg='yellow').place(relx=0.6,rely=0.7)
Label(lable_view1,text='Normal-\nWeight',font=('edwardian script itc',30,'bold'),bg='green').place(relx=0.1,rely=0)
Label(lable_view1,text='18.5-25',font=('algerian',15,'bold'),bg='green').place(relx=0.6,rely=0.7)
Label(lable_view2,text='Over-\nWeight',font=('edwardian script itc',30,'bold'),bg='red').place(relx=0,rely=0)
Label(lable_view2,text='>25',font=('algerian',15,'bold'),bg='red').place(relx=0.7,rely=0.7)
Label(left_view1,text='Name',font=('algerian',20,'bold'),bg='#34b1eb').place(relx=0,rely=0.1)
Entry(left_view1,width=12,textvariable=name_strvar,font=('algerian',25),bg='white').place(relx=0.2,rely=0.1)
Label(left_view1,text='Age',font=('algerian',20,'bold'),bg='#34b1eb').place(relx=0,rely=0.3)
Entry(left_view1,width=12,textvariable=age_strvar,font=('algerian',25),bg='white').place(relx=0.2,rely=0.3)
Label(left_view1,text='Height',font=('algerian',20,'bold'),bg='#34b1eb').place(relx=0,rely=0.5)
Entry(left_view1,width=12,textvariable=height_strvar,font=('algerian',25),bg='white').place(relx=0.2,rely=0.5)
Label(left_view1,text='Weight',font=('algerian',20,'bold'),bg='#34b1eb').place(relx=0,rely=0.7)
Entry(left_view1,width=12,textvariable=weight_strvar,font=('algerian',25),bg='white').place(relx=0.2,rely=0.7)
Label(left_view1,text='Gender',font=('algerian',20,'bold'),bg='#34b1eb').place(relx=0,rely=0.9)
OptionMenu(left_view1, gender_strvar, 'Male', "Female").place(relx=0.2,rely=0.9,relwidth=0.4)
Label(lable_view3,text='Your\n BMI \n is ',font=('algerian',19,'bold'),bg='#34b1eb').place(relx=0.26,rely=0.1)
Button(left_view1,text='CALCULATE 📲',font=('algerian',15,'bold'),width=13,bg='silver',command=bmi_calculation).place(relx=0.7, rely=0.1)
Button(left_view1,text='DELETE 🧿',font=('algerian',15,'bold'), width=13,bg='silver', command=delete_record).place(relx=0.7, rely=0.3)
Button(left_view1,text='CLEAR 🥏',font=('algerian',15,'bold'),width=13,bg='silver', command=clear_records).place(relx=0.7, rely=0.5)
Button(left_view1,text='VIEW RECORD 💾',font=('algerian',15,'bold'), width=13,bg='silver', command=view_record).place(relx=0.7, rely=0.7)
Button(left_view1,text='EXIT ❌➡',font=('algerian',15,'bold'), width=13,bg='silver',command=exit).place(relx=0.7, rely=0.89)


tree = ttk.Treeview(right_view,height=200,selectmode=BROWSE,
                    columns=("Name","Age","Gender","BMI","BMI range"))
X_scroller = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
Y_scroller = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
X_scroller.pack(side=BOTTOM, fill=X)
Y_scroller.pack(side=RIGHT, fill=Y)
tree.config(yscrollcommand=Y_scroller.set, xscrollcommand=X_scroller.set)
tree.heading('Name', text='Name', anchor=CENTER)
tree.heading('Age', text='Age', anchor=CENTER)
tree.heading('Gender', text='Gender', anchor=CENTER)
tree.heading('BMI', text='BMI', anchor=CENTER)
tree.heading('BMI range', text='BMI range', anchor=CENTER)
tree.column('#0', width=00, stretch=NO,anchor=CENTER)
tree.column('#1', width=80, stretch=NO,anchor=CENTER)
tree.column('#2', width=50, stretch=NO,anchor=CENTER)
tree.column('#3', width=50, stretch=NO,anchor=CENTER)
tree.column('#4', width=80, stretch=NO,anchor=CENTER)
tree.column('#5', width=80, stretch=NO,anchor=CENTER)
tree.place(x=0,y=0, relwidth=1, relheight=1)

calculate.mainloop()