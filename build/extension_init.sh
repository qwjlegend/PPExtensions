#!/bin/sh
jupyter nbextension install github --user --py
jupyter nbextension enable github --user --py
jupyter serverextension enable github --py --user
git config --global user.email $githubemail
git config --global user.name $githubname
git-nbmergedriver config --enable --global
