# Import required libraries
import pickle
import base64
import io
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import nltk.data
import nltk.tokenize
from nltk.book import *
from textwrap import dedent


suppress_callback_exceptions=True

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server


def build_modal_info_overlay(id, side, content):
    """
    Build div representing the info overlay for a plot panel
    """
    div = html.Div([  # modal div
        html.Div([  # content div
            html.Div([
                html.H4([
                    "Info",
                    html.Img(
                        id=f'close-{id}-modal',
                        src="assets/close-circle-solid.png",
                        n_clicks=0,
                        className='info-icon',
                        style={'margin': 0},
                    ),
                ], className="container_title", style={'color': 'white'}),

                dcc.Markdown(
                    content
                ),
            ])
        ],
            className=f'modal-content {side}',
        ),
        html.Div(className='modal')
    ],
        id=f"{id}-modal",
        style={"display": "none"},
    )

    return div



# Create app layout
app.layout = html.Div(
    [
    	html.Div(children=[
    		build_modal_info_overlay('radio', 'bottom', dedent("""
            The _**App**_  displays ...
        	"""))
    		]
    	),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="three columns",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Natural Language Processing",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "For Dummies", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="six column",
                    id="title",
                ),
				html.Div(children=[
				                html.H6([
				                    "About App",
				                    html.Img(
				                        id='show-radio-modal',
				                        src="assets/question-circle-solid.svg",
				                        className='info-icon',
				                    ),
				                ], className="aboutme_title"),
				], className='two columns', id="radio-div"),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
        	[
				html.Div(
                    [
                    	html.P(
                            "What is the format of your input text:",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="type_of_input",
                            options=[
                                {"label": "Text ", "value": "Text"},
                                {"label": "File ", "value": "File"},
                                {"label": "Examples ", "value": "Examples"},
                            ],
                            value="Text",
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                ),
                html.Div(
                	[
                		dcc.Textarea(
                			id='input_type',
						    placeholder='Enter a value...',
						    value='Please, enter your text here.',
						    style={'width': '100%'}
						), 
                		html.Button('Submit', id='button_input'),
                	],
                	className="pretty_container eight columns",
                )
        	],
        	className="row flex-display",
        ),
        html.Div(
        	id='result-input',
        	style = {"height" : "20vh", "overflow-y": "scroll"},
       		className="pretty_container twelve columns",
        ),
        html.Div(
        	[
        		html.Div(
        			[html.P("No. of Words"), html.H6(id="result-input-words")],
        			id="words",
        			className="mini_container three columns",
        			),
        		html.Div(
        			[html.P("No. of Sentences"), html.H6(id="result-input-sents"), ],
        			id="sentences",
        			className="mini_container three columns",
        			),
        		html.Div(
        			[html.P("Longuest Word(s)"), html.H6(id="result-input-long")],
        			id="longuest",
        			className="mini_container four columns",
        			),
        		html.Div(
        			[html.P("Most Frequent Word"), html.H6(id="result-input-frequent")],
        			id="frequent",
        			className="mini_container four columns",
       				),
            ],
            id="info-container",
            className="row container-display",
         ),
        html.Div(
    		[
    			# html.Div(
    			# 	[
    			# 		html.H4('What can we do with this raw text ?')
    			# 	],
    			# 	className="pretty_container twelve columns"
    			# ),
				# html.H1('Dash Tabs component demo'),
		    	dcc.Tabs(id="tabs", value='tab-1', children=[
		        dcc.Tab(label='Basic Processing Steps', value='tab-1'),
		        dcc.Tab(label='Advanced Statistics', value='tab-2'),
		        dcc.Tab(label='Grammatical Analysis', value='tab-3')]),
		    	html.Div(id='tabs-content')
    		],
    		className="pretty_container",
    	)
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper Functions
def longuest_token(tokens):
	maxlen = max(len(word) for word in tokens)
	return ', '.join(list(set([word for word in tokens if len(word) == maxlen])))

def most_frequent_token(tokens):
	fdist1 = FreqDist(tokens)
	most = fdist1.most_common(1)[0]
	return ' : '.join([most[0], str(most[1])])

# Create callbacks
        # Create show/hide callbacks for each info modal
@app.callback([Output("radio-modal", 'style'), Output("radio-div", 'style')],
	[Input('show-radio-modal', 'n_clicks'),
	Input('close-radio-modal', 'n_clicks')])
def toggle_modal(n_show, n_close):
	ctx = dash.callback_context
	if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('show-'):
		return {"display": "block"}, {'zIndex': 1003}
	else:
		return {"display": "none"}, {'zIndex': 0}


@app.callback(
    [Output('result-input', 'children'),
    Output('result-input-words', 'children'),
    Output('result-input-sents', 'children'),
    Output('result-input-long', 'children'),
    Output('result-input-frequent', 'children')],
    [Input('button_input', 'n_clicks')],
    [State("type_of_input", "value"),
    State("input_type", "value")])
def display_uploade_text(n_clicks, flag, value):
	if n_clicks is None:
		return 'Waiting for an input ...', 0, 0, None, None
	else:
		if flag == 'Text':
			tokenized_words=nltk.word_tokenize(value.lower())
			tokenized_sentences=nltk.sent_tokenize(value)
			return dcc.Markdown(value), len(tokenized_words), len(tokenized_sentences), longuest_token(tokenized_words), most_frequent_token(tokenized_words)

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(
        	[
				html.Div(
                    [
                    	html.P(
                            "Select the actions you want to apply on the text",
                            className="control_label",
                        ),
						dcc.Dropdown(
							id='actions',
						    options=[
						        {'label': 'Removing Stop Words', 'value': 'stopwords'},
						        {'label': 'Lemmatization', 'value': 'lemma'},
						        {'label': 'Stemming', 'value': 'stem'}
						    ],
						    multi=True,
						    value=None
						),
						html.P(
                            "!! Order of selection can impact the final outcome !!",
                            className="control_label",
                        ),
                    ],
                    className="pretty_container four columns",
                ),
                html.Div(
                	[
                		html.H4('Results'),
                		dcc.Textarea(
                			id='input_type_2',
						    placeholder='Enter a value...',
						    value='Please, enter your text here.',
						    style={'width': '100%'}
						)
                	],
                	className="pretty_container eight columns",
                )
        	],
        	className="row flex-display",
        ),
    elif tab == 'tab-2':
        return html.Div([
			html.P(
                'To be determined',
                className = 'pretty_container'

            )
        ])

    elif tab == 'tab-3':
        return html.Div([
            html.P(
                'To be determined',
                className = 'pretty_container'
            )
        ])

# Main
if __name__ == "__main__":
    app.run_server(debug=True)