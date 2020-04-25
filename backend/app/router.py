from api.add_grow import add_grow_bp
from api.favorit_product import favorit_product_bp
from api.get_label import get_label_bp

from personal_area.auth import auth_bp
from personal_area.logout import logout_bp
from personal_area.registration import registration_bp
from personal_area.personal_area import personal_area_bp
from personal_area.cart import cart_bp
from personal_area.cart import order_bp


def routers(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(personal_area_bp)
    app.register_blueprint(add_grow_bp)
    app.register_blueprint(favorit_product_bp)
    app.register_blueprint(get_label_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    return True


def csrf_exempt(csrf):
    csrf.exempt(auth_bp)
    csrf.exempt(logout_bp)
    csrf.exempt(registration_bp)
    csrf.exempt(personal_area_bp)
    csrf.exempt(add_grow_bp)
    csrf.exempt(favorit_product_bp)
    csrf.exempt(get_label_bp)
    csrf.exempt(cart_bp)
    csrf.exempt(order_bp)
    return True
