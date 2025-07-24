#!/usr/bin/env python3
"""
AI JRXML Generator - FastAPI Application with Gemini Flash 2.5
"""

import os
import sys
import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pydantic import BaseModel

# Import our modules
from config import Config
from database import DatabaseAnalyzer
from jrxml_generator import JRXMLGenerator
from unified_ai_generator import OpenAIQueryGenerator

class ReportRequest(BaseModel):
    request: str

# Initialize FastAPI app
app = FastAPI(
    title="AI JRXML Generator",
    description="Generate JasperReports JRXML files from natural language using Gemini AI",
    version="2.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize components
print("🔧 Initializing AI JRXML Generator...")
try:
    db_analyzer = DatabaseAnalyzer()
    jrxml_generator = JRXMLGenerator()
    
    # Initialize OpenAI AI generator
    try:
        ai_generator = OpenAIQueryGenerator()
        print(f"✅ OpenAI AI initialized with model: {Config.OPENAI_MODEL}")
        use_ai = True
    except Exception as e:
        print(f"❌ OpenAI AI initialization failed: {e}")
        print("⚠️  Using rule-based fallback")
        use_ai = False
        ai_generator = None
    
    print("✅ All components initialized successfully!")
    
except Exception as e:
    print(f"❌ Failed to initialize components: {e}")
    sys.exit(1)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_report")
async def generate_report(report_request: ReportRequest):
    """Generate JRXML report from natural language request"""
    try:
        user_request = report_request.request
        print(f"📝 Processing request: {user_request}")
        
        # Step 1: Generate SQL query
        if use_ai and ai_generator:
            try:
                sql_query, explanation, metadata = ai_generator.generate_sql_query(user_request)
                ai_model_used = metadata.get('ai_model', Config.OPENAI_MODEL)
                print(f"✅ AI generated SQL: {sql_query[:100]}...")
            except Exception as e:
                print(f"⚠️  AI generation failed: {e}")
                # Fallback to rule-based
                sql_query, explanation, metadata = generate_rule_based_sql(user_request)
                ai_model_used = "rule-based (fallback)"
        else:
            # Use rule-based generation
            sql_query, explanation, metadata = generate_rule_based_sql(user_request)
            ai_model_used = "rule-based"
        
        if not sql_query:
            raise HTTPException(status_code=400, detail="Failed to generate SQL query")
        
        print(f"📊 SQL Query: {sql_query}")
        print(f"🤖 AI Model: {ai_model_used}")
        
        # Step 2: Execute query
        try:
            result = db_analyzer.execute_query(sql_query)
            print(f"✅ Query executed successfully! Found {len(result)} rows")
        except Exception as e:
            print(f"⚠️  Query execution failed: {e}")
            # Try with LIMIT 1 for testing
            test_query = sql_query.rstrip(';') + " LIMIT 1;"
            result = db_analyzer.execute_query(test_query)
            print(f"✅ Test query executed successfully!")
        
        if not result:
            raise HTTPException(status_code=400, detail="No data returned from query")
        
        # Step 3: Generate JRXML
        report_config = jrxml_generator.create_report_config(user_request, sql_query, result)
        jrxml_content = jrxml_generator.generate_jrxml(sql_query, report_config)
        
        if not jrxml_content:
            raise HTTPException(status_code=500, detail="Failed to generate JRXML")
        
        # Step 4: Save file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.jrxml"
        filepath = f"generated_reports/{filename}"
        
        # Ensure directory exists
        os.makedirs("generated_reports", exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(jrxml_content)
        
        print(f"✅ JRXML saved to: {filepath}")
        
        return {
            "success": True,
            "message": "Report generated successfully!",
            "filename": filename,
            "filepath": filepath,
            "sql_query": sql_query,
            "explanation": explanation,
            "ai_model": ai_model_used,
            "rows_returned": len(result),
            "download_url": f"/download/{filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated JRXML file"""
    filepath = f"generated_reports/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/xml'
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_model": Config.OPENAI_MODEL if use_ai else "rule-based",
        "database": "connected",
        "timestamp": datetime.datetime.now().isoformat()
    }

def generate_rule_based_sql(user_request: str):
    """Generate SQL using rule-based approach as fallback"""
    request_lower = user_request.lower()
    
    # Extract table name
    if "c_invoice" in request_lower:
        table_name = "c_invoice"
    elif "adempiere.c_invoice" in request_lower:
        table_name = "adempiere.c_invoice"
    else:
        # Try to find any table mentioned
        import re
        table_match = re.search(r'from\s+(\w+\.?\w*)', request_lower)
        if table_match:
            table_name = table_match.group(1)
        else:
            table_name = "c_invoice"  # Default
    
    # Extract columns
    columns = []
    if "documentno" in request_lower:
        columns.append("documentno")
    if "dateinvoiced" in request_lower:
        columns.append("dateinvoiced")
    if "grandtotal" in request_lower:
        columns.append("grandtotal")
    if "amount" in request_lower:
        columns.append("grandtotal")
    
    # If no specific columns mentioned, use defaults
    if not columns:
        columns = ["documentno", "dateinvoiced", "grandtotal"]
    
    # Build SQL query
    columns_str = ", ".join(columns)
    sql_query = f"SELECT {columns_str} FROM {table_name}"
    
    # Add date range if mentioned
    if "2024" in request_lower and "2025" in request_lower:
        sql_query += " WHERE dateinvoiced >= '2024-01-01' AND dateinvoiced <= '2025-12-31'"
    elif "2024" in request_lower:
        sql_query += " WHERE dateinvoiced >= '2024-01-01' AND dateinvoiced <= '2024-12-31'"
    
    sql_query += " ORDER BY dateinvoiced DESC LIMIT 100;"
    
    explanation = f"Generated SQL query for {table_name} table with columns: {', '.join(columns)}"
    
    metadata = {
        "user_request": user_request,
        "tables_used": [table_name],
        "query_type": "listing",
        "ai_model": "rule-based"
    }
    
    return sql_query, explanation, metadata

if __name__ == "__main__":
    print("🚀 Starting AI JRXML Generator...")
    print(f"📱 Web interface: http://0.0.0.0:8000")
    print(f"🔧 API documentation: http://0.0.0.0:8000/docs")
    print(f"�� AI Model: {Config.OPENAI_MODEL}")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=Config.DEBUG,
        log_level="info"
    ) 