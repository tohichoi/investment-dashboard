
streamlit chart 기능은 3.13 에서 안정적으로 동작하므로 3.13으로 사용해야함

```shell
cd dashbarod
py -V:3.13 -m venv .venv
.\.venv\scripts\activate.ps1
pip install -r .\requirements.txt
python.exe -m pip install --upgrade pip
```

## run

`streamlit run .\index.py`
