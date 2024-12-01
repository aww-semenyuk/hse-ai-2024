```sh
sudo apt install python3.10
sudo apt install python3-pip
python3.10 -m pip install -U virtualenv
virtualenv --python="/usr/bin/python3.10" .venv
source .venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
python app.py
```
