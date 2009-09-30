#!/usr/bin/env python
# Anniversary calendar by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wsgiref.handlers
from google.appengine.ext import webapp
from icalendar import Calendar, Event
from datetime import datetime,date,time
from icalendar import UTC # timezone
from time import strptime

class MainHandler(webapp.RequestHandler):

	def get(self):
		name = self.request.get("name")
		start = self.request.get("start")
		
		try:
			start = strptime(start, "%Y-%m-%d")
			start = date(*start[:3])
		except ValueError,e:
			start = self.request.get("start")
			self.response.out.write("""
				<title>Anniversary Calendar</title>
				<body>
				  <h1>Anniversary Calendar</h1>
				  <small>(Built by <a href="http://tevp.net">Tom Parker</a>. <a href="http://github.com/palfrey/palfrey-projects">Source Code</a>)</small>
				  <form action="/anniversary" method="get">
					<div><br/>Name: <input type="text" name="name" value="%s"</div>
					<div>Start of relationship (YYYY-MM-DD): <input type="text" name="start" value="%s"</div>
					<div><input type="submit" value="Get Calendar"></div>
				  </form>
			"""%(name,start))
			if start!="":
				self.response.out.write("Unable to determine start date from '%s'"%start)
			return
		cal = Calendar()
		cal.add('prodid', '-//calendars-anniversary//tevp.net//')
		cal.add('version', '2.0')

		now = date.today()

		if now.day<start.day:
			next = date(now.year, now.month, start.day)
		else:
			if now.month==12:
				next = date(now.year+1, 1, start.day)
			else:
				next = date(now.year, now.month+1, start.day)

		if next.month > start.month:
			months = ((next.year-start.year)*12)+(next.month-start.month)
		else:
			assert next.year > start-year
			months = ((next.year-start.year-1)*12)+(next.month-start.month)

		for i in range(months,months+36): # next 3 years
			event = Event()
			text = ""
			if i>=12:
				if i<24:
					text = "1 year"
				else:
					text = '%d years'%(i/12)
			if i%12 !=0: # some months
				if text !="":
					text +=" and "
				if i%12 == 1:
					text += '1 month'
				else:
					text += '%d months'%(i%12)
			event.add('summary', "%s with %s"%(text,name))
			event.add('dtstart', datetime.combine(next,time(0)))
			event.add('dtend', datetime.combine(next,time(23,59)))
			event.add('dtstamp', datetime.combine(next,time(0)))
			event.add('priority', 5)
			cal.add_component(event)

			if next.month == 12:
				next = date(next.year+1, 1, next.day)
			else:
				next = date(next.year, next.month+1, next.day)

		self.response.out.write(cal.as_string())

def main():
	application = webapp.WSGIApplication([('/anniversary', MainHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()
