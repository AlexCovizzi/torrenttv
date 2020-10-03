import os

os.system("npm run build")
os.system("pipenv run pyinstaller torrenttv.spec")
