from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from datetime import timedelta, datetime, date
import imp
import os

surfix = "_".join(os.path.splitext(os.path.basename(__file__))[0].split('_')[1:])
module_path = '/etl/LVS/dmetldata11/scaas/scheduler/airflow_home_mount/variables/var_' + surfix + '.py'
config_module = imp.load_source('mymod', module_path)
conf_instance = config_module.Config()
CONF = conf_instance.getConf()
start_time = CONF['start_time']
start_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
end_time = CONF['end_time']
end_date = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
username = CONF['username']
notebook_name = CONF['notebook_name']
notebook_path = CONF['notebook_path']
interval = CONF['interval']
email_list_failure = CONF['email_list_failure']
email_list_success = CONF['email_list_success']
email_on_failure = len(email_list_failure) != 0 and len(email_list_failure[0]) != 0
email_on_success = len(email_list_success) != 0 and len(email_list_success[0]) != 0

default_args = {
    'owner': username,
    'depends_on_past': False,
    'start_date': start_date,
    'end_date': end_date,
    'email': email_list_failure,
    'email_on_failure': email_on_failure,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
    'catchup': False,
}


dag = DAG(
    notebook_name,
    default_args=default_args,
    schedule_interval=interval)

bash = '''sudo su - {} -c 'jupyter nbconvert "{}" --to notebook --inplace --ClearOutputPreprocessor.enabled=True; python /etl/LVS/dmetldata11/scaas/scheduler/airflow_home_mount/nbexecution_operator.py "{}"' '''.format(username, notebook_path, notebook_path)

