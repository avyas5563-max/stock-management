import os
from app import create_app, db
from app.models.user import User
from app.models.category import Category
from app.models.item import Item
from app.models.supplier import Supplier
from app.models.customer import Customer
from app.models.purchase import Purchase, PurchaseItem
from app.models.sale import Sale, SaleItem
from app.models.inventory import Inventory
from app.models.money import Money
from app.models.log import Log

app = create_app(os.getenv('FLASK_ENV') or 'default')


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Category': Category,
        'Item': Item,
        'Supplier': Supplier,
        'Customer': Customer,
        'Purchase': Purchase,
        'PurchaseItem': PurchaseItem,
        'Sale': Sale,
        'SaleItem': SaleItem,
        'Inventory': Inventory,
        'Money': Money,
        'Log': Log
    }


@app.cli.command()
def initdb():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def create_admin():
    """Create an admin user"""
    from werkzeug.security import generate_password_hash
    
    admin = User(
        name='Admin User',
        username='admin',
        password=generate_password_hash('admin123'),
        role='admin',
        status='active'
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created! Username: admin, Password: admin123')


@app.cli.command()
def sync_inventory():
    """Create inventory records for items that don't have them"""
    items = Item.query.all()
    count = 0
    for item in items:
        inventory = Inventory.query.filter_by(item_id=item.item_id).first()
        if not inventory:
            inventory = Inventory(
                item_id=item.item_id,
                current_stock=0.0
            )
            db.session.add(inventory)
            count += 1
    
    db.session.commit()
    print(f'Synced {count} inventory records!')


if __name__ == '__main__':
    app.run(debug=True)
