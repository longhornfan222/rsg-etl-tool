from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine

def createTable():

    engine = create_engine('mysql://etl_client:simlab@localhost/UMiami', echo=True)
    metadata = MetaData()

    users = Table('users', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            Column('fullname', String(50)),
            Column('nickname', String(50))
        )
    
    # Create table if it doesn't exist
    metadata.create_all(engine, checkfirst=True)

def insert():
    engine = create_engine('mysql://etl_client:simlab@localhost/UMiami', echo=True)
    metadata = MetaData()

    users = Table('users', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            Column('fullname', String(50)),
            Column('nickname', String(50))
        )
    
    # Create table if it doesn't exist
    #metadata.create_all(engine, checkfirst=True)

    # Prepare data
    ins = users.insert()
    print ins
    ins = users.insert().values(name='jack', fullname='Jack Jones')
    print ins
    print ins.compile().params

    
    conn = engine.connect()
    print conn
    
    # Execute insert
    result = conn.execute(ins)
    print result    

def drop():
    engine = create_engine('mysql://etl_client:simlab@localhost/UMiami', echo=True)

    # This works too
    #sql = str('DROP TABLE IF EXISTS users;')
    #result = engine.execute(sql)

    metadata = MetaData()
    users = Table('users', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            Column('fullname', String(50)),
            Column('nickname', String(50))
        )    
    
    users.drop(engine)

def insertReflected():
    engine = create_engine('mysql://etl_client:simlab@localhost/UMiami', echo=True)
    metadata = MetaData()

    try:
        users = Table('users', metadata, autoload=True, autoload_with=engine)
    except Exception as e:
        print 'ERROR: Table ' + str(e) + ' probably does not exists in schema'
        return False
    print users

    ins = users.insert().values(name='Ryan', fullname='Ryan E')        
        
    # Execute insert
    conn = engine.connect()
    result = conn.execute(ins)      

def createUserTableNamePk():

    engine = create_engine('mysql://etl_client:simlab@localhost/UMiami', echo=True)
    metadata = MetaData()

    users = Table('usersPk', metadata,
            #Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            Column('fullname', String(50), primary_key=True),
            Column('nickname', String(50))
        )
    
    # Create table if it doesn't exist
    metadata.create_all(engine, checkfirst=True)

def insertUserReflectedPk():
    engine = create_engine('mysql://etl_client:simlab@localhost/UMiami', echo=True)
    metadata = MetaData()

    try:
        users = Table('userspk', metadata, autoload=True, autoload_with=engine)
    except Exception as e:
        print 'ERROR: Table ' + str(e) + ' probably does not exists in schema'
        return False
    print users

    ins = users.insert().values(name='Ryan', fullname='Ryan E')        

    # Execute insert
    try:
        conn = engine.connect()
        result = conn.execute(ins)  
    except Exception as e:
        print 'ERROR: ' + str(e) + ' '
        return False


def createUserTableCompositePk():
    
    engine = create_engine('mysql://etl_client:simlab@localhost/UMiami', echo=True)
    metadata = MetaData()

    users = Table('usersCompositePk', metadata,
            #Column('id', Integer, primary_key=True),
            Column('firstname', String(50), primary_key=True),
            Column('lastname', String(50), primary_key=True),
            Column('nickname', String(50))
        )
    
    # Create table if it doesn't exist
    metadata.create_all(engine, checkfirst=True)

def insertUserReflectedCompositePk():
    engine = create_engine('mysql://etl_client:simlab@localhost/UMiami', echo=True)
    metadata = MetaData()

    try:
        users = Table('usersCompositePk', metadata, autoload=True, autoload_with=engine)
    except Exception as e:
        print 'ERROR: Table ' + str(e) + ' probably does not exists in schema'
        return False
    print users

    ins = users.insert().values(firstname='Ryan', lastname='Engle')        

    # Execute insert
    try:
        conn = engine.connect()
        result = conn.execute(ins)  
    except Exception as e:
        print 'ERROR: ' + str(e) + ' '
        return False


if __name__ == '__main__':
    #createTable()
    #insert()    
    #insertReflected()    
    #drop() # users
    #createUserTableNamePk()
    #insertUserReflectedPk()

    createUserTableCompositePk()
    insertUserReflectedCompositePk()