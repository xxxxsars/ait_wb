import datetime, os, platform, re


def clean_tmp_download():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_path = path + r'\download_folder\\'
    else:
        source_path = path + '/download_folder/'

    yesterday_time = datetime.datetime.now() + datetime.timedelta(days=-1)

    for f in os.listdir(source_path):
        if re.search("^.+\.zip$", f):
            file = os.path.join(source_path, f)
            create_time = datetime.datetime.fromtimestamp(os.path.getmtime(file))

            if create_time < yesterday_time:
                os.remove(file)


if __name__ == "__main__":
    clean_tmp_download()
