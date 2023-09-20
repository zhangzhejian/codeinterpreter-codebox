import os
ENV_FLAG = os.environ.get('ENV_FLAG')
APP_ID=os.environ.get('APP_ID')
APP_SECRET= os.environ.get('APP_SECRET')

TCP_SERVICE_PORT=8000

allowed_tokens = [
    'zhejianzhang'
]

# codebox_root_path='/Users/zhejianzhang/PrivateProject/codebox_server_code/'
codebox_root_path = os.environ.get('CODEBOX_ROOT_PATH')
input_code_path = '/input_code/'
upload_file_path='/upload/'
output_file_path='/output_file/'
log_file_path='/logs/'

codebox_error_log_title = 'Codebox Error Log:\n\n'

