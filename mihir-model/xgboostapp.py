import streamlit as st
import pandas as pd
import numpy as np
import joblib
import datetime
import streamlit as st
import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
import joblib
import matplotlib.pyplot as plt


model = joblib.load("xgb_model.pkl")
encoder_dict = joblib.load("encoders.pkl")


st.title("XGBoost - CRZ Entries Predictor")
st.write("Enter the features below to get a predicted `crz_entries` value:")

# List of available features
all_features = [
    "toll_date",
    "hour_of_day",
    "day_of_week_int",
    "time_period",
    "vehicle_class",
    "detection_group",
    "detection_region"
]

# Use a multiselect to allow feature selection (checkboxes)
selected_features = st.multiselect("Select Features", all_features, default=all_features)

# Display the selected features (for debugging/verification)
st.write("Selected Features:", selected_features)

df = pd.read_csv('cleaned_data.csv')

if st.button("Understand"):
    with st.spinner("Running XGBoost..."):
        # Prepare features and target
        X = df[selected_features]
        y = df["crz_entries"]

        # Encode categorical columns if necessary
        cat_cols = X.select_dtypes(include=['object']).columns
        encoder_dict = {}
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])
            encoder_dict[col] = le

        # Split data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Build and train the XGBoost model
        model = XGBRegressor(n_estimators=500, learning_rate=0.4, max_depth=5, random_state=42)
        model.fit(X_train, y_train)

        # Make predictions on the test set
        y_pred = model.predict(X_test)

        # Calculate performance metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

    st.success("Prediction complete!")


    # st.write(f"**RMSE:** {rmse:.2f}")
    # st.write(f"**MAE:** {mae:.2f}")")
    st.write(f"## These features account for {(r2 * 100):.2f}% of the variance in the data.")

    st.write("### Feature Importances Visual")
    importances = model.feature_importances_
    feature_importances = pd.DataFrame({
        "Feature": selected_features,
        "Importance": importances
    }).sort_values(by="Importance", ascending=True)  # sort for horizontal bar chart

    fig, ax = plt.subplots()
    ax.barh(feature_importances["Feature"], feature_importances["Importance"])
    ax.set_xlabel("Importance")
    ax.set_title("Feature Importances")
    st.pyplot(fig)

    # Showcase predictions alongside actual values
    # st.write("### Prediction Results")
    # results_df = X_test.copy()
    # results_df["Actual CRZ Entries"] = y_test
    # results_df["Predicted CRZ Entries"] = y_pred
    # st.dataframe(results_df)

    # Optionally, save the model and encoders for later use
    joblib.dump(model, "xgb_model.pkl")
    joblib.dump(encoder_dict, "encoders.pkl")