from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

#.\.venv\Scripts\Activate.ps1
#uv run --python 3.12 --with-requirements requirements.txt flask --app run.py run --debug
