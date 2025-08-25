# 🚀 **SKU Review Generator - Production Ready**

> **AI-Powered Review Generation for Indian E-commerce Products**  
> Generate authentic, varied customer reviews with Indian names, Hinglish language mixing, and medical accuracy.

## ✨ **Key Features**

### **🎯 Core Capabilities**
- **AI-Powered Reviews**: Uses OpenAI GPT models for realistic content
- **Indian User Names**: 95% Indian names from comprehensive database
- **Language Mixing**: Natural Hinglish, English, and Hindi combinations
- **Medical Accuracy**: Product-specific benefits and medical conditions
- **Checkpointing**: Resume from interruptions, no data loss
- **Production Ready**: Handles huge files with automatic saves

### **🌐 Language Support**
- **Hinglish**: Natural Indian English + Hindi mixing
- **English**: Pure English reviews (20%)
- **Hindi**: Pure Hindi reviews
- **Mixed**: Complex natural combinations

### **📊 File Formats**
- **Input**: Excel (.xlsx, .xls) and CSV files
- **Output**: CSV with comprehensive review data
- **Checkpoints**: JSON files for resume functionality

## 📋 **Input File Requirements**

### **Required Columns (7 columns)**
| Column | Description | Example |
|--------|-------------|---------|
| `sku_id` | Product identifier | "CER0576", "LIM001" |
| `Name` | Product name | "CeraVe Moisturizing Cream", "Limcee 500mg Vitamin C" |
| `brand` | Brand name | "CeraVe", "Limcee" |
| `product_discount_category` | Product category | "FMCG", "Pharma" |
| `Classifier 1` | Main category | "PERSONAL CARE", "NUTRITION & METABOLISM" |
| `classifier 2` | Sub-category | "SKIN CARE", "VITAMINS AND MINERALS" |
| `classifier 3` | Specific type | "BODY CARE", "VITAMINS AND MINERALS" |

### **Example Input Data**
```excel
sku_id    | Name                           | brand      | Classifier 1           | classifier 2        | classifier 3
CER0576   | CeraVe Moisturizing Cream     | CeraVe     | PERSONAL CARE          | SKIN CARE           | BODY CARE
NEU0830   | Neurobion Forte Tablet        | Neurobion  | NUTRITION & METABOLISM | VITAMINS AND MINERALS| VITAMINS AND MINERALS
EVI0105   | Evion 400mg Capsule           | Evion      | NUTRITION & METABOLISM | VITAMINS AND MINERALS| VITAMINS AND MINERALS
```

## 🎯 **Output Format**

### **Generated Columns (10 columns)**
| Column | Description | Example |
|--------|-------------|---------|
| `SKUId` | Original SKU ID | "CER0576" |
| `Brand` | Brand name | "CeraVe" |
| `ProductName` | Combined brand + product name | "CeraVe - CeraVe Moisturizing Cream" |
| `Category` | Main classification | "PERSONAL CARE" |
| `SubCategory` | Sub-classification | "SKIN CARE" |
| `SpecificType` | Specific type | "BODY CARE" |
| `Review` | Generated review | "Skin bilkul soft ho gayi hai, really satisfied!" |
| `Username` | Generated username | "Arjun Patel" |
| `Rating` | Generated rating | 5 |
| `Date` | Generated date | "2024-01-15" |

### **Example Output**
```csv
SKUId,Brand,ProductName,Category,SubCategory,SpecificType,Review,Username,Rating,Date
CER0576,CeraVe,CeraVe - CeraVe Moisturizing Cream,PERSONAL CARE,SKIN CARE,BODY CARE,"Skin bilkul soft ho gayi hai, really satisfied!",Arjun Patel,5,2024-01-15
NEU0830,Neurobion,Neurobion - Neurobion Forte Tablet,NUTRITION & METABOLISM,VITAMINS AND MINERALS,VITAMINS AND MINERALS,"Immunity boost mil gaya, energy level badh gaya. Perfect hai!",Diya Sharma,4,2024-01-15
```

## 🚀 **Quick Start Guide**

### **Step 1: Installation**
```bash
# Clone or download the project
cd "Review Seeding"

# Install dependencies
pip install -r requirements.txt

# Update config.py with your OpenAI API key
```

### **Step 2: Configuration**
Edit `config.py`:
```python
OPENAI_API_KEY = "your-actual-api-key-here"
OPENAI_MODEL = "gpt-4o-mini"  # or gpt-3.5-turbo
```

### **Step 3: Run the Program**
```bash
python3 review_generator.py
```

## 📖 **Detailed Usage Guide**

