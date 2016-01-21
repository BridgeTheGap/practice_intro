import webapp2
import jinja2

env = jinja2.Environment(loader=jinja2.PackageLoader("intro", "templates"),
                         autoescape=True,)

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

# FIXME: get method not working
class LessonPage(PageHandler):
	def get(self):
		print "!!!!!!!!!!!!!!!!"
		lesson = self.request.get("lesson")

app = webapp2.WSGIApplication([
	('/', MainPage),
	], debug=True)