import os
from typing import List
import logging

class ConfigManager:
    def __init__(self):
        print("LOADING CONFIG")

        self.flask_secret_key  = os.environ.get("flask_secret_key", "bb1437ce01a2c388bbf3e0f5d98d41ab5d762c2059acc479a20dc674a24ff2b1")
        self.user_session_lifetime = 15

        # Azure Blob Storage
        try:
            self.blob_storage_connection_string = os.environ.get("azure_blob_storage_connection_string")
            print(f"Blob Storage Environment Variables: Import Success")
        except:
            print(f"Blob Storage Environment Variables: Import Failure")

        self.blob_storage_container_unprocessed_data = "data-unprocessed"
        self.blob_storage_container_processed_data = "data-processed"
        self.blob_storage_container_data_failed_to_process = "data-failed-to-process"
        self.blob_storage_container_logs = "python-logs"
        self.blob_storage_container_revenue_pdf = "revenue-pdf"

        # Azure SQL Database
        try:
            self.azure_sql_database_connection_string = os.environ.get("azure_sql_database_connection_string")
        except:
            print("CANT GET SQL DB ENV VARS")

        self.azure_sql_database_error_messages = {
            "40615": "Verbindung verweigert: Deine IP-Adresse ist nicht berechtigt auf den Server zuzugreifen.",
            "64": "Verbindung fehlgeschlagen: Möglicherweise war die Datenbank im Ruhzustand. Bitte versuche es in einer Minute noch einmal.",
            "18456": "Login failed: Invalid username or password. Verify your credentials.",
            "40532": "Cannot open server: Requested server not found. Verify server name.",
            "8180": "SQL error: Statement could not be prepared. Check SQL syntax.",
            "102": "Syntax error: Incorrect syntax near the specified token.",
            "0": "Connection busy: Connection is busy with results for another command.",
            "111": "Connection refused: The server refused the connection. Check firewall and network settings.",
            "28000": "Invalid authorization: Login failed due to invalid credentials or insufficient permissions.",
            "20009": "Server unavailable: Unable to connect; the server is unavailable or does not exist.",
            "11001": "DNS error: SQL Server does not exist or access denied. Verify server address.",
            "42000": "Syntax error: Incorrect syntax in SQL statement. Review your query.",
            "08001": "Connection error: Unable to connect to SQL Server. Check server availability.",
            "01000": "Driver error: ODBC driver reported an error. Check driver installation.",
            "40613": "Database unavailable: The database is currently unavailable due to maintenance, pausing, or resource constraints. Try again later."
        }
        
        self.azure_sql_database_connection_timeout_limit = 120

        # Logging
        self.debug_mode = True
        self.print_to_console = True

        self.valid = True
        logging.info("CONFIG LOAD SUCCESS")
        
# Create a single ConfigManager instance
global_config = ConfigManager()