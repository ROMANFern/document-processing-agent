import streamlit as st
import sys
import os
import json
import pandas as pd
from io import StringIO
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

os.environ['PYARROW_IGNORE_TIMEZONE'] = '1'

# Add src to path to import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from extractor import InvoiceExtractor
from smart_validator import SmartValidator

def display_invoice_result(invoice, validation, filename):
    """Display a single invoice result with formatting"""
    
    # Determine card style based on validation
    if validation.is_valid and not validation.warnings:
        card_class = "valid-card"
        status_icon = "✅"
        status_text = "VALID"
    elif validation.is_valid and validation.warnings:
        card_class = "warning-card"
        status_icon = "⚠️"
        status_text = "VALID (with warnings)"
    else:
        card_class = "invalid-card"
        status_icon = "❌"
        status_text = "INVALID"
    
    # Invoice header card
    st.markdown(f"""
    <div class="invoice-card {card_class}">
        <h3>{status_icon} {invoice.invoice_number} - {status_text}</h3>
        <p><strong>File:</strong> {filename}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Details in expandable sections
    with st.expander("📋 Invoice Details", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Basic Information**")
            st.write(f"**Invoice Number:** {invoice.invoice_number}")
            st.write(f"**Date:** {invoice.invoice_date}")
            st.write(f"**Due Date:** {invoice.due_date}")
        
        with col2:
            st.markdown("**Vendor Information**")
            st.write(f"**Name:** {invoice.vendor_name}")
            if invoice.vendor_abn:
                st.write(f"**ABN:** {invoice.vendor_abn}")
        
        with col3:
            st.markdown("**Customer Information**")
            st.write(f"**Name:** {invoice.customer_name}")
    
    with st.expander("🧾 Line Items", expanded=True):
        # Create a nice table for line items
        if invoice.line_items:
            line_items_data = []
            for item in invoice.line_items:
                line_items_data.append({
                    "Description": item.description,
                    "Quantity": f"{item.quantity:,.2f}",
                    "Unit Price": f"${item.unit_price:,.2f}",
                    "Amount": f"${item.amount:,.2f}"
                })
            
            st.table(line_items_data)
            
            # Totals
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                st.markdown("**Subtotal:**")
                st.markdown("**Tax:**")
                st.markdown("**Total:**")
            with col3:
                st.markdown(f"${invoice.subtotal:,.2f}")
                st.markdown(f"${invoice.tax_amount:,.2f}")
                st.markdown(f"**${invoice.total_amount:,.2f}**")
    
    with st.expander("🔍 Validation Results", expanded=True):
        if validation.issues:
            st.markdown("#### 🚨 Critical Issues")
            for issue in validation.issues:
                st.error(f"• {issue}")
        
        if validation.warnings:
            st.markdown("#### ⚠️ Warnings")
            for warning in validation.warnings:
                st.warning(f"• {warning}")
        
        if not validation.issues and not validation.warnings:
            st.success("✅ No issues or warnings detected. Invoice looks good!")

def export_to_csv(results):
    """Convert results to CSV format"""
    data = []
    
    for result in results:
        invoice = result['invoice']
        validation = result['validation']
        
        # Basic invoice data
        row = {
            'Filename': result['filename'],
            'Invoice Number': invoice.invoice_number,
            'Invoice Date': invoice.invoice_date,
            'Due Date': invoice.due_date,
            'Vendor Name': invoice.vendor_name,
            'Vendor ABN': invoice.vendor_abn or '',
            'Customer Name': invoice.customer_name,
            'Subtotal': invoice.subtotal,
            'Tax Amount': invoice.tax_amount,
            'Total Amount': invoice.total_amount,
            'Line Items Count': len(invoice.line_items),
            'Status': 'VALID' if validation.is_valid else 'INVALID',
            'Issues Count': len(validation.issues),
            'Warnings Count': len(validation.warnings),
            'Issues': ' | '.join(validation.issues) if validation.issues else '',
            'Warnings': ' | '.join(validation.warnings) if validation.warnings else '',
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    return df

def export_line_items_to_csv(results):
    """Export detailed line items to CSV"""
    data = []
    
    for result in results:
        invoice = result['invoice']
        
        for item in invoice.line_items:
            row = {
                'Invoice Number': invoice.invoice_number,
                'Vendor Name': invoice.vendor_name,
                'Line Item Description': item.description,
                'Quantity': item.quantity,
                'Unit Price': item.unit_price,
                'Amount': item.amount,
            }
            data.append(row)
    
    df = pd.DataFrame(data)
    return df

def process_with_status(uploaded_file, extractor, validator, show_logs=False):
    """Process a single invoice with detailed status updates"""
    try:
        if show_logs:
            st.write(f"📄 Reading file: {uploaded_file.name}")
        
        invoice_text = uploaded_file.read().decode('utf-8')
        
        if show_logs:
            st.write(f"📝 Text length: {len(invoice_text)} characters")
            st.write("🤖 Calling extraction API...")
        
        invoice = extractor.extract_from_text(invoice_text)
        
        if show_logs:
            st.write(f"✅ Extracted {len(invoice.line_items)} line items")
            st.write("🔍 Running validation...")
        
        validation = validator.validate(invoice)
        
        if show_logs:
            st.write(f"✅ Validation complete: {len(validation.issues)} issues, {len(validation.warnings)} warnings")
        
        return invoice, validation, None
        
    except Exception as e:
        return None, None, str(e)

# Page configuration
st.set_page_config(
    page_title="Smart Document Processing Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .invoice-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .valid-card {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .invalid-card {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .warning-card {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📄 Smart Document Processing Agent")
st.markdown("""
AI-powered invoice extraction and validation system that combines rule-based checks 
with intelligent semantic analysis.
""")

# Welcome message for new users
if 'results' not in st.session_state or len(st.session_state.get('results', [])) == 0:
    st.info("""
    👋 **Welcome to the Smart Document Processing Agent!**
    
    Get started by uploading an invoice in the **Upload & Process** tab.
    You can process single invoices or batch upload multiple files.
    
    💡 **Tip:** Try the sample invoice generator in the sidebar to create test files!
    """)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This system uses:
    - **GPT-4** for data extraction
    - **Rule-based validation** for math & format checks
    - **AI semantic analysis** for context understanding
    
    **Features:**
    - ✅ Extract structured data from invoices
    - ✅ Validate calculations and formats
    - ✅ Detect duplicates and suspicious patterns
    - ✅ Batch processing support
    - ✅ Export to JSON/CSV
    - ✅ Visual analytics dashboard
    """)
    
    st.markdown("---")
    st.header("📊 Session Statistics")
    
    # Initialize session state
    if 'processed_count' not in st.session_state:
        st.session_state.processed_count = 0
    if 'valid_count' not in st.session_state:
        st.session_state.valid_count = 0
    if 'invalid_count' not in st.session_state:
        st.session_state.invalid_count = 0
    if 'total_api_calls' not in st.session_state:
        st.session_state.total_api_calls = 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Processed", st.session_state.processed_count)
        st.metric("Valid", st.session_state.valid_count)
    with col2:
        st.metric("Invalid", st.session_state.invalid_count)
        success_rate = (st.session_state.valid_count / st.session_state.processed_count * 100) if st.session_state.processed_count > 0 else 0
        st.metric("Success Rate", f"{success_rate:.0f}%")
    
    st.markdown("---")
    st.header("🛠️ Settings")
    
    # Add processing options
    with st.expander("⚙️ Processing Options"):
        st.checkbox("Enable AI validation", value=True, help="Use AI for semantic analysis (costs ~$0.05/invoice)", key="enable_ai")
        st.checkbox("Show detailed logs", value=False, help="Display processing logs for debugging", key="show_logs")
        
    with st.expander("📁 Sample Files"):
        st.markdown("""
        **Test with sample invoices:**
        - sample_invoice_1.txt ✅ (Valid)
        - sample_invoice_2.txt ❌ (Duplicate warning)
        - sample_invoice_3.txt ❌ (Duplicate number)
        
        Create your own test files following the same format!
        """)
    
    st.markdown("---")
    st.header("🧪 Testing Tools")
    
    with st.expander("Generate Sample Invoice"):
        st.write("Create a test invoice for development")
        
        sample_type = st.selectbox(
            "Sample type:",
            ["Valid Invoice", "Invoice with Math Error", "Duplicate Warning", "High Value Invoice"]
        )
        
        if st.button("Generate Sample", use_container_width=True):
            if sample_type == "Valid Invoice":
                sample_text = f"""INVOICE

Bill To:                          Invoice Number: INV-TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}
Test Company Pty Ltd              Date: {datetime.now().strftime('%B %d, %Y')}
123 Test Street                   Due Date: {datetime.now().strftime('%B %d, %Y')}
Melbourne VIC 3000

From:
Sample Vendor Ltd
456 Vendor Ave
Sydney NSW 2000
ABN: 12 345 678 901

Description                       Quantity    Unit Price    Amount
----------------------------------------------------------------
Professional Services            10 hours    $150.00       $1,500.00
Software License                 1           $500.00       $500.00

                                             Subtotal:      $2,000.00
                                             GST (10%):     $200.00
                                             Total:         $2,200.00

Payment Terms: Net 30 days
"""
            elif sample_type == "Invoice with Math Error":
                sample_text = f"""INVOICE

Invoice Number: INV-ERROR-{datetime.now().strftime('%Y%m%d-%H%M%S')}
Date: {datetime.now().strftime('%B %d, %Y')}

From: Test Vendor
To: Test Customer

Line Items:
Item A    5    $100.00    $500.00
Item B    3    $200.00    $650.00  <- ERROR: Should be $600.00

Subtotal: $1,150.00  <- ERROR: Should be $1,100.00
GST: $115.00
Total: $1,265.00
"""
            elif sample_type == "Duplicate Warning":
                sample_text = f"""INVOICE

Invoice Number: INV-DUP-{datetime.now().strftime('%Y%m%d-%H%M%S')}
Date: {datetime.now().strftime('%B %d, %Y')}

From: Test Vendor
To: Test Customer

Line Items:
Service A    1    $1,000.00    $1,000.00

Subtotal: $1,000.00
GST: $100.00
Total: $1,100.00

NOTE: This is a DUPLICATE of previous invoice INV-2024-999
"""
            else:  # High Value Invoice
                sample_text = f"""INVOICE

Invoice Number: INV-HIGH-{datetime.now().strftime('%Y%m%d-%H%M%S')}
Date: {datetime.now().strftime('%B %d, %Y')}

From: Enterprise Vendor Ltd
To: Large Customer Corp

Line Items:
Enterprise Software Suite    1    $75,000.00    $75,000.00
Implementation Services      200 hours    $250.00    $50,000.00

Subtotal: $125,000.00
GST: $12,500.00
Total: $137,500.00
"""
            
            # Offer download
            st.download_button(
                label="⬇️ Download Sample Invoice",
                data=sample_text,
                file_name=f"sample_{sample_type.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.code(sample_text, language="text")

    with st.expander("⌨️ Keyboard Shortcuts"):
        st.markdown("""
        - `R` - Rerun app
        - `Ctrl/Cmd + K` - Clear cache
        - `Ctrl/Cmd + Enter` - Run command
        """)
        
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit & OpenAI")
    st.caption("v1.0 | Smart Document Processing Agent")

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "📊 Results", "📈 Dashboard", "💾 Export"])
with tab1:
    st.header("Upload Invoice(s)")
    
    # Add option for single or batch upload
    upload_mode = st.radio(
        "Upload Mode:",
        ["Single Invoice", "Batch Upload"],
        horizontal=True
    )
    
    if upload_mode == "Single Invoice":
        uploaded_file = st.file_uploader(
            "Choose an invoice file",
            type=['txt'],
            help="Upload a text file containing invoice data"
        )
        uploaded_files = [uploaded_file] if uploaded_file else []
    else:
        uploaded_files = st.file_uploader(
            "Choose invoice files",
            type=['txt'],
            accept_multiple_files=True,
            help="Upload multiple text files containing invoice data"
        )
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) selected")
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        process_button = st.button("🚀 Process", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.results = []
            st.session_state.processed_count = 0
            st.session_state.valid_count = 0
            st.session_state.invalid_count = 0
            st.rerun()
    
    if uploaded_files and process_button:
        # Initialize processors once
        extractor = InvoiceExtractor()
        validator = SmartValidator()
        
        # Process each file
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_files = len(uploaded_files)
        successful = 0
        failed = 0
        
        for idx, uploaded_file in enumerate(uploaded_files):
            if uploaded_file is None:
                continue
                
            try:
                # Update progress
                progress = (idx + 1) / total_files
                progress_bar.progress(progress)
                status_text.text(f"Processing {idx + 1}/{total_files}: {uploaded_file.name}")
                
                # Read the file
                invoice_text = uploaded_file.read().decode('utf-8')
                
                # Extract and validate
                invoice = extractor.extract_from_text(invoice_text)
                validation = validator.validate(invoice)
                
                # Update statistics
                st.session_state.processed_count += 1
                if validation.is_valid:
                    st.session_state.valid_count += 1
                else:
                    st.session_state.invalid_count += 1
                
                # Store results
                if 'results' not in st.session_state:
                    st.session_state.results = []
                
                st.session_state.results.append({
                    'invoice': invoice,
                    'validation': validation,
                    'filename': uploaded_file.name
                })
                
                successful += 1
                
            except Exception as e:
                failed += 1
                st.error(f"❌ Failed to process {uploaded_file.name}: {str(e)}")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Show summary
        if successful > 0:
            st.success(f"✅ Successfully processed {successful}/{total_files} invoice(s)")
        if failed > 0:
            st.warning(f"⚠️ Failed to process {failed}/{total_files} invoice(s)")
        
        # Show results summary
        if successful > 0:
            st.markdown("---")
            st.subheader("Quick Summary")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Processed", successful)
            with col2:
                valid = sum(1 for r in st.session_state.results if r['validation'].is_valid)
                st.metric("Valid", valid, delta=f"{valid/successful*100:.0f}%")
            with col3:
                invalid = successful - valid
                st.metric("Invalid", invalid, delta=f"{invalid/successful*100:.0f}%" if invalid > 0 else "0%")
            
            st.info("💡 View detailed results in the 'Results' tab")

with tab2:
    st.header("Processing Results")
    
    if 'results' in st.session_state and st.session_state.results:
        st.write(f"**Total Processed:** {len(st.session_state.results)} invoice(s)")
        
        for idx, result in enumerate(st.session_state.results):
            st.markdown(f"### Invoice {idx + 1}")
            display_invoice_result(
                result['invoice'],
                result['validation'],
                result['filename']
            )
            st.markdown("---")
    else:
        st.info("📭 No invoices processed yet. Upload and process an invoice in the 'Upload & Process' tab.")

with tab3:
    st.header("📈 Processing Dashboard")
    
    if 'results' in st.session_state and st.session_state.results:
        results = st.session_state.results
        
        # Overview metrics
        st.subheader("Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(results)
        valid = sum(1 for r in results if r['validation'].is_valid)
        invalid = total - valid
        total_value = sum(r['invoice'].total_amount for r in results)
        
        with col1:
            st.metric("Total Invoices", total)
        with col2:
            st.metric("Valid", valid, delta=f"{valid/total*100:.0f}%", delta_color="normal")
        with col3:
            st.metric("Invalid", invalid, delta=f"{invalid/total*100:.0f}%" if invalid > 0 else "0%", delta_color="inverse")
        with col4:
            st.metric("Total Value", f"${total_value:,.2f}")
        
        st.markdown("---")
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Validation Status")
            
            # Pie chart for validation status
            fig = go.Figure(data=[go.Pie(
                labels=['Valid', 'Invalid'],
                values=[valid, invalid],
                marker=dict(colors=['#28a745', '#dc3545']),
                hole=0.3
            )])
            fig.update_layout(
                showlegend=True,
                height=300,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Invoice Values")
            
            # Bar chart for invoice values
            invoice_data = pd.DataFrame([
                {
                    'Invoice': r['invoice'].invoice_number,
                    'Amount': r['invoice'].total_amount,
                    'Status': 'Valid' if r['validation'].is_valid else 'Invalid'
                }
                for r in results
            ])
            
            fig = px.bar(
                invoice_data,
                x='Invoice',
                y='Amount',
                color='Status',
                color_discrete_map={'Valid': '#28a745', 'Invalid': '#dc3545'},
                title='Invoice Amounts by Status'
            )
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="",
                yaxis_title="Amount ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Issue analysis
        st.subheader("Issue Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Count issues and warnings
            issue_count = sum(len(r['validation'].issues) for r in results)
            warning_count = sum(len(r['validation'].warnings) for r in results)
            
            st.metric("Total Issues", issue_count, delta="Critical" if issue_count > 0 else "None", delta_color="inverse")
            st.metric("Total Warnings", warning_count, delta="Review needed" if warning_count > 0 else "None", delta_color="off")
            
            # Most common issues
            if issue_count > 0:
                st.markdown("**Most Common Issues:**")
                all_issues = []
                for r in results:
                    all_issues.extend(r['validation'].issues)
                
                # Count occurrences
                from collections import Counter
                issue_counts = Counter(all_issues)
                
                for issue, count in issue_counts.most_common(5):
                    st.write(f"• {issue[:80]}{'...' if len(issue) > 80 else ''} ({count}x)")
        
        with col2:
            # Vendor analysis
            vendor_data = {}
            for r in results:
                vendor = r['invoice'].vendor_name
                if vendor not in vendor_data:
                    vendor_data[vendor] = {'count': 0, 'total': 0, 'valid': 0}
                vendor_data[vendor]['count'] += 1
                vendor_data[vendor]['total'] += r['invoice'].total_amount
                if r['validation'].is_valid:
                    vendor_data[vendor]['valid'] += 1
            
            st.markdown("**Vendor Summary:**")
            vendor_df = pd.DataFrame([
                {
                    'Vendor': vendor,
                    'Invoices': data['count'],
                    'Total': f"${data['total']:,.2f}",
                    'Valid Rate': f"{data['valid']/data['count']*100:.0f}%"
                }
                for vendor, data in vendor_data.items()
            ])
            st.dataframe(vendor_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Detailed breakdown
        st.subheader("Detailed Breakdown")
        
        with st.expander("📋 All Issues and Warnings"):
            for idx, result in enumerate(results):
                invoice = result['invoice']
                validation = result['validation']
                
                if validation.issues or validation.warnings:
                    st.markdown(f"**{invoice.invoice_number}** - {result['filename']}")
                    
                    if validation.issues:
                        st.error("Issues:")
                        for issue in validation.issues:
                            st.write(f"  • {issue}")
                    
                    if validation.warnings:
                        st.warning("Warnings:")
                        for warning in validation.warnings:
                            st.write(f"  • {warning}")
                    
                    st.markdown("---")
        
        with st.expander("💰 Financial Summary"):
            col1, col2, col3 = st.columns(3)
            
            total_subtotal = sum(r['invoice'].subtotal for r in results)
            total_tax = sum(r['invoice'].tax_amount for r in results)
            avg_invoice = total_value / total
            
            with col1:
                st.metric("Total Subtotal", f"${total_subtotal:,.2f}")
                st.metric("Total Tax", f"${total_tax:,.2f}")
            
            with col2:
                st.metric("Average Invoice", f"${avg_invoice:,.2f}")
                highest = max(r['invoice'].total_amount for r in results)
                st.metric("Highest Invoice", f"${highest:,.2f}")
            
            with col3:
                total_items = sum(len(r['invoice'].line_items) for r in results)
                st.metric("Total Line Items", total_items)
                st.metric("Avg Items/Invoice", f"{total_items/total:.1f}")
        
    else:
        st.info("📭 No data to display yet. Process some invoices first!")
        
        st.markdown("---")
        st.markdown("""
        ### 📈 Dashboard Features
        
        Once you process invoices, you'll see:
        
        **Overview Metrics**
        - Total invoices processed
        - Validation success rate
        - Total invoice value
        
        **Visual Analytics**
        - Validation status distribution (pie chart)
        - Invoice values comparison (bar chart)
        - Trend analysis
        
        **Issue Analysis**
        - Most common issues
        - Warning patterns
        - Vendor reliability scores
        
        **Financial Summary**
        - Total amounts and taxes
        - Average invoice values
        - Line item statistics
        """)

with tab4:
    st.header("Export Results")
    
    if 'results' in st.session_state and st.session_state.results:
        st.write(f"📊 Export {len(st.session_state.results)} processed invoice(s)")
        
        # Export options
        st.subheader("Choose Export Format")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📄 Summary CSV")
            st.write("Invoice-level summary with validation results")
            
            if st.button("Generate Summary CSV", use_container_width=True):
                df = export_to_csv(st.session_state.results)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Download Summary CSV",
                    data=csv,
                    file_name="invoice_summary.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                with st.expander("Preview Summary CSV"):
                    st.dataframe(df, use_container_width=True)
        
        with col2:
            st.markdown("#### 🧾 Line Items CSV")
            st.write("Detailed line-by-line item breakdown")
            
            if st.button("Generate Line Items CSV", use_container_width=True):
                df = export_line_items_to_csv(st.session_state.results)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Download Line Items CSV",
                    data=csv,
                    file_name="invoice_line_items.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                with st.expander("Preview Line Items CSV"):
                    st.dataframe(df, use_container_width=True)
        
        with col3:
            st.markdown("#### 📦 Complete JSON")
            st.write("Full data export with all details")
            
            # Prepare data for export
            export_data = []
            for result in st.session_state.results:
                export_data.append({
                    'filename': result['filename'],
                    'invoice': result['invoice'].to_dict(),
                    'validation': result['validation'].to_dict()
                })
            
            json_str = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="⬇️ Download JSON",
                data=json_str,
                file_name="processed_invoices.json",
                mime="application/json",
                use_container_width=True
            )
            
            with st.expander("Preview JSON Structure"):
                st.json(export_data[0] if export_data else {})
        
        # Show export statistics
        st.markdown("---")
        st.subheader("Export Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_amount = sum(r['invoice'].total_amount for r in st.session_state.results)
        valid_amount = sum(r['invoice'].total_amount for r in st.session_state.results if r['validation'].is_valid)
        total_items = sum(len(r['invoice'].line_items) for r in st.session_state.results)
        
        with col1:
            st.metric("Total Invoice Value", f"${total_amount:,.2f}")
        with col2:
            st.metric("Valid Invoice Value", f"${valid_amount:,.2f}")
        with col3:
            st.metric("Total Line Items", total_items)
        with col4:
            avg_items = total_items / len(st.session_state.results)
            st.metric("Avg Items/Invoice", f"{avg_items:.1f}")
        
    else:
        st.info("📭 No results to export yet. Process some invoices first!")
        
        st.markdown("---")
        st.subheader("Available Export Formats")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📄 Summary CSV")
            st.write("""
            - Invoice number, dates, amounts
            - Vendor and customer info
            - Validation status
            - Issue and warning counts
            - Perfect for accounting systems
            """)
        
        with col2:
            st.markdown("#### 🧾 Line Items CSV")
            st.write("""
            - Detailed line item breakdown
            - Item descriptions and quantities
            - Pricing information
            - Linked to invoice numbers
            - Great for inventory tracking
            """)
        
        with col3:
            st.markdown("#### 📦 Complete JSON")
            st.write("""
            - Full structured data export
            - All extracted fields
            - Complete validation results
            - API-ready format
            - For system integration
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Built with Streamlit, OpenAI GPT-4, and Python</p>
    <p>Smart Document Processing Agent v1.0</p>
</div>
""", unsafe_allow_html=True)