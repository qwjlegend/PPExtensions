define(["jquery",
    "base/js/namespace",
    "base/js/utils",
    "./scheduler",
    ], function($, Jupyter, utils, scheduleoperation){

    function load_ipython_extension(){

        var scheduler_html = $.parseHTML("<button title=\"Schedule selected\" id=\"schedule_button\" class=\"edit-button btn btn-default btn-xs\">Schedule</button>");
        var scheduler_tab_html = $.parseHTML("<li><a href=\"#scheduledjobs\" class=\"scheduled_jobs\" data-toggle=\"tab\">Scheduled Jobs</a></li>");
        var scheduler_tab_content_html = $.parseHTML("         <div id=\"scheduledjobs\" class=\"tab-pane\">\n" +
            "           <div id=\"schedule_toolbar\" class=\"row\" style=\"margin-top:10px; margin-bottom:10px\">\n" +
            "            <div class=\"col-sm-8 no-padding\">\n" +
            "              <span id=\"schedule_list_info\">Currently scheduled airflow jobs</span>\n" +
            "            </div>\n" +
            "            <div class=\"col-sm-4 no-padding tree-buttons\">\n" +
            "              <span id=\"schedule_buttons\" class=\"pull-right\">\n" +
            "              <button id=\"refresh_schedule_list\" title=\"Refresh schedule list\" class=\"btn btn-default btn-xs\"><i class=\"fa fa-refresh\"></i></button>\n" +
            "              </span>\n" +
            "            </div>\n" +
            "           </div>\n" +
            "           <div class=\"panel-group\" id=\"scheduled\" >\n" +
            "            <div class=\"panel panel-default\">\n" +
            "              <div class=\"panel-heading\">\n" +
            "                <a data-toggle=\"collapse\" data-target=\"#collapseThree\" href=\"#\">\n" +
            "                  Airflow Jobs:\n" +
            "                </a>\n" +
            "              </div>\n" +
            "              <div id=\"collapseThree\" class=\"collapse in\">\n" +
            "                <div class=\"panel-body\">\n" +
            "                  <div id=\"schedule_list\">\n" +
            "                    <div id=\"schedule_list_placeholder\" class=\"row list_placeholder\">\n" +
            "                    </div>\n" +
            "                  </div>\n" +
            "                </div>\n" +
            "              </div>\n" +
            "            </div>\n" +
            "          </div>\n" +
            "        </div>")


        $(".dynamic-buttons").prepend(scheduler_html);
        $(".tab-content").append(scheduler_tab_content_html);
        $("#tab_content > #tabs").append(scheduler_tab_html);


        var url_whitelist = utils.url_path_join(Jupyter.notebook_list.base_url, '/scheduler/is_whitelist');
        var url_get_dag = utils.url_path_join(Jupyter.notebook_list.base_url, '/scheduler/get_dag');
        var url_add_to_whitelist = utils.url_path_join(Jupyter.notebook_list.base_url, '/scheduler/add_to_whitelist');
        $('#refresh_schedule_list, .scheduled_jobs').click(function(){
            $.get(url_whitelist, function(res){
            if(res == 'True'){
                    $("#schedule_list_placeholder").load(url_get_dag);
                    }else{
                    var t1 = $("<p>Scheduling is in a closed beta. Once the feature is rolled out to you, you will be able to see your scheduled jobs here.</p>");
                    var t2 = $("<p>To request the whitelist role, please click on the button below</p>");
                    var bt = $("<div/>").append($('<button id="whitelist" onclick="addtowhitelist()" class="btn btn-primary">Add me to whitelist</button>'));
                    $("#schedule_list_placeholder").append(t1).append(t2).append(bt);
                    }
                });
        });

        function addtowhitelist(){
            alert("You have been added to whitelist!");
            $.get(url_add_to_whitelist, function(){
                        $('a[href=#scheduledjobs]').click().tab('show');
                    });
        };

        var schedule = new scheduleoperation.ScheduleOperation();
        var _selection_changed = Jupyter.notebook_list.__proto__._selection_changed;
        Jupyter.notebook_list.__proto__._selection_changed = function(){
            _selection_changed.apply(this);
            selected = this.selected;
            if(selected.length == 1){
                $('.schedule-button').css('display', 'block');
            } else {
                $('.schedule-button').css('display', 'none');
            }
        };
        Jupyter.notebook_list._selection_changed();
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});
