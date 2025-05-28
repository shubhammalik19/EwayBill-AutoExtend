# extendEwayBill Automation 🚛

**Automated E-Way Bill Extension Tool for Indian GST Portal**

A Python-based Selenium automation script that streamlines the process of extending E-Way Bills that are expiring today on the official ewaybillgst.gov.in portal. Perfect for businesses and logistics professionals who need to manage multiple E-Way Bill extensions efficiently.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Browser](https://img.shields.io/badge/Browser-Firefox-orange.svg)

---

## 🎯 What This Tool Does

This automation script handles the tedious process of extending E-Way Bills by:

- **🔐 Automatic Login**: Uses your saved credentials to log into the GST portal
- **📊 Smart Filtering**: Identifies E-Way Bills expiring today from your CSV data
- **🚛 Vehicle Detection**: Automatically scrapes current vehicle details from print pages
- **🔄 Bulk Extension**: Processes multiple E-Way Bills in sequence
- **📝 Detailed Logging**: Tracks success/failure with comprehensive logs
- **⚠️ Manual CAPTCHA**: Pauses for user to complete CAPTCHA verification

---

## ✨ Key Features

### 🤖 **Intelligent Automation**
- Filters E-Way Bills by expiration date (today's date)
- Extracts vehicle numbers and kilometers from existing records
- Handles form filling with validation and error recovery

### 📊 **Smart Time Management**
- Early morning detection (00:00-08:00) uses previous day's date
- Recommended execution window: 08:00-16:00 for optimal performance

### 🛡️ **Robust Error Handling**
- Multiple retry mechanisms for network issues
- Comprehensive logging system with 4 different log levels
- Graceful handling of missing data and timeouts

### 📋 **Professional Logging**
- **Debug logs**: Complete execution trace
- **Error logs**: Issues and exceptions only  
- **Operations logs**: High-level progress tracking
- **Results log**: Simple success/failure summary

---

## 🚀 Quick Start Guide

### 1. **Install Dependencies**

```bash
# Clone or download the script
git clone <your-repository-url>
cd extendEwayBill-automation

# Install required packages
pip install pandas selenium beautifulsoup4
```

### 2. **Setup Firefox Browser**

```bash
# Download and install Firefox browser
# Download geckodriver from: https://github.com/mozilla/geckodriver/releases
# Add geckodriver to your system PATH
```

### 3. **Prepare Configuration Files**

Create two essential files in the script directory:

#### **`user.json`** - Your Login Credentials
```json
{
    "user_name": "your_username",
    "password": "your_password"
}
```

#### **`eway.csv`** - Your E-Way Bill Data
```csv
EWB.No,Valid Untill,From Place,To Place,Document No
12345678901,28/05/2025,Mumbai,Delhi,DOC001
12345678902,28/05/2025,Chennai,Bangalore,DOC002
```

### 4. **Run the Script**

```bash
python extendEwayBill.py
```

---

## 📁 File Structure & Requirements

### **Required Files (You Create These)**

| File | Purpose | Format |
|------|---------|--------|
| `user.json` | Login credentials | JSON with `user_name` and `password` |
| `eway.csv` | E-Way Bill data | CSV with columns: `EWB.No`, `Valid Untill`, etc. |

### **Generated Files (Script Creates These)**

| File | Purpose | When to Share |
|------|---------|---------------|
| `logs/debug_TIMESTAMP.log` | Complete execution trace | 📧 **Send to support for debugging** |
| `logs/errors_TIMESTAMP.log` | Errors and exceptions only | 📧 **Send to support if issues occur** |
| `logs/operations_TIMESTAMP.log` | High-level progress | 📊 For your review |
| `log.txt` | Simple success/failure results | 📋 Quick reference |
| `eway.txt` | E-Way Bill and vehicle mapping | 🚛 Vehicle tracking |

---

## 🔧 Detailed Setup Instructions

### **Python Dependencies**

```bash
pip install pandas>=1.3.0
pip install selenium>=4.0.0
pip install beautifulsoup4>=4.9.0
```

### **Firefox & WebDriver Setup**

1. **Install Firefox Browser** (latest version recommended)
2. **Download GeckoDriver**:
   - Visit: https://github.com/mozilla/geckodriver/releases
   - Download version matching your OS
   - Extract to a folder in your system PATH

3. **Verify Installation**:
   ```bash
   geckodriver --version
   ```

### **CSV Data Format**

Your `eway.csv` must include these columns:

| Column | Example | Required |
|--------|---------|----------|
| `EWB.No` | `12345678901` | ✅ Yes |
| `Valid Untill` | `28/05/2025` | ✅ Yes |
| `From Place` | `Mumbai` | ❌ Optional |
| `To Place` | `Delhi` | ❌ Optional |
| `Document No` | `DOC001` | ❌ Optional |

**Date Format**: DD/MM/YYYY (e.g., `28/05/2025`)

---

## 🖥️ Browser & CAPTCHA Instructions

### **Browser Behavior**
- **Browser Type**: Firefox (non-headless by default)
- **Window**: Maximized for better visibility
- **Session**: Maintains login across multiple operations

### **CAPTCHA Handling** ⚠️
The script **DOES NOT** solve CAPTCHAs automatically. Here's what happens:

1. **Script pauses** at login screen when CAPTCHA appears
2. **You manually complete** the CAPTCHA
3. **Script automatically continues** once login is successful
4. **No manual intervention** needed after successful login

**💡 Tip**: Keep the browser window visible during execution to handle any unexpected CAPTCHAs.

---

## 📋 Usage Workflow

### **Step-by-Step Process**

1. **🔐 Login Phase**
   - Script navigates to ewaybillgst.gov.in
   - Enters your credentials from `user.json`
   - **PAUSES for CAPTCHA** (you complete manually)
   - Continues automatically after successful login

2. **🔍 Data Collection Phase**
   - Reads E-Way Bills from `eway.csv`
   - Filters bills expiring today
   - Visits print pages to extract vehicle details
   - Saves vehicle information for extensions

3. **🔄 Extension Phase**
   - Processes each E-Way Bill individually
   - Fills extension forms with collected data
   - Submits requests and monitors results
   - Logs success/failure for each bill

4. **📊 Completion**
   - Generates comprehensive logs
   - Creates summary report
   - Provides troubleshooting information

### **Recommended Execution Schedule**

- **⏰ Best Time**: 08:00 AM - 4:00 PM
- **🌅 Early Morning**: Uses previous day's date (00:00-08:00)
- **📅 Daily Run**: Execute once per day for expiring bills

---

## 🛠️ Developer Guide

### **Code Structure**

```
extendEwayBill.py
├── 📊 Logging Configuration (Lines 1-100)
├── 🔧 Utility Functions (Lines 101-200)
├── 🔐 Login Management (Lines 201-350)
├── 🚛 Vehicle Data Extraction (Lines 351-450)
├── 🔄 Extension Processing (Lines 451-600)
└── 🚀 Main Execution (Lines 601-700)
```

### **Key Classes & Methods**

| Component | Purpose | Entry Point |
|-----------|---------|-------------|
| `extendEwayBill` | Main automation class | `__init__()` |
| `fresh_login()` | Handles login with CSRF protection | Called before major operations |
| `getPrintEwayAndFindCurrentVehicle()` | Extracts vehicle details | Called in Step 1 |
| `extendEwayBills()` | Processes extensions | Called in Step 2 |

### **Adding New Features**

1. **🔍 Data Extraction**: Modify `getPrintEwayAndFindCurrentVehicle()`
2. **📝 Form Handling**: Update `extend_single_eway()`
3. **📊 Logging**: Use existing decorators `@log_function_call` or `@log_selenium_action`
4. **🛡️ Error Handling**: Follow existing try-catch patterns

### **Debugging Tips**

- **🐛 Debug Logs**: Check `logs/debug_TIMESTAMP.log` for detailed execution
- **🌐 URL Tracking**: Script logs all page navigation
- **📄 Element Detection**: Uses explicit waits for reliable element interaction
- **🔄 Retry Logic**: Most operations have 5-attempt retry mechanisms

---

## 🤝 Contributing

### **Getting Started**

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow coding standards**: Use existing logging patterns
4. **Test thoroughly**: Verify with sample data
5. **Submit pull request**: Include detailed description

### **Code Standards**

- **📊 Logging**: Use decorators for function entry/exit tracking
- **🛡️ Error Handling**: Implement retry logic for network operations
- **📝 Documentation**: Add docstrings for new functions
- **🧪 Testing**: Test with various CSV formats and scenarios

### **Areas for Contribution**

- **🔧 Enhanced Error Recovery**: Improve handling of network failures
- **🎨 UI Improvements**: Better progress indication
- **📊 Reporting**: Enhanced success/failure analytics
- **🌐 Browser Support**: Add Chrome/Edge compatibility
- **📱 Notifications**: Email/SMS alerts for completion

---

## ⚠️ Important Disclaimers

### **🔒 Security**
- **Never commit** `user.json` with real credentials to version control
- **Use environment variables** for production deployments
- **Regularly update** passwords and review access logs

### **🏛️ Legal & Compliance**
- **Authorized Use Only**: Use only with your own GST credentials
- **Rate Limiting**: Script includes delays to avoid overwhelming servers
- **Terms of Service**: Ensure compliance with GST portal's terms of use
- **Data Protection**: Handle E-Way Bill data according to your privacy policies

### **🛡️ Technical Limitations**
- **CAPTCHA Manual**: Cannot solve CAPTCHAs automatically
- **Network Dependent**: Requires stable internet connection
- **Portal Changes**: May need updates if GST portal changes structure
- **Browser Specific**: Currently supports Firefox only

### **📞 Support**
- **🐛 Bug Reports**: Include debug logs and detailed steps to reproduce
- **💡 Feature Requests**: Describe use case and expected behavior
- **❓ Questions**: Check logs first, then contact with specific error messages

---

## 📊 Performance & Monitoring

### **Typical Execution Times**
- **🔐 Login**: 30-60 seconds (including CAPTCHA)
- **🚛 Vehicle Data**: 15-30 seconds per E-Way Bill
- **🔄 Extension**: 20-40 seconds per E-Way Bill
- **📊 Total**: ~1-2 minutes per E-Way Bill

### **Resource Usage**
- **💾 Memory**: ~100-200 MB during execution
- **🌐 Network**: Moderate (respects server rate limits)
- **💾 Disk**: Minimal (logs and result files)

---

## 🏷️ Tags & Keywords

`python` `selenium` `automation` `gst` `eway-bill` `indian-government` `logistics` `firefox` `web-scraping` `business-automation` `tax-compliance` `bulk-processing` `data-extraction` `form-automation` `transportation`

---

---

## 👨‍💻 About the Creator

**Created by Shubham Malik** | **Version 1.0** | **Last Updated: May 2025**

### 🚛 **Mission Statement**
*"Always committed to the development of Transport and Logistics Infrastructure to speed up the supply chain and help the country grow."*

Shubham Malik is dedicated to building automation solutions that streamline India's logistics ecosystem, reduce bureaucratic delays, and empower businesses to focus on growth rather than paperwork. This tool represents a commitment to:

- **🇮🇳 National Growth**: Supporting India's economic development through efficient logistics
- **⚡ Supply Chain Acceleration**: Reducing manual processing time from hours to minutes  
- **🏢 Business Empowerment**: Enabling small and large enterprises to manage compliance effortlessly
- **🔬 Continuous Innovation**: Developing tools that adapt to India's evolving digital infrastructure

### 🌟 **Vision for Indian Logistics**
By automating repetitive government portal interactions, we aim to:
- **📈 Boost Productivity**: Free up valuable human resources for strategic work
- **🔄 Improve Accuracy**: Eliminate manual errors in compliance processes
- **💰 Reduce Costs**: Lower operational overhead for transportation businesses
- **🚀 Scale Operations**: Enable businesses to handle larger volumes efficiently

---

## ⚖️ Legal Disclaimer & Terms of Use

### 🛡️ **Creator's Liability Limitation**

**IMPORTANT NOTICE**: This software is provided "AS IS" without warranty of any kind. The creator, Shubham Malik, shall NOT be held liable for:

- **❌ Misuse of Software**: Any unauthorized, illegal, or non-compliant use of this tool
- **🚫 Portal Violations**: Breach of GST portal terms of service by end users
- **💸 Financial Losses**: Any direct or indirect financial damages resulting from software use
- **📊 Data Issues**: Loss, corruption, or mishandling of user data
- **🏛️ Legal Consequences**: Any legal action arising from improper usage
- **⚡ System Failures**: Server downtime, network issues, or technical malfunctions

### 📋 **User Responsibilities**

By using this software, you agree to:

1. **🔐 Authorized Access Only**: Use only your own legitimate GST credentials
2. **📜 Compliance**: Ensure all activities comply with Indian GST laws and regulations  
3. **🛡️ Security**: Protect your credentials and use secure systems
4. **📊 Data Accuracy**: Verify all automated submissions for correctness
5. **⚖️ Legal Accountability**: Accept full responsibility for all consequences of usage
6. **🚫 No Misuse**: Refrain from any activities that violate portal terms or applicable laws

### 🎯 **Intended Use Only**

This tool is designed exclusively to assist **legitimate business operations** in:
- ✅ Extending valid E-Way Bills before expiration
- ✅ Streamlining compliance processes for authorized users
- ✅ Reducing manual effort in routine logistics operations

### 🚨 **Prohibited Activities**

Users must NOT use this tool for:
- ❌ Fraudulent transactions or false documentation
- ❌ Accessing accounts without proper authorization  
- ❌ Circumventing government security measures
- ❌ Any activity that violates GST portal terms of service
- ❌ Commercial misuse or unauthorized redistribution

### 📞 **Support & Contact**

For legitimate technical support or business inquiries:
- **📧 Email**: [Include your contact information]
- **🐛 Issues**: Report bugs with detailed logs and reproduction steps
- **💡 Suggestions**: Feature requests for logistics automation improvements

**Note**: Support is provided for legitimate use cases only. Requests related to circumventing security measures or unauthorized access will not be entertained.

---

### 🇮🇳 **Contributing to India's Digital Growth**

*This tool represents our commitment to India's digital transformation in logistics. By using it responsibly, you contribute to building a more efficient, transparent, and growth-oriented supply chain ecosystem for our nation.*

**Always ensure compliance with applicable laws and regulations when using automation tools with government portals.**

---

*Developed with 🧡 for Indian Transport & Logistics Industry*
