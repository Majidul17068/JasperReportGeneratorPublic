from jinja2 import Template
from typing import Dict, List, Any
import os
from datetime import datetime
from config import Config

class JRXMLGenerator:
    def __init__(self):
        self.template_dir = Config.TEMPLATES_DIR
        self.output_dir = Config.OUTPUT_DIR
        self.base_template = self._load_base_template()
    
    def _load_base_template(self) -> str:
        """Load the base JRXML template"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports
              http://jasperreports.sourceforge.net/xsd/jasperreport.xsd"
              name="{{ report_name }}"
              pageWidth="595"
              pageHeight="842"
              columnWidth="555"
              leftMargin="20"
              rightMargin="20"
              topMargin="20"
              bottomMargin="20"
              uuid="{{ report_uuid }}">
    
    <property name="com.jaspersoft.studio.data.defaultdataadapter" value="PostgreSQL Data Adapter"/>
    
    <queryString>
        <![CDATA[{{ sql_query }}]]>
    </queryString>
    
    <field name="{{ field_name }}" class="{{ field_type }}">
        <fieldDescription><![CDATA[{{ field_description }}]]></fieldDescription>
    </field>
    {% for field in additional_fields %}
    <field name="{{ field.name }}" class="{{ field.type }}">
        <fieldDescription><![CDATA[{{ field.description }}]]></fieldDescription>
    </field>
    {% endfor %}
    
    <title>
        <band height="50" splitType="Stretch">
            <textField>
                <reportElement x="0" y="0" width="555" height="30" uuid="{{ title_uuid }}"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="16" isBold="true"/>
                </textElement>
                <textFieldExpression><![CDATA["{{ report_title }}"]]></textFieldExpression>
            </textField>
            <textField pattern="dd/MM/yyyy HH:mm">
                <reportElement x="0" y="30" width="555" height="20" uuid="{{ date_uuid }}"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="10"/>
                </textElement>
                <textFieldExpression><![CDATA[new java.util.Date()]]></textFieldExpression>
            </textField>
        </band>
    </title>
    
    <columnHeader>
        <band height="30" splitType="Stretch">
            {% for column in columns %}
            <staticText>
                <reportElement x="{{ column.x }}" y="0" width="{{ column.width }}" height="30" uuid="{{ column.uuid }}"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="12" isBold="true"/>
                </textElement>
                <text><![CDATA[{{ column.header }}]]></text>
            </staticText>
            {% endfor %}
        </band>
    </columnHeader>
    
    <detail>
        <band height="20" splitType="Stretch">
            {% for column in columns %}
            <textField isBlankWhenNull="true">
                <reportElement x="{{ column.x }}" y="0" width="{{ column.width }}" height="20" uuid="{{ column.field_uuid }}"/>
                <textElement textAlignment="{{ column.alignment }}" verticalAlignment="Middle">
                    <font size="10"/>
                </textElement>
                <textFieldExpression><![CDATA[$F{ {{ column.field_name }} }]]></textFieldExpression>
            </textField>
            {% endfor %}
        </band>
    </detail>
    
    {% if show_summary %}
    <summary>
        <band height="30" splitType="Stretch">
            <staticText>
                <reportElement x="0" y="0" width="100" height="30" uuid="{{ summary_uuid }}"/>
                <textElement textAlignment="Left" verticalAlignment="Middle">
                    <font size="12" isBold="true"/>
                </textElement>
                <text><![CDATA[Total Records:]]></text>
            </staticText>
            <textField evaluationTime="Report">
                <reportElement x="100" y="0" width="100" height="30" uuid="{{ count_uuid }}"/>
                <textElement textAlignment="Left" verticalAlignment="Middle">
                    <font size="12" isBold="true"/>
                </textElement>
                <textFieldExpression><![CDATA[$V{PAGE_NUMBER}]]></textFieldExpression>
            </textField>
        </band>
    </summary>
    {% endif %}
    
</jasperReport>"""
    
    def generate_jrxml(self, sql_query: str, report_config: Dict[str, Any]) -> str:
        """
        Generate JRXML content from SQL query and configuration
        
        Args:
            sql_query: The SQL query to execute
            report_config: Configuration for the report including:
                - report_name: Name of the report
                - report_title: Display title
                - columns: List of column configurations
                - show_summary: Whether to show summary band
        """
        
        # Generate UUIDs for JasperReports
        import uuid
        
        template_data = {
            "report_name": report_config.get("report_name", "GeneratedReport"),
            "report_title": report_config.get("report_title", "Generated Report"),
            "report_uuid": str(uuid.uuid4()),
            "title_uuid": str(uuid.uuid4()),
            "date_uuid": str(uuid.uuid4()),
            "summary_uuid": str(uuid.uuid4()),
            "count_uuid": str(uuid.uuid4()),
            "sql_query": sql_query,
            "columns": [],
            "additional_fields": [],
            "show_summary": report_config.get("show_summary", True)
        }
        
        # Process columns
        columns = report_config.get("columns", [])
        x_position = 0
        column_width = 555 // max(len(columns), 1)  # Distribute columns evenly
        
        for i, column in enumerate(columns):
            column_config = {
                "header": column.get("header", column.get("field_name", f"Column {i+1}")),
                "field_name": column.get("field_name", f"field_{i+1}"),
                "x": x_position,
                "width": column.get("width", column_width),
                "alignment": column.get("alignment", "Left"),
                "uuid": str(uuid.uuid4()),
                "field_uuid": str(uuid.uuid4())
            }
            template_data["columns"].append(column_config)
            x_position += column_config["width"]
            
            # Add field definition
            field_config = {
                "name": column_config["field_name"],
                "type": column.get("type", "java.lang.String"),
                "description": column.get("description", column_config["header"])
            }
            template_data["additional_fields"].append(field_config)
        
        # Add main field if no columns defined
        if not columns:
            template_data["field_name"] = "field_1"
            template_data["field_type"] = "java.lang.String"
            template_data["field_description"] = "Data Field"
        
        # Render template
        template = Template(self.base_template)
        return template.render(**template_data)
    
    def auto_generate_columns(self, sql_query: str, sample_data: List[Dict]) -> List[Dict]:
        """Automatically generate column configuration from sample data"""
        if not sample_data:
            return []
        
        columns = []
        sample_row = sample_data[0]
        
        for field_name, value in sample_row.items():
            # Determine field type
            if isinstance(value, (int, float)):
                field_type = "java.lang.Double" if isinstance(value, float) else "java.lang.Integer"
                alignment = "Right"
            elif isinstance(value, datetime):
                field_type = "java.util.Date"
                alignment = "Center"
            else:
                field_type = "java.lang.String"
                alignment = "Left"
            
            column_config = {
                "field_name": field_name,
                "header": field_name.replace("_", " ").title(),
                "type": field_type,
                "alignment": alignment,
                "description": f"Field: {field_name}",
                "width": 100  # Default width
            }
            columns.append(column_config)
        
        return columns
    
    def save_jrxml_file(self, jrxml_content: str, filename: str) -> str:
        """Save JRXML content to file"""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(jrxml_content)
        
        return filepath
    
    def create_report_config(self, user_request: str, sql_query: str, sample_data: List[Dict]) -> Dict[str, Any]:
        """Create a report configuration based on user request and sample data"""
        
        # Generate report name from user request
        report_name = user_request.replace(" ", "_").replace("'", "").replace('"', "")[:50]
        report_name = f"Report_{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Auto-generate columns from sample data
        columns = self.auto_generate_columns(sql_query, sample_data)
        
        # Determine if we should show summary based on query type
        show_summary = any(word in user_request.lower() for word in ['count', 'sum', 'total', 'report'])
        
        return {
            "report_name": report_name,
            "report_title": user_request.title(),
            "columns": columns,
            "show_summary": show_summary
        } 