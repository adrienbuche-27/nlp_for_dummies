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
# from nltk.book import *

from extra_info import *
from helpers import *


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
    )

app.config.suppress_callback_exceptions = True

server = app.server

# Create app layout
app.layout = html.Div(
    [
    html.Div(children=[
      build_modal_info_overlay('about', 'Info', 'top', about_app),
      build_modal_info_overlay('input', 'Input Box', 'top', input_text)
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
            html.P([
                "About App",
                html.Img(
                    id='show-about-modal',
                    src="assets/question-circle-solid.svg",
                    className='info-icon',
                    ),
                ], className="aboutme_title",),
            ], className='pretty_container two columns', id="about-div"),
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
            [
            "What is the format of your input text:",
            html.Img(
                id='show-input-modal',
                src="assets/question-circle-solid.svg",
                className='info-icon',
                ),
            ], className="control_label",
            ),
        dcc.Dropdown(
            id="type_of_input",
            options=[
            {'label': v, 'value': v, 'disabled': d} for v, d in dropdown_input
            ],
            value="Text",
            className="dcc_control",
            ),
        ],
        className="pretty_container four columns", 
        ),
       html.Div(
        id = 'type_of_input_option',
        className="pretty_container eight columns",
        )
       ],
        className="row flex-display", style={'zIndex':10}, id="input-div"
    ),
    html.Div(
       [
       html.Div(
        id='result-input',
        style = {"height" : "20vh", "overflow-y": "scroll"},
        className="pretty_container twelve columns",)
       ], className="row flex-display", style={'zIndex':9},
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
         [html.P("Longuest Word(s)"), html.Div(id="result-input-long")],
         id="longuest",
         style = {"width" : "fixed", "height" : "18vh",  "overflow-y": "scroll", "overflow-x": "scroll"},
         className="mini_container four columns",
         ),
       html.Div(
         [html.P("Most Frequent Word"), html.H6(id="result-input-frequent")],
         id="frequent",
         style = {"width" : "fixed", "overflow-y": "scroll", "overflow-x": "scroll"},
         className="mini_container four columns",
         ),
       ],
       id="info-container",
       className="row container-display",
       ),
    html.Div(
      [
                # html.Div(
                #   [
                #       html.H4('What can we do with this raw text ?')
                #   ],
                #   className="pretty_container twelve columns"
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

##################################################################################################
#                                       Create callbacks                                         #
##################################################################################################

# Create show/hide callbacks for each info modal
for id in ['about', 'input']:
    @app.callback([Output(f"{id}-modal", 'style'), Output(f"{id}-div", 'style')],
        [Input(f'show-{id}-modal', 'n_clicks'),
        Input(f'close-{id}-modal', 'n_clicks')])
    def toggle_modal(n_show, n_close):
        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('show-'):
            return {"display": "block"}, {'zIndex': 1003}
        else:
            return {"display": "none"}, {'zIndex': 10}

@app.callback(Output('type_of_input_option', 'children'),
    [Input('type_of_input', 'value')])
def display_input_option(value):
    if value == 'Text':
        return html.Div([
            dcc.Textarea(
                id='input_type',
                placeholder='Enter a value...',
                value='Please, enter your text here.',
                style={'width': '100%'}
                ),
            html.Button('Submit', id='button_input')])
    elif value == 'Examples':
        return html.Div([
            dcc.Dropdown(
                id="input_type",
                options=[
                {'label' : x.split('.')[0], 'value' : x} for x in gutenberg
                ],
                value=gutenberg[0],
                className="dcc_control",),
            html.Button('Submit', id='button_input')
            ])


@app.callback(
    [Output('result-input', 'children'),
    Output('result-input-words', 'children'),
    Output('result-input-sents', 'children'),
    Output('result-input-long', 'children'),
    Output('result-input-frequent', 'children')],
    [Input('button_input', 'n_clicks')],
    [State("type_of_input", "value"),
    State("input_type", "value")])
def display_uploaded_text(n_clicks, flag, value):
    if n_clicks is None:
        return 'Waiting for an input ...', 0, 0, None, None
    else:
        if flag == 'Text':
            tokenized_words=nltk.word_tokenize(value.lower())
            tokenized_sentences=nltk.sent_tokenize(value)
            return dcc.Markdown(value), len(tokenized_words), len(tokenized_sentences), dcc.Markdown(longuest_token(tokenized_words)), None
        elif flag == 'Examples':
            corpus = nltk.corpus.gutenberg.open(value).read()
            tokenized_words=nltk.word_tokenize(corpus.lower())
            tokenized_sentences=nltk.sent_tokenize(corpus)
            return dcc.Markdown(corpus), len(tokenized_words), len(tokenized_sentences), dcc.Markdown(longuest_token(tokenized_words)), None


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