# seed_db.py
"""Seeds a fictional test tenant and its categories for local dev/pilot testing.

Uses a fictional municipality name, not a real target customer's name --
Rivergate is not an actual prospect. Tenant is inserted with explicit id=1
to match the frontend's hardcoded CURRENT_TENANT_ID
(frontend/src/components/TicketQueue.tsx). Categories are inserted in the
same order main.py's /webhook route hardcodes (Roads, Utilities, Parks,
Code Violations) so the AI-returned category_id lines up with real rows.
"""
from sqlalchemy import text
from database import SessionLocal
from models import Tenant, Category

CATEGORY_NAMES = ["Roads", "Utilities", "Parks", "Code Violations"]

def seed():
    db = SessionLocal()
    try:
        existing = db.query(Tenant).filter(Tenant.id == 1).first()
        if existing:
            print(f"Tenant id=1 already exists ({existing.name!r}); skipping seed.")
            return

        tenant = Tenant(id=1, name="City of Rivergate", config={})
        db.add(tenant)
        db.flush()  # assign tenant.id before categories reference it

        for name in CATEGORY_NAMES:
            db.add(Category(tenant_id=tenant.id, name=name, is_emergency_flag=False))

        db.commit()

        # Realign the sequences so future inserts don't collide with the
        # explicit id=1 we just used.
        db.execute(text(
            "SELECT setval('tenants_id_seq', (SELECT MAX(id) FROM tenants))"
        ))
        db.execute(text(
            "SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories))"
        ))
        db.commit()

        print("Seeded tenant 'City of Rivergate' (id=1) with 4 categories.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
