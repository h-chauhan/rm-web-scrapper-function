getParams = lambda type: {
    'loginUrl': 'http://tnp.dtu.ac.in/rm_2016-17/intern/intern_login',
    'username_field': 'intern_student_username_rollnumber',
    'password_field': 'intern_student_password',
    'notifsUrl': 'http://tnp.dtu.ac.in/rm_2016-17/intern/intern_student',
    'jobsUrl': 'http://tnp.dtu.ac.in/rm_2016-17/intern/intern_student/job_openings',
    'notifications_table': 'rm-internship-notifications',
    'jobs_table': 'rm-internship-jobs',
} if type == 'internship' else {
    'loginUrl': 'http://tnp.dtu.ac.in/rm_2016-17/login',
    'username_field': 'student_username_rollnumber',
    'password_field': 'student_password',
    'notifsUrl': 'http://tnp.dtu.ac.in/rm_2016-17/student',
    'jobsUrl': 'http://tnp.dtu.ac.in/rm_2016-17/student/job_openings/',
    'notifications_table': 'rm-placement-notifications',
    'jobs_table': 'rm-placement-jobs'
}
