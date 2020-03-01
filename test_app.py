# Exclusively to test some dash functionnalities

import dash
import dash_table
import pandas as pd
import nltk
from nltk.book import FreqDist, text1

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

test = "Please, enter some text here."

tokenized_words=nltk.word_tokenize(test.lower())
tmp = FreqDist(tokenized_words)
df = pd.DataFrame(tmp.most_common())
df.columns = ['Words', 'Frequency']
print(df.head())
print(df.to_dict('records'))

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
)

if __name__ == '__main__':
    app.run_server(debug=True)