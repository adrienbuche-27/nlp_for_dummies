from textwrap import dedent
import nltk

# Info Modules Text

about_app = dedent("""
	The _**App**_  displays ...
	""")

input_text = dedent("""
	The _**Input Box**_  allows the users to provide data into the application in different manners.

	For the moment, there are 4 different ways to input data : Text, File, Examples, Audio.
	""")


dropdown_input = [('Text', False),
				('File', False),
				('Examples', False),
				('Audio', True)]


inaugural = nltk.corpus.inaugural.fileids()
gutenberg = nltk.corpus.gutenberg.fileids()