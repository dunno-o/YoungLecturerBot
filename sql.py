import sqlite3


def create_table_person():
    db = sqlite3.connect('db.db')
    sql = db.cursor()
    sql.execute("""DROP TABLE IF EXISTS person""")
    sql.execute("""CREATE TABLE IF NOT EXISTS person (
        UserID INTEGER Default 0,
        Nickname TEXT Default 'None',
        Level INTEGER Default 0,
        HP INTEGER Default 100,
        CurHP INTEGER Default 100,
        Money INTEGER Default 100,
        Attack INTEGER Default 2,
        MagicAttack INTEGER Default 1,
        XP INTEGER Default 0,
        Armour INTEGER Default 2,
        MagicArmour INTEGER Default 1,
        LocationID INTEGER Default 11);""")
    db.commit()


def create_table_mobs():
    db = sqlite3.connect('db.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS mobs (
        MobID INTEGER Primary Key Autoincrement,
        HP INTEGER Default 100,
        XP INTEGER Default 0,
        ReqLevel INTEGER Default 0,
        AttackType TEXT Default 'Physical',
        Attack INTEGER Default 0,
        Armour INTEGER Default 0,
        MagicArmour INTEGER Default 0);""")
    db.commit()


def create_table_locations():
    db = sqlite3.connect('db.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS locations (
    LocationID INTEGER Primary Key Autoincrement,
    XCoord INTEGER Default 0,
    YCoord INTEGER Default 0,
    LocationType TEXT Default 'City',
    LocationName TEXT Default 'None');""")
    db.commit()


def create_table_items():
    db = sqlite3.connect('db.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS items (
    ItemID INTEGER Primary Key Autoincrement,
    ItemName TEXT Default 'None',
    Cost INTEGER Default 0,
    CostToSale INTEGER Default 0,
    ItemType TEXT Default 'Weapon',
    HP INTEGER Default 0,
    Mana INTEGER Default 0,
    Attack INTEGER Default 0,
    MagicAttack INTEGER Default 0,
    Armour INTEGER Default 0,
    MagicArmour INTEGER Default 0,
    ReqLevel INTEGER Default 0);""")
    db.commit()

def create_table_inventory():
    db = sqlite3.connect('db.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS inventory (
    UserID INTEGER Default 0,
    ItemID INTEGER Default 0,
    Used INTEGER Default 1);""")
    db.commit()