#! /usr/bin/python

from feedgen.feed import FeedGenerator
import argparse
import os
import sys
import time
from stat import S_ISREG, ST_CTIME, ST_MODE
import subprocess
from pathlib import Path
import markdown
from datetime import datetime

parser = argparse.ArgumentParser(prog="pog", description="python weblog", epilog="python weblog")
parser.add_argument("option", help="post [-n, --name] to make a post, title following -n with no spaces. init to initialize new blog in a directory. edit [-n, --name] to edit a post. update to rebuild site")
parser.add_argument("-n", "--name", help="name of post to edit/create")
args = parser.parse_args()

# settings:

author = "flat"  # i think all options except maybe the last few are pretty self-explanatory
contact = "flat@fuckup.club"
website = "https://tilde.team/~flat/"
bloglink = "https://tilde.team/~flat/blog/"
description = 'infrequent rambles about whatever i really feel like thinking about at the moment.'
title = author + "'s blog"
header = f'<h1><a href="index.html">{title}</a></h1>'
footer = f'<hr><p>anything to say? <a href="mailto:{contact}?subject=in%20response%20to...">email me!</a><br><em>written by <a href="{website}">{author}</a> - generated with pog!</p>'
dateformat = '%Y-%m-%d'
exceptions = {"index.html",  # all pages to ignore when building blog
              "pog.py",
              "atom.xml",
              "README.md"
              }
pages = ["../index.html", "atom.xml"] # other pages to show on the navbar

tildeMode = True  # just a failsafe feature cause sometimes tilde.team bugs out with the editing, this forces nvim

def update():
  with open("index.html", "w") as f:
    f.write(f'<h1>{title}</h1>')
    for page in pages:
      f.write(f'<li><a href="{page}">{Path(page).stem}</a></li>')
    f.write(f'<p>{description}</p>')
    f.write('<h3>posts:</h3>')
  files = (os.listdir("drafts/"))
  files = ((os.stat(f'drafts/{path}'), path) for path in files)
  files = ((stat[ST_CTIME], f'drafts/{path}')
           for stat, path in files if S_ISREG(stat[ST_MODE]))
  entries = []
  files = sorted(files)[::-1]
  for cdate, path in files:
    if os.path.basename(path) not in exceptions:
      open("index.html", "a").write(f'<a href="{Path(os.path.basename(path)).stem}.html">{time.ctime(cdate)} - {Path(os.path.basename(path)).stem}</a><br>')
      markdown.markdownFromFile(input=f'drafts/{os.path.basename(path)}', output=f'{Path(path).stem}.html', output_format="html")
  fg = FeedGenerator()
  fg.title(title)
  fg.author( {"name" : author, "email" : contact} )
  fg.subtitle(description)
  fg.link({"href": bloglink, "rel": "self"})
  fg.link({"href": website, "rel": "alternate"})
  fg.id(bloglink)
  for path in os.listdir("drafts/"):
    if path not in exceptions:
      fe = fg.add_entry()
      fe.id(bloglink + Path(path).stem + ".html")
      fe.title(Path(path).stem)
      fe.link({"href": bloglink + Path(path).stem + ".html", "rel": "self"})
      fe.link({"href": bloglink, "rel": "alternate"})
      fe.author({"name" : author, "email" : contact})
      fe.content("".join((open(Path(path).stem + ".html").readlines())))
      fe.pubDate(datetime.fromtimestamp(int(os.path.getmtime(Path(path).stem + ".html"))).strftime("%a, %d %b %Y %H:%M:%S GMT"))
      fe.updated(datetime.fromtimestamp(int(os.path.getmtime(Path(path).stem + ".html"))).strftime("%a, %d %b %Y %H:%M:%S GMT"))
      fe.source({"url": bloglink, "title": title})
  fg.atom_file('atom.xml')
  for cdate, path in files:
    if os.path.basename(path) not in exceptions:
      with open(Path(os.path.basename(path)).stem + ".html", "r") as r:
        lines = r.readlines()
        count = 1
        savelines = []
        for line in lines[:-1]:
          savelines.append(lines[count])
          count += 1
      with open(Path(os.path.basename(path)).stem + ".html", "w") as r:
        r.write(header)
        for line in savelines:
          r.write(line)
        r.write(footer)

match args.option:
    case "init":
      os.mkdir("drafts")
      with open("index.html", "w") as f:
        for page in pages:
          f.write(f'<li><a href="{page}">{Path(page).stem}</a></li>')
        f.write(f'<h1>{title}</h2>')
        f.write(f'<p>{description}</p>')
        f.write('<h3>posts:</h3>')
        update()

    case "update":
      update()

    case "post":
      with open(f'drafts/{args.name}.md', "w") as f:
        date = datetime.today().strftime(dateformat)
        f.write("<!-- post starts below: -->")
        f.write("\n" + f'## {args.name}')
        f.write(f'\n_{date}_')
      if tildeMode is False:
        subprocess.call(("xdg-open", f'drafts/{args.name}.md'))
      else:
        subprocess.call(("nvim", f'drafts/{args.name}.md'))
      opt = input("post written, what do you want to do now?\n(s) save draft (p) post (d) discard post\n> ")
      match opt:
        case "s":
          print(f"saved draft in drafts/{args.name}.md")
        case "p":
          update()
          print("post succesful")
        case "d":
          os.remove(f"drafts/{args.name}.md")
          print("file removed")

    case "edit":
      subprocess.call(("xdg-open", f'drafts/{args.name}.md'))
      opt = input("post written, what do you want to do now?\n(s) save draft (p) post (d) discard post\n> ")
      match opt:
        case "s":
          print(f"saved draft in drafts/{args.name}.md")
        case "p":
          update()
          print("post succesful")
        case "d":
          os.remove(f"drafts/{args.name}.md")
          print("file removed")

    case other:
        print("invalid command")
