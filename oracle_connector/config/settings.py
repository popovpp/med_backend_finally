import os


# Oracle connection parameters
ORACLE_USERNAME = os.environ.get('ORACLE_USERNAME', default='user')
ORACLE_PASSWORD = os.environ.get('ORACLE_PASSWORD', default=1111111111)
ORACLE_CONNECTIONSTRING = os.environ.get('ORACLE_CONNECTIONSTRING', default='http://')

# Oracle procedures
ORACLE_PROC_CHECK_PATIENT = 'solution_med.pkg_lk_virilis.check_patient'
ORACLE_PROC_CREATE_USER_PATIENT = 'solution_med.pkg_lk_virilis.create_user_patient'
ORACLE_PROC_CONFIRM_PATIENT_BY_EMAIL = 'solution_med.pkg_lk_virilis.create_email_confirm_code'
ORACLE_PROC_UDATE_USER_PATIENT = 'solution_med.pkg_lk_virilis.update_user_patient'
ORACLE_PROC_SET_TICKET_PATIENT = 'solution_med.pkg_lk_virilis.set_ticket_patient'
ORACLE_PROC_FREE_TICKET = 'solution_med.pkg_lk_virilis.free_ticket'
ORACLE_PROC_CREATE_PATIENT_SERVICE = 'solution_med.pkg_lk_virilis.create_patient_service'
ORACLE_PROC_UPDATE_PATIENT_SERVICE = 'solution_med.pkg_lk_virilis.update_patient_service'
ORACLE_PROC_CREATE_PAYMENT_FOR_PATSERV = 'solution_med.pkg_lk_virilis.create_payment_for_patserv'
ORACLE_PROC_CONFIRM_PAYMENT = 'solution_med.pkg_lk_virilis.confirm_payment'
ORACLE_PROC_CHANGE_RNUMB_FOR_PATSERV = 'solution_med.pkg_lk_virilis.change_rnumb_for_patserv'
ORACLE_PROC_GET_PATIENT_FILES = 'solution_med.pkg_lk_virilis.get_patient_files'
ORACLE_PROC_GET_LIST_OF_AVALAIBLE_DOCS = 'solution_med.pkg_lk_virilis.get_list_of_available_docs'
ORACLE_PROC_DELETE_PAYMENT='solution_med.pkg_lk_virilis.delete_payment'
ORACLE_PROC_CREATE_EMAIL_PAYSERV_INFO = 'solution_med.pkg_lk_virilis.create_email_patserv_return_info'
ORACLE_PROC_REQUEST_DOCUMENT = 'solution_med.pkg_lk_virilis.request_document'
ORACLE_PROC_GET_LIST_OF_REQUIRED_FILES = 'solution_med.pkg_lk_virilis.get_list_of_requested_files'
ORACLE_PROC_GET_PATIENT_PROTOCOLS = 'solution_med.pkg_lk_virilis.get_patient_protocols'
ORACLE_PROC_P_TEST = 'solution_med.pkg_lk_virilis.p_test'
ORACLE_PROC_ADD_PATIENT_RELATIVE = 'solution_med.pkg_lk_virilis.add_patient_relative'
ORACLE_PROC_GET_PATIENT_BALANCE = 'solution_med.pkg_lk_virilis.get_patient_balance'
ORACLE_PROC_GET_PATIENT_DEBT = 'solution_med.pkg_lk_virilis.get_patient_debt'
ORACLE_PROC_UPDATE_USER_DEFAULT_MC = 'solution_med.pkg_lk_virilis.update_users_default_mc'


REPEATING_OF_ORACLE_PROC = 7
