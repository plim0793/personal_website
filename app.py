import logging
import json

from flask import Flask, jsonify, render_template, redirect, url_for, send_from_directory, request, send_file
from flask_wtf import FlaskForm
from wtforms import fields
from wtforms.validators import Required, InputRequired

from sklearn.externals import joblib
from textblob import TextBlob
import numpy as np
import pandas as pd

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

debug = True


# create the application object
app = Flask(__name__)
app.config.from_object("config")

# unpickle my model
estimator = joblib.load('tfidf.pkl')
title_vect = joblib.load('tfidf_vect_title.pkl')
body_vect = joblib.load('tfidf_vect_body.pkl')
target_names = ['Try again.. Question will not be answered quickly.',\
				'Great job! Question will be answered quickly!']

class PredictForm(FlaskForm):
    """Fields for Predict"""
    q_title = fields.TextField('Question Title:', [InputRequired()])
    q_body = fields.TextAreaField('Question Body:', [InputRequired()])

    submit = fields.SubmitField('Submit')

# use decorators to link the function to a url
# create a link for just the initial domain

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/home')
def home():
	return redirect(url_for('index'))

@app.route('/projects')
def projects():

	projects = [
			{
				'img': 'images/nba.png', 
				'title': 'Predicting Market Value of NBA Players', 
				'prev': "Collecting data through web scraping and \
						using regression models to determine an \
						athlete's salary from their individual \
						performance metrics.",
				'link': '/projects/nba'
			},
			{
				'img': 'images/stackoverflow.png', 
				'title': "How to Get Your Stackoverflow Question Answered!",
				'prev': "Using AWS and SQL queries to manage databases. Classification \
						methods (Log Reg, SVM, Gradient Descent) were used to \
						classify which tags will get the highest view counts.",
				'link': '/projects/stackoverflow'
			}
		]

	return render_template('projects.html', projects=projects)

@app.route('/blog')
def blogs():

	blogs = [
		{
			'title': 'Week 1 at Metis', 
			'date': '04/17/2017',
			'prev': 'Coming into the Metis Data Science Immersive Program, \
					I had no real idea of what I was getting myself into...',
			'link': '/blogs/week_1'
		},
		{
			'title': 'Already 1/3 of the Way Done?!',
			'date': '05/04/2017',
			'prev': 'Weeks 2-4 have been a blur to say the least.. Second \
					project, six challenge sets, and one investigation down and \
					there’s still 2/3 of the course left...',
			'link': '/blogs/one_third_done'
		}
	]
	return render_template('blog.html', blogs=blogs)

@app.route('/blogs/week_1')
def week_1():
	return render_template('/blogs/week_1.html')

@app.route('/blogs/one_third_done')
def one_third_done():
	return render_template('/blogs/one_third_done.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/resume.pdf/')
def show_static_pdf():
    with open('/static/etc/Paul_Lim_resume.pdf', 'rb') as static_file:
        return send_file(static_file, attachment_filename='Paul_lim_resume.pdf')

@app.route('/projects/stackoverflow', methods=['GET','POST'])
def stackoverflow():

	if request.method == 'POST':
		form = PredictForm(request.form)
		print('FORM: ', form)
		data = json.loads(request.data.decode('utf-8'), strict=False)
		print(data)

	else:
		form = PredictForm()
		data = {'title': 'sample title', 'body': 'sample body'}

	predicted_ans = None
	final_pred = 0
	prob = 0
	q_title = ''
	q_body = ''
	final_pred = None

	# print(form.validate_on_submit())
	# if form.validate_on_submit():
	print('BEFORE IF: ', data)

	print('AFTER IF: ', data)
	q_title = data['title']
	q_body = data['body']

	print('TITLE: ', q_title)
	print('BODY: ', q_body)

	# Create array from values
	sample_title_dtm = title_vect.transform([q_title])
	sample_body_dtm = body_vect.transform([q_body])

	sample_title_df = pd.DataFrame(sample_title_dtm.toarray(), columns=title_vect.get_feature_names())
	sample_body_df = pd.DataFrame(sample_body_dtm.toarray(), columns=body_vect.get_feature_names())

	sample_df = pd.concat([sample_title_df, sample_body_df], axis=1)

	my_prediction = estimator.predict(sample_df)
	print('INPUT: ', sample_df)

	final_pred = target_names[my_prediction]

	prob_arr = estimator.predict_proba(sample_df)
	prob = prob_arr[0][1]

	prob_str = str(round(prob,2))
	
	print('PROB: ', prob)
	print('PREDICTION: ', final_pred)

	if request.method == 'POST':
		return jsonify(
					prob=prob,
					prob_str=prob_str,
					pred=final_pred
				)


	return render_template('/projects/stackoverflow.html',
							form=form,
							pred=final_pred,
							prob_str=prob_str)

@app.route('/projects/data/<path:path>')
def send_data(path):
    return send_from_directory('templates/projects/data/', path)

@app.route('/projects/nba')
def nba():
	return render_template('/projects/nba.html')




# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)


