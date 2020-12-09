from application.dash import app
from settings import config

server = app.server
app.run_server(debug=config.debug, host=config.host, port=config.port)