define(['base/js/namespace', 'base/js/dialog', 'tree/js/notebooklist', 'base/js/utils', 'jquery'], function (Jupyter, dialog, notebooklist, utils, $) {
    var GithubOperation = function () {
        this.base_url = Jupyter.notebook_list.base_url;
        this.bind_events();
    };

    GithubOperation.prototype = Object.create(notebooklist.NotebookList.prototype);

    GithubOperation.prototype.bind_events = function () {
        var that = this;
        $('.private-github-push').click($.proxy(that.private_github_push, this));
        $('.private-github-pull').click($.proxy(that.private_github_pull, this));
    };


    GithubOperation.prototype.private_github_push = function () {
        var that = this;
        var repo = $('<select id="repo" class="form-control">');
        repo.append('<option value="" disabled selected>Please select a repo</option>');
        var branch = $('<select id="branch" class="form-control">');
        branch.append('<option value="" disabled selected>Please select a branch</option>');

        function initializeDropdown(res){
             for (var rp in res) {repo.append(new Option(rp, rp));}
             repo.change(function () {
                var branches = res[repo.val()];
                branch.empty();
                branch.append('<option value="" disabled selected>Please select a branch</option>');
                $.each(branches, function (i, el) {
                    branch.append(new Option(el, el));
                });
             });
        }

        var url = utils.url_path_join(that.base_url, '/github/private_github_get_repo');
        var settings = {
            method: 'GET',
            cache: true,
            success: function (result) {
                sessionStorage.setItem(url, result);
		        var res = JSON.parse(result);
                initializeDropdown(res);
            },
            error: function (res) {
                console.log(res);
            }
        };
        if (sessionStorage.getItem(url) != null){
            var res = JSON.parse(sessionStorage.getItem(url));
            initializeDropdown(res);
        }else{
            utils.ajax(url, settings);
        }

        var commit_msg = $('<textarea class="form-control" placeholder="Enter Commit Message" id="msg"></textarea>').css('margin-left', '12px');
        var repo_div = $('<div class="form-group"></div>')
            .append('<label for="repo"><b>Github Repository:</b></label>')
            .append(repo);
        var branch_div = $('<div class="form-group"></div>')
            .append('<label for="branch"><b>Github Branch:</b></label>')
            .append(branch);
        var text_div = $('<div class="form-group"></div>')
            .append('<label for="msg"><b>Commit Message:</b></label>')
            .append(commit_msg);
        var dialog_body = $('<form></form>')
            .append(repo_div)
            .append(branch_div)
            .append(text_div);

        dialog.modal({
            title: "Push to Github",
            body: dialog_body,
            buttons: {
                Push: {
                    class: "btn-primary",
                    click: function () {
                        var notebook = Jupyter.notebook_list.selected[0];
                        var payload = {
                            "msg": commit_msg.val(),
                            "branch": branch.val(),
                            "repo": repo.val(),
                            "filename": encodeURI(notebook['name'])
                        };
                        var settings = {
                            method: 'POST',
                            data: payload,
                            success: function (res) {
                                spin.modal('hide');
                                dialog.modal({
                                    title: "Git Push Success",
                                    body: $('<div/>').text(res),
                                    button: {
                                        OK: {'class': 'btn-primary',
                                        click: function () {
                                                Jupyter.notebook_list.load_list();
                                            }
					                    }
                                    }
                                });
                            },
                            error: function (res) {
                                spin.modal('hide');
                                dialog.modal({
                                    title: "Git Push Failed",
                                    body: $('<div/>').text(res.responseText),
                                    button: {
                                        OK: {'class': 'btn-primary',
                                        click: function () {
                                                Jupyter.notebook_list.load_list();
                                            }
					                    }
                                    }
                                });
                            }
                        };
                        var url = utils.url_path_join(that.base_url, '/github/private_github_push');
                        utils.ajax(url, settings);
                        var spin = dialog.modal({
                            title: "Pushing...",
                            body: $('<div style="text-align:center"><i class="fa fa-spinner fa-spin" style="font-size:100px"></i></div>')
                                .append($('<div style="text-align:center"><strong>Notebook is being pushing from github, please wait for a few seconds.</strong></div>')),
                        });
                    }
                },
                Cancel: {}
            }
        });
    };
    GithubOperation.prototype.private_github_pull = function () {
        var that = this;

        var dialog_body = $('<div/>')
            .append($('<label for="github_repo_url"><b>Please enter the github repo url of the notebook: </b></label>'))
            .append($('<input id="gru" class= "form-control" type="text" placeholder="Enter Github Repo Url" name="github_repo_url" required>'))

        dialog.modal({
            title: "Pull from Github",
            body: dialog_body,
            buttons: {
                Pull: {
                    class: "btn-primary",
                    click: function () {
                        var payload = {
                            'github_repo_url': $('#gru').val(),
                        };
                        var settings = {
                            method: 'POST',
                            data: payload,
                            success: function (res) {
                                spin.modal('hide');
                                dialog.modal({
                                    title: 'Pull success!',
                                    body: $('<div/>').text(res),
                                    buttons: {
                                        OK: {
                                            class: "btn-primary",
                                            click: function () {
                                                Jupyter.notebook_list.load_list();
                                            }
                                        }
                                    }
                                });
                            },
                            error: function (res) {
                                spin.modal('hide');
                                dialog.modal({
                                    title: 'Pull failed!',
                                    body: $('<div/>').text(res.responseText),
                                    buttons: {
                                        OK: {class: "btn-primary"}
                                    }
                                });
                            }
                        };
                        var url = utils.url_path_join(that.base_url, '/github/private_github_pull');
                        utils.ajax(url, settings);
                        var spin = dialog.modal({
                            title: "Pulling...",
                            body: $('<div style="text-align:center"><i class="fa fa-spinner fa-spin" style="font-size:100px"></i></div>')
                                .append($('<div style="text-align:center"><strong>Notebook is being pulled from github, please wait for a few seconds.</strong></div>')),
                        });
                    }
                },
                Cancel: {}
            }
        });
    };

    return {GithubOperation: GithubOperation};
});
