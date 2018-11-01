from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from git import Repo, exc
from shutil import move
from urllib.parse import urlparse, unquote
from getpass import getuser

import requests
import json
import git
import base64
import os

LOCAL_REPO_FOLDER = "Private Sharing"
USER_HOME_PATH_PREFIX = "/home/" + getuser() + "/"
LOCAL_REPO_PREFIX = USER_HOME_PATH_PREFIX + LOCAL_REPO_FOLDER
GITHUB_URL_PREFIX = "https://github.paypal.com/"
GITHUB_TOKEN_PATH = USER_HOME_PATH_PREFIX + ".githubtoken"
GITHUB_API_PREFIX = GITHUB_URL_PREFIX + "api/v3"
GITHUB_WHITELIST = "/etl/LVS/dmetldata11/scaas/scheduler/airflow_home_mount/whitelist/git_whitelist.txt"


class PrivateGitHandler(IPythonHandler):
    @staticmethod
    def gettoken():
        with open(GITHUB_TOKEN_PATH) as f:
            token = f.read().strip()
        return token 

    def gitclone(self, local_repo_path, repo_url):
        try:
            isexisted = True
            repo_instance = Repo(local_repo_path)
        except exc.NoSuchPathError:
            gittoken = self.gettoken()
            o = urlparse(repo_url)
            repo_url_with_token = o.scheme + "://" + gittoken + "@" + o.hostname + o.path
            Repo.clone_from(repo_url_with_token, local_repo_path)
            repo_instance = Repo(local_repo_path)
            isexisted = False
        finally:
            return repo_instance, isexisted

    @staticmethod
    def gitcommit(from_path, to_path, repo_instance, commit_message):
        try:
            move(from_path, to_path)
        except Exception as e:
            pass
        git_instance = repo_instance.git
        git_instance.add('.')
        try:
            git_instance.commit("-m", commit_message)
        except Exception as e:
            pass 
    
    @staticmethod
    def gitcommitsinglefile(repo_name, file_name, commit_message):
        local_repo_path = USER_HOME_PATH_PREFIX + unquote(repo_name) 
        try:
            repo_instance = Repo(local_repo_path) 
        except exc.InvalidGitRepositoryError:
            return False
        git_instance = repo_instance.git
        git_instance.add([file_name])
        try:
           git_instance.commit("-m", commit_message)
        except Exception as e:
            pass
        return True

    @staticmethod
    def gitpull(repo_instance, branch="master"):
        git_instance = repo_instance.git
        try:
            git_instance.pull("origin", branch)
            return True
        except Exception as e:
            err = e
            if "conflict" in err.stdout:
                return ",".join(err.stdout.split('\n')[1].split(' ')[4:])
            else:
                return "Error:" + ''.join(err.stderr.splitlines())

    def forcegitpull(self, repo, path, branch):
        headers = {'Authorization': 'token ' + self.gettoken()}
        res = requests.get(GITHUB_API_PREFIX + "/repos{}/contents{}?ref={}".format(repo, path, branch), headers=headers)
        content = res.json()['content']
        ct = base64.b64decode(content).decode()
        with open(LOCAL_REPO_PREFIX + repo + path, "w") as f:
            f.write(ct)

    @staticmethod
    def gitpush(repo_instance, branch):
        resp = repo_instance.remote().push("master:" + branch)
        return resp

    def getrepo(self):
        repos = dict()
        headers = {'Authorization': 'token ' + self.gettoken()}
        repo = requests.get(GITHUB_API_PREFIX + '/user/repos?affiliation=owner,collaborator', headers=headers)
        for rp in repo.json():
            repo_name = rp['full_name']
            branch = requests.get(GITHUB_API_PREFIX + '/repos/' + repo_name + '/branches', headers=headers)
            repos[repo_name] = [br['name'] for br in branch.json()]
        return json.dumps(repos)

    def add_collaborator(self, repo, collaborators):
        gittoken = self.gettoken()
        headers = {'Authorization': 'token ' + gittoken}
        for col in collaborators.split(','):
            cb = requests.put(GITHUB_API_PREFIX + "/repos/" + repo + "/collaborators/" + col, headers=headers)
            try:
                if 'message' in cb.json():
                    err = ['message']
                    return err
            except:
                return "This User is already a collaborator!"
        return False

class PrivateGitGetRepoHandler(PrivateGitHandler):
    def get(self):
        try:
            repos = self.getrepo()
            self.finish(repos)
        except Exception as e:
            self.set_stauts(400)
            self.finish(str(e))


class PrivateGitGetLocalRepoHandler(PrivateGitHandler):
    def get(self):
        try:
            repos = self.getlocalreponame()
            self.finish(json.dumps(repos))
        except Exception as e:
            self.set_status(400)
            self.finish(str(e))

