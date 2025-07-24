#!/usr/bin/env python3
"""
Debug database connection and schema
"""

from config import Config
from sqlalchemy import create_engine, text

def debug_database():
    """Debug database connection and find schemas/tables"""
    print("🔍 Debugging Database Connection")
    print("=" * 50)
    
    try:
        engine = create_engine(Config.DATABASE_URL)
        print(f"🔗 Connecting to: {Config.DATABASE_URL}")
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ Basic connection successful!")
            
            # Get current schema
            result = conn.execute(text("SELECT current_schema()"))
            current_schema = result.scalar()
            print(f"📋 Current schema: {current_schema}")
            
            # List all schemas
            print("\n📚 All available schemas:")
            result = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
            schemas = [row[0] for row in result.fetchall()]
            for schema in schemas:
                print(f"  - {schema}")
            
            # Check tables in each schema
            for schema in schemas:
                print(f"\n📋 Tables in schema '{schema}':")
                result = conn.execute(text(f"""
                    SELECT table_name, table_type 
                    FROM information_schema.tables 
                    WHERE table_schema = '{schema}'
                    ORDER BY table_name
                """))
                tables = result.fetchall()
                
                if tables:
                    for table_name, table_type in tables:
                        print(f"  - {table_name} ({table_type})")
                else:
                    print("  (no tables)")
            
            # Check for specific tables we know about
            print(f"\n🔍 Looking for specific tables:")
            known_tables = ['c_invoice', 'adempiere.c_invoice', 'public.c_invoice']
            
            for table_name in known_tables:
                try:
                    if '.' in table_name:
                        schema, table = table_name.split('.')
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table} LIMIT 1"))
                    else:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} LIMIT 1"))
                    print(f"  ✅ {table_name} - EXISTS")
                except Exception as e:
                    print(f"  ❌ {table_name} - NOT FOUND ({str(e)[:50]}...)")
            
            # Check user permissions
            print(f"\n🔐 Checking permissions:")
            result = conn.execute(text("SELECT current_user, session_user"))
            current_user, session_user = result.fetchone()
            print(f"  Current user: {current_user}")
            print(f"  Session user: {session_user}")
            
    except Exception as e:
        print(f"❌ Database debug failed: {e}")

if __name__ == "__main__":
    debug_database() 