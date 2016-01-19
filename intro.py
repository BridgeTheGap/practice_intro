import webapp2
import jinja2

env = jinja2.Environment(loader=jinja2.PackageLoader("intro", "templates"),
                         autoescape=True)

class PageHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		template = env.get_template(template)
		return template.render(params)

	def render(self, template, **params):
		self.write(self.render_str(template, **params))

class Survey(PageHandler):
	def get(self):
		page = self.request.get("page")
		if not page:
			page = 1
		self.render("survey.html", page=page)

class MainPage(PageHandler):
	def get(self):
		menu = self.request.get("menu")
		if menu == "survey":
			self.redirect("survey")
		elif menu == "game":
			self.redirect("game")
		self.render("mainpage.html")

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/survey', Survey),
	], debug=True)