define(["jquery",
    "base/js/namespace",
    "base/js/utils",
    "./github"
    ], function($, Jupyter, utils, githuboperation){

    function load_ipython_extension(){
        var github_html = $.parseHTML(<div id="github" class="btn-group">
                  <button class="dropdown-toggle btn btn-default btn-xs" data-toggle="dropdown">
                  <span>Sharing</span>
                  <span class="caret"></span>
                  </button>
                  <ul id="new-menu" class="dropdown-menu">
                      <li role="presentation" id="privategithubpush">
                         <a role="menuitem" tabindex="-1" href="#" class="private-github-push">Push to Personal Github</a>
                      </li>
                      <li role="presentation" id="privategithubpull">
                         <a role="menuitem" tabindex="-1" href="#" class="private-github-pull">Pull from Personal Github</a>
                      </li>
                  </ul>
                </div>);

        $(".tree-buttons > .pull-right").prepend(github_html);

        var gitoperation = new githuboperation.GithubOperation();
        var _selection_changed = Jupyter.notebook_list.__proto__._selection_changed;

        Jupyter.notebook_list.__proto__._selection_changed = function(){
        _selection_changed.apply(this);
        selected = this.selected;

        if(selected.length == 1){
           $('.private-github-push').css('display', 'block');
           } else {
           $('.private-github-push').css('display', 'none');
           }
            Jupyter.notebook_list._selection_changed();
        };
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});
