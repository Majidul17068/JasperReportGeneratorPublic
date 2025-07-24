#!/usr/bin/env python3
"""
Configuration management for the JRXML Generator
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "YOUR_DB_CONNECTION")
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # OpenAI configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # File paths
    TEMPLATES_DIR = "templates"
    OUTPUT_DIR = "generated_reports"
    
    # Ensure directories exist
    @classmethod
    def create_directories(cls):
        os.makedirs(cls.TEMPLATES_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True) 
