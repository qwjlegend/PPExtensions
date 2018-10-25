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
        $('.private-github-collaborator').click($.proxy(that.private_github_collaborator, this));
        $('.private-github-token').click($.proxy(that.private_github_token, this));
    };


    GithubOperation.prototype.private_github_push = function () {
        var that = this;
        var repo = $('<select id="repo" class="form-control">');
        repo.append('<option value="" disabled selected>Please select a repo</option>');
        var branch = $('<select id="branch" class="form-control">');
        branch.append('<option value="" disabled selected>Please select a branch</option>');

        var settings = {
            method: 'GET',
            success: function (res) {
		var res = JSON.parse(res);
                for (var rp in res) {repo.append(new Option(rp, rp));} 
                repo.change(function () {
                    var branches = res[repo.val()];
                    branch.empty();
                    branch.append('<option value="" disabled selected>Please select a branch</option>');
                    $.each(branches, function (i, el) {
                        branch.append(new Option(el, el));
                    });
                });
            },
            error: function (res) {
                console.log(res.responseText)
            },
        };
        var url = utils.url_path_join(that.base_url, '/github/private_github_get_repo');
        utils.ajax(url, settings);
        var commit_msg = $('<textarea class="form-control" placeholder="Enter Commit Message" id="msg"></textarea>').css('margin-left', '12px');
        var repo_div = $('<div class="form-group"></div>')
            .append('<label for="repo"><b>Github Repository:</b></label>')
            .append(repo)
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
            title: "Push to private Github",
            body: dialog_body,
            buttons: {
                Push: {
                    class: "btn-primary",
                    click: function () {
                        var notebook = Jupyter.notebook_list.selected[0];
                        console.log(commit_msg.val());
                        console.log(branch.val());
                        console.log(repo.val());
                        console.log(notebook['name']);
                        console.log(notebook['path']);
                        var payload = {
                            "msg": commit_msg.val(),
                            "branch": branch.val(),
                            "repo": repo.val(),
                            "filepath": notebook['path'],
                            "filename": encodeURI(notebook['name'])
                        };
                        var settings = {
                            method: 'POST',
                            data: payload,
                            success: function (res) {
                                spin.modal('hide');
                                dialog.modal({
                                    title: "Github Push Successfull",
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
                                    title: "Github Push Failed",
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

        var navs = $('<ul class="nav nav-tabs"/>')
            .append($('<li class="active"><a data-toggle="tab" href="#normalgitpull">Normal Git Pull</a></li>'))
            .append($('<li><a data-toggle="tab" href="#forcegitpull">Force Git Pull</a></li>'));
        var content = $('<div class="tab-content">')
            .append($('<div id="normalgitpull" class="tab-pane fade in active">')
                .append($('<label for="github_repo_url"><b>Please enter the github repo url of the notebook: (This option is equivalent to normal git pull command)</b></label>'))
                .append($('<input id="gru" class= "form-control" type="text" placeholder="Enter Github Repo Url" name="github_repo_url" required>')))
            .append($('<div id="forcegitpull" class="tab-pane fade">')
                .append($('<label for="github_file_url"><b>Please enter the github file url of the notebook: (This option will download the remote notebook and force override your local notebook)</b></label>'))
                .append($('<input id="gfu" class= "form-control" type="text" placeholder="Enter Github File Url" name="github_file_url" required>')));

        var dialog_body = $('<div/>').addClass('form-group').append(navs).append(content);

        dialog.modal({
            title: "Pull from private Github",
            body: dialog_body,
            buttons: {
                Pull: {
                    class: "btn-primary",
                    click: function () {
                        var gru = $("#gru").val().trim();
                        var gfu = $("#gfu").val().trim();
                        if (gru.length != 0 && gfu.length != 0){
                            alert("Please do not submit two urls!");
                            return false;
                        }
                        var payload = {
                            'github_repo_url': gru,
                            'github_file_url': gfu
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
                        }
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

    GithubOperation.prototype.private_github_collaborator = function () {
        var that = this;
        var repo = $('<select id="repo" class="form-control">');
        repo.append('<option value="" disabled selected>Please select a repo</option>');

        var settings = {
            method: 'GET',
            success: function (res) {
                var res = JSON.parse(res);
		for (var rp in res){repo.append(new Option(rp, rp))}
            },
            error: function (res) {
                console.log(res.statusText)
            },
        };
        var url = utils.url_path_join(that.base_url, '/github/private_github_get_repo');
        utils.ajax(url, settings);

        var collaborators = $('<input class= "form-control" type="text" placeholder="Enter Collaborators Corp ID" name="clb" required>').css('margin-left', '12px');
        var dialog_body = $('<div/>').addClass('form-group')
            .append('<label for="repo"><b>Repo Name:</b></label>')
            .append(repo)
            .append('<br/>')
            .append('<label for="clb"><b>Collaborators (Separate by comma):</b></label>')
            .append(collaborators);


        dialog.modal({
            title: "Add collaborators to repo",
            body: dialog_body,
            default_button: "Cancel",
            buttons: {
                Cancel: {},
                Add: {
                    class: "btn-primary",
                    click: function () {
                        var payload = {
                            'repo': repo.val(),
                            'collaborators': collaborators.val()
                        };
                        var settings_cl = {
                            data: payload,
                            method: 'POST',
                            success: function (res) {
                                spin.modal('hide');
                                dialog.modal({
                                    title: 'Add Collaborator Success!',
                                    body: $('<div/>').text(res),
                                    buttons: {
                                        OK: {class: "btn-primary"}
                                    }
                                });
                            },
                            error: function (res) {
                                console.log(res);
                                spin.modal('hide');
                                dialog.modal({
                                    title: 'Add Collaborator Failed!',
                                    body: $('<div/>').text(res.responseText),
                                    buttons: {
                                        OK: {class: "btn-primary"}
                                    }
                                });
                            }
                        };
                        url = utils.url_path_join(that.base_url, '/github/private_github_collaborator');
                        utils.ajax(url, settings_cl);
                        var spin = dialog.modal({
                            title: "Adding...",
                            body: $('<div style="text-align:center"><i class="fa fa-spinner fa-spin" style="font-size:100px"></i></div>')
                                .append($('<div style="text-align:center"><strong>Adding collaborator, please wait for a few seconds.</strong></div>')),
                        });
                    }
                }
            }
        });
    };

    GithubOperation.prototype.private_github_token = function () {
        var username = $('<input class= "form-control" type="text" placeholder="Enter Github Username" name="name" required>');
        var password = $('<input class= "form-control" type="password" placeholder="Enter Password" name="pwd" required>');
        var dialog_body = $('<div/>').addClass('form-group')
            .append('<label for="name"><b>Github Username:</b></label>')
            .append(username)
            .append('<br/>')
            .append('<label for="pwd"><b>Corp Password:</b></label>')
            .append(password);
        var payload = {
            "scopes": ["public_repo"],
            "note": "Git Token for PayPal Notebook"
        };
        var that = this;
        dialog.modal({
            title: "Generate private Github Token",
            body: dialog_body,
            default_button: "Cancel",
            buttons: {
                Cancel: {},
                Register: {
                    class: "btn-primary",
                    click: function () {
                        var settings = {
                            url: "https://github.paypal.com/api/v3/authorizations",
                            data: JSON.stringify(payload),
                            dataType: "json",
                            contentType: "application/json; charset=utf-8",
                            method: 'POST',
                            beforeSend: function (xhr) {
                                xhr.setRequestHeader("Authorization", "Basic " + btoa(username.val() + ":" + password.val()));
                            },
                            success: function (res) {
                                var token = res['token'];
                                var url = utils.url_path_join(that.base_url, '/github/private_github_token')
                                $.get(url + "?token=" + token);
                                dialog.modal({
                                    title: 'Register success!',
                                    body: $('<div/>').text("Your github token is successfully generated and stored!"),
                                    buttons: {
                                        OK: {class: "btn-primary"}
                                    }
                                });
                            },
                            error: function (res) {
                                var err = res.responseJSON['message'];
                                if (err == 'Validation Failed') {
                                    err = "Your token is existed!";
                                }
                                dialog.modal({
                                    title: 'Register failed!',
                                    body: $('<div/>').text('Error: ' + err),
                                    buttons: {
                                        OK: {class: "btn-primary"}
                                    }
                                });
                            }
                        };
                        $.ajax(settings);
                    }
                }
            }
        });
    };

    return {GithubOperation: GithubOperation};
});
