import re


# set parameter regex find input id
set_parameter_arg= re.compile(r'arg_([0-9A]+)_(.+)')
set_parameter_other = re.compile(r"^\w+_([0-9A]{6})$")


# modify error message compare
modify_error_message = re.compile(r".+(no valid.+|.+error|.+only allow.+).+")


# form regex
input_task_id = re.compile(r"^[0-2][0-9A]\d{2}$")
input_argument = re.compile(r"[^\w|_]+")