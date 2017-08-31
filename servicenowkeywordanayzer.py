#!/usr/bin/env python
from os import path
from PIL import Image
import numpy as np
import string
from os import popen

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
d = path.dirname(__file__)

'''
   Analyze keywords from servicenow short description and close notes with wordcloud
'''

# Read the whole text.
sql="select t.short_description from [[ table with short description]]"
cursor=[[execute sql]]
rows = cursor.fetchall()
text=""
for row in rows:
    row[0].translate(None, string.punctuation)
    text+=row[0]

# read the mask / color image taken from
# http://jirkavinse.deviantart.com/art/quot-Real-Life-quot-Alice-282261010
alice_coloring = np.array(Image.open(path.join(d, "alice_color.png")))
stopwords = set(STOPWORDS)
stopwords.add("said")
stopwords.add("add")
stopwords.add("unable")
stopwords.add("close")
stopwords.add("closing")
stopwords.add("hence")
stopwords.add("still")
stopwords.add("alert")
stopwords.add("cleared")
stopwords.add("thanks")
stopwords.add("closure")
stopwords.add("time")
stopwords.add("fine")
stopwords.add("false")
stopwords.add("case")
stopwords.add("reply")

wc = WordCloud(background_color="black", max_words=100, mask=alice_coloring,
               stopwords=stopwords, max_font_size=45, random_state=42)
# generate word cloud
wc.generate(text)

# create coloring from image
image_colors = ImageColorGenerator(alice_coloring)
file=[[out file path ]]
wc.to_file(file)
command="chmod 777 "+file
popen(command,"r")

