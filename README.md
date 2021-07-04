# nordbayern_news_downloader
download pdf e-newspaper from nordbayern.de (for registered accounts)

2021 version for new website

# prerequisites
- selenium
- chrome browser and chromedriver (in $PATH)
- only standard python modules os, pathlib, time
- be paying customer of nordbayern.de e-paper

OR
- docker
- be paying customer of nordbayern.de e-paper

# usage
- change username and pw (yes, its in plain text)
- pray that they haven't modified their website yet (again)
- run py file

OR
- run docker-container, mount target download dir as volume and pass with "--dir $PATH" argument

# known issues
- only works for Nürnberger Nachrichten for now, need to edit browser.get(...) at the end of step 1 for other papers
