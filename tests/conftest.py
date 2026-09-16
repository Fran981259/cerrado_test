import os
import tempfile


_test_dir = tempfile.mkdtemp(prefix="portal-cerrado-tests-")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_test_dir, 'test.db')}"
os.environ.setdefault("ENABLE_LOCAL_SCHEDULER", "0")


def pytest_configure():
    from app.database import init_db, get_session
    from app.schema import Reporter

    init_db()
    db = get_session()
    try:
        if not db.query(Reporter).first():
            db.add(Reporter(slug="enzo.bianchi", display_name="Enzo Bianchi", role="technology", email="enzo.test@portalcerrado.local"))
            db.commit()
    finally:
        db.close()
