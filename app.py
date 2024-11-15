from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def main_menu():
    breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
    ]

    return render_template("main_menu.html", breadcrumbs=breadcrumbs)


@app.route("/personal")
def personal():
    breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Личный кабинет", "link": "/personal", "icon": "bi-person"},
    ]

    return render_template("personal.html", breadcrumbs=breadcrumbs)


@app.route("/goods")
def search():
    breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Поиск товара", "link": "/goods", "icon": "bi-search"},
    ]

    return render_template("search.html", breadcrumbs=breadcrumbs)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
