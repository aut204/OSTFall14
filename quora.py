import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

from django.core.paginator import Paginator

#count = 0

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class Question(ndb.Model):
	author = ndb.UserProperty()
	#name = ndb.StringProperty(indexed=False)
	content = ndb.StringProperty(indexed=False)
	#tags = ndb.StringProperty(repeated=True)
	created= ndb.DateTimeProperty(auto_now_add=True)
	#q_vote = db.StringProperty(choices=['Up', 'Down'])
	q_total_votes = ndb.IntegerProperty(default=0)

class Answer(ndb.Model):
	author = ndb.UserProperty()
	que_id = ndb.KeyProperty()
	content = ndb.StringProperty(indexed=False)
	ans_id = ndb.KeyProperty()
	#tags = ndb.StringProperty(repeated=True)
	created= ndb.DateTimeProperty(auto_now_add=True)
	#a_vote = db.StringProperty(choices=['Up', 'Down'])
	a_total_votes = ndb.IntegerProperty(default=0)

class createQuestion(webapp2.RequestHandler):
	""" Creates a new question """
	def get(self):
		"""Create question only if user is logged in"""
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			self.redirect(users.create_login_url(self.request.uri))            
			url = users.create_login_url(self.request.uri)
 			url_linktext = 'Login'

		""" Give template values"""
		template_values = {
		'url': url,
		'url_linktext': url_linktext
		}
		template = JINJA_ENVIRONMENT.get_template('create.html')
		self.response.write(template.render(template_values))

	def post(self):
		question = Question()
		question.author = users.get_current_user()
		#question.name = self.request.get('name')
		question.content = self.request.get('content')
		question.put()
		self.redirect('/')

class MainPage(webapp2.RequestHandler):
	""" List all the questions asked. Can be seen without any login"""
	def get(self):
		user = users.get_current_user()
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		
		quest_query = Question.query().order(-Question.created)
		#que = quest_query.fetch()

		cursor = ndb.Cursor(urlsafe=self.request.get('cursor'))
		que, next_curs, more = quest_query.fetch_page(10, start_cursor=cursor) 
		if more:
			next_c = next_curs.urlsafe()
		else:
			next_c = None
		#self.generate('home.html', {'items': items, 'cursor': next_c })

		template_values = {
	    'url': url,
	    'url_linktext': url_linktext,
		'question': que,
		'cursor': next_c
	    }
		template = JINJA_ENVIRONMENT.get_template('startPage.html')
		self.response.write(template.render(template_values))

class viewQuestion(webapp2.RequestHandler):
	def get (self):
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			#self.redirect(users.create_login_url(self.request.uri))            
			url = users.create_login_url(self.request.uri)
 			url_linktext = 'Login'

 		quest = self.request.get('id')
 		que_id = ndb.Key(urlsafe=quest)
 		question = que_id.get()

 		cursor = ndb.Cursor(urlsafe=self.request.get('cursor'))
 		ans_query = Answer.query(Answer.que_id==que_id).order(-Answer.created)

 		ans, next_curs, more = ans_query.fetch_page(10, start_cursor=cursor) 
		if more:
			next_c = next_curs.urlsafe()
		else:
			next_c = None
		#self.generate('home.html', {'items': items, 'cursor': next_c })

		template_values = {
	    'url': url,
	    'url_linktext': url_linktext,
		'question': question,
		'answer': ans,
		'cursor': next_c
	    }
		template = JINJA_ENVIRONMENT.get_template('view.html')
		self.response.write(template.render(template_values))

	def post(self):
		if users.get_current_user():
			answer = Answer()
			answer.author = users.get_current_user()
			questID = self.request.get('id')
			answer.que_id = ndb.Key(urlsafe=questID)
			#question.name = self.request.get('name')
			answer.content = self.request.get('content')
			answer.put()
			redirString = '/view.html?id='+answer.que_id.urlsafe()
			self.redirect(redirString)
		else:
			self.redirect(users.create_login_url(self.request.uri))



application = webapp2.WSGIApplication([
	('/', MainPage),
	('/create.html', createQuestion),
	('/view.html', viewQuestion),
], debug=True)