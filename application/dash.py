import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from settings import config, about
from py.data import Data
from py.model import Model
from py.result import Result 

# read data
data = Data()
data.get_data()

# app instance
app = dash.Dash(name=config.name, assets_folder=config.root+'/application/static', external_stylesheets=[dbc.themes.LUX, config.fontawesome])
# app = dash.Dash(name=config.name, external_stylesheets=[dbc.themes.LUX, config.fontawesome])
app.title=config.name

# navbar
navbar = dbc.Nav(className = 'nav nav-pills pt-3 pl-2 bg-secondary', children=[
	# logo/home
	# dbc.NavItem(html.Img(src=app.get_asset_url('logo.png'),height='40px')),
	dbc.NavItem(html.H2(config.name, id='nav-pills')),
	# about
	dbc.NavItem(className='',children=[html.Div([
		dbc.NavLink('About', href='/',id='about-popover',active=False),
		dbc.Popover(id='about',is_open=False,target='about-popover',children=[
			dbc.PopoverHeader('How it works'),
			dbc.PopoverBody(about.txt) #settings/about.py (txt = '...'')
		])
	])]),
	# links
	dbc.DropdownMenu(label='Links',nav=True,children=[
		dbc.DropdownMenuItem([
			html.I(className='fa fa-linkedin'),' Contacts'
		],href=config.contacts, target='blank'),
		dbc.DropdownMenuItem([
			html.I(className='fa fa-github'),' Code'
		],href=config.code, target='blank')
	])
])

# Input
inputs = dbc.FormGroup([
	html.H4('Select Country'),
	dcc.Dropdown(id='country',options=[{'label':x,'value':x} for x in data.countrylist], value='World')
])

md_dshbd = '''
This is a test site for a real time dashboard using python plotly dash.
Data is covid-19 daily cases gathered by [Jons Hopkins University](). Default scenario aggregate worldwide and sceanrio can be selectable by country.  
Graph then have both total cumulative case and active daily cases since Jan 2020. Based on previous cases to date model predicts next 30 days (currently using parametric fitting and machine learning prediction is under development)  
Reference [app and code](https://github.com/mdipietro09/App_VirusForecaster).
'''

# App layout
app.layout = dbc.Container(fluid=True,children=[
		# Top
		navbar,
		# html.Br(),html.Br(),
		# html.H2(config.name, id='nav-pills'),
		dcc.Markdown(md_dshbd, className='ml-2 mt-2'),
		html.Br(),
		html.Br(),
	
		# Body
		dbc.Row([
			# input + panel
			dbc.Col(md=3, children=[
				inputs,
				html.Br(),html.Br(),html.Br(),
				html.Div(id='output-panel')
			]),
			# plots
			dbc.Col(md=9, children=[
				dbc.Col(html.H4('Forecast 30 days from today'), width={'size':6,'offset':0}),
				dbc.Tabs(className='nav nav-pills', children=[
					dbc.Tab(dcc.Graph(id='plot-total'),label='Total cases'),
					dbc.Tab(dcc.Graph(id='plot-active'),label='Active cases')
				])
			])
		])
])


# python functions for about navitem-popover
@app.callback(output=Output('about','is_open'),
			inputs=[Input('about-popover','n_clicks')],
			state=[State('about', 'is_open')])
def about_popover(n,is_open):
		if n:
			return not is_open
		return is_open

@app.callback(output=Output('about-popover','active'),
			inputs=[Input('about-popover','n_clicks')],
			state=[State('about-popover','active')])
def about_popover(n,active):
		if n:
			return not active
		return active

# python function to plot total cases
@app.callback(output=Output('plot-total','figure'),
			inputs=[Input('country','value')])
def plot_total_cases(country):
	data.process_data(country)
	model = Model(data.dtf)
	model.forecast()
	model.add_deaths(data.mortality)
	result = Result(model.dtf)
	return result.plot_total(model.today)

# python function to plot active cases
@app.callback(output=Output('plot-active','figure'),
			inputs=[Input('country','value')])
def plot_active_cases(country):
	data.process_data(country)
	model = Model(data.dtf)
	model.forecast()
	model.add_deaths(data.mortality)
	result = Result(model.dtf)
	return result.plot_active(model.today)

# python function to render output panel
@app.callback(output=Output('output-panel','children'),
			inputs=[Input('country','value')])
def render_output_panel(country):
	data.process_data(country)
	model = Model(data.dtf)
	model.forecast()
	model.add_deaths(data.mortality)
	result = Result(model.dtf)
	peak_day, num_max, total_cases_until_today, total_cases_in_30days, active_cases_today, active_cases_in_30days = result.get_panel()
	peak_color = 'white' if model.today > peak_day else 'red'
	panel = html.Div([
		html.H4(country),
		dbc.Card(body=True, className='text-white bg-primary',children=[
			html.H6('Total cases until today:',style={'color':'white'}),
			html.H3('{:,.0f}'.format(total_cases_until_today),style={'color':'white'}),

			html.H6('Total cases in 30 days:',className='text-danger'),
			html.H3('{:,.0f}'.format(total_cases_in_30days), className='text-danger'),

			html.H6('Active cases today:', style={'color':'white'}),
			html.H3('{:,.0f}'.format(active_cases_today), style={'color':'white'}),

			html.H6('Active cases in 30 days:', className='text-danger'),
			html.H3('{:,.0f}'.format(active_cases_in_30days), className='text-danger'),

			html.H6('Peak day:', style={'color':peak_color}),
			html.H3(peak_day.strftime('%Y-%m-%d'),style={'color':peak_color}),
			html.H6('widh {:,.0f} cases'.format(num_max),style={'color':peak_color})
		])
	])
	return panel