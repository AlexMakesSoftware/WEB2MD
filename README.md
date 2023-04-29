# README.md

Just a script I put together which scrapes an entire website and converts it to markdown. Probably badly. Very specific to my needs and probably not useful to anyone else - page links don't seem to work but I don't need them to really. I just wanted something I could cut and paste without grabing a whole load of Wordpress 'div soup' with it.

Bear in mind if you try to use this that most hosts will perform some kind of rate limiting and/or bot detection and you'll probably get your IP address banned if you use it without permission, or if you try to scrape too fast. If the site belongs to you, you're probably better off using some tool to download the site as a static site (Simply Static works well for Wordpress sites) and then using this to convert it to markdown. You can serve the static site using python like so:

```
python -m http.server
```

## Setup
```
conda create --name web2markdown --file requirements.txt
conda activate web2markdown
```

N.B. For some reason on windows, you need to use to conda powershell prompt to get the environment to activate properly.

## Running
URL of the website you want goes as the first and only argument. For example:
```
python web2markdown.py https://www.example.com
```
