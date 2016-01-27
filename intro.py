import webapp2
import jinja2
import cgi
import urllib
from google.appengine.ext import ndb

env = jinja2.Environment(loader=jinja2.PackageLoader("intro", "templates"),
                         autoescape=True,)

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

    # FIXME: Doesn't redirect very well....
	def post(self):
		comment = Comment(alias="Anonymous",
						  comment=self.request.get("comment"))
		comment.put()
		self.redirect("/notes?lesson="+self.request.get("lesson"))

	def render_with_comment(self, html):
		response = self.render_str(html)

		comment_start = response.find("<!-- Comments -->")
		comment_end = response.find("<!-- Comment box -->")

		notes = response[:comment_start]
		comments = response[comment_start:comment_end]
		textarea = response[comment_end:]

		for comment in Comment.query().order(Comment.date).fetch():
			comments += "<p>"+comment.comment+"</p>"

		self.write(notes+comments+textarea)

# Implement comment class
class Comment(ndb.Model):
	alias = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now=True)
	comment = ndb.StringProperty(indexed=False)


app = webapp2.WSGIApplication([
	('/', MainPage),
	('/notes', NotesPage),
	], debug=True)
