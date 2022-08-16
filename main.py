from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewTask(FlaskForm):
    name = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "Task Name"})
    task_description = StringField("Description", validators=[DataRequired()], render_kw={"placeholder": "What to do?"})
    submit = SubmitField("Add Task")


app = Flask(__name__)
Bootstrap(app)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Task TABLE Configuration
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)

# db.create_all()


@app.route("/")
def home():
    all_tasks = Task.query.all()
    db.session.commit()
    return render_template("index.html", all_tasks=all_tasks)


@app.route("/new-task", methods=["POST", "GET"])
def new_task():
    form = NewTask(meta={'csrf': False})
    if form.validate_on_submit():
        add_task = Task(
            name=request.form.get("name"),
            description=request.form.get("task_description")
        )
        db.session.add(add_task)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("new_task.html", form=form)


@app.route("/delete/<int:task_id>", methods=["DELETE", "GET"])
def delete_task(task_id):
    task = db.session.query(Task).get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404


@app.route("/done/<int:task_id>", methods=["GET", "POST"])
def task_done(task_id):
    task = db.session.query(Task).get(task_id)
    if task:
        task.done = True
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404


@app.route("/delete-all", methods=["DELETE", "GET"])
def delete_all_tasks():
    all_tasks = Task.query.all()
    if all_tasks:
        db.session.query(Task).delete()
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404


if __name__ == '__main__':
    app.run(debug=True)
