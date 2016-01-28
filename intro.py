import webapp2
import jinja2
import cgi
import urllib
from google.appengine.ext import ndb
from datetime import datetime

env = jinja2.Environment(loader=jinja2.PackageLoader("intro"),
                         autoescape=True,)

DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

def get_lesson_key(lesson="default"):
	return ndb.Key("Lesson", lesson)

def get_lesson_page(lesson_number):
	return "lesson"+lesson_number+".html"

class PageHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		template = env.get_template(template)
		return template.render(params)

	def render(self, template, **params):
		self.write(self.render_str(template, **params))

class MainPage(PageHandler):
	def get(self):
		self.render("mainpage.html")

class NotesPage(PageHandler):
	def get(self):
		self.render_with_comment(get_lesson_page(self.request.get("lesson")))

	def post(self):
		lesson = self.request.get("lesson")
		comment = Comment(parent=get_lesson_key(lesson),
						  alias="Anonymous",
						  comment=self.request.get("comment"))
		comment.put()
		self.redirect("/notes?lesson="+self.request.get("lesson"))

	def render_with_comment(self, html):
		lesson = self.request.get("lesson")
		response = self.render_str(html)

		comment_start = response.find("<!-- Comments -->")
		comment_end = response.find("<!-- Comment box -->")

		notes = response[:comment_start]
		comments = response[comment_start:comment_end]
		textarea = response[comment_end:]

		comment_list = Comment.query(ancestor=get_lesson_key(lesson)).order(Comment.date).fetch()

		if comment_list:
			for comment in comment_list:
				template = env.get_template("comment.html")
				formatted_date = comment.date.strftime("%Y-%m-%d %H:%M:%S")
				comments += template.render({"comment": comment.comment, "simple_date": formatted_date,
											 "lesson": self.request.get("lesson"),
											 "date": comment.date})
		else:
			comments += env.get_template("no_comments.html").render()

		self.write(notes+comments+textarea)

class Delete(PageHandler):
	def post(self):
		lesson = self.request.get("lesson")
		date_string = self.request.get("date")
		date = datetime.strptime(date_string, DATE_FORMAT)
		comment = Comment.query(ancestor=get_lesson_key(lesson)).filter(Comment.date == date).fetch()[0]
		comment.key.delete()
		self.redirect("/notes?"+urllib.urlencode({"lesson": lesson}))

class Comment(ndb.Model):
	alias = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now=True)
	comment = ndb.StringProperty(indexed=False)


app = webapp2.WSGIApplication([
	('/', MainPage),
	('/notes', NotesPage),
	('/delete', Delete),
	], debug=True)
