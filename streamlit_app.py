import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time
import json
import streamlit.components.v1 as components

# Set your Google Sheet ID here
SHEET_ID = '1A9vyxOShQvSdZIPGdHJBMwD7dGgxE_M5ICEFrNthuTI'
# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = 'service_account.json'


def clean_data(data):
    """
    Cleans the scanned data by removing quotes, brackets, and other unwanted characters.
    """
    # Remove quotes, brackets, and extra whitespace
    cleaned = data.replace('"', '').replace('[', '').replace(']', '').strip()
    return cleaned


def check_duplicate_student(sheet, student_id):
    """
    Checks if a student ID already exists in the selected worksheet.
    Returns True if duplicate found, False otherwise.
    """
    try:
        # Get all values from column B (2nd column) where student IDs are located
        column_b_values = sheet.col_values(2)

        # Check if the student ID exists in column B
        for value in column_b_values:
            if value and value.strip() == student_id:
                return True
        return False
    except Exception as e:
        st.error(f"Error checking for duplicate: {e}")
        return False


def log_data_to_file(sheet_name, column_a, column_b, column_c, column_d):
    """
    Logs the posted data to a log file with timestamp.
    """
    try:
        log_filename = "qr_scan_log.txt"
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Sheet: {sheet_name} | A: {column_a} | B: {column_b} | C: {column_c} | D: {column_d}\n"

        with open(log_filename, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

        st.success(f"Data logged to {log_filename}")
    except Exception as e:
        st.error(f"Failed to log data: {e}")


def post_data_to_server(data, sheet_name):
    """
    Posts the scanned data to Google Sheets with data in columns A, B, C and timestamp in column D.
    Checks for duplicates before posting.
    """
    try:
        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Clean the scanned data first
        cleaned_data = clean_data(data)

        # Split the cleaned data by comma
        data_parts = cleaned_data.split(',')
        # Ensure we have at least 3 parts, pad with empty strings if needed
        while len(data_parts) < 3:
            data_parts.append('')
        # Process the data parts for columns A, B, C
        column_a = data_parts[0].strip() if len(data_parts) > 0 else ''
        column_b = data_parts[1].strip() if len(data_parts) > 1 else ''
        column_c = data_parts[2].strip() if len(data_parts) > 2 else ''
        column_d = current_time

        # Define the required scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        # Authenticate using the service account
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=scopes)
        client = gspread.authorize(creds)
        # Open the Google Sheet using the selected sheet name
        sheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)

        # Check for duplicate student
        if check_duplicate_student(sheet, column_b):
            st.warning(
                f"Student {column_b} already exists in sheet '{sheet_name}'. Duplicate entry prevented.")
            return False

        # Find the next empty row
        all_values = sheet.get_all_values()
        next_row = len(all_values) + 1  # More reliable than col_values(1)
        # Update the cells in columns A, B, C, D of the next empty row
        sheet.update_cell(next_row, 1, column_a)  # Column A
        sheet.update_cell(next_row, 2, column_b)  # Column B
        sheet.update_cell(next_row, 3, column_c)  # Column C
        sheet.update_cell(next_row, 4, column_d)  # Column D

        # Log the data to file
        log_data_to_file(sheet_name, column_a, column_b, column_c, column_d)

        st.success(f"Data posted to Google Sheet '{sheet_name}':")
        st.info(f"Column A: {column_a}")
        st.info(f"Column B: {column_b}")
        st.info(f"Column C: {column_c}")
        st.info(f"Column D: {column_d}")
        st.info(f"Posted to row {next_row}")

        return True

    except Exception as e:
        st.error(f"Failed to post data to Google Sheet: {e}")
        return False


