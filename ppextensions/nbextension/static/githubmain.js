define(["jquery",
    "base/js/namespace",
    "base/js/utils",
    "./github",
    ], function($, Jupyter, utils, githuboperation){

    function load_ipython_extension(){

        var github_html = $.parseHTML("                <div id=\"github\" class=\"btn-group\">\n" +
            "                  <button class=\"dropdown-toggle btn btn-default btn-xs\" data-toggle=\"dropdown\">\n" +
            "                  <span>Sharing</span>\n" +
            "                  <span class=\"caret\"></span>\n" +
            "                  </button>\n" +
            "                  <ul id=\"new-menu\" class=\"dropdown-menu\">\n" +
            "                      <li role=\"presentation\" id=\"githubpush\">\n" +
            "                        <a href=\"#\" class=\"github-button-push\">Push to Github</a>\n" +
            "                      </li>\n" +
            "                      <li role=\"presentation\" id=\"gitpull\">\n" +
            "                        <a href=\"#\" class=\"github-button-pull \">Pull from Github</a>\n" +
            "                      </li>\n" +
            "                      <li role=\"presentation\" id=\"privategithubpush\">\n" +
            "                         <a role=\"menuitem\" tabindex=\"-1\" href=\"#\" class=\"private-github-push\">Push to Private Github</a>\n" +
            "                      </li>\n" +
            "                      <li role=\"presentation\" id=\"privategithubpull\">\n" +
            "                         <a role=\"menuitem\" tabindex=\"-1\" href=\"#\" class=\"private-github-pull\">Pull from Private Github</a>\n" +
            "                      </li>\n" +
            "                      <li class=\"divider private-github-repo\"></li>\n" +
            "                      <li role=\"presentation\" id=\"privategithubcollaborator\">\n" +
            "                         <a role=\"menuitem\" tabindex=\"-1\" href=\"#\" class=\"private-github-collaborator\">Add Collaborator to Repository</a>\n" +
            "                      </li>\n" +
            "                      <li role=\"presentation\" id=\"register\">\n" +
            "                         <a role=\"menuitem\" tabindex=\"-1\" href=\"#\" class=\"private-github-token\">Register Private Github Token</a>\n" +
            "                      </li>\n" +
            "                  </ul>\n" +
            "                </div>");

        $("#notebook_toolbar > .tree-buttons > .pull-right").prepend(github_html);

        var gitoperation = new githuboperation.GithubOperation();
        var url_whitelist = utils.url_path_join(Jupyter.notebook_list.base_url, '/github/is_whitelist');
        var _selection_changed = Jupyter.notebook_list.__proto__._selection_changed;

        $.get(url_whitelist, function(res){
            if (res == "False"){
                $('.private-github-push').css('display', 'none');
                $('.private-github-pull').css('display', 'none');
                $('.private-github-collaborator').css('display', 'none');
                $('.private-github-token').css('display', 'none');
            }else{
                Jupyter.notebook_list.__proto__._selection_changed = function(){
                _selection_changed.apply(this);
                selected = this.selected;
                if(selected.length == 1){
                    $.get(url_whitelist, function(res){
                        if (res == "True"){
                            $('.private-github-push').css('display', 'block');
                        }else{
                            $('.private-github-push').css('display', 'none');
                        }
                    })
                } else {
                    $('.private-github-push').css('display', 'none');
                };
            };
            Jupyter.notebook_list._selection_changed();
            };
        });

    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});
