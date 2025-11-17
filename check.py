import pandas as pd
import joblib

# Load your model
model = joblib.load("C:\\Users\\sanskruti\\OneDrive\\Desktop\\Al_Powered_loan_eligibility\\model (1).pkl")   # change filename as needed

# Load sample input data used during training
data = pd.read_csv("train (1).csv")  # change filename

def check_input_format(df):
    for col in df.columns:
        unique_vals = df[col].dropna().unique()

                        # CASE 1: Binary numeric input
        if set(unique_vals).issubset({0, 1}):
            print(f"{col}: Binary input expected (0/1)")
        
                        # CASE 2: Text Labels
        elif df[col].dtype == 'object':
            print(f"{col}: Text input expected → {list(unique_vals)}")
        
                        # CASE 3: Numeric but not binary
        elif df[col].dtype in ['int64', 'float64']:
            print(f"{col}: Numeric input (range: {df[col].min()} to {df[col].max()})")
        
                        # OTHER TYPES
        else:
            print(f"{col}: Unknown format")

# RUN CHECK
check_input_format(data)
