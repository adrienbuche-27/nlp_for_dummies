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



suppress_callback_exceptions=True

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server



# Create app layout
app.layout = html.Div(
    [
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
                    className="one-third column",
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
                    className="one-half column",
                    id="title",
                ),
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
                        dcc.RadioItems(
                            id="type_of_input",
                            options=[
                                {"label": "Text ", "value": "Text"},
                                {"label": "File ", "value": "File"},
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
						    value='This is a TextArea component',
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
        			[html.H6(id="oilText"), html.P("Oil")],
        			id="oil",
        			className="mini_container three columns",
        			),
        		html.Div(
        			[html.H6(id="waterText"), html.P("Water")],
        			id="water",
        			className="mini_container three columns",
       				),
            ],
            id="info-container",
            className="row container-display",
         ),
        html.Div(
    		[
    			html.Div(
    				[
    					html.H4('What can we do with this raw text ?')
    				],
    				className="pretty_container twelve columns"
    			),
    		],
    		className="row flex-display",
    	)
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper Functions

# Create callbacks
@app.callback(
    [Output('result-input', 'children'),
    Output('result-input-words', 'children'),
    Output('result-input-sents', 'children')],
    [Input('button_input', 'n_clicks')],
    [State("type_of_input", "value"),
    State("input_type", "value")])
def display_uploade_text(n_clicks, flag, value):
	if n_clicks is None:
		return 'Waiting for an input ...', 0, 0
	else:
		if flag == 'Text':
			return dcc.Markdown(value), len(value.split()), len(value.split('.'))



# Main
if __name__ == "__main__":
    app.run_server(debug=True)