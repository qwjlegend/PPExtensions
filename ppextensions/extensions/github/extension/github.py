from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from git import Repo, exc
from urllib.parse import urlparse, unquote
from ppextensions.extensions.extension_logger import extension_logger

import requests
import json
import git
import os

GITHUB_URL_PREFIX = "https://github.com/"
GITHUB_API_PREFIX = "https://api.github.com"
GITHUB_TOKEN = os.environ['githubtoken']
NOTEBOOK_STARTUP_PATH = os.getcwd() + "/"


class PrivateGitHandler(IPythonHandler):
    @staticmethod
    def git_clone(local_repo_path, repo_url):
        try:
            repo_instance = Repo(local_repo_path)
        except exc.NoSuchPathError:
            o = urlparse(repo_url)
            repo_url_with_token = o.scheme + "://" + GITHUB_TOKEN + "@" + o.hostname + o.path
            Repo.clone_from(repo_url_with_token, local_repo_path)
            repo_instance = Repo(local_repo_path)
        return repo_instance

    @staticmethod
    def git_commit(repo_instance, commit_message):
        try:
            git_instance = repo_instance.git
            git_instance.add('.')
            git_instance.commit("-m", commit_message)
        except Exception as e:
            extension_logger.logger.error(str(e))

    @staticmethod
    def git_pull(repo_instance, branch="master"):
        try:
            git_instance = repo_instance.git
            git_instance.pull("origin", branch)
            return True
        except Exception as e:
            if "conflict" in e.stdout:
                return ",".join(e.stdout.split('\n')[1].split(' ')[4:])
            else:
                return "Error:" + ''.join(e.stderr.splitlines())

    @staticmethod
    def git_push(repo_instance, branch):
        resp = repo_instance.remote().push("master:" + branch)
        return resp

    @staticmethod
    def get_repo():
        repos = dict()
        headers = {'Authorization': 'token ' + GITHUB_TOKEN}
        repo = requests.get(GITHUB_API_PREFIX + '/user/repos?affiliation=owner', headers=headers)
        for rp in repo.json():
            repo_name = rp['full_name']
            branch = requests.get(GITHUB_API_PREFIX + '/repos/' + repo_name + '/branches', headers=headers)
            repos[repo_name] = [br['name'] for br in branch.json()]
        return json.dumps(repos)

    @staticmethod
    def git_commit_single(repo_name, file_name, commit_message):
        if repo_name == "/":
            return "Please commit the notebook inside the local repo!"
        local_repo_path = NOTEBOOK_STARTUP_PATH + unquote(repo_name)
        try:
            repo_instance = Repo(local_repo_path)
        except exc.InvalidGitRepositoryError as e:
            extension_logger.logger.error(str(e))
            return str(e)
        try:
            git_instance = repo_instance.git
            git_instance.add([file_name])
            git_instance.commit("-m", commit_message)
        except Exception as e:
            extension_logger.logger.error(str(e))
            return str(e)
        return True


class PrivateGitGetRepoHandler(PrivateGitHandler):
    """
    Get the accessible github repos and display them in the dropdown in github push menu
    """

    def get(self):
        try:
            repos = self.get_repo()
            self.finish(repos)
        except Exception as e:
            self.set_stauts(400)
            self.finish(str(e))


class PrivateGitPushHandler(PrivateGitHandler):
    """
    Private sharing handler to push a notebook or a folder to remote repo.
    Step1: Git Clone (If necessary)
    Step2: Git Commit
    Step3: Git Push
    """

    def post(self):
        repo_name = self.get_argument("repo")
        repo_url = GITHUB_URL_PREFIX + repo_name + ".git"
        branch = self.get_argument("branch")
        commit_message = self.get_argument("msg")
        file_name = self.get_argument("filename")

        try:
            local_repo_path = NOTEBOOK_STARTUP_PATH + "/" + repo_name
            repo_instance = self.git_clone(local_repo_path, repo_url)
            self.git_commit(repo_instance, commit_message)
            resp = self.git_push(repo_instance, branch)
            if resp[0].flags == git.remote.PushInfo.UP_TO_DATE:
                self.finish("Everything up-to-date")
            elif resp[0].flags in [git.remote.PushInfo.FAST_FORWARD, git.remote.PushInfo.NEW_HEAD,
                                   git.remote.PushInfo.NEW_TAG]:
                self.finish(unquote(file_name) + " has been successfully pushed! ")
            elif resp[0].flags == 1032:
                self.set_status(400)
                self.finish("Updates were rejected because the remote contains work that you do not have locally. "
                            "Please do git pull and fix the possible conflicts before pushing again!")
            else:
                self.set_status(400)
                self.finish("Could not push to remote {}".format(resp[0].remote_ref_string))
        except Exception as e:
            self.set_status(400)
            self.finish(str(e))


class PrivateGitPullHandler(PrivateGitHandler):
    """
    Private Sharing handler to pull a notebook or an entire repo to local.
    If there is a conflict, it will show the conflict in notebook and ask the user to fix.
    """

    def post(self):
        github_repo_url = self.get_argument("github_repo_url")
        o = urlparse(github_repo_url)
        split_word = "blob" if "blob" in o.path else "tree"
        repo_name = o.path.split("/" + split_word)[0]
        local_repo_path = NOTEBOOK_STARTUP_PATH + repo_name
        repo_url = github_repo_url.split("/" + split_word)[0] + ".git"
        try:
            repo_instance = self.git_clone(local_repo_path, repo_url)
            res = self.git_pull(repo_instance)
            if res is True:
                self.finish("Successfully pulled to " + repo_name)
            else:
                self.set_status(400)
                if "Error" in res:
                    self.finish(str(res))
                else:
                    self.finish(str("Please fix conflict file(s) " + res + " in " + repo_name))
        except Exception as e:
            self.set_status(400)
            self.finish(str(e))


class PrivateGitCommitHandler(PrivateGitHandler):
    """
        GitCommit handler used by the git commit button in notebook toolBar
    """

    def post(self):
        repo = self.get_argument("repo")
        file = self.get_argument("file")
        message = "Commit from PayPal Notebook"
        res = self.git_commit_single(repo, file, message)
        if res is True:
            self.finish("Commit Success!")
        else:
            self.set_status(400)
            self.finish(str(res))


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
        (r'/github/private_github_commit', PrivateGitCommitHandler),
    ]

    base_url = web_app.settings['base_url']
    handlers = [(url_path_join(base_url, h[0]), h[1]) for h in handlers]

    host_pattern = '.*$'
    web_app.add_handlers(host_pattern, handlers)
