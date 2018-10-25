define(['base/js/namespace', 'base/js/dialog', 'tree/js/notebooklist', 'base/js/utils', 'jquery'], function (Jupyter, dialog, notebooklist, utils, $) {

    var ScheduleOperation = function () {
        this.base_url = Jupyter.notebook_list.base_url;
        this.bind_events();
    };

    ScheduleOperation.prototype = Object.create(notebooklist.NotebookList.prototype);

    ScheduleOperation.prototype.bind_events = function () {
        var that = this;
        $('#schedule_button').click($.proxy(that.schedule_selected, this));
    };


    ScheduleOperation.prototype.schedule_selected = function () {
        var that = this;
        var selected = Jupyter.notebook_list.selected;
        if (selected.length > 1){
                alert("Cannot schedule more than one notebook at the same time!");
                return;
        }
        var lst = [];
        for (var i=4;i<=23;i++){
              lst.push(i);
           }
        var every_num = $('<select id= "num"></select>');
        $.each(lst, function(i, el){every_num.append(new Option(el, el));});

        var every_unit = $('<select id="unit"></select>');
        var unitList = ['hours', 'days', 'months', 'weeks']
        $.each(unitList, function(i, el){every_unit.append(new Option(el, el));});

        every_unit.change(function() {
           lst = [];
           if (every_unit.val() == "hours"){
                for (var i=4;i<=23;i++){
                        lst.push(i);
                }
           }
           else if (every_unit.val() == "days"){
                for (var i=1;i<=30;i++){
                        lst.push(i);
                }
           }
           else if (every_unit.val() == "months"){
                for (var i=1;i<=12;i++){
                        lst.push(i);
                }
           }
           else if (every_unit.val() == "weeks"){
                for (var i=1;i<=52;i++){
                        lst.push(i);
                }
           }
           every_num.empty();
           $.each(lst, function(i, el){every_num.append(new Option(el, el));});
        });

        var start_time = $('<input type="time" id="time">').val("00:00");
        var start_date = $('<input type="date" id="date">').val(new Date().toISOString().split('T')[0]);
        var end_after = $('<select id= "end"></select>');
        var endafterList = ['1 time', '2 times', '3 times', '4 times', '5 times', '10 times'];
        $.each(endafterList, function(i, el){end_after.append(new Option(el, el));});

        var schedule_part = $('<div/>')
                .append('<label for="num">Every:</label>')
                .append(every_num)
                .append(every_unit)
                .append('<br>')
                .append('<label for="time">Start at:</label>')
                .append(start_time)
                .append('<br>')
                .append('<label for="date">Start on:</label>')
                .append(start_date)
                .append('<br>')
                .append('<label for="end">end after</lable>')
                .append(end_after);

        //Part2 Notification
        var inst1 = $("<p>Please check the box and input the emails (separate by comma) that you want us to send email alert to</p>")
        var notify_on_failure = $("<input type='checkbox'  name='checkbox1' checked='checked'></input>").css('margin-right','5px');
        var notify_on_success = $("<input type='checkbox'  name='checkbox3'></input>").css('margin-right','5px');
        var username = that.base_url.split("/")[3]; //fecth username according to url, be aware of url change in production env
        var email_list_for_failure = $("<input type='text' name='text'></input>").attr('value',username + '@paypal.com,').css('margin-left', '12px');
        var email_list_for_success = $("<input type='text' name='text'></input>").attr('value',username + '@paypal.com,');


        var notification_part = $("<div/>")
        .append(inst1)
        .append(notify_on_failure)
        .append($("<label for='checkbox1'>Notify on Failure</label>"))
        .append(email_list_for_failure)
        .append("<br/>")
        .append(notify_on_success)
        .append($("<label for='checkbox3'>Notify on Success</label>"))
        .append(email_list_for_success);

        //Part3 Push to Github
        var inst2 = $("<p>Please check the box if you also want to push the notebook that you have scheduled to github</p>")
        var push_to_git = $("<input type='checkbox'  name='checkbox2'></input>").css('margin-right','5px');
        var github_part  = $("<div/>")
        .append(inst2)
        .append(push_to_git)
        .append($("<label for='checkbox2'>Push to Github</label>"))


        //Integrate
        var dialog_body = $('<div/>').css('display', 'block').css('overflow','auto')
        .append($('<b>Schdule</b>'))
        .append(schedule_part)
        .append($('<hr>').css('border-top','1px dotted'))
        .append($('<b>Email Notification</b>'))
        .append(notification_part)
        .append($('<hr>').css('border-top','1px dotted'))
        .append($('<b>Auto Push to Github</b>'))
        .append(github_part)

        dialog.modal({
        title : "Create Schedule (Beta)",
        body : dialog_body,
        default_button: "Cancel",
        buttons : {
            Cancel: {},
            Schedule : {
                class: "btn-primary",
                click: function() {
                    var emails_failure;
                    if (notify_on_failure.is(':checked')){
                        emails_failure = email_list_for_failure.val();
                    }else{
                        emails_failure = "*";
                    }
                    var emails_success;
                    if (notify_on_success.is(':checked')){
                        emails_success = email_list_for_success.val();
                    }else{
                        emails_success = "*";
                    }
                    if (start_date.val() == undefined || start_time.val() == undefined){
                        alert("Please sepcify the start date and time");
                        return false;
                    }
                    var sttime = start_date.val() + " " + start_time.val() + ":00";
                    var minute = start_time.val().split(":")[1];
                    var hour = start_time.val().split(":")[0];
                    var date = start_date.val().split('-')[2];
                    var now = new Date();
                    var scheduled_time = new Date(sttime.replace(new RegExp('-','g'), '/'));
                    if (scheduled_time < now){
                        alert("Cannot schedule in the past!");
                        return false;
                    }
	                if ($('#end').val() != null){
                        var edtime = parseInt(every_num.val()) * parseInt($('#end').val().split(' ')[0]) + ' ' + every_unit.val();}
                    else{
                        var edtime = parseInt(every_num.val()) + ' ' + every_unit.val();}
                    var ispushed = 'N';
                    var interval = every_num.val() + " " + every_unit.val();
                    var notebookPath= selected[0].path.substr(0,selected[0].path.lastIndexOf('.'));
                    var notebookName = selected[0].name.substr(0,selected[0].name.lastIndexOf('.')).replace(new RegExp(/[`~!@#$%^&*()|+=?;:'",<>\{\}\[\]\\\/ ]/gi, 'g'), '_');
                    var url = utils.url_path_join(that.base_url, '/scheduler/can_schedule');
                    $.get(url + '?notebook_name=' + notebookName, function(res){
                        if (res == 'False'){
                            alert('Cannot schedule more than 5 jobs!');
                            return false;
                        }else if(res == 'Exist'){
                            dialog.modal({
                                title: "Please confirm ...",
                                body:  'You have already scheduled this notebook, are you sure you want to override it?',
                                buttons : {
                                    Cancel: {
                                        click: function(){
                                                return;
                                        }},
                                    Override : {
                                        class: "btn-primary",
                                        click:  function(){
                                                //call delete flask service
                                                $.get('/scheduler/delete?dag_id=' + username + '_' + notebookName, function(){schedule();});
                                        }}
                                    }
                                });
                        }
                        else{
                                schedule();
                        }
                        function schedule(){
                            console.log(notebookName);
                                var settings = {
                                        data:{
                                                'notebook_name': notebookName,
                                                'notebook_path': notebookPath,
                                                'emails_failure': emails_failure,
                                                'emails_success': emails_success,
                                                'sttime': sttime,
                                                'edtime': edtime,
                                                'interval': interval
                                                },
                                        method: 'POST',
                                        success: function(picked){
                                                if(picked == 'True'){
                                                        if (push_to_git.is(':checked')){
                                                                ispushed = 'Y';
                                                                //that.github_selected();//re-enable github selected
                                                        }
                                                        $.get('/scheduler/set_dag?notebook_name=' + notebookName + '&ispushed=' + ispushed + '&interval=' + interval + '&start_time=' + sttime);
                                                        $('a[href=#scheduledjobs]').click().tab('show');
                                                        spin.modal('hide');
                                                }
                                        },
                                        error: function(picked){
                                                spin.modal('hide');
                                                dialog.modal({
                                                        title: 'Schedule Failed!',
                                                        body: $('<div/>').text('Error: something wrong in scheduling, please check your notebook and try again!'),
                                                        buttons:{
                                                                OK:{class: "btn-primary"}
                                                        }
                                                });
                                        }
                                }
                                var url = utils.url_path_join(that.base_url, '/scheduler/create_dag');
                                utils.ajax(url, settings);
                                var spin = dialog.modal({
                                        title: "Scheduling...",
                                        body: $('<div style="text-align:center"><i class="fa fa-spinner fa-spin" style="font-size:100px"></i></div>').append($('<div style="text-align:center"><strong>Your notebook will be scheduled in a few seconds.\nNote: If you do not see your notebook in scheduled jobs, please wait and refresh because scheduler is working on picking up your job.</strong></div>')),
                                });
                            }
                      });
                }
            }
        }
   });


    };


    return {ScheduleOperation: ScheduleOperation};
});
