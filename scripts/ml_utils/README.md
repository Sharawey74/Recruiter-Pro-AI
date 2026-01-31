# ML Utilities

ML model training, evaluation, and metadata management scripts.

## Scripts

### Training
- **`train_ats_model.py`** - Quick start training script
  - Trains Logistic Regression, Random Forest, and XGBoost models
  - Performs hyperparameter tuning with cross-validation
  - Saves best model to `models/production/`
  - Estimated time: 20-30 minutes

### Evaluation & Metrics
- **`add_evaluation_metrics.py`** - Add evaluation metrics to model metadata
- **`create_complete_metadata.py`** - Create comprehensive metadata for all models
- **`show_complete_metadata.py`** - Display model metadata in formatted view
- **`show_training_results.py`** - Show latest training experiment results
- **`extract_model_metadata.py`** - Extract metadata from saved model files

## Usage

**Train New Model:**
```bash
cd Recruiter-Pro-AI
python scripts/ml_utils/train_ats_model.py
```

**View Training Results:**
```bash
python scripts/ml_utils/show_training_results.py
```

**View Complete Metadata:**
```bash
python scripts/ml_utils/show_complete_metadata.py
```

## Requirements

All scripts use:
- `data/AI_Resume_Screening.csv` as the dataset
- `src/ml_engine/` components for training
- `models/production/` for final model storage
- `models/experiments/` for training experiments

## Output

Models are saved to:
- **Production:** `models/production/ats_model.joblib`
- **Experiments:** `models/experiments/experiment_YYYYMMDD_HHMMSS/`

Metadata includes:
- Model parameters
- Training metrics (accuracy, precision, recall, F1)
- Test set performance
- Feature importance (for tree-based models)
- Class imbalance handling (SMOTE)
