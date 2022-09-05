from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session


app = Flask(__name__)
app.secret_key = "abc"  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskerdb.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
taskerdb = SQLAlchemy(app)

userID = 0
userName = ''


class Todo(taskerdb.Model):
    id = taskerdb.Column(taskerdb.Integer, primary_key=True)
    listname = taskerdb.Column(taskerdb.String(100))
    userId = taskerdb.Column(taskerdb.Integer)

class Tasks(taskerdb.Model):
    id = taskerdb.Column(taskerdb.Integer, primary_key=True)
    title = taskerdb.Column(taskerdb.String(100))
    content = taskerdb.Column(taskerdb.String)
    deadline = taskerdb.Column(taskerdb.String)
    flag = taskerdb.Column(taskerdb.Integer)
    belongTo = taskerdb.Column(taskerdb.Integer)

class Users(taskerdb.Model):
    id = taskerdb.Column(taskerdb.Integer, primary_key=True)
    name = taskerdb.Column(taskerdb.String(100))
    email = taskerdb.Column(taskerdb.String)
    password = taskerdb.Column(taskerdb.String)

#-----------------------------------------
#Add tasks
@app.route('/addtask', methods=['POST'])
def addtask():
    title = request.form.get("title")
    content = request.form.get("content")
    deadline = request.form.get("deadline")
    flag = request.form.get("flag")
    belongTo = request.form.get("belongTo")

    new_task = Tasks(title=title, content=content, deadline=deadline, flag=flag, belongTo=belongTo)
    taskerdb.session.add(new_task)
    taskerdb.session.commit()
    return redirect(url_for("index"))

@app.route('/')
def index():
    
        if not session.get('id'):
            return redirect(url_for('login'))
        canAdd = True
        tableCount = Todo.query.count()
        if tableCount >= 5:
            canAdd = False
        todo_list = Todo.query.all()
        task_list = Tasks.query.all()
        return render_template('base.html', todo_list=todo_list, task_list=task_list, canAdd=canAdd, userID=session["id"], userName=session["name"])
   

#------------------------------------
#adding table
@app.route("/add", methods=["POST"])
def add():
    # add new item in the list
    listname = request.form.get("listname")
    new_todo = Todo(listname=listname, userId=session['id'])
    taskerdb.session.add(new_todo)
    taskerdb.session.commit()
    return redirect(url_for("index"))


#----------------------------------------
#Delete tasks from List
@app.route("/delete/<int:task_id>")
def delete(task_id):
    # add new item in the list
    task = Tasks.query.filter_by(id=task_id).first()
    taskerdb.session.delete(task)
    taskerdb.session.commit()
    return redirect(url_for("index"))

#------------------------------------------
# Delete Whole List
@app.route("/deletelist/<int:todo_id>")
def deletelist(todo_id):
    deletelistID = Todo.query.filter_by(id=todo_id).first()
    taskCount = Tasks.query.filter_by(belongTo=todo_id).count()
    if taskCount >0:
        deletetasks = Tasks.query.filter_by(belongTo=todo_id).first()
        taskerdb.session.delete(deletetasks)
        
    taskerdb.session.delete(deletelistID)
    taskerdb.session.commit()
    return redirect(url_for("index"))


#----------------------------------------
#Update Query
@app.route("/edit/<int:task_id>")
def edit(task_id):
    taskedit = Tasks.query.filter_by(id=task_id).first()
    todo_list = Todo.query.all()
    taskerdb.session.commit()
    print("TaskEdit",taskedit)
    return render_template("edit.html",tasks=taskedit, todo_list=todo_list)


#-----------------------------------------------------
#Update Tasks
@app.route("/update/<int:task_id>",methods=["POST"])

def update(task_id):
    taskdata = Tasks.query.filter_by(id=task_id).first()
    taskdata.title = request.form.get("title")
    taskdata.content = request.form.get("content")
    taskdata.deadline = request.form.get("deadline")
    taskdata.flag = request.form.get("flag")
    taskdata.belongTo = request.form.get("belongTo")
    taskerdb.session.commit()
    return redirect(url_for('index'))

#------------------------------------------------------
#Register User
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        user=Users.query.filter_by(email=email).count()
        if user > 0:
            flash("User Already Registered")
            return redirect(url_for('register'))

        registeruser = Users(name=name, email=email, password=password)
        taskerdb.session.add(registeruser)
        taskerdb.session.commit()
        #flash("User registered Successfully")
        return redirect(url_for('index'))

#-----------------------------------------------
#Login User
@app.route('/login', methods=["POST", "GET"])
def login():

    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user=Users.query.filter_by(email=email, password=password).count()
        if user > 0:
            userdata=Users.query.filter_by(email=email, password=password).first()
            session["name"] = userdata.name
            session["id"] = userdata.id
            return redirect(url_for('index'))
        else:
            flash("User Not Registered")
            return redirect(url_for('login'))
            
        

if __name__ == "__main__":
    taskerdb.create_all()
    app.run(debug=True)