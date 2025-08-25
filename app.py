# app.py - Main Flask Web Application
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
import os
import tempfile
from werkzeug.utils import secure_filename
from review_generator_simple import ReviewGenerator
import traceback
import pandas as pd

app = Flask(__name__)
app.secret_key = 'reviewgene-secret-key-2024'  # Session ke liye

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('❌ No file selected! Please choose a file.', 'error')
            return redirect(url_for('home'))
        
        file = request.files['file']
        
        # Check if file is empty
        if file.filename == '':
            flash('❌ No file selected! Please choose a file.', 'error')
            return redirect(url_for('home'))
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            flash('❌ Invalid file type! Please upload Excel (.xlsx, .xls) or CSV (.csv) files.', 'error')
            return redirect(url_for('home'))
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = tempfile.mktemp(suffix='.' + filename.rsplit('.', 1)[1].lower())
        file.save(temp_path)
        
        # Initialize generator
        generator = ReviewGenerator()
        
        # Generate reviews
        flash('🔄 Generating reviews... This may take a few minutes.', 'info')
        results = generator.process_file(temp_path, "new_rules")
        
        # Create output file
        output_filename = f"generated_reviews_{filename.rsplit('.', 1)[0]}.csv"
        output_path = tempfile.mktemp(suffix='.csv')
        generator.write_results(results, output_path)
        
        # Clean up input file
        os.unlink(temp_path)
        
        # Return success message and file
        flash(f'✅ Successfully generated {len(results)} reviews!', 'success')
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'error')
        print(f"Error: {traceback.format_exc()}")
        return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/sample')
def sample():
    return render_template('sample.html')

@app.route('/download-sample')
def download_sample():
    # Create sample data
    sample_data = [
        {
            "sku_id": "CER0576",
            "Name": "CeraVe Moisturizing Cream",
            "brand": "CeraVe",
            "product_discount_category": "FMCG",
            "Classifier 1": "PERSONAL CARE",
            "classifier 2": "SKIN CARE",
            "classifier 3": "BODY CARE"
        },
        {
            "sku_id": "NEU0830",
            "Name": "Neurobion Forte Tablet",
            "brand": "Neurobion",
            "product_discount_category": "FMCG",
            "Classifier 1": "NUTRITION & METABOLISM",
            "classifier 2": "VITAMINS AND MINERALS",
            "classifier 3": "VITAMINS AND MINERALS"
        },
        {
            "sku_id": "EVI0105",
            "Name": "Evion 400mg Capsule",
            "brand": "Evion",
            "product_discount_category": "FMCG",
            "Classifier 1": "NUTRITION & METABOLISM",
            "classifier 2": "VITAMINS AND MINERALS",
            "classifier 3": "VITAMINS AND MINERALS"
        }
    ]
    
    # Create DataFrame and save as Excel
    df = pd.DataFrame(sample_data)
    output_path = tempfile.mktemp(suffix='.xlsx')
    df.to_excel(output_path, index=False)
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name="sample_products.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=8080)
