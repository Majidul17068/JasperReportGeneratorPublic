#!/usr/bin/env python3
"""
Progress checker for database schema analysis
"""

import time
import psutil
import os

def check_app_process():
    """Check if the app.py process is still running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'] and proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'app.py' in cmdline:
                    return proc.info['pid'], proc.info['cmdline']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None, None

def check_database_connection():
    """Test database connection"""
    try:
        from config import Config
        from sqlalchemy import create_engine, text
        
        print("🔍 Testing database connection...")
        engine = create_engine(Config.DATABASE_URL)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ Database connection successful!")
            
            # Get table count from all schemas
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            """))
            table_count = result.scalar()
            print(f"📊 Found {table_count} tables in database")
            
            # Get sample tables from all schemas
            result = conn.execute(text("""
                SELECT table_schema || '.' || table_name as full_table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                LIMIT 5
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Sample tables: {', '.join(tables)}")
            
            return True, table_count
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False, 0

def check_gemini_api():
    """Test Gemini API connection"""
    try:
        from config import Config
        import google.generativeai as genai
        
        print("🤖 Testing Gemini API...")
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        response = model.generate_content("Hello, this is a test.")
        if response.text:
            print("✅ Gemini API connection successful!")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def main():
    """Main progress checker"""
    print("🔍 Progress Checker for AI JRXML Generator")
    print("=" * 50)
    
    # Check if app.py is running
    pid, cmdline = check_app_process()
    if pid:
        print(f"✅ app.py is running (PID: {pid})")
        print(f"📝 Command: {' '.join(cmdline)}")
        
        # Get process info
        try:
            proc = psutil.Process(pid)
            print(f"⏱️  Running time: {time.time() - proc.create_time():.1f} seconds")
            print(f"💾 Memory usage: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
            print(f"🔄 CPU usage: {proc.cpu_percent()}%")
        except:
            print("⚠️  Could not get detailed process info")
    else:
        print("❌ app.py is not running")
        return
    
    print("\n" + "=" * 50)
    
    # Check database connection
    db_ok, table_count = check_database_connection()
    
    print("\n" + "=" * 50)
    
    # Check Gemini API
    gemini_ok = check_gemini_api()
    
    print("\n" + "=" * 50)
    
    # Summary
    print("📊 SUMMARY:")
    print(f"✅ App Process: {'Running' if pid else 'Not Running'}")
    print(f"✅ Database: {'Connected' if db_ok else 'Failed'}")
    print(f"✅ Gemini API: {'Connected' if gemini_ok else 'Failed'}")
    
    if db_ok and table_count > 0:
        print(f"📋 Database has {table_count} tables to analyze")
        if table_count > 50:
            print("⚠️  Large database - analysis may take several minutes")
        elif table_count > 20:
            print("⏳ Medium database - analysis should complete soon")
        else:
            print("🚀 Small database - analysis should be quick")
    
    print("\n💡 TIPS:")
    print("- The system analyzes each table's structure, relationships, and sample data")
    print("- Large tables with many columns take longer to analyze")
    print("- Network latency to database can affect analysis time")
    print("- You can safely leave it running - it will complete automatically")

if __name__ == "__main__":
    main() 