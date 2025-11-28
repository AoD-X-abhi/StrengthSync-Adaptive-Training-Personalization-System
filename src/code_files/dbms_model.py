import pandas as pd
import glob
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

def predict_rpe(model, wellness_data: dict) -> float:
    """Predicts RPE based on user's wellness metrics using a loaded model."""
    features_df = pd.DataFrame({
        'sleep_quality': [wellness_data['sleep_quality']],
        'readiness': [wellness_data['readiness']],
        'stress_inv': [10 - wellness_data['stress']],
        'soreness_inv': [10 - wellness_data['soreness']]
    })
    predicted_rpe = model.predict(features_df)[0]
    return predicted_rpe

def adjust_workout_reps(predicted_rpe: float, base_reps: int) -> int:
    """Adjusts reps for the first set based on the model's predicted RPE."""
    if predicted_rpe > 8:
        return base_reps - 2
    elif predicted_rpe < 6:
        return base_reps + 1
    else:
        return base_reps

def get_next_set_recommendation(reps_done: int, rpe_logged: int) -> dict:
    """Provides a recommendation for the next set using the Rep-RPE Zone logic."""
    target_rep_min, target_rep_max = 8, 12
    target_rpe_min, target_rpe_max = 7, 9
    
    if rpe_logged > target_rpe_max:
        return {"action": "DECREASE_WEIGHT", "message": "Too hard. Decrease the weight by 5-10% for the next set."}
    elif reps_done > target_rep_max:
        return {"action": "INCREASE_WEIGHT", "message": "Too easy. Increase the weight by 2-5% for the next set."}
    elif reps_done < target_rep_min:
        return {"action": "FATIGUE_DROP", "message": "Fatigue detected. Drop the weight by 10-15% to stay in the rep zone."}
    else:
        return {"action": "MAINTAIN_WEIGHT", "message": "Perfect. Keep the weight the same for the next set."}


def run_training_pipeline():
    """
    This function contains your entire model training process.
    It loads data, trains the model, and saves the .pkl file.
    """
    print("--- Running Model Training Pipeline ---")
    
    data_path = '/Users/aadithkrishna/Downloads/osfstorage-archive/pmdata' 
    all_wellness_files = glob.glob(data_path + "/p*/pmsys/wellness.csv")
    all_srpe_files = glob.glob(data_path + "/p*/pmsys/srpe.csv")
    
    if not all_wellness_files or not all_srpe_files:
        raise FileNotFoundError("CRITICAL ERROR: Could not find data files.")

    li_wellness, li_srpe = [], []
    for filename in all_wellness_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        participant_id = filename.replace(os.sep, '/').split('/')[-3] 
        df['participant_id'] = participant_id
        li_wellness.append(df)
    for filename in all_srpe_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        participant_id = filename.replace(os.sep, '/').split('/')[-3]
        df['participant_id'] = participant_id
        li_srpe.append(df)

    all_wellness = pd.concat(li_wellness, axis=0, ignore_index=True)
    all_srpe = pd.concat(li_srpe, axis=0, ignore_index=True)
    
    all_wellness = all_wellness.rename(columns={'effective_time_frame': 'date'})
    all_srpe = all_srpe.rename(columns={'end_date_time': 'date'})
    
    all_wellness['date'] = pd.to_datetime(all_wellness['date']).dt.date
    all_srpe['date'] = pd.to_datetime(all_srpe['date']).dt.date
    
    df_merged = pd.merge(all_wellness, all_srpe, on=['participant_id', 'date'])
    df_clean = df_merged.dropna().copy()
    
    df_clean['stress_inv'] = 10 - df_clean['stress']
    df_clean['soreness_inv'] = 10 - df_clean['soreness']
    features = ['sleep_quality', 'readiness', 'stress_inv', 'soreness_inv']
    target = 'perceived_exertion'
    df_model_data = df_clean[features + [target]].copy()
    
    X = df_model_data[features]
    y = df_model_data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = lgb.LGBMRegressor(random_state=42)
    model.fit(X_train, y_train)
    
    model_filename = 'readiness_model_multi.pkl'
    joblib.dump(model, model_filename)
    print(f"\n✅ Training complete. Model saved as '{model_filename}'")


if __name__ == '__main__':
    run_training_pipeline()