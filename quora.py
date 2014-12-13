import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class Question(ndb.Model):
	author = ndb.UserProperty()
	#name = ndb.StringProperty(indexed=False)
	content = ndb.StringProperty(indexed=False)
	tags = ndb.StringProperty(repeated=True)
	created= ndb.DateTimeProperty(auto_now_add=True)
	modified= ndb.DateTimeProperty(auto_now=True)
	q_total_votes = ndb.IntegerProperty(default=0)
	q_up_votes = ndb.StringProperty(repeated=True,indexed=False)
	q_down_votes = ndb.StringProperty(repeated=True,indexed=False)

class Answer(ndb.Model):
	author = ndb.UserProperty()
	que_id = ndb.KeyProperty()
	content = ndb.StringProperty(indexed=False)
	ans_id = ndb.KeyProperty()
	#tags = ndb.StringProperty(repeated=True)
	created= ndb.DateTimeProperty(auto_now_add=True)
	modified= ndb.DateTimeProperty(auto_now=True)
	a_total_votes = ndb.IntegerProperty(default=0)
	a_up_votes = ndb.StringProperty(repeated=True,indexed=False)
	a_down_votes = ndb.StringProperty(repeated=True,indexed=False)

class createQuestion(webapp2.RequestHandler):
	""" Creates a new question """
	def get(self):
		user = users.get_current_user()
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
		'user': user,
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
		tags = str(self.request.get('tags'))
		tags_new=[]
		for t in range(len(tags.split(','))):
			tags_new.append(tags.split(',')[t])
		question.tags = tags_new
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
		'user': user,
	    'url': url,
	    'url_linktext': url_linktext,
		'question': que,
		'cursor': next_c
	    }
		template = JINJA_ENVIRONMENT.get_template('startPage.html')
		self.response.write(template.render(template_values))

class viewQuestion(webapp2.RequestHandler):
	def get (self):
		user = users.get_current_user()
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
		'user': user,
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

class editQuestion(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		ID=self.request.get('id')
 		checkID=ndb.Key(urlsafe=ID)
 		question = checkID.get()
 		if users.get_current_user()==question.author:
 			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			tags=""
			for tag in question.tags:
				tags=tags+tag+","
			""" Give template values"""
			template_values = {
			'user': user,
			'tags': tags,
			'question': question,
			'url': url,
			'url_linktext': url_linktext
			}
			template = JINJA_ENVIRONMENT.get_template('edit_q.html')
			self.response.write(template.render(template_values))
		elif not users.get_current_user():
			self.redirect(users.create_login_url(self.request.uri))
		elif users.get_current_user():
			self.redirect('/')

	def post(self):
		ID_new=self.request.get('id')
 		check=ndb.Key(urlsafe=ID_new)
 		questi = check.get()
		questi.content = self.request.get('content')
		tags = str(self.request.get('tags'))
		tags_new=[]
		for t in range(len(tags.split(','))):
			tags_new.append(tags.split(',')[t])
		questi.tags = tags_new
		questi.put()
		redirString = '/view.html?id='+check.urlsafe()
		self.redirect(redirString)

class editAnswer(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		ID=self.request.get('id')
 		checkID=ndb.Key(urlsafe=ID)
 		answer = checkID.get()
 		qid = answer.que_id
 		#checkQ = ndb.Key(urlsafe=qid)
 		question = qid.get()
 		if users.get_current_user()==answer.author:
 			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			""" Give template values"""
			template_values = {
			'user': user,
			'question': question,
			'answer': answer,
			'url': url,
			'url_linktext': url_linktext
			}
			template = JINJA_ENVIRONMENT.get_template('edit_a.html')
			self.response.write(template.render(template_values))
		elif not users.get_current_user():
			self.redirect(users.create_login_url(self.request.uri))
		elif users.get_current_user():
			self.redirect('/')

	def post(self):
		ansid = self.request.get('aid')
		checkA = ndb.Key(urlsafe=ansid)
		answer = checkA.get()
		answer.content = self.request.get('content')
		answer.put()
		ID_new=self.request.get('qid')
 		check=ndb.Key(urlsafe=ID_new)
		redirString = '/view.html?id='+check.urlsafe()
		self.redirect(redirString)

class rssGenerate(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		ID=self.request.get('id')
 		checkID=ndb.Key(urlsafe=ID)
 		question = checkID.get()
 		answer_query = Answer.query(Answer.que_id==checkID)
 		answers = answer_query.fetch()
 		template_values = {
 		'answer': answers,
 		'question': question
 		}
 		template = JINJA_ENVIRONMENT.get_template('rss.xml')
 		self.response.headers['Content-Type']='text/xml'
		self.response.write(template.render(template_values))

class vote(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect('/')
		elif user:
			typeQuery = self.request.get('type')
			if typeQuery=="que":
				ID=self.request.get('id')
				checkID=ndb.Key(urlsafe=ID)
				question = checkID.get()
				#votes=[]
				voteType = self.request.get('vote')
				if voteType=="up":
					#votes = question.q_up_votes
					if str(user) not in question.q_up_votes:
						question.q_up_votes.append(str(user))
						if str(user) in question.q_down_votes:
							question.q_down_votes.remove(str(user))
					#question.q_up_votes = votes
				elif voteType=="down":
					#votes = question.q_down_votes
					if str(user) not in question.q_down_votes:
						question.q_down_votes.append(str(user))
						if str(user) in question.q_up_votes:
							question.q_up_votes.remove(str(user))
					#question.q_down_votes = votes
				question.q_total_votes = len(question.q_up_votes) - len(question.q_down_votes)
				question.put()
				redirString = '/view.html?id='+checkID.urlsafe()
			elif typeQuery=="ans":
				ID=self.request.get('id')
				checkID=ndb.Key(urlsafe=ID)
				answer = checkID.get()
				#votes=[]
				voteType = self.request.get('vote')
				if voteType=="up":
					#votes = answer.a_up_votes
					if str(user) not in answer.a_up_votes:
						answer.a_up_votes.append(str(user))
						if str(user) in answer.a_down_votes:
							answer.a_down_votes.remove(str(user))
					#answer.a_up_votes = votes
				elif voteType=="down":
					#votes = answer.a_down_votes
					if str(user) not in answer.a_down_votes:
						answer.a_down_votes.append(str(user))
						if str(user) in answer.a_up_votes:
							answer.a_up_votes.remove(str(user))
					#answer.a_down_votes = votes
				answer.a_total_votes = len(answer.a_up_votes) - len(answer.a_down_votes)
				redirString = '/view.html?id='+answer.que_id.urlsafe()
				answer.put()
			self.redirect(redirString)

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/create.html', createQuestion),
	('/view.html', viewQuestion),
	('/edit_q.html', editQuestion),
	('/edit_a.html', editAnswer),
	('/vote.html', vote),
	('/rss.xml', rssGenerate),
], debug=True)