def create_qr_scanner():
    """
    Creates the QR scanner HTML component
    """
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Scanner</title>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <style>
            #reader {
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
            }
            .scanner-container {
                text-align: center;
                padding: 20px;
                background: #f0f2f6;
                border-radius: 10px;
                margin: 10px 0;
            }
            .status {
                margin-top: 10px;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="scanner-container">
            <h3>📱 QR Code Scanner</h3>
            <div id="reader"></div>
            <div id="status"></div>
        </div>
        
        <script>
        let lastScannedData = '';
        let scanCount = 0;
        
        function onScanSuccess(decodedText, decodedResult) {
            // Prevent duplicate scans of the same data
            if (decodedText === lastScannedData) {
                return;
            }
            
            lastScannedData = decodedText;
            scanCount++;
            
            // Show success message
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `
                <div class="status success">
                    ✅ QR Code Scanned Successfully!<br>
                    Data: ${decodedText}<br>
                    Scan #${scanCount}
                </div>
            `;
            
            // Send data to Streamlit
            if (window.parent && window.parent.postMessage) {
                window.parent.postMessage({
                    type: 'qr-scanned',
                    data: decodedText,
                    timestamp: new Date().toISOString()
                }, '*');
            }
            
            // Clear status after 3 seconds
            setTimeout(() => {
                statusDiv.innerHTML = '';
                lastScannedData = '';
            }, 3000);
        }
        
        function onScanFailure(error) {
            console.warn(`Code scan error = ${error}`);
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `
                <div class="status error">
                    ❌ Scan failed. Please try again.
                </div>
            `;
            
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 2000);
        }
        
        // Initialize QR Scanner
        let html5QrcodeScanner = new Html5QrcodeScanner(
            "reader", 
            { 
                fps: 10, 
                qrbox: { width: 250, height: 250 },
                aspectRatio: 1.0
            }
        );
        html5QrcodeScanner.render(onScanSuccess, onScanFailure);
        
        // Add manual input option
        const manualInput = document.createElement('div');
        manualInput.innerHTML = `
            <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 5px;">
                <h4>🔧 Manual Input</h4>
                <input type="text" id="manualData" placeholder="Enter QR code data here..." 
                       style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;">
                <button onclick="submitManualData()" 
                        style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    Submit
                </button>
            </div>
        `;
        document.querySelector('.scanner-container').appendChild(manualInput);
        
        function submitManualData() {
            const manualData = document.getElementById('manualData').value;
            if (manualData.trim()) {
                onScanSuccess(manualData.trim());
                document.getElementById('manualData').value = '';
            }
        }
        </script>
    </body>
    </html>
    """
    return html_code


def main():
    st.set_page_config(
        page_title="QR Code Scanner",
        page_icon="📱",
        layout="wide"
    )

    st.title("📱 QR Code Scanner for Google Sheets")
    st.markdown("---")

    # Sidebar for sheet selection
    st.sidebar.header("📋 Sheet Selection")

    sheet_names = ['工作表1', '工作表2', '工作表3', '工作表4']
    selected_sheet = st.sidebar.selectbox(
        "Select Worksheet:",
        sheet_names,
        index=0
    )

    st.sidebar.success(f"Selected: {selected_sheet}")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📷 QR Code Scanner")

        # QR Code Scanner using HTML component
        qr_html = create_qr_scanner()
        components.html(qr_html, height=600)

        # Manual input option (backup)
        st.markdown("---")
        st.subheader("🔧 Manual Input (Backup)")

        manual_data = st.text_input(
            "Enter QR Code Data:",
            placeholder="Enter the QR code data here..."
        )

        if st.button("📤 Submit Manual Data"):
            if manual_data:
                if post_data_to_server(manual_data, selected_sheet):
                    st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.error("Please enter data first!")

    with col2:
        st.header("📊 Status")

        # Display current sheet info
        st.info(f"**Current Sheet:** {selected_sheet}")

        # Recent activity
        st.subheader("🕒 Recent Activity")

        # Display log file content
        try:
            with open("qr_scan_log.txt", "r", encoding="utf-8") as log_file:
                log_lines = log_file.readlines()
                if log_lines:
                    # Show last 5 entries
                    recent_entries = log_lines[-5:]
                    for entry in recent_entries:
                        st.text(entry.strip())
                else:
                    st.text("No recent activity")
        except FileNotFoundError:
            st.text("No log file found")

        # Instructions
        st.markdown("---")
        st.subheader("📖 Instructions")
        st.markdown("""
        1. **Select a worksheet** from the sidebar
        2. **Point your camera** at a QR code
        3. **Wait for scan** - data will be posted automatically
        4. **Check status** for confirmation
        """)

        # Data format info
        st.markdown("---")
        st.subheader("📋 Expected Data Format")
        st.markdown("""
        QR codes should contain comma-separated data:
        ```
        Course Name, Student ID, Student Name
        ```
        Example:
        ```
        影音行銷培力課程,STU001,張小明
        ```
        """)

        # Connection status
        st.markdown("---")
        st.subheader("🔗 Connection Status")

        try:
            # Test Google Sheets connection
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=scopes)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID).worksheet(selected_sheet)
            st.success("✅ Connected to Google Sheets")
        except Exception as e:
            st.error(f"❌ Google Sheets connection failed: {e}")


if __name__ == "__main__":
    main()
