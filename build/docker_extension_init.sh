#!/bin/sh
cd ~/PPExtensions/ppextensions/extensions/github
jupyter nbextension install static
cd ~/PPExtensions/ppextensions/extensions/scheduler
jupyter nbextension install static

jupyter nbextension enable static/github --section='tree'
jupyter nbextension enable static/githubmain --section='tree'
jupyter nbextension enable static/githubcommit --section='notebook'
jupyter nbextension enable static/schedulermain --section='tree'
jupyter nbextension enable static/scheduler --section='tree'

jupyter serverextension enable --user ppextensions.extensions.github.github
jupyter serverextension enable --user ppextensions.extensions.scheduler.scheduler

git config --global user.email $githubemail
git config --global user.name $githubname
git-nbmergedriver config --enable --global