### **1. Program Startup**
```bash
$ python3 review_generator.py

=== SKU Review Generator ===
✅ Using OpenAI model: gpt-4o-mini

🌐 Language Mixing Capabilities:
🎯 Primary Style: Hinglish
📊 Language Distribution:
   Pure Hinglish: 20%
   Hinglish + English: 25%
   English + Hindi: 25%
   Pure English: 20%
   Hindi + English: 8%
   Mixed Natural: 2%

🔬 Product Benefit Analysis Capabilities:
📁 File Format Support:
✅ Supported Formats: Excel (.xlsx, .xls) and CSV (.csv)
📊 Required Columns:
   • sku_id
   • Name
   • brand
   • product_discount_category
   • Classifier 1
   • classifier 2
   • classifier 3
```

### **2. File Input**
```
Enter the path to your Excel/CSV file (or press Enter to create a sample): 
```

**Option A - Use your existing file:**
```
product_list.xlsx
```

**Option B - Use sample data (for testing):**
```
[Press Enter - no text needed]
```

### **3. Mode Selection**
```
🎯 Choose review generation mode:
1. Quick mode (1 review per SKU)
2. Medium mode (3-5 reviews per SKU)
3. Comprehensive mode (15-20 reviews per SKU) - Recommended

Enter your choice (1, 2, or 3, default is 3): 3
```

### **4. Checkpoint Detection (New Feature!)**
```
🔍 Checking for existing checkpoints...
📊 Found 3 checkpoints:
   1. product_list_comprehensive_3_20241215_143456.json (45.2 KB)
   2. product_list_comprehensive_2_20241215_143245.json (32.1 KB)
   3. product_list_comprehensive_1_20241215_143022.json (18.7 KB)

🔄 Resuming from checkpoint: checkpoints/product_list_comprehensive_3_20241215_143456.json
   Previous progress: 150 reviews

Found checkpoint with 150 reviews. Resume from checkpoint? (y/n, default: y): y
🔄 Resuming from checkpoint with 150 existing reviews...
```

### **5. Processing with Checkpoints**
```
🚀 Processing product_list.xlsx in comprehensive mode...
📊 Read Excel file: product_list.xlsx
   Columns: ['sku_id', 'Name', 'brand', 'product_discount_category', 'Classifier 1', 'classifier 2', 'classifier 3']
   Rows: 163066
✅ All required columns found!

🔄 Generating reviews for: CeraVe - CeraVe Moisturizing Cream
   Category: PERSONAL CARE > SKIN CARE > BODY CARE
   Generating 18 reviews...
     Progress: 1/18
     Progress: 6/18
     Progress: 11/18
     Progress: 16/18
   ✅ Completed 18 reviews for CeraVe - CeraVe Moisturizing Cream

💾 Checkpoint saved: checkpoints/product_list_comprehensive_4_20241215_143556.json
💾 Backup created: 200 reviews
```

### **6. Completion**
```
✅ Generated 168 total reviews. Results saved to: product_list_comprehensive_reviews.csv

🎉 Review generation completed successfully!
📁 Total reviews generated: 168
💾 Results saved to output file
🚀 You can now use these reviews for your products!

============================================================
✅ Program completed successfully!
============================================================
```

## 🔧 **Checkpointing System**

### **What It Does**
- **Auto-saves** every 50 reviews
- **Creates backups** every 100 reviews
- **Resumes automatically** from interruptions
- **Manages disk space** (keeps last 10 checkpoints)

### **Checkpoint Files**
```
checkpoints/
├── product_list_comprehensive_1_20241215_143022.json
├── product_list_comprehensive_2_20241215_143156.json
├── product_list_comprehensive_3_20241215_143245.json
└── product_list_comprehensive_final_20241215_143456.json
```

### **Backup Files**
```
product_list_comprehensive_reviews.csv.backup_100
product_list_comprehensive_reviews.csv.backup_200
product_list_comprehensive_reviews.csv.backup_300
```

### **Resume Scenarios**
1. **System crash** → Resume from last checkpoint
2. **Power outage** → Resume from last checkpoint
3. **Manual interruption** → Resume from last checkpoint
4. **API rate limits** → Resume from last checkpoint

## ⚙️ **Configuration Options**

### **OpenAI Settings**
```python
OPENAI_API_KEY = "your-api-key-here"
OPENAI_MODEL = "gpt-4o-mini"  # or gpt-3.5-turbo
```

### **Language Mixing**
```python
LANGUAGE_MIXING = {
    "enabled": True,
    "primary_language": "Hinglish",
    "distribution": {
        "Pure Hinglish": 20,      # "Product bahut accha hai yaar"
        "Hinglish + English": 25, # "Great product hai, quality top notch"
        "English + Hindi": 25,    # "Works perfectly, bilkul perfect hai"
        "Pure English": 20,       # "Excellent product, highly recommend"
        "Hindi + English": 8,     # "Product accha hai, very good quality"
        "Mixed Natural": 2        # Complex natural combinations
    }
}
```

