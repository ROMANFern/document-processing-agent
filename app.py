import streamlit as st
import sys
import os
os.environ['PYARROW_IGNORE_TIMEZONE'] = '1'

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from extractor import InvoiceExtractor
from smart_validator import SmartValidator
import json

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
    st.header("Upload Invoice")
    
    uploaded_file = st.file_uploader(
        "Choose an invoice file",
        type=['txt'],
        help="Upload a text file containing invoice data"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        process_button = st.button("🚀 Process Invoice", type="primary", use_container_width=True)
    
    if uploaded_file is not None and process_button:
        with st.spinner("🔄 Processing invoice..."):
            try:
                # Read the file
                invoice_text = uploaded_file.read().decode('utf-8')
                
                # Initialize processors
                extractor = InvoiceExtractor()
                validator = SmartValidator()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Extract
                status_text.text("⚙️ Extracting data from invoice...")
                progress_bar.progress(33)
                invoice = extractor.extract_from_text(invoice_text)
                
                # Step 2: Validate
                status_text.text("⚙️ Running validation checks...")
                progress_bar.progress(66)
                validation = validator.validate(invoice)
                
                # Step 3: Complete
                status_text.text("✅ Processing complete!")
                progress_bar.progress(100)
                
                # Update statistics
                st.session_state.processed_count += 1
                if validation.is_valid:
                    st.session_state.valid_count += 1
                else:
                    st.session_state.invalid_count += 1
                
                # Store results in session state
                if 'results' not in st.session_state:
                    st.session_state.results = []
                
                st.session_state.results.append({
                    'invoice': invoice,
                    'validation': validation,
                    'filename': uploaded_file.name
                })
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Show success message
                if validation.is_valid:
                    st.success(f"✅ Invoice {invoice.invoice_number} processed successfully - No issues found!")
                else:
                    st.error(f"❌ Invoice {invoice.invoice_number} has issues that need attention!")
                
                # Display results immediately
                st.markdown("---")
                display_invoice_result(invoice, validation, uploaded_file.name)
                
            except Exception as e:
                st.error(f"❌ Error processing invoice: {str(e)}")
                st.exception(e)

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
        st.write(f"Export {len(st.session_state.results)} processed invoice(s)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export as JSON", use_container_width=True):
                # Prepare data for export
                export_data = []
                for result in st.session_state.results:
                    export_data.append({
                        'filename': result['filename'],
                        'invoice': result['invoice'].to_dict(),
                        'validation': result['validation'].to_dict()
                    })
                
                # Convert to JSON
                json_str = json.dumps(export_data, indent=2)
                
                # Create download button
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json_str,
                    file_name="processed_invoices.json",
                    mime="application/json"
                )
        
        with col2:
            st.info("📊 CSV export coming soon!")
        
        # Show preview
        with st.expander("👁️ Preview Export Data"):
            for result in st.session_state.results:
                st.json({
                    'invoice_number': result['invoice'].invoice_number,
                    'vendor': result['invoice'].vendor_name,
                    'total': result['invoice'].total_amount,
                    'status': 'VALID' if result['validation'].is_valid else 'INVALID',
                    'issues': len(result['validation'].issues),
                    'warnings': len(result['validation'].warnings)
                })
    else:
        st.info("📭 No results to export yet. Process some invoices first!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Built with Streamlit, OpenAI GPT-4, and Python</p>
    <p>Smart Document Processing Agent v1.0</p>
</div>
""", unsafe_allow_html=True)