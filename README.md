# 📄 Smart Document Processing Agent

AI-powered invoice extraction and validation system that combines rule-based checks with intelligent semantic analysis.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Live Demo

**[Try it here →](https://document-processing-agent-srwydtlh8che4ey2eahklo.streamlit.app/)**

## 🎯 Problem Statement

Finance teams at small-to-medium businesses manually process hundreds of invoices monthly. Each document takes 5-10 minutes to:
- Extract vendor, date, amount, and line items
- Validate calculations and check for duplicates
- Flag policy violations or suspicious patterns
- Enter data into accounting systems

**Cost:** 50-80 hours/month of manual work = $2,500-4,000 in labor costs

## 💡 Solution

An intelligent document processing agent that:
1. **Extracts** structured data from unstructured invoices using GPT-4
2. **Validates** with 9+ rule-based checks (math, duplicates, format)
3. **Analyzes** semantically with AI to detect warnings and suspicious patterns
4. **Exports** results to CSV/JSON for accounting system integration

**Impact:** Reduces processing time by 80%, saving 40-60 hours per month

## ✨ Features

### Core Functionality
- ✅ **AI-Powered Extraction** - GPT-4 converts unstructured invoice text to structured JSON
- ✅ **Hybrid Validation** - Combines fast rule-based checks with intelligent semantic analysis
- ✅ **Batch Processing** - Upload and process multiple invoices simultaneously
- ✅ **Multi-Format Export** - Summary CSV, Line Items CSV, and complete JSON export

### Intelligence Layer
- 🧠 **Duplicate Detection** - Catches both identical invoice numbers and text-based warnings
- 🧮 **Math Validation** - Verifies subtotals, tax calculations, and line item amounts
- 📊 **Pattern Recognition** - Identifies suspicious patterns and policy violations
- 💰 **Threshold Alerts** - Flags high-value items requiring approval

### Analytics Dashboard
- 📈 **Visual Analytics** - Pie charts for validation status, bar charts for invoice values
- 📊 **Issue Analysis** - Most common problems, vendor reliability metrics
- 💵 **Financial Summary** - Total amounts, averages, and line item statistics
- 🎯 **Real-time Metrics** - Processing stats and success rates

## 🛠️ Tech Stack

**AI/ML:**
- OpenAI GPT-4-mini for data extraction
- Custom prompt engineering for semantic analysis
- Hybrid validation architecture (rule-based + AI)

**Backend:**
- Python 3.11
- OpenAI API v2.8.1
- Custom validation engine with 9+ check types

**Frontend:**
- Streamlit for web interface
- Plotly for interactive visualizations
- Pandas for data processing and export

**Architecture:**
- Multi-layer validation (rules → AI → human review)
- Session state management for batch processing
- Modular design for easy extension

## 📁 Project Structure
```
document-processing-agent/
├── app.py                      # Main Streamlit application
├── src/
│   ├── extractor.py           # GPT-4 extraction logic
│   ├── validator.py           # Rule-based validation
│   ├── smart_validator.py    # AI-powered semantic validation
│   ├── models.py              # Data models (Invoice, LineItem, etc.)
│   ├── test_pipeline.py       # End-to-end testing suite
│   └── test_extraction.py     # Extraction module tests
├── data/                       # Sample invoices for testing
├── output/                     # Processed results (JSON)
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ROMANFern/document-processing-agent.git
cd document-processing-agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_api_key_here
```

5. **Run the application:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Testing

Run the test suite to verify everything works:
```bash
# Test extraction only
python src/test_extraction.py

# Test complete pipeline
python src/test_pipeline.py
```

## 📊 Usage Examples

### Single Invoice Processing

1. Navigate to **"Upload & Process"** tab
2. Upload a `.txt` invoice file
3. Click **"Process"**
4. View extracted data and validation results

### Batch Processing

1. Switch to **"Batch Upload"** mode
2. Select multiple invoice files
3. Click **"Process"** to process all files
4. View summary metrics and individual results

### Export Data

1. Go to **"Export"** tab after processing
2. Choose format:
   - **Summary CSV** - Invoice-level data for accounting systems
   - **Line Items CSV** - Detailed item breakdown for inventory
   - **Complete JSON** - Full structured data for API integration

### Analytics Dashboard

1. Navigate to **"Dashboard"** tab
2. View validation status distribution
3. Analyze invoice values by vendor
4. Review common issues and warnings
5. Check financial summaries

## 🎯 Validation Checks

### Rule-Based Checks (9 types)
1. Required fields validation
2. Duplicate invoice number detection
3. Math accuracy (subtotals, line items)
4. Tax calculation verification (10% GST)
5. Total amount validation
6. High-value threshold alerts ($50k+ invoices)
7. Line item amount checks ($10k+ items)
8. ABN format validation
9. Date consistency checks

### AI-Powered Semantic Analysis
- Explicit duplicate warnings in text
- Suspicious payment detail changes
- Unusual payment method requests
- Context-aware pattern recognition
- Natural language understanding of notes/warnings

## 💰 Cost Optimization

**API Costs per invoice:**
- Extraction: ~$0.03-0.05 (GPT-4-mini)
- Validation: ~$0.02-0.03 (semantic analysis)
- **Total: ~$0.05-0.08 per invoice**

**For 500 invoices/month:** ~$25-40 in API costs vs $2,500-4,000 in labor savings

**Cost reduction strategies:**
- Use GPT-4-mini instead of GPT-4 (90% cheaper, minimal quality loss)
- Rule-based validation first (free, instant)
- AI validation only for semantic analysis
- Batch processing to reduce overhead

## 🔮 Future Enhancements

- [ ] PDF support with OCR
- [ ] Multi-language invoice processing
- [ ] Purchase order matching
- [ ] Approval workflow automation
- [ ] Integration with accounting systems (QuickBooks, Xero)
- [ ] Email ingestion (process invoices from inbox)
- [ ] Mobile app for on-the-go processing
- [ ] Advanced fraud detection models
- [ ] Custom validation rule builder

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Manusha Fernando**
- LinkedIn: [Manusha Fernando](https://linkedin.com/in/manusha-fernando/)
- GitHub: [@ROMANFern](https://github.com/ROMANFern)
- Email: manusha@romanfern.com

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI GPT-4](https://openai.com/)
- Visualization with [Plotly](https://plotly.com/)

## 📸 Screenshots

### Main Interface
*Upload and process invoices with real-time progress tracking*

### Dashboard Analytics
*Visual insights into processing results and validation status*

### Export Options
*Multiple export formats for seamless integration*

---

**⭐ If you find this project useful, please consider giving it a star!**