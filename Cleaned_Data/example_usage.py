"""
Example Usage Script for Resume-Job Matching Dataset
Demonstrates how to load and use the dataset for ML training
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("RESUME-JOB MATCHING DATASET - EXAMPLE USAGE")
print("="*70)

# ==================== LOAD DATASET ====================

print("\n📥 Loading dataset...")
df = pd.read_csv('final_training_dataset_v2.csv')

print(f"✓ Loaded {len(df):,} records")
print(f"✓ Columns: {', '.join(df.columns)}")
print(f"✓ Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# ==================== BASIC EXPLORATION ====================

print("\n" + "="*70)
print("DATASET EXPLORATION")
print("="*70)

print("\nMatch Label Distribution:")
print(df['match_label'].value_counts())
print("\nPercentage:")
print(df['match_label'].value_counts(normalize=True) * 100)

print("\nData Source Distribution:")
print(df['data_source'].value_counts())

print("\nTop 10 Categories:")
print(df['category'].value_counts().head(10))

print("\nScore Statistics:")
print(df['match_score'].describe())

print("\nProfile Text Length Statistics:")
text_lengths = df['profile_text'].str.len()
print(f"  Min: {text_lengths.min():,} characters")
print(f"  Max: {text_lengths.max():,} characters")
print(f"  Mean: {text_lengths.mean():.0f} characters")
print(f"  Median: {text_lengths.median():.0f} characters")

# ==================== DATA PREVIEW ====================

print("\n" + "="*70)
print("SAMPLE RECORDS")
print("="*70)

print("\n[HIGH MATCH EXAMPLE]")
high_sample = df[df['match_label'] == 'High'].iloc[0]
print(f"Profile ID: {high_sample['profile_id']}")
print(f"Job Title: {high_sample['job_title']}")
print(f"Match Score: {high_sample['match_score']}")
print(f"Profile Text Preview: {high_sample['profile_text'][:200]}...")

print("\n[MEDIUM MATCH EXAMPLE]")
medium_sample = df[df['match_label'] == 'Medium'].iloc[0]
print(f"Profile ID: {medium_sample['profile_id']}")
print(f"Job Title: {medium_sample['job_title']}")
print(f"Match Score: {medium_sample['match_score']}")
print(f"Profile Text Preview: {medium_sample['profile_text'][:200]}...")

print("\n[LOW MATCH EXAMPLE]")
low_sample = df[df['match_label'] == 'Low'].iloc[0]
print(f"Profile ID: {low_sample['profile_id']}")
print(f"Job Title: {low_sample['job_title']}")
print(f"Match Score: {low_sample['match_score']}")
print(f"Profile Text Preview: {low_sample['profile_text'][:200]}...")

# ==================== SIMPLE ML MODEL EXAMPLE ====================

print("\n" + "="*70)
print("SIMPLE ML MODEL TRAINING EXAMPLE")
print("="*70)

print("\n🤖 Training a simple classification model...")

# Prepare features and target
# Combine text features
df['combined_text'] = (
    df['profile_text'] + ' ' + 
    df['job_title'] + ' ' + 
    df['job_skills'].fillna('')
)

X = df['combined_text']
y = df['match_label']

# Split data (stratified)
print("\n✂️ Splitting data (70% train, 15% val, 15% test)...")
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp  # 0.176 * 0.85 ≈ 0.15
)

print(f"  Training set: {len(X_train):,} samples")
print(f"  Validation set: {len(X_val):,} samples")
print(f"  Test set: {len(X_test):,} samples")

# Vectorize text
print("\n📊 Vectorizing text with TF-IDF (this may take a minute)...")
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train_vec = vectorizer.fit_transform(X_train)
X_val_vec = vectorizer.transform(X_val)
X_test_vec = vectorizer.transform(X_test)

print(f"  Feature matrix shape: {X_train_vec.shape}")

# Train model
print("\n🎯 Training Random Forest classifier...")
clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
clf.fit(X_train_vec, y_train)

# Evaluate on validation set
print("\n📈 Validation Set Performance:")
y_val_pred = clf.predict(X_val_vec)
print(classification_report(y_val, y_val_pred))

# Evaluate on test set
print("\n📊 Test Set Performance:")
y_test_pred = clf.predict(X_test_vec)
print(classification_report(y_test, y_test_pred))

print("\n🎊 Confusion Matrix (Test Set):")
cm = confusion_matrix(y_test, y_test_pred, labels=['High', 'Medium', 'Low'])
print(pd.DataFrame(
    cm, 
    index=['True High', 'True Medium', 'True Low'],
    columns=['Pred High', 'Pred Medium', 'Pred Low']
))

# Feature importance
print("\n🔍 Top 20 Most Important Features:")
feature_names = vectorizer.get_feature_names_out()
importances = clf.feature_importances_
indices = np.argsort(importances)[-20:]

for i, idx in enumerate(indices[::-1], 1):
    print(f"  {i:2d}. {feature_names[idx]:20s} - {importances[idx]:.4f}")

# ==================== REGRESSION EXAMPLE ====================

print("\n" + "="*70)
print("REGRESSION TASK EXAMPLE")
print("="*70)

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

print("\n🎯 Training score prediction model...")

# Use match_score as target
y_score_train = df.loc[X_train.index, 'match_score']
y_score_val = df.loc[X_val.index, 'match_score']
y_score_test = df.loc[X_test.index, 'match_score']

# Train regressor
reg = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
reg.fit(X_train_vec, y_score_train)

# Predict
y_score_val_pred = reg.predict(X_val_vec)
y_score_test_pred = reg.predict(X_test_vec)

# Evaluate
print("\n📈 Validation Set Regression Metrics:")
print(f"  MAE: {mean_absolute_error(y_score_val, y_score_val_pred):.4f}")
print(f"  RMSE: {np.sqrt(mean_squared_error(y_score_val, y_score_val_pred)):.4f}")
print(f"  R²: {r2_score(y_score_val, y_score_val_pred):.4f}")

print("\n📊 Test Set Regression Metrics:")
print(f"  MAE: {mean_absolute_error(y_score_test, y_score_test_pred):.4f}")
print(f"  RMSE: {np.sqrt(mean_squared_error(y_score_test, y_score_test_pred)):.4f}")
print(f"  R²: {r2_score(y_score_test, y_score_test_pred):.4f}")

# ==================== ADVANCED FEATURE IDEAS ====================

print("\n" + "="*70)
print("ADVANCED FEATURE ENGINEERING IDEAS")
print("="*70)

print("""
1. SKILL OVERLAP FEATURES
   - Extract skills from profile_text using regex/NER
   - Calculate Jaccard similarity with job_skills
   - Count number of matching skills
   - Percentage of requirements met

2. EXPERIENCE FEATURES
   - Parse years of experience from profile_text
   - Calculate delta between candidate and required experience
   - Binary features: within_range, underqualified, overqualified

3. TEXT EMBEDDINGS
   - Use Sentence-BERT for profile_text embeddings
   - Calculate cosine similarity between profile and job description
   - Use pre-trained models like 'all-MiniLM-L6-v2'

4. CATEGORY FEATURES
   - One-hot encode category
   - Calculate category similarity scores
   - Use category embeddings

5. LENGTH-BASED FEATURES
   - Profile text length
   - Job skills count
   - Ratio of profile length to job requirements

6. LINGUISTIC FEATURES
   - Readability scores
   - Sentiment analysis
   - Formality detection
   - Grammar quality scores
""")

print("\n" + "="*70)
print("✅ EXAMPLE COMPLETED SUCCESSFULLY!")
print("="*70)
print(f"\n💡 This dataset is ready for:")
print("  - Binary classification (Match/No Match)")
print("  - Multi-class classification (High/Medium/Low)")
print("  - Regression (Score prediction)")
print("  - Ranking (Candidate ordering per job)")
print("  - Deep learning experiments (BERT, RoBERTa, etc.)")
print("\n🚀 Happy modeling!\n")
