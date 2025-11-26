import streamlit as st
import sys
import os
import json
import pandas as pd
from io import StringIO

os.environ['PYARROW_IGNORE_TIMEZONE'] = '1'

# Add src to path so we can import our modules
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

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This system uses:
    - **GPT-4** for data extraction
    - **Rule-based validation** for math & format checks
    - **AI semantic analysis** for context understanding
    
    **Features:**
    - Extract structured data from invoices
    - Validate calculations and formats
    - Detect duplicates and suspicious patterns
    - Export results to JSON/CSV
    """)
    
    st.header("📊 Statistics")
    # We'll add stats here later
    if 'processed_count' not in st.session_state:
        st.session_state.processed_count = 0
    if 'valid_count' not in st.session_state:
        st.session_state.valid_count = 0
    if 'invalid_count' not in st.session_state:
        st.session_state.invalid_count = 0
    
    st.metric("Processed", st.session_state.processed_count)
    st.metric("Valid", st.session_state.valid_count)
    st.metric("Invalid", st.session_state.invalid_count)

# Main content area
tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📊 Results", "💾 Export"])

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