# 🤖 AI-Powered JRXML Generator

An intelligent system that generates JasperReports JRXML files from natural language queries using Gemini AI and comprehensive database analysis.

## 🚀 Features

### **Intelligent Query Understanding**
- **Any Table**: Works with any table in your database
- **Any Column**: Understands all column names and data types
- **Any Filter**: Handles complex filtering logic
- **Any Relationship**: Automatically detects and uses table relationships
- **Any Aggregation**: Supports SUM, COUNT, AVG, MIN, MAX, and more

### **Advanced AI Capabilities**
- **Gemini Flash 2.5**: Uses Google's latest AI model for intelligent SQL generation
- **Schema Analysis**: Comprehensive database schema understanding
- **Relationship Detection**: Automatically finds foreign keys and joins
- **Query Optimization**: Intelligent query optimization and performance tuning
- **Error Handling**: Graceful fallback to rule-based generation

### **Smart Report Generation**
- **Dynamic JRXML**: Generates appropriate JRXML based on data structure
- **Flexible Layout**: Adapts to different data types and query results
- **Download Ready**: Generated files are ready for JasperReports
- **Real-time Processing**: Instant report generation from natural language

## 🏗️ Architecture

```
User Request → AI Analysis → Schema Understanding → SQL Generation → Query Execution → JRXML Generation → Download
```

### **Components**

1. **Database Analyzer** (`database.py`)
   - Comprehensive schema analysis
   - Relationship detection
   - Sample data collection
   - Performance optimization

2. **AI Query Generator** (`unified_ai_generator.py`)
   - Gemini Flash 2.5 integration
   - Intelligent SQL generation
   - Query optimization
   - Error handling

3. **JRXML Generator** (`jrxml_generator.py`)
   - Dynamic template generation
   - Data type adaptation
   - Layout optimization

4. **Web Interface** (`app.py`)
   - FastAPI backend
   - Modern chat interface
   - File download system

## 🛠️ Installation

### **1. Clone and Setup**
```bash
git clone <repository>
cd DB_experiment
```

### **2. Create Environment**
```bash
python create_env.py
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure Database**
Edit `.env` file with your database credentials:
```env
DATABASE_URL=postgresql://username:password@host:port/database
GEMINI_API_KEY=your_gemini_api_key
```

### **5. Run the Application**
```bash
python app.py
```

## 🎯 Usage

### **Web Interface**
1. Open http://localhost:8000
2. Type your request in natural language
3. Get instant JRXML file generation
4. Download the generated file

### **Example Queries**

#### **Simple Reports**
```
"Show me all invoices from 2024"
"List customers with their contact information"
"Get product catalog with prices"
```

#### **Complex Reports**
```
"Generate a sales report showing total revenue by month for 2024"
"Compare invoice amounts between different regions"
"Show customer purchase history with product details"
```

#### **Aggregated Reports**
```
"Calculate total sales by product category"
"Count orders by status for the last 30 days"
"Average order value by customer type"
```

#### **Filtered Reports**
```
"Show invoices above $1000 from premium customers"
"List products with stock less than 10 units"
"Find customers who haven't ordered in 6 months"
```

## 🔧 Configuration

### **Environment Variables**
```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# AI Model
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-1.5-flash

# Application
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

### **AI Model Options**
- `gemini-1.5-flash`: Fast and efficient (recommended)
- `gemini-1.5-pro`: More powerful but slower
- `gemini-1.0-pro`: Legacy model

## 📊 Database Schema Analysis

The system automatically analyzes your database to provide the AI with:

- **Table Information**: Names, row counts, descriptions
- **Column Details**: Types, constraints, sample values
- **Relationships**: Foreign keys, primary keys
- **Indexes**: Performance optimization hints
- **Constraints**: Data integrity rules
- **Sample Data**: Understanding of actual data

## 🎨 Generated JRXML Features

### **Dynamic Layout**
- Adapts to query results
- Handles different data types
- Optimizes column widths
- Professional formatting

### **Data Handling**
- Proper data type conversion
- NULL value handling
- Date formatting
- Number formatting

### **Report Structure**
- Header with title and date
- Data table with proper columns
- Footer with summary information
- Professional styling

## 🔍 Query Types Supported

### **Simple Queries**
- Basic SELECT statements
- WHERE conditions
- ORDER BY clauses
- LIMIT clauses

### **Complex Queries**
- Multi-table JOINs
- Subqueries and CTEs
- Window functions
- UNION operations

### **Aggregated Queries**
- GROUP BY operations
- Aggregate functions
- HAVING clauses
- Conditional aggregations

### **Advanced Features**
- Date range filtering
- Text search and patterns
- Conditional logic (CASE statements)
- Ranking and sorting

## 🚀 Performance Features

### **Query Optimization**
- Automatic LIMIT addition for large tables
- Smart ORDER BY suggestions
- Index-aware query generation
- Performance monitoring

### **Caching**
- Schema analysis caching
- Query result caching
- Template caching

### **Error Handling**
- Graceful AI fallback
- Query validation
- Error recovery
- User-friendly messages

## 🔒 Security

- **Environment Variables**: All secrets in .env file
- **Query Validation**: SQL injection prevention
- **Access Control**: Database connection security
- **Error Sanitization**: Safe error messages

## 📈 Monitoring

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐛 Troubleshooting

### **Common Issues**

1. **Database Connection Failed**
   - Check DATABASE_URL in .env
   - Verify database credentials
   - Ensure network connectivity

2. **AI Generation Failed**
   - Check GEMINI_API_KEY
   - Verify API quota
   - Check internet connection

3. **Query Execution Failed**
   - Review generated SQL
   - Check table/column names
   - Verify permissions

### **Debug Mode**
Set `DEBUG=True` in .env for detailed logging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub

---

**Made with ❤️ using Gemini AI and FastAPI** 