exec_operator = BashOperator(
    task_id='notebook_task',
    bash_command=bash,
    dag=dag
)
if email_on_success:
    html_content = '''
    <html>
   <table border="0" cellspacing="0" cellpadding="0" width="853">
      <tbody>
         <tr>
            <td width="817" colspan="6" valign="top">
               <p align="center">
               <p><img width="800" height="80" src="https://lh3.googleusercontent.com/GQwsVdDCYN7Y536ze_BCVFz-VVDbHWeCIjRC4iU2DSs6Ms6UNXQF4AHEwZDUe9rqtoh1-FjDPLiJIY8dGW1BMyZijG6ruoK2qQBITRni6ECk6s3hBtyBx_-H2rpm3AB7GorB01N0ksk=w1440-h144-no" alt="Notebooks-Image"></p>
               <p>
               </p>
               </p>
            </td>
            <td width="36">
               <p>
               </p>
            </td>
         </tr>
         <tr>
            <td width="41">
               <p>
          <p>
          </p>
          </p>
       </td>
       <td style="width: 273.85pt; padding: 0in 20.15pt 0in 0.1in;" colspan="2" width="365">
          <p style="margin: 0in 0in 0.0001pt; font-size: 11pt; font-family: Calibri, sans-serif;"><span style="font-size: 12pt; font-family: 'PayPal Sans Big Light', sans-serif; color: #5a5b5d;">&nbsp;</span></p>
          <p style="margin: 0in 0in 0.0001pt; font-size: 11pt; font-family: Calibri, sans-serif;"><span style="font-size: 15pt; font-family: 'PayPal Sans Big Light', sans-serif; color: #d32464; letter-spacing: 0.75pt;"> Your scheduled notebook job {} has completed successfully. </span></p>
       </td>
       <td width="362" valign="top">
          <p align="right">
          <p>
          </p>
          </p>
       </td>
       <td width="48" colspan="2">
          <p>
          <p>
          </p>
          </p>
       </td>
       <td width="36">
          <p>
          </p>
       </td>
    </tr>
    <tr>
       <td width="817" colspan="6" valign="top">
          <p align="center">
             <img
                width="800"
                height="1"
                src="cid:image002.jpg@01D37591.33C9B080"
                />
          <p>
          </p>
          </p>
       </td>
       <td width="36">
          <p>
          </p>
       </td>
    </tr>
    <tr>
       <td width="42" colspan="2" valign="top">
          <p>
          <p>
          </p>
          </p>
       </td>
       <td width="762" colspan="3" valign="top">
          <table border="0" cellspacing="0" cellpadding="0" width="740">
             <tbody>
                <tr>
                <tr>
                   <td width="817" colspan="6" valign="top">
                      <p align="center">
                         <img
                            width="800"
                            height="1"
                            id="Picture_x0020_2"
                            src="cid:image002.jpg@01D37591.33C9B080"
                            alt="Header_102215_Artboard 1 copy 16"
                            />
                      <p>
                      </p>
                      </p>
                   </td>
                </tr>
                <td style="width: 554.9pt; padding: 0in 5.4pt;" width="740">
                <p style="margin: 0in 4pt 0.0001pt 0in; font-size: 11pt; font-family: Calibri, sans-serif;"><span style="font-size: 12pt; font-family: 'PayPal Sans Big Light', sans-serif; color: #5a5b5d;">For your information, the job schedule details are <a href="{}{}">[here]</a>.</span></p>
                            <br/>
                            <p style="margin: 0in 0in 0.0001pt; font-size: 11pt; font-family: Calibri, sans-serif;">Please reach out to <a style="color: #954f72; text-decoration: underline;" href="mailto:help-notebooks@paypal.com?subject=PayPal%20Notebooks%20Launch:%20Need%20more%20info"><span style="color: #0b4cb4;">help-notebooks@paypal.com</span></a> or </span><img border="0" width="20" height="20" src="https://lh3.googleusercontent.com/K31rwf_q1jRLDigd3NGgsjQVbw-HYdzyW6zsoM3pzhx3sS-Tincrr3_4FK-E9h-weK9eYsihxPDJdoDpOlphto0kRqfWDnwdDdPoA3XrnZgjT16j3RSOf2qb45_fRgWS0jZU1lR8oko=w41-h42-no" alt="Notebooks-Image"><span style="font-size: 12pt; font-family: 'Calibri Light', sans-serif; color: #5a5b5d;">&nbsp;</span><span style="font-size: 12pt; font-family: 'PayPal Sans Big Light', sans-serif; color: #5a5b5d;"><a style="color: #954f72; text-decoration: underline;" href="https://paypal.slack.com/archives/help-notebooks"><span style="color: #0b4cb4;">#help-notebooks</span></a> if you have any questions or concerns.</span></p>
    <p style="margin: 0in 0in 0.0001pt; font-size: 11pt; font-family: Calibri, sans-serif;"><span style="font-size: 12pt; font-family: 'PayPal Sans Big Light', sans-serif; color: #5a5b5d;">&nbsp;</span></p>
                            <p style="margin: 0in 0in 0.0001pt; font-size: 11pt; font-family: Calibri, sans-serif;"><span style="font-size: 12pt; font-family: 'Calibri Light', sans-serif; color: #5a5b5d;">Thank you,</span></p>
                            <p style="margin: 0in 0in 0.0001pt; font-size: 11pt; font-family: Calibri, sans-serif;"><span style="font-size: 12pt; font-family: 'Calibri Light', sans-serif; color: #5a5b5d;">PayPal Notebooks Team</span></p>
                         </td>
                         </tr>
                      </tbody>
                   </table>
                </td>
                <td width="49" colspan="2" valign="top">
                   <p>
                   <p>
                   </p>
                   </p>
                </td>
             </tr>
             <tr>
                <td width="817" colspan="6" valign="top">
                   <p align="center">
                      <p><img border="0" width="800" height="1" src="https://lh3.googleusercontent.com/ZIs5iBp6OFoW0FfU9u_G9N0bsfGXrN-xQBKESzclEXMSP99vpCxvRYVfMZ-plFJbitSVUyRNB62gC8hVKAEt6xm-E8l5Adx-3erwN_ts34vQyBjrrPlKNt8T-O3gMjtAOQ1k2ux0Jd4=w1440-h25-no" alt="Notebooks-Image"></p>
                   <p>
                   </p>
                   </p>
                </td>
                <td width="36">
                   <p>
                   </p>
                </td>
             </tr>
             <tr>
                <td width="41" valign="top">
                   <p>
                   <p>
                   </p>
                   </p>
                </td>
                <td width="727" colspan="3">
                   <p align="center">
                       2018 Confidential &amp; Proprietary For Employees Only
                   <p>
                   </p>
                   </p>
                </td>
                <td width="48" colspan="2" valign="top">
                   <p>
                   <p>
                   </p>
                   </p>
                </td>
                <td width="36">
                   <p>
                   </p>
                </td>
             </tr>
             <tr>
                <td width="817" colspan="6" valign="top">
                   <p align="center">
                      <p><img border="0" width="800" height="20" src="https://lh3.googleusercontent.com/ZIs5iBp6OFoW0FfU9u_G9N0bsfGXrN-xQBKESzclEXMSP99vpCxvRYVfMZ-plFJbitSVUyRNB62gC8hVKAEt6xm-E8l5Adx-3erwN_ts34vQyBjrrPlKNt8T-O3gMjtAOQ1k2ux0Jd4=w1440-h25-no" alt="Notebooks-Image"></p>
                   <p>
                   </p>
                   </p>
                </td>
             </tr>
             <tr height="0">
                <td width="61">
                </td>
                <td width="1">
                </td>
                <td width="352">
                </td>
                <td width="380">
                </td>
                <td width="34">
                </td>
                <td width="13">
                </td>
                <td width="13">
                </td>
             </tr>
          </tbody>
       </table>
       <p>
       <p>
       </p>
       </p>
       <p>
       <p>
       </p>
       </p>
    </html>
        '''.format(notebook_name,
                   "https://engineering.paypalcorp.com/notebooks/services/naas_airflow_webserver/admin/airflow/graph?dag_id=",
                   notebook_name)
    email_operator = EmailOperator(
        task_id='email_task',
        to=email_list_success,
        subject='{} completed successfully'.format(notebook_name),
        dag=dag,
        html_content=html_content
    )
    email_operator.set_upstream(exec_operator)