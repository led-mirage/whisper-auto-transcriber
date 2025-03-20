create-version-file version.yaml --outfile version.txt
pyinstaller --onefile --ico assets/app.ico --name audioscribe src/main.py --version-file=version.txt
