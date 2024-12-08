from flask import Flask
from database import init_mysql
import json

from auth_blueprint import auth_blueprint
from goods_blueprint import goods_blueprint
from main_menu_blueprint import main_menu_blueprint
from defect_blueprint import defect_blueprint
from order_blueprint import order_blueprint
from report_blueprint import report_blueprint
from supply_blueprint import supply_blueprint
from classes import OrderStatus, UserRole

app = Flask(__name__)

with open("db_config.json") as f:
    app.config["db_config"] = json.load(f)

init_mysql(app)


app.register_blueprint(auth_blueprint)
app.register_blueprint(main_menu_blueprint)
app.register_blueprint(goods_blueprint)
app.register_blueprint(defect_blueprint)
app.register_blueprint(order_blueprint)
app.register_blueprint(report_blueprint)
app.register_blueprint(supply_blueprint)


@app.template_filter("status_color")
def status_color_filter(status):
    return OrderStatus.to_color(status)


@app.template_filter("user_role")
def user_role_filter(status):
    return UserRole.to_name(status)


@app.context_processor
def inject_enums():
    return {"UserRole": UserRole, "OrderStatus": OrderStatus}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