### **Checkpointing Settings**
```python
CHECKPOINT_SETTINGS = {
    "enabled": True,              # Enable checkpointing
    "save_interval": 50,          # Save every 50 reviews
    "checkpoint_dir": "checkpoints", # Directory for checkpoint files
    "max_checkpoints": 10,        # Keep last 10 checkpoints
    "resume_enabled": True,       # Enable resume from checkpoint
    "backup_interval": 100        # Create backup every 100 reviews
}
```

### **Review Length Settings**
```python
REVIEW_LENGTH_SETTINGS = {
    "max_sentences": 2,           # Maximum 2 sentences per review
    "target_length": "1-2 lines", # Like real customer reviews
    "distribution": {
        "1_sentence": 50,         # 50% single sentence reviews
        "2_sentences": 40,        # 40% two sentence reviews  
        "brief_2_sentences": 10   # 10% brief two sentence reviews
    }
}
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. "API key not found"**
```bash
# Update your API key in config.py
OPENAI_API_KEY = "sk-..."  # Your actual key

# Or set environment variable
export OPENAI_API_KEY="sk-..."
```

#### **2. "File not found"**
- Check file path and ensure Excel/CSV exists
- Use absolute path if needed: `/Users/username/path/to/file.xlsx`

#### **3. API errors**
- Verify OpenAI account has credits
- Check API key validity
- Try different model (gpt-3.5-turbo for cost-effective)

#### **4. Rate limiting**
- System includes automatic delays
- Increase delays in config if needed
- Use checkpointing to resume after interruptions

#### **5. "module 'openai' has no attribute 'OpenAI'"**
```bash
# Quick fix
python3 fix_openai.py

# Or fix manually
pip uninstall openai -y
pip install openai>=1.0.0
```

### **Performance Tips**

- **Use `gpt-3.5-turbo`** for cost-effective bulk processing
- **Enable checkpointing** for large files
- **Monitor API usage** in OpenAI dashboard
- **Use sample data first** to test configuration

## 📁 **File Structure**

```
Review Seeding/
├── config.py                 # Configuration settings
├── review_generator.py       # Main program
├── requirements.txt          # Python dependencies
├── fix_openai.py            # OpenAI library fix script
├── README.md                # This file
├── checkpoints/             # Checkpoint files (auto-created)
│   ├── product_list_comprehensive_1_*.json
│   ├── product_list_comprehensive_2_*.json
│   └── ...
├── sample_skus.xlsx         # Sample input file
└── product_list_comprehensive_reviews.csv  # Output file
```

## 🎯 **Production Use Cases**

### **E-commerce Platforms**
- Generate product reviews for new listings
- Create authentic customer testimonials
- Build trust with realistic feedback

### **Marketing Agencies**
- Bulk review generation for clients
- A/B testing different review styles
- Localized content for Indian markets

### **Product Research**
- Understand customer sentiment patterns
- Analyze product benefit perceptions
- Generate training data for ML models

## 🚀 **Advanced Features**

### **Product Benefit Analysis**
- **Automatic classification** based on product categories
- **Medical accuracy** for health products
- **Brand-aware** review generation
- **Fallback benefits** if API fails

### **Language Intelligence**
- **Natural mixing** of Hinglish, English, and Hindi
- **Context-aware** language selection
- **Authentic Indian** writing style
- **Varied sentence** structures

### **Quality Assurance**
- **Length control** (1-2 sentences max)
- **Sentiment variety** (positive, neutral, negative)
- **Product specificity** (no generic reviews)
- **Realistic ratings** (50% 5★, 25% 4★, 15% 3★, 10% 2★)

## 📞 **Support & Updates**

### **Getting Help**
1. Check this README for common solutions
2. Verify configuration settings
3. Test with sample data first
4. Check OpenAI API status

### **Updates**
- **Checkpointing**: Resume from interruptions
- **Language mixing**: Better English/Hinglish balance
- **Column structure**: Updated for new requirements
- **Error handling**: Robust production-ready system

## 🎉 **Ready for Production!**

The system is now production-ready with:
- ✅ **Checkpointing** for huge files
- ✅ **Resume functionality** from interruptions
- ✅ **Regular backups** every 100 reviews
- ✅ **Language variety** (English, Hinglish, Hindi)
- ✅ **Indian names** from comprehensive database
- ✅ **Medical accuracy** for health products
- ✅ **Robust error handling** and recovery

**Start generating authentic Indian customer reviews today!** 🚀✨ 