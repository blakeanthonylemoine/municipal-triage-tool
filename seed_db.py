# seed_db.py
"""Seeds fictional test tenants for local dev/pilot testing.

Never use a real target customer's name here -- these are throwaway dev
fixtures, not real prospects. Each tenant is provisioned through
tenant_service.provision_tenant so it gets real, working login
credentials the same way the admin panel creates one -- no more pinning
an explicit tenant id to match a frontend hardcode; tenant identity now
comes from the JWT issued at login, not a hardcoded constant.
"""
from database import SessionLocal
from models import Category, Tenant
from tenant_service import provision_tenant

TEST_TENANTS = [
    {
        "name": "City of Rivergate",
        "login_email": "rivergate@gmail.com",
        "password": "rivergate",
        "categories": ["Roads", "Utilities", "Parks", "Code Violations"],
    },
    {
        "name": "Town of Ashcombe",
        "login_email": "ashcombe@example.com",
        "password": "ashcombe123",
        "categories": ["Sanitation", "Animal Control", "Streetlights", "Permitting"],
    },
]


def seed():
    db = SessionLocal()
    try:
        for spec in TEST_TENANTS:
            existing = db.query(Tenant).filter(
                (Tenant.name == spec["name"]) | (Tenant.login_email == spec["login_email"])
            ).first()
            if existing:
                print(f"Tenant {spec['name']!r} already exists; skipping.")
                continue

            tenant = provision_tenant(
                db, name=spec["name"], login_email=spec["login_email"], password=spec["password"]
            )
            for category_name in spec["categories"]:
                db.add(Category(tenant_id=tenant.id, name=category_name, is_emergency_flag=False))
            db.commit()

            print(f"Seeded tenant {spec['name']!r} ({spec['login_email']}) with {len(spec['categories'])} categories.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
