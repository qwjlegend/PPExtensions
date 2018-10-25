from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import imp
from tornado.template import Template
from shutil import copyfile
from dateutil.relativedelta import relativedelta
import getpass

import datetime
import os
import json
import time
from sqlalchemy import create_engine

CONNECTION_STRING = "mysql+mysqlconnector://root:123456@jupy-weqian.pp-devcos-cdp-bdpe.us-central1.gcp.dev.paypalinc.com:3306/airflow_jupytercon"
AIRFLOW_HOME_MOUNT = "/Users/weqian/Documents/Work/Dev/airflow/airflow_home_mount/"
DAG_TEMPLATE = "/Users/weqian/Documents/Work/Dev/airflow/conf/dag_template.py"   #"/etl/LVS/dmetldata11/scaas/pp_notebooks/conf/dag_template.py"
VAR_TEMPLATE = "/Users/weqian/Documents/Work/Dev/airflow/conf/var_template.py" #"/etl/LVS/dmetldata11/scaas/pp_notebooks/conf/var_template.py"

class SchedulerHandler(IPythonHandler):
    engine = create_engine(CONNECTION_STRING)

    # def initialize(self, notebook_name, notebook_path, username, email_list_failure, email_list_success, start_time, end_time, interval):
    #         self.notebook_name = notebook_name
    #         self.notebook_path = notebook_path
    #         self.username = username
    #         self.email_list_failure = email_list_failure
    #         self.email_list_success = email_list_success
    #         self.start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    #         itv_num, itv_unit = interval.split(' ')
    #         if itv_unit == 'hours':
    #             delta = datetime.timedelta(hours=int(itv_num))
    #             self.interval = "timedelta(hours={})".format(int(itv_num))
    #         elif itv_unit == 'days':
    #             delta = datetime.timedelta(days=int(itv_num))
    #             self.interval = "timedelta(days={})".format(int(itv_num))
    #         elif itv_unit == 'months':
    #             adjusttime = self.start_time + relativedelta(months=int(itv_num))
    #             delta = adjusttime - self.start_time
    #             self.interval = "timedelta(days={})".format(int(str(adjusttime - self.start_time).split('days')[0].strip()))
    #         elif itv_unit == 'weeks':
    #             delta = datetime.timedelta(weeks=int(itv_num))
    #             self.interval = "timedelta(weeks={})".format(int(itv_num))
    #         self.start_time -= delta
    #
    #         ed_num, ed_unit = end_time.split(' ')
    #         if ed_unit == 'hours':
    #             self.end_time = self.start_time + datetime.timedelta(hours=int(ed_num))
    #         elif ed_unit == 'days':
    #             self.end_time = self.start_time + datetime.timedelta(days=int(ed_num))
    #         elif ed_unit == 'months':
    #             self.end_time = self.start_time + relativedelta(months=int(ed_num))
    #         elif ed_unit == 'weeks':
    #             self.end_time = self.start_time + datetime.timedelta(weeks=int(ed_num))

    @staticmethod
    def init_dag(dag_desti):
        copyfile(DAG_TEMPLATE, dag_desti)

    @staticmethod
    def init_var(var_desti, notebook_name, notebook_path, username, email_list_failure, email_list_success, start_time, end_time, interval):
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        itv_num, itv_unit = interval.split(' ')
        if itv_unit == 'hours':
            delta = datetime.timedelta(hours=int(itv_num))
            interval = "timedelta(hours={})".format(int(itv_num))
        elif itv_unit == 'days':
            delta = datetime.timedelta(days=int(itv_num))
            interval = "timedelta(days={})".format(int(itv_num))
        elif itv_unit == 'months':
            adjusttime = start_time + relativedelta(months=int(itv_num))
            delta = adjusttime - start_time
            interval = "timedelta(days={})".format(int(str(adjusttime - start_time).split('days')[0].strip()))
        elif itv_unit == 'weeks':
            delta = datetime.timedelta(weeks=int(itv_num))
            interval = "timedelta(weeks={})".format(int(itv_num))
        start_time -= delta

        ed_num, ed_unit = end_time.split(' ')
        if ed_unit == 'hours':
            end_time = start_time + datetime.timedelta(hours=int(ed_num))
        elif ed_unit == 'days':
            end_time = start_time + datetime.timedelta(days=int(ed_num))
        elif ed_unit == 'months':
            end_time = start_time + relativedelta(months=int(ed_num))
        elif ed_unit == 'weeks':
            end_time = start_time + datetime.timedelta(weeks=int(ed_num))

        with open(VAR_TEMPLATE, "r") as f:
            filedata = f.readlines()
        with open(var_desti, "w") as d:
            for line in filedata:
                if len(line.strip()) != 0:
                    d.write(line)
                else:
                    d.write("        config['notebook_name'] = '{}'".format(notebook_name))
                    d.write("\n")
                    d.write("        config['interval'] = {}".format(interval))
                    d.write("\n")
                    d.write("        config['notebook_path'] = '{}'".format(notebook_path))
                    d.write("\n")
                    d.write("        config['start_time'] = '{}'".format(start_time))
                    d.write("\n")
                    d.write("        config['end_time'] = '{}'".format(end_time))
                    d.write("\n")
                    d.write("        config['username'] = '{}'".format(username))
                    d.write("\n")
                    d.write("        config['email_list_failure'] = {}".format(email_list_failure))
                    d.write("\n")
                    d.write("        config['email_list_success'] = {}".format(email_list_success))
                    d.write("\n")

    def check_dag_exist(self, dag):
        username = getpass.getuser()
        dag = username + '_' + dag
        with self.engine.begin() as con:
            cursor = con.execute("select dag_id from dag where dag_id='{}';".format(dag))
            res = cursor.fetchall()
            if len(res) == 0:
                return False
            return True

    def find_dag_desti(self, dag):
        dag_desti = AIRFLOW_HOME_MOUNT + "dags/" + "dag_" + dag + ".py"
        var_desti = AIRFLOW_HOME_MOUNT + "variables/" + "var_" + dag + ".py"
        return dag_desti, var_desti


    def create_dag(self, notebook_name, notebook_path, emails_failure, emails_success, start_time, end_time, interval):
        username = getpass.getuser()
        notebook_name = username + '_' + notebook_name
        notebook_path = '/x/home/' + username + '/' + notebook_path + '.ipynb'
        self.configure(username, notebook_name, notebook_path, emails_failure, emails_success, start_time, end_time, interval)

    def get_dag(self, username):
        with self.engine.begin() as con:
            cursor1 = con.execute("select dag_id from dag where owners = '{}'".format(username))
            res = cursor1.fetchall()
            dags = []
            for dag in res:
                cursor2 = con.execute("select `ispushed`, `interval`, `starttime` from dag_info where dag_id = '{}'".format(dag[0]))
                daginfo = cursor2.fetchone()
                if daginfo:
                    ispushed, interval, start_time = daginfo
                else:
                    continue
                cursor3 = con.execute("select dag_id, date_add(execution_date, interval {}), state, duration, "
                                      "date_add(execution_date, interval 2 * {}), '{}' from task_instance "
                                      "where dag_id = '{}' order by execution_date desc limit 1;".format(
                                        interval.strip('s'), interval.strip('s'), ispushed, dag[0]))
                dagdetail = cursor3.fetchone()
                if dagdetail is None:
                    cursor4 = con.execute("select date_add('{}', interval {});".format(
                        start_time, interval.strip('s')))
                    nextrun = cursor4.fetchone()[0]
                    dagdetail = (dag[0], 'N/A', 'N/A', 'N/A', nextrun, ispushed)
                dags.append(dagdetail)
        return dags

    def set_dag(self, dag_id, ispushed, interval, start_time):
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        with self.engine.begin() as con:
            con.execute("insert into dag_info values('{}','{}', '{}', date_sub('{}', interval {})) on duplicate key "
                        "update `ispushed` = '{}', `interval` = '{}',`starttime` = date_sub('{}', interval {});".format(
                        dag_id, ispushed, interval, start_time, interval.strip('s'), ispushed, interval, start_time,
                        interval.strip('s')))

    def delete_dag(self, dag):
        dag_desti, var_desti = self.find_dag_desti(dag)
        with self.engine.begin() as con:
            for t in ["dag_info", "dag", "xcom", "task_instance", "sla_miss", "log", "job", "dag_run",  "task_fail", "dag_stats"]:
                query = "delete from {} where dag_id='{}'".format(t, dag)
                con.execute(query)
        os.remove(dag_desti)
        os.remove(var_desti)


    def get_conf(self, dagid):
        module_path = AIRFLOW_HOME_MOUNT + 'variables/var_' + dagid + '.py'
        config_module = imp.load_source('mymod', module_path)
        conf_instance = config_module.Config()
        conf = conf_instance.getConf()
        return conf


    def extend_dag(self, dagid):
        module_path = AIRFLOW_HOME_MOUNT + 'variables/var_' + dagid + '.py'
        config_module = imp.load_source('mymod', module_path)
        conf_instance = config_module.Config()
        conf = conf_instance.getConf()
        notebook_name = conf['notebook_name']
        notebook_path = conf['notebook_path']
        username = conf['username']
        email_list_failure = conf['email_list_failure']
        email_list_success = conf['email_list_success']
        emails_failure = ','.join(email_list_failure)
        emails_success = ','.join(email_list_success)
        interval = conf['interval']
        start_time = datetime.datetime.strptime(conf['start_time'], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(conf['end_time'], "%Y-%m-%d %H:%M:%S")
        today = datetime.datetime.today()
        today_plus_two_weeks = datetime.datetime(today.year, today.month, today.day) + datetime.timedelta(days=15)
        if today_plus_two_weeks < end_time:
            return "This job is not eligible for extending!"
        start = str(start_time + interval)
        extend_length = end_time - start_time
        extend_from_start = str(2 * extend_length).split(',')[0]
        itv = self.get_dag_interval(dagid)
        self.configure(username, notebook_name, notebook_path, emails_failure, emails_success, start, extend_from_start, itv)



    def update_dag(self, dag_id, interval, start_time):
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        with self.engine.begin() as con:
            con.execute("update dag_info set `interval` = '{}', `starttime` = date_sub('{}', interval {}) where "
                        "`dag_id` = '{}';".format(interval, start_time, interval.strip('s'), dag_id))

    def get_dag_interval(self, dag_id):
        with self.engine.begin() as con:
            cursor = con.execute("select `interval` from dag_info where `dag_id` = '{}'".format(dag_id))
            dag_itv = cursor.fetchone()
            if dag_itv is not None:
                return dag_itv[0]
            else:
                return None

    def can_schedule(self, username, notebook_name):
        return "True"
        notebook_name = username + "_" + notebook_name
        with self.engine.begin() as con:
            cursor = con.execute("select dag_id from dag where owners='{}';".format(username))
            res = cursor.fetchall()
            dags = [dag[0] for dag in res]
            if notebook_name in dags:
                return "Exist"
            elif len(dags) >= 5 and username not in ["weqian", "pkanamarlapudi", "pkasinathan", "romehta"]:
                return "False"
            return "True"

    @staticmethod
    def is_whitelist(username):
        return True
        with open(AIRFLOW_HOME_MOUNT + "whitelist/whitelist.txt") as f:
            names = [name.strip() for name in f.readlines()]
            if username in names:
                return True
            return False

    @staticmethod
    def add_to_whitelist(username):
        with open(AIRFLOW_HOME_MOUNT + "whitelist/whitelist.txt", "a") as f:
            f.write(username + "\n")

    def configure(self, username, notebook_name, notebook_path, emails_failure, emails_success, start_time, end_time, interval):
        email_list_failure = [a.strip() for a in emails_failure.split(',') if a] if emails_failure != "*" else []
        email_list_success = [a.strip() for a in emails_success.split(',') if a] if emails_failure != "*" else []
        dag_desti = AIRFLOW_HOME_MOUNT + "dags/dag_" + notebook_name + ".py"
        var_desti = AIRFLOW_HOME_MOUNT + "variables/var_" + notebook_name + ".py"
        self.init_var(var_desti, notebook_name, notebook_path, username, email_list_failure, email_list_success, start_time, end_time, interval)
        self.init_dag(dag_desti)


class CreateDagHandler(SchedulerHandler):
    def post(self):
        notebook_name = self.get_argument('notebook_name')
        notebook_path = self.get_argument('notebook_path')
        emails_failure = self.get_argument('emails_failure')
        emails_success = self.get_argument('emails_success')
        start_time = self.get_argument('sttime')
        end_time = self.get_argument('edtime')
        interval = self.get_argument('interval')
        self.create_dag(notebook_name, notebook_path, emails_failure, emails_success, start_time, end_time, interval)
        count = 0
        while count <= 15:
            time.sleep(1)
            if self.check_dag_exist(notebook_name):
                break
            count += 1
        self.finish("True")


class GetDagHandler(SchedulerHandler):
    def get(self):
        daglist = self.get_dag(getpass.getuser())
        self.render('daginfo.html', daglist=daglist)


class SetDagHandler(SchedulerHandler):
    def get(self):
        notebook_name = self.get_argument("notebook_name")
        start_time = self.get_argument("start_time")
        ispushed = self.get_argument("ispushed")
        interval = self.get_argument("interval")
        dag_id = getpass.getuser() + '_' + notebook_name
        self.set_dag(dag_id, ispushed, interval, start_time)
        self.set_status(204, "")
        #self.redirect((url_for('getdaginfo', _external=True, _scheme='https'))) #find url_for equivalent


class DeleteDagHandler(SchedulerHandler):
    def post(self):
        dag_id = self.get_argument("dag_id")
        self.delete_dag(dag_id)
        self.set_status(204, "")


class EditDagHandler(SchedulerHandler):
    def get(self):
        dag_id = self.get_argument("dag_id")
        conf = self.get_conf(dag_id)
        email_list_failure = conf['email_list_failure']
        email_list_success = conf['email_list_success']
        emails_failure = ','.join(email_list_failure)
        emails_success = ','.join(email_list_success)
        interval = conf['interval']
        start_time = (datetime.datetime.strptime(conf['start_time'], "%Y-%m-%d %H:%M:%S") + interval).strftime("%Y-%m-%d %H:%M")
        itv = self.get_dag_interval(dag_id)
        configuration = [dag_id, start_time, itv, emails_failure, emails_success]
        self.render("editdag.html", configuration=configuration)

    def post(self):
        dag_id = self.get_argument("dag_id")
        conf = self.get_conf(dag_id)
        notebook_name = conf['notebook_name']
        notebook_path = conf['notebook_path']
        start_time = self.get_argument('start')
        freq = self.get_argument('freq')
        unit = self.get_argument('unit')
        end_time = self.get_argument('end')
        interval = freq + ' ' + unit
        emails_failure = self.get_argument("emailfailure")
        emails_success = self.get_argument("emailsuccess")
        self.configure(getpass.getuser(), notebook_name, notebook_path, emails_failure, emails_success, start_time, end_time,interval)
        self.update_dag(notebook_name, interval, start_time)
        self.set_status(204, "")


class ExtendDagHandler(SchedulerHandler):
    def get(self):
        dag_id = self.get_argument("dag_id")
        conf = self.get_conf(dag_id)
        notebook_name = conf['notebook_name']
        notebook_path = conf['notebook_path']
        username = conf['username']
        email_list_failure = conf['email_list_failure']
        email_list_success = conf['email_list_success']
        emails_failure = ','.join(email_list_failure)
        emails_success = ','.join(email_list_success)
        interval = conf['interval']
        start_time = datetime.datetime.strptime(conf['start_time'], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(conf['end_time'], "%Y-%m-%d %H:%M:%S")
        today = datetime.datetime.today()
        today_plus_two_weeks = datetime.datetime(today.year, today.month, today.day) + datetime.timedelta(days=15)
        if today_plus_two_weeks < end_time:
            self.finish("This job is not eligible for extending!")
        else:
            start = str(start_time + interval)
            extend_length = end_time - start_time
            extend_from_start = str(2 * extend_length).split(',')[0]
            itv = self.get_dag_interval(dag_id)
            self.configure(username, notebook_name, notebook_path, emails_failure, emails_success, start, extend_from_start,itv)
            self.finish("Your job has been extended for " + str(extend_length).split(',')[0])

class IsWhitelistHandler(SchedulerHandler):
    def get(self):
        if self.is_whitelist(getpass.getuser()):
            self.finish("True")
        else:
            self.finish("False")


class AddToWhitelistHandler(SchedulerHandler):
    def get(self):
        self.add_to_whitelist(getpass.getuser())
        self.finish(None)

class CanScheduleHandler(SchedulerHandler):
    def get(self):
        notebook_name = self.get_argument("notebook_name")
        res = self.can_schedule(getpass.getuser(), notebook_name)
        self.finish(res)

class PrivateGitTokenHandler(IPythonHandler):
    def get(self):
        self.finish("Token generated successfully!")

def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app

    handlers = [
        (r'/scheduler/create_dag', CreateDagHandler),
        (r'/scheduler/get_dag', GetDagHandler),
        (r'/scheduler/set_dag', SetDagHandler),
        (r'/scheduler/delete_dag', DeleteDagHandler),
        (r'/scheduler/edit_dag', EditDagHandler),
        (r'/scheduler/extend_dag', ExtendDagHandler),
        (r'/scheduler/is_whitelist', IsWhitelistHandler),
        (r'/scheduler/add_to_whitelist', AddToWhitelistHandler),
        (r'/scheduler/can_schedule', CanScheduleHandler),
    ]
    web_app.settings['template_path'] = '/Users/weqian/Documents/Work/Dev/Paypalnotebooks/nbextension/static'
    base_url = web_app.settings['base_url']
    handlers = [(url_path_join(base_url, h[0]), h[1]) for h in handlers]

    host_pattern = '.*$'
    web_app.add_handlers(host_pattern, handlers)
