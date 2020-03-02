# Import required libraries
import pickle
import base64
import io
import copy
import pathlib
import dash
import dash_table
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate

import nltk.data
import nltk.tokenize
# from nltk.book import FreqDist, text1, text6

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
    dcc.Store(id='memory-output'),
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
        style={"margin-bottom": "25px", "height" : "8vh"},
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
       dcc.Loading(
        html.Div(
            id='result-input',
            style = {"height" : "25vh", "overflow-y": "scroll"},
            className="pretty_container twelve columns"
            ),
        type = 'default',
        style = {"padding": "125px", "height" : "25vh"},
        className='pretty_container twelve columns'
        )], className="row flex-display", style={'zIndex':9},
       ),
    html.Div(
       [
       html.Div(
         [html.P("No. of Words"), dcc.Loading(html.H1(id="result-input-words"), style = {"padding": "25px"})],
         id="words",
         className="mini_container three columns",
         ),
       html.Div(
         [html.P("No. of Sentences"), dcc.Loading(html.H1(id="result-input-sents"), style = {"padding": "25px"})],
         id="sentences",
         className="mini_container three columns",
         ),
       html.Div(
         [html.P("Longuest Word(s)"), dcc.Loading(html.H3(id="result-input-long"), style = {"padding": "25px"})],
         id="longuest",
         style = {"width" : "fixed", "height" : "18vh",  "overflow-y": "scroll", "overflow-x": "scroll"},
         className="mini_container four columns",
         ),
       html.Div(
         [html.P("Most Frequent Word"), dcc.Loading(html.H3(id="result-input-frequent"), style = {"padding": "25px"})],
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
            html.Div(
                id='range-slider-input',
                style={'height':'5vh'},
                className="pretty_container twelve columns"),
            # html.Div(id='output-container-range-slider')
        ],className="row flex-display"
    ),
    html.Div(
      [
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
                {'label' : x.split('.')[0], 'value' : x} for x in inaugural
                ],
                value=inaugural[0],
                className="dcc_control",),
            html.Button('Submit', id='button_input')
            ])


@app.callback(
    Output('memory-output', 'data'),
    [Input('button_input', 'n_clicks')],
    [State("type_of_input", "value"),
    State("input_type", "value")])
def loading_data(n_clicks, flag, value):
    if n_clicks is None:
        return None
    else:
        if flag == 'Text':
            pass
        elif flag == 'Examples':
            value = nltk.corpus.inaugural.raw(value)
            # value = nltk.corpus.inaugural.open(value).read()
        return value


@app.callback([
    Output('result-input', 'children'),
    Output('result-input-words', 'children'),
    Output('result-input-sents', 'children'),
    Output('result-input-long', 'children'),
    Output('result-input-frequent', 'children'),
    Output('range-slider-input','children')],
    [Input('memory-output', 'data')])
def display_uploaded_text(data):
    if data is None:
        raise PreventUpdate
    else:
        tokenized_words=nltk.word_tokenize(data.lower())
        tokenized_sentences=nltk.sent_tokenize(data)
        words = len(tokenized_words)
        sents = len(tokenized_sentences)
        
        if sents <= 10:
            range_marks = {0: {'label': 'First Sentence', 'style': {'margin-left': '35px', 'text-align': 'rigth', 'width': '200px'}},
                            sents: {'label': 'Last Sentence [{}]'.format(sents), 'style': {'margin-rigth': '50px', 'text-align': 'left', 'width': '200px'}}}
        else:
            range_marks = {0: {'label': 'First Sentence', 'style': {'margin-left': '35px', 'text-align': 'rigth', 'width': '200px'}},
                        int(sents*0.25): {'label': '25% [{}]'.format(int(sents*0.25))}, #'style': {'margin-left': '35px', 'text-align': 'rigth', 'width': '200px'},
                        int(sents*0.5): {'label': '50% [{}]'.format(int(sents*0.5))}, #'style': {'margin-left': '35px', 'text-align': 'rigth', 'width': '200px'},
                        int(sents*0.75): {'label': '75% [{}]'.format(int(sents*0.75))}, #'style': {'margin-left': '35px', 'text-align': 'rigth', 'width': '200px'},
                        sents: {'label': 'Last Sentence [{}]'.format(sents), 'style': {'margin-rigth': '50px', 'text-align': 'left', 'width': '200px'}}}
        
        range_slider = dcc.RangeSlider(
            id='my-range-slider',
            min=0,
            max=sents,
            step=1,
            value=[0, sents],
            marks= range_marks,
            className="dcc_control")

        return dcc.Markdown(data), str(words), str(sents) , dcc.Markdown(longuest_token(tokenized_words)), most_frequent_token(tokenized_words), range_slider

@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('my-range-slider', 'value')])
def update_output_slider(value):
    return 'You have selected "{}"'.format(value)

@app.callback(Output('type_of_input_act', 'children'),
    [Input('button_input_act', 'n_clicks')],
    [State("actions", "value"),
    State("memory-output", "data")])
def render_basic_action(n_clicks, flags, value):
    if n_clicks is None:
        return ''
    else:
        tmp = nltk.word_tokenize(value)
        for action in flags:
            if action == 'stopwords':
                tmp = removing_stop_words(tmp)
            elif action == 'punctuations':
                tmp = ' '.join(tmp)
                tmp = removing_punct(tmp)
        return dcc.Markdown(' '.join(tmp))

@app.callback(Output('type_of_input_adv', 'children'),
    [Input('button_input_adv', 'n_clicks')],
    [State("actions_adv", "value"),
    State("memory-output", "data")])
def render_advanced_analytics(n_clicks, flag, value):
    if n_clicks is None:
        return ''
    else:
        if flag == 'WF':
            tokenized_words=nltk.word_tokenize(value.lower())
            tmp = FreqDist(tokenized_words)
            df = pd.DataFrame(tmp.most_common())
            df.columns = ['Words', 'Frequency']
            return dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={
                            'maxHeight': '300px',
                            'overflowY': 'scroll'
                        }
                )

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
               {'label': 'Removing Punctuations', 'value': 'punctuations'},
               {'label': 'Lemmatization', 'value': 'lemma'},
               {'label': 'Stemming', 'value': 'stem'}
               ],
               multi=True,
               value=None
               ),
            html.Button('Submit', id='button_input_act', style={'float':'right', 'margin-top':'10px'}),
            html.P(
                "!! Order of selection can impact the final outcome !!",
                className="control_label",
            )
            ],
            className="pretty_container four columns",
            ),
            html.Div(
                dcc.Loading(id = 'type_of_input_act', style = {"padding": "25px"}),
                style = {"height" : "25vh", "overflow-y": "scroll"},
                className="pretty_container eight columns")
         ],
         className="row flex-display",
         ),
    elif tab == 'tab-2':
        return html.Div([
         html.Div(
            [
            html.P(
                "Select the actions you want to apply on the text",
                className="control_label",
                ),
            dcc.Dropdown(
               id='actions_adv',
               options=[
               {'label': 'Words Frequency', 'value': 'WF'}
               ],
               multi=False,
               value=None
               ),
            html.Button('Submit', id='button_input_adv', style={'float':'right', 'margin-top':'10px'})
            ],
            className="pretty_container four columns",
            ),
         html.Div(
            dcc.Loading(id = 'type_of_input_adv', style = {"padding": "25px"}),
            className="pretty_container eight columns")
           ], className="row flex-display")

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