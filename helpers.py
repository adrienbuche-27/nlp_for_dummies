import dash
import dash_core_components as dcc
import dash_html_components as html

from nltk.book import FreqDist, text1, text6
from nltk.corpus import stopwords
stopwords = set(stopwords.words('english'))
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

def build_modal_info_overlay(id, title, side, content):
    """
    Build div representing the info overlay for a plot panel
    """
    div = html.Div([  # modal div
        html.Div([  # content div
            html.Div([
                html.H4([
                    title,
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


# Helper Functions
def longuest_token(tokens):
	maxlen = max(len(word) for word in tokens)
	longuest = """Length : {} letters \n\n""".format(maxlen) + ", ".join(list(set([word for word in tokens if len(word) == maxlen])))
	return longuest


def most_frequent_token(tokens):
	fdist1 = FreqDist(tokens)
	most = fdist1.most_common(1)[0]
	return ' : '.join([most[0], str(most[1])])

def removing_stop_words(tokens):
	return [word for word in tokens if word not in stopwords]

def removing_punct(text):
	return tokenizer.tokenize(text)