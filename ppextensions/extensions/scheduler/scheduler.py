from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from shutil import copyfile
from sqlalchemy import create_engine
from airflow import settings, models
from ppextensions.extensions.extension_logger import extension_logger

import datetime
import configparser
import getpass
import os


CONNECTION_STRING = os.environ["AIRFLOW_METADATA_CONNECTION_STRING"]
AIRFLOW_HOME = os.environ["AIRFLOW_HOME"]
NOTEBOOK_STARTUP_PATH = os.getcwd() + "/"
DAG_TEMPLATE = os.path.dirname(os.path.abspath(__file__)) + "/template/dag_template.py"
VAR_TEMPLATE = os.path.dirname(os.path.abspath(__file__)) + "/template/var_template.conf"
SCHEDULER_STATIC_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/static"


class SchedulerHandler(IPythonHandler):
    session = settings.Session()
    engine = create_engine(CONNECTION_STRING)
    cf = configparser.ConfigParser()

    @staticmethod
    def get_delta(start, interval):
        start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        itv = interval.split(" ")
        delta = datetime.timedelta(**dict([(itv[1], int(itv[0]))]))
        return start, delta

    def dag_info(self, dag_inst):
        interval = dag_inst.schedule_interval
        notebook_name = dag_inst.dag_id.split('_')[1]
        task_id = 'notebook_task'
        task = dag_inst.get_task(task_id)
        start_date = task.start_date
        end_date = task.end_date
        task_instances = task.get_task_instances(self.session, start_date=start_date, end_date=end_date)
        if len(task_instances) != 0:
            for ti in task_instances[::-1]:
                dag_run = dag_inst.get_dagrun(execution_date=ti.execution_date)
                if dag_run.external_trigger is False:
                    last_run_time = ti.execution_date + interval
                    last_run_status = ti.state
                    last_run_duration = ti.duration
                    next_run_time = last_run_time + interval
                    return [notebook_name, last_run_time, last_run_status, last_run_duration, next_run_time]
            return [notebook_name, 'N/A', 'N/A', 'N/A', task.start_date + interval]
        else:
            return [notebook_name, 'N/A', 'N/A', 'N/A', task.start_date + interval]

    def get_dag(self, username):
        dag_bag = models.DagBag(settings.DAGS_FOLDER)
        dag_instances = [dag_inst for (dag_id, dag_inst) in dag_bag.dags.items() if dag_inst.owner == username]
        dags = []
        for dag_inst in dag_instances:
            dags.append(self.dag_info(dag_inst))
        return dags

    def delete_dag(self, notebook_name):
        dag_id = getpass.getuser() + "_" + notebook_name
        dag_path = AIRFLOW_HOME + "/dags/dag_" + dag_id + ".py"
        var_path = AIRFLOW_HOME + "/variables/var_" + dag_id + ".conf"
        with self.engine.begin() as con:
            for t in ["dag", "xcom", "task_instance", "sla_miss", "log", "job", "dag_run",  "task_fail", "dag_stats"]:
                query = "delete from {} where dag_id='{}'".format(t, dag_id)
                con.execute(query)
        os.remove(dag_path)
        os.remove(var_path)

    def extend_dag(self, dag_id):
        var_path = AIRFLOW_HOME + '/variables/var_' + dag_id + '.conf'
        self.cf.read(var_path)
        start = datetime.strptime(self.cf.get("config", "start"), "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(self.cf.get("config", "end"), "%Y-%m-%d %H:%M:%S")
        today = datetime.today()
        today_plus_two_weeks = datetime(today.year, today.month, today.day) + datetime.timedelta(days=15)
        if today_plus_two_weeks < end:
            return "This job is not eligible for extending!"
        extended_end = end + (end - start)
        self.cf.set("config", "end", extended_end)

    def configure(self, username, dag_id, notebook_path, emails_failure, emails_success, start, runs, interval):
        dag_path = AIRFLOW_HOME + "/dags/dag_" + dag_id + ".py"
        var_path = AIRFLOW_HOME + "/variables/var_" + dag_id + ".conf"
        copyfile(DAG_TEMPLATE, dag_path)
        copyfile(VAR_TEMPLATE, var_path)
        self.cf.read(var_path)
        start, delta = self.get_delta(start, interval)
        start -= delta
        end = start + int(runs) * delta
        self.cf.set("config", "dag_id", dag_id)
        self.cf.set("config", "username", username)
        self.cf.set("config", "interval", interval)
        self.cf.set("config", "notebook_path", notebook_path)
        self.cf.set("config", "start", str(start))
        self.cf.set("config", "end", str(end))
        self.cf.set("config", "emails_failure", emails_failure)
        self.cf.set("config", "emails_success", emails_success)
        self.cf.write(open(var_path, "w"))

class CreateDagHandler(SchedulerHandler):
    def post(self):
        notebook_name = self.get_argument('notebook_name')
        notebook_path = self.get_argument('notebook_path')
        emails_failure = self.get_argument('emails_failure')
        emails_success = self.get_argument('emails_success')
        start = self.get_argument('start')
        runs = self.get_argument('runs')
        interval = self.get_argument('interval')
        username = getpass.getuser()
        dag_id = username + '_' + notebook_name
        notebook_path = NOTEBOOK_STARTUP_PATH + notebook_path
        self.configure(username, dag_id, notebook_path, emails_failure, emails_success, start, runs, interval)
        self.set_status(204, "")


class GetDagHandler(SchedulerHandler):
    def get(self):
        dag_list = self.get_dag(getpass.getuser())
        base_url = self.get_argument('base_url')
        self.render('daginfo.html', base_url=base_url, dag_list=dag_list)


class DeleteDagHandler(SchedulerHandler):
    def post(self):
        notebook_name = self.get_argument("notebook_name")
        try:
            self.delete_dag(notebook_name)
        except Exception as e:
            extension_logger.logger.error(str(e))
            self.set_status(400)
            self.finish(str(e))
        self.set_status(204, "")


class EditDagHandler(SchedulerHandler):
    def get(self):
        notebook_name = self.get_argument("notebook_name")
        dag_id = getpass.getuser() + "_" + notebook_name
        var_path = AIRFLOW_HOME + '/variables/var_' + dag_id + '.conf'
        self.cf.read(var_path)
        dag_id = self.cf.get("config", "dag_id")
        interval = self.cf.get("config", "interval")
        start = self.cf.get("config", "start")
        start, delta = self.get_delta(start, interval)
        start += delta
        emails_failure = self.cf.get("config", "emails_failure")
        emails_success = self.cf.get("config", "emails_success")
        base_url = self.get_argument("base_url")
        configuration = [dag_id, start, interval, emails_failure, emails_success, base_url]
        self.render("editdag.html", configuration=configuration)

    def post(self):
        dag_id = self.cf.get("config", "dag_id")
        notebook_path = self.cf.get("config", "notebook_path")
        start = self.get_argument('start')
        freq = self.get_argument('freq')
        unit = self.get_argument('unit')
        runs = self.get_argument('runs')
        interval = freq + ' ' + unit
        emails_failure = self.get_argument("emails_failure")
        emails_success = self.get_argument("emails_success")
        username = getpass.getuser()
        extension_logger.logger.info(start)
        self.configure(username, dag_id, notebook_path, emails_failure, emails_success, start, runs, interval)
        self.set_status(204, "")


class CheckDagHandler(SchedulerHandler):
    def get(self):
        dag_bag = models.DagBag(settings.DAGS_FOLDER)
        notebook_name = self.get_argument("notebook_name")
        dag_id = getpass.getuser() + "_" + notebook_name
        if dag_id in dag_bag.dags:
            self.finish("True")
        else:
            self.finish("False")


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
        (r'/scheduler/delete_dag', DeleteDagHandler),
        (r'/scheduler/edit_dag', EditDagHandler),
        (r'/scheduler/check_dag', CheckDagHandler)
    ]
    web_app.settings['template_path'] = SCHEDULER_STATIC_FILE_PATH 
    base_url = web_app.settings['base_url']
    handlers = [(url_path_join(base_url, h[0]), h[1]) for h in handlers]

    host_pattern = '.*$'
    web_app.add_handlers(host_pattern, handlers)
