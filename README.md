# ❓❔👾 Gquestions CLI Usage ❔❓

Are you looking for a ready-to-use tool? Check my [NeuralText People Also Ask free tool](https://www.neuraltext.com/ai/people-also-ask)


[![asciicast](https://asciinema.org/a/4wrOzHnxQVcTImuofzdMxB35L.svg)](https://asciinema.org/a/4wrOzHnxQVcTImuofzdMxB35L)

## ⚠ Disclaimer
> This software is not authorized by Google and doesn't follow Google's
> robots.txt. Scraping without Google explicit written permission is a violation of thei
> terms and conditions on scraping and can potentially cause a lawsuit

## Install dependencies
```
pip install -r requirements.txt
```

## 🔍 Usage:

```
python gquestions.py query <keyword> (en|es|fr) [depth <depth>] [--csv] [--headless]
```

Print help message.

```
gquestions.py (-h | --help)
```

## 💡 Examples:
Search "flights" in English and export in html

```
python gquestions.py query "flights" en
```

Search headlessly "flights" in English and export in html
```
python gquestions.py query "flights" en --headless   

```

Search "vuelos" in Spanish and export in html and csv
```
python gquestions.py query "vuelos" es --csv
```

Search "vuelos" in Spanish with a depth of 1 and export in html
```
python gquestions.py query "vuelos" es depth 1 
```

Advanced use: using operators with queries:

```
python gquestions.py query '"vpn" site:https://protonmail.com/blog' en --csv
```

## License
All assets and code are under the GPL v3 License unless specified otherwise.

## 👀 Help:
Got stuck? Check help!
```
python gquestions.py -h
```

![Gquestions_graph](https://i.gyazo.com/5f9677d13ba9845e0f38972e4d8c6ed3.png)