class PrivateGitPushHandler(PrivateGitHandler):
    def post(self):
        repo_name = self.get_argument("repo")
        repo_url = GITHUB_URL_PREFIX + repo_name + ".git"
        branch = self.get_argument("branch")
        commit_message = self.get_argument("msg")
        file_path = self.get_argument("filepath")
        file_name = self.get_argument("filename")
        local_repo_path = LOCAL_REPO_PREFIX + "/" + repo_name
        inside = True
        if not file_path.startswith(LOCAL_REPO_FOLDER):
            inside = False
            local_repo_file_path = local_repo_path  + "/" + file_path
        else:
            local_repo_file_path = USER_HOME_PATH_PREFIX + file_path
        repo_instance, isexisted = self.gitclone(local_repo_path, repo_url)
        message1 = "Notice: A local github repo Private Sharing/" + repo_name + " has been created and your notebook has been moved to there!" if not isexisted else ""
        message2 = "Your notebook has been moved to local github repo: Private Sharing/" + repo_name if inside == False and message1 == "" else ""

        self.gitcommit(file_path, local_repo_file_path, repo_instance, commit_message)
        try:
            resp = self.gitpush(repo_instance, branch)
            if resp[0].flags == git.remote.PushInfo.UP_TO_DATE:
                self.finish("Everything up-to-date")
            elif resp[0].flags in [git.remote.PushInfo.FAST_FORWARD, git.remote.PushInfo.NEW_HEAD, git.remote.PushInfo.NEW_TAG]:
                self.finish(unquote(file_name) + " has been successfully pushed! " + message1 + message2)
            elif resp[0].flags == 1032:
                self.set_status(400)
                self.finish("Updates were rejected because the remote contains work that you do not have locally. Please do git pull and fix the possible conflicts before pushing again!")
            else:
                self.set_status(400)
                self.finish("Could not push to remote {}".format(resp[0].remote_ref_string) + message)
        except Exception as e:
            self.set_status(400)
            self.finish(str(e))


class PrivateGitPullHandler(PrivateGitHandler):
    def post(self):
        github_file_url = self.get_argument("github_file_url")
        github_repo_url = self.get_argument("github_repo_url")
        if github_repo_url:
            o = urlparse(github_repo_url)
            splitword = "blob" if "blob" in o.path else "tree"
            repo_name = o.path.split("/" + splitword)[0]
            local_repo_path = LOCAL_REPO_PREFIX + repo_name
            repo_url = github_repo_url.split("/" + splitword)[0] + ".git"
            repo_instance, _ = self.gitclone(local_repo_path, repo_url)
            try:
                res = self.gitpull(repo_instance)
                if res is True:
                    self.finish("Successfully pulled to Private Sharing" + repo_name)
                else:
                    self.set_status(400)
                    if "Error" in res:
                        self.finish(str(res))
                    else:
                        self.finish(str("Please fix conflict file(s) " + res + " in Private Sharing" + repo_name))
            except Exception as e:
                self.set_status(400)
                self.finish(str(e))
        elif github_file_url:
            o = urlparse(github_file_url)
            splitword = "blob" if "blob" in o.path else "tree"
            repo = o.path.split("/" + splitword)[0]
            branch = o.path.split(splitword + "/")[1].split('/')[0]
            path = unquote(github_file_url.split(branch)[1])
            try:
                self.forcegitpull(repo, path, branch)
                self.finish("Successfully pulled to Private Sharing" + repo)
            except Exception as e:
                self.set_status(400)
                self.finish(str(e))


class PrivateGitCommitHandler(PrivateGitHandler):
    '''GitCommit Handler Used by the Git Commit Button in Notebook ToolBar'''
    def post(self):
        repo_name = self.get_argument("repo")
        file_name = self.get_argument("file")
        commit_message = "Commit from PayPal Notebook" 
        res = self.gitcommitsinglefile(repo_name, file_name, commit_message)
        if res:   
            self.finish("Commit Success!")
        else:
            self.set_status(400)
            self.finish("Please commit a notebook inside local repository!")

class PrivateGitCollaboratorHandler(PrivateGitHandler):
    def post(self):
        repo = self.get_argument('repo')
        collaborators = self.get_argument('collaborators')
        res = self.add_collaborator(repo, collaborators)
        if not res:
            self.finish("Successfully added " + collaborators + " to repo " + repo)
        else:
            self.set_status(400)
            self.finish(str(res))

class PrivateGitTokenHandler(PrivateGitHandler):
    def get(self):
        token = self.get_argument('token')
        with open(GITHUB_TOKEN_PATH, 'w') as f:
            f.write(token)
        self.finish("Token generated successfully!")

class WhitelistCheckHandler(IPythonHandler):
    def get(self):
        with open(GITHUB_WHITELIST) as f:
            names = [name.strip() for name in f.readlines()]
            if getuser() in names:
                res = "True"
            else:
                res = "False"
        self.finish(res)

class GithtokenHandler(PrivateGitHandler):
    def get(self):
        if os.path.isfile(GITHUB_TOKEN_PATH):
            self.finish('True')
        else:
            self.finish('False')

def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    handlers = [
        (r'/github/private_github_push', PrivateGitPushHandler),
        (r'/github/private_github_pull', PrivateGitPullHandler),
        (r'/github/private_github_get_repo', PrivateGitGetRepoHandler),
        (r'/github/private_github_get_local_repo', PrivateGitGetLocalRepoHandler),
        (r'/github/private_github_commit', PrivateGitCommitHandler),
        (r'/github/private_github_collaborator', PrivateGitCollaboratorHandler),
        (r'/github/private_github_token', PrivateGitTokenHandler),
        (r'/github/is_whitelist', WhitelistCheckHandler),
        (r'/github/gittoken', GithtokenHandler)
    ]

    base_url = web_app.settings['base_url']
    handlers = [(url_path_join(base_url, h[0]), h[1]) for h in handlers]

    host_pattern = '.*$'
    web_app.add_handlers(host_pattern, handlers)
