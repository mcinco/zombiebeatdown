from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import cgi, json, mongo
from task import Task

PORT_NUMBER = 8080

# This class will handles any incoming request from
# the browser 
class myHandler(BaseHTTPRequestHandler):
	
	# Handler for the GET requests
	def do_GET(self):
		if self.path == "/":
			self.path = "/server.html"

		try:
			# Check the file exists

			sendReply = False
			if self.path.endswith(".html"):
				mimetype = 'text/html'
				sendReply = True

			if sendReply == True:
				# Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type', mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

	# Handler for the POST requests
	def do_POST(self):
		if self.path == "/send":
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})

			data = form.getvalue("urls")
			urls = [x.strip() for x in data.split(',')]
			timeout = form.getvalue("timeout")
			priority = form.getvalue("priority")
			
			t = Task(urls, timeout, priority)
			self.send_response(200)
			self.end_headers()
			
			mongo.push_task(t)
			self.wfile.write("Task pushed to DB successfully")
			return			
			
			
try:
	# Create a web server and define the handler to manage the
	# incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	# Wait forever for incoming http requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
