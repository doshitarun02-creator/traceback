# app/__init__.py  (your existing factory)
from app.routes.auth import auth_bp
from app.routes.complaints import complaints_bp

app.register_blueprint(auth_bp)
app.register_blueprint(complaints_bp)
from app.routes.experts import experts_bp
from app.routes.cases   import cases_bp
from app.routes.admin   import admin_bp

app.register_blueprint(experts_bp, url_prefix="/api/experts")
app.register_blueprint(cases_bp,   url_prefix="/api/cases")
app.register_blueprint(admin_bp,   url_prefix="/api/admin")