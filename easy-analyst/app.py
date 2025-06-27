import streamlit as st
import pandas as pd
import plotly.express as px
import time
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import io
import numpy as np
import scipy.stats as stats
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder # For transformations
from io import BytesIO # For Excel export
import base64 # Import for base64 encoding

st.set_page_config(page_title="Dashboard Suite", layout="wide")
        
# Function to convert image to base64
def get_image_as_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Logo file not found at {path}")
        return None
logo_path = "/Users/arjunsathishkumar/easy-analyst/easy-analyst/giflogo.gif"
logo_base64 = get_image_as_base64(logo_path)
if logo_base64:
    # Ensure the logo is centered and uses the desired width (e.g., 400px)
    # Using text-align on a block container for an inline-block or inline image.
    st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/gif;base64,{logo_base64}" width="400"></div>', unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Global dark background and light text */
    .stApp, body {
        background-color: #222831 !important; /* Very Dark Grey Background */
        color: #EEEEEE !important; /* Light Grey/Off-White Text */
    }

    /* Headers with gold accent */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #D4AF37 !important; /* Muted Gold for headers */
    }

    /* Buttons with gold accent */
    .stButton > button {
        background-color: #D4AF37 !important; /* Muted Gold */
        color: #222831 !important; /* Dark text on gold button */
        border: 1px solid #B08D57 !important; /* Slightly darker gold border */
    }

    /* Input boxes, select boxes, expanders - dark background, light text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stRadio > div,
    .stExpander > div > summary,
    .stExpander > div > div[data-testid="stExpanderDetails"] {
        background-color: #393E46 !important; /* Slightly Lighter Dark Grey for boxes */
        color: #EEEEEE !important;
        border: 1px solid #4A5568 !important; /* Subtle border */
    }

    /* Ensure text inside selectbox dropdowns is also light */
    .stSelectbox div[data-baseweb="select"] > div {
         color: #EEEEEE !important;
    }

    /* Dataframe styling to fit the dark theme */
    .stDataFrame {
        background-color: #393E46 !important;
        border: 1px solid #4A5568 !important;
    }
    .stDataFrame > div > div > table th, .stDataFrame > div > div > table td {
        color: #EEEEEE !important;
        border-bottom: 1px solid #4A5568; /* Lighter lines within dataframe */
    }
    .stDataFrame > div > div > table th {
        background-color: #222831 !important; /* Darker header for dataframe */
    }

    /* Title with cursive font - ensure it's light */
    h1[style*="font-family: cursive"] {
        color: #EEEEEE !important;
    }

    /* Premium Spinner Styling */
    .stSpinner {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100% !important; /* Changed to 100% to ensure it covers the viewport correctly with fixed positioning */
        background-color: rgba(34, 40, 49, 0.8) !important; /* Darker semi-transparent overlay, matches #222831 */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        z-index: 9999 !important;
        backdrop-filter: blur(4px) !important;
        -webkit-backdrop-filter: blur(4px) !important;
        /* Ensure it's a positioning context for its children */
        position: fixed !important; 
    }

    /* Container for spinner icon and text */
    .stSpinner > div[data-testid="stSpinner"] {
        /* This element is already centered by the parent's flex properties.
           We just need to ensure it scales and its children are arranged. */
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transform: scale(2.5); /* Make the spinner and text significantly larger */
    }

    /* Spinner icon (SVG) */
    .stSpinner > div[data-testid="stSpinner"] > svg {
        width: 80px !important; /* Adjust size as needed */
        height: 80px !important; /* Adjust size as needed */
        margin-bottom: 25px !important;
    }

    /* Spinner text ("Analyzing") */
    .stSpinner > div[data-testid="stSpinner"] > div:last-of-type { /* Targets the text div */
        color: #D4AF37 !important; /* Gold accent for analyzing text */
        font-size: 1.8em !important; /* Explicitly increase text size */
        font-weight: bold;
    }

    /* Animated dots after "Analyzing" */
    .stSpinner > div[data-testid="stSpinner"] > div:last-of-type::after {
        content: ' .....'; /* Initial state for animation */
        display: inline-block;
        animation: animatedDots 1.5s infinite steps(5, end);
        width: 3.5em; /* Adjust width to fit max dots */
        text-align: left;
        vertical-align: bottom;
    }

    @keyframes animatedDots {
        0%   { content: ' .'; }
        20%  { content: ' ..'; }
        40%  { content: ' ...'; }
        60%  { content: ' ....'; }
        80%  { content: ' .....'; }
        100% { content: ' .....'; } /* Hold last frame or cycle */
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-family: cursive;'>Dashboard Suite</h1>", unsafe_allow_html=True)

# --- File Upload (only once) ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = "processed_data"


def load_data(uploaded_file_obj):
    try:
        if uploaded_file_obj.name.endswith('.csv'):
            return pd.read_csv(uploaded_file_obj)
        elif uploaded_file_obj.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file_obj)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

def clean_data(df, missing_value_strategy="mean"):  # Added function for data cleaning
    df = df.drop_duplicates()
    if df.isnull().sum().sum() > 0:  # only impute if there are missing values
        num_cols = df.select_dtypes(include=np.number).columns
        imputer = SimpleImputer(strategy=missing_value_strategy)
        df[num_cols] = imputer.fit_transform(df[num_cols])
    return df

# --- Data Export Helper Functions ---
@st.cache_data
def convert_df_to_csv(df_to_convert):
    return df_to_convert.to_csv(index=False).encode('utf-8')

def convert_df_to_excel(df_to_convert):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_convert.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data


tab1, tab2 = st.tabs(["📤 Upload Dataset", "✍️ Enter Data Manually"])

with tab1:
    uploaded_file_obj = st.file_uploader("📂 Upload your Dataset", type=["csv", "xlsx", "xls"], key="main_upload", help="Supported file types: CSV, XLSX, XLS")
    if uploaded_file_obj:
        st.session_state.df = load_data(uploaded_file_obj)
        if st.session_state.df is not None:
            st.session_state.uploaded_file_name = uploaded_file_obj.name.split('.')[0]
            st.success("✅ Dataset Uploaded Successfully.")

with tab2:
    st.subheader("Manually Create or Edit Data")
    if st.button("Load Sample Editable Table"):
        sample_data = {'Column1': [1, 2, 3], 'Column2': ['A', 'B', 'C'], 'Column3': [True, False, True]}
        st.session_state.df_manual = pd.DataFrame(sample_data)

    if 'df_manual' not in st.session_state:
        st.session_state.df_manual = pd.DataFrame({'col1': [None]*3, 'col2': [None]*3}) # Default empty

    st.session_state.df_manual = st.data_editor(st.session_state.df_manual, num_rows="dynamic", key="manual_data_editor")

    # --- Row and Column Operations ---
    st.markdown("---") # Separator
    st.subheader("Modify Table Structure")

    op_col1, op_col2 = st.columns(2)

    with op_col1: # Add Row
        if st.button("➕ Add Row", key="add_manual_row_button", use_container_width=True):
            if st.session_state.df_manual is not None:
                new_row = pd.DataFrame([[None] * len(st.session_state.df_manual.columns)], columns=st.session_state.df_manual.columns)
                st.session_state.df_manual = pd.concat([st.session_state.df_manual, new_row], ignore_index=True)
                st.rerun()

    with op_col2: # Add Column - Initial Button
        if st.button("➕ Add Column", key="init_add_column_button", use_container_width=True):
            # Toggle the visibility of the add column form
            st.session_state.show_add_column_form = not st.session_state.get("show_add_column_form", False)
            if st.session_state.show_add_column_form:
                 st.session_state.add_column_name_value = "" # Reset previous input when showing
            st.rerun() # Rerun to show/hide the form immediately

# Conditional form for adding a column
if st.session_state.get("show_add_column_form", False):
    with st.form("add_column_form", clear_on_submit=True):
        new_col_name_input = st.text_input(
            "Enter name for the new column:",
            key="new_col_name_input_manual_form" # Unique key for the input within the form
        )
        submitted_add = st.form_submit_button("Confirm Add Column")

        if submitted_add:
            if st.session_state.df_manual is not None and new_col_name_input:
                if new_col_name_input not in st.session_state.df_manual.columns:
                    st.session_state.df_manual[new_col_name_input] = [None] * len(st.session_state.df_manual)
                    st.session_state.show_add_column_form = False # Hide form
                    st.success(f"Column '{new_col_name_input}' added.")
                    st.rerun()
                else:
                    st.warning(f"Column '{new_col_name_input}' already exists. Form will remain open to correct.")
            elif not new_col_name_input:
                st.warning("Please enter a name for the new column.")
    # Add a cancel button outside the form but within the conditional block
    if st.button("Cancel Add Column", key="cancel_add_column_action_button"):
        st.session_state.show_add_column_form = False
        st.rerun()

    # --- Rename Column ---
    with st.expander("✏️ Rename Column"):
        st.caption("Note: `st.data_editor` does not natively support renaming columns by double-clicking headers. Use this section instead.")

        # Check and apply reset flag for the rename form
        if st.session_state.get("reset_rename_form_flag", False):
            if "select_col_to_rename_manual" in st.session_state:
                st.session_state.select_col_to_rename_manual = ""
            if "new_name_for_rename_input_manual" in st.session_state:
                st.session_state.new_name_for_rename_input_manual = ""
            del st.session_state.reset_rename_form_flag # Consume the flag

        if st.session_state.df_manual is not None and not st.session_state.df_manual.empty:
            current_columns_rename = st.session_state.df_manual.columns.tolist()
            col_to_rename = st.selectbox(
                "Select column to rename:",
                options=[""] + current_columns_rename, # Add a blank option
                index=0,
                key="select_col_to_rename_manual"
            )

            if col_to_rename: # Only show input if a column is selected
                new_name_for_rename = st.text_input(
                    f"Enter new name for '{col_to_rename}':",
                    key="new_name_for_rename_input_manual",
                    value=st.session_state.get("new_name_for_rename_input_manual", "") # Ensure input reflects reset
                )
                if st.button(f"Rename '{col_to_rename}'", key="confirm_rename_button_manual"):
                    if new_name_for_rename and new_name_for_rename.strip():
                        if new_name_for_rename not in current_columns_rename or new_name_for_rename == col_to_rename:
                            updated_columns = current_columns_rename[:] # Create a copy
                            col_index = updated_columns.index(col_to_rename)
                            updated_columns[col_index] = new_name_for_rename
                            st.session_state.df_manual.columns = updated_columns
                            st.success(f"Column '{col_to_rename}' renamed to '{new_name_for_rename}'.")
                            st.session_state.reset_rename_form_flag = True # Set flag to reset on next run
                            st.rerun() # Trigger a rerun to apply the reset and show updated state
                        else:
                            st.warning(f"Column name '{new_name_for_rename}' already exists.")
                    else:
                        st.warning("New column name cannot be empty.")
        else:
            st.caption("Add data or columns to the table to enable renaming.")

    if st.button("Use Manually Entered Data as Current Dataset"):
        st.session_state.df = st.session_state.df_manual.copy()
        st.session_state.uploaded_file_name = "manual_data"
        st.success("✅ Manual data is now the current dataset.")


if st.session_state.df is not None:
    df = st.session_state.df # Use the DataFrame from session state
    with st.spinner("🔎 Analyzing"): # Text changed, dots will be added by CSS
        st.subheader("📄 Dataset Preview")
        st.data_editor(df.head(), use_container_width=True, key="data_preview_editor", num_rows="dynamic", disabled=True)

        # --- Data Cleaning Option ---
        with st.expander("🧹 Clean Dataset", expanded=False):
            cleaning_strategy = st.radio("Missing Value Imputation Strategy:", ("mean", "median", "most_frequent"), horizontal=True)
            if st.button("Apply Cleaning"):
                st.session_state.df = clean_data(st.session_state.df, cleaning_strategy)
                df = st.session_state.df # update local df variable
                st.success("✅ Dataset cleaned. Duplicates removed and missing values imputed.")
                st.rerun()

        # --- Automated Data Quality Insights ---
        with st.expander("💡 Automated Data Quality Insights", expanded=False):
            st.markdown("Basic checks and suggestions for your dataset.")
            issues_found = False
            if not df.empty: # Ensure dataframe is not empty
                for col in df.columns:
                    # Missing Values
                    missing_percentage = df[col].isnull().sum() * 100 / len(df)
                    if missing_percentage > 0:
                        issues_found = True
                        st.warning(f"**{col}**: {missing_percentage:.2f}% missing values. Consider imputation or dropping if too high (e.g., > 50-70%).")

                    # Low Variance (Single Unique Value)
                    if df[col].nunique() == 1:
                        issues_found = True
                        st.info(f"**{col}**: Contains only a single unique value. May not be useful for some analyses.")

                    # Outliers (Simple IQR for numerical columns)
                    if pd.api.types.is_numeric_dtype(df[col]):
                        Q1 = df[col].quantile(0.25)
                        Q3 = df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        # Ensure Q1, Q3, IQR are not NaN (can happen with all-NaN columns or very small data)
                        if pd.notna(Q1) and pd.notna(Q3) and pd.notna(IQR):
                            outliers = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
                            if not outliers.empty:
                                issues_found = True
                                st.info(f"**{col}**: Potential outliers detected using IQR method ({len(outliers)} points). Review or consider capping/removing.")
                if not issues_found:
                    st.success("No immediate data quality red flags detected by basic checks!")
            else:
                st.info("No data loaded to perform quality checks.")

        # --- Data Export Buttons ---
        st.subheader("📤 Export Processed Data")
        col1_export, col2_export = st.columns(2)
        with col1_export:
            csv_export = convert_df_to_csv(df)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_export,
                file_name=f"{st.session_state.uploaded_file_name}_processed.csv",
                mime='text/csv',
            )
        with col2_export:
            excel_export = convert_df_to_excel(df)
            st.download_button(
                label="📥 Download as Excel",
                data=excel_export,
                file_name=f"{st.session_state.uploaded_file_name}_processed.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )

        # --- Dashboard Configuration ---
        st.subheader("✨ Dashboard Configuration (Visualizations)")
        dashboard_title = st.text_input("Dashboard Title", value="My Interactive Dashboard")
        num_cols_per_row = st.slider("Number of Charts Per Row", 1, 3, 2)
        include_eda = st.checkbox("Include Exploratory Data Analysis (EDA) Visualizations", value=True)
        include_descriptive = st.checkbox("Include Descriptive Statistics", value=True)

        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # --- Data Transformation Section ---
        with st.expander("🔄 Transform Data", expanded=False):
            st.markdown("Apply transformations to your data columns.")
            transform_col = st.selectbox("Select column to transform:", options=[None] + df.columns.tolist(), key="transform_col_select")
            if transform_col:
                selected_dtype = df[transform_col].dtype
                st.write(f"Selected column: **{transform_col}** (Type: {selected_dtype})")

                if pd.api.types.is_numeric_dtype(selected_dtype):
                    transform_type_num = st.selectbox("Select numerical transformation:",
                                                      [None, "Log Transform (log1p)", "Square Root Transform", "Standardize (Z-score)"],
                                                      key="num_transform_type")
                    if transform_type_num and st.button(f"Apply {transform_type_num} to '{transform_col}'", key=f"apply_{transform_type_num}"):
                        new_col_name = f"{transform_col}_{transform_type_num.lower().replace(' ', '_').split('(')[0]}"
                        transformed_series = df[transform_col].copy()
                        if transform_type_num == "Log Transform (log1p)":
                            transformed_series = np.log1p(df[transform_col])
                        elif transform_type_num == "Square Root Transform":
                            transformed_series = np.sqrt(df[transform_col].clip(lower=0)) # clip to avoid sqrt of negative
                        elif transform_type_num == "Standardize (Z-score)":
                            scaler = StandardScaler()
                            transformed_series = scaler.fit_transform(df[[transform_col]]).flatten()
                        
                        st.session_state.df[new_col_name] = transformed_series
                        st.success(f"Transformation '{transform_type_num}' applied. New column: '{new_col_name}'.")
                        st.rerun()

                elif pd.api.types.is_object_dtype(selected_dtype) or pd.api.types.is_categorical_dtype(selected_dtype):
                    transform_type_cat = st.selectbox("Select categorical transformation:",
                                                       [None, "One-Hot Encode", "Label Encode"],
                                                       key="cat_transform_type")
                    if transform_type_cat and st.button(f"Apply {transform_type_cat} to '{transform_col}'", key=f"apply_{transform_type_cat}"):
                        if transform_type_cat == "One-Hot Encode":
                            dummies = pd.get_dummies(df[transform_col], prefix=transform_col)
                            st.session_state.df = pd.concat([st.session_state.df, dummies], axis=1)
                            # st.session_state.df = st.session_state.df.drop(columns=[transform_col]) # Optionally drop original
                            st.success(f"One-Hot Encoding applied for '{transform_col}'. New columns added.")
                        elif transform_type_cat == "Label Encode":
                            le = LabelEncoder()
                            new_col_name = f"{transform_col}_label_encoded"
                            st.session_state.df[new_col_name] = le.fit_transform(df[transform_col])
                            st.success(f"Label Encoding applied. New column: '{new_col_name}'.")
                        st.rerun()
                else:
                    st.info("Select a column with a numeric or categorical/object type for transformations.")

        # --- Main Analysis Expander ---
        with st.expander("🔬 Explore & Analyze Data", expanded=False):
            st.markdown("#### Select Analyses to Display:")
            
            # Define available analyses and their default states
            analysis_options = {
                "Descriptive Analysis": "show_descriptive_analysis",
                "Exploratory Data Analysis (EDA)": "show_eda_analysis",
                "Predictive Analysis": "show_predictive_analysis",
                "Inferential Analysis": "show_inferential_analysis",
                "Prescriptive Analysis": "show_prescriptive_analysis",
                "Causal Analysis": "show_causal_analysis",
                "ANOVA": "show_anova_analysis"
            }

            # Create checkboxes for each analysis
            # Use columns for better layout if many analyses
            cols_analysis_select = st.columns(3) 
            idx = 0
            for display_name, state_key in analysis_options.items():
                with cols_analysis_select[idx % 3]:
                    st.session_state[state_key] = st.checkbox(display_name, value=st.session_state.get(state_key, True), key=f"cb_{state_key}")
                idx += 1
            st.markdown("---")

            # --- Analysis Sections (Descriptive, EDA, Predictive, etc.) ---
            if st.session_state.get(analysis_options["Descriptive Analysis"], True):
                st.subheader("📊 Descriptive Analysis")
                st.markdown("Summarizing and describing the main features of the dataset.")
                st.write("Summary Statistics (Overall):")
                st.write(df.describe(include='all'))

                if numerical_cols:
                    st.markdown("Measures for Numerical Columns:")
                    selected_num_col_desc = st.selectbox("Select Numerical Column for Descriptive Stats", numerical_cols, key="desc_num_col")
                    if selected_num_col_desc:
                        st.write(f"**{selected_num_col_desc}**: ")
                        st.write(f"Mean: {df[selected_num_col_desc].mean():.2f}")
                        st.write(f"Median: {df[selected_num_col_desc].median():.2f}")
                        st.write(f"Mode(s): {', '.join(map(str, df[selected_num_col_desc].mode().tolist()))}")
                        st.write(f"Skewness: {df[selected_num_col_desc].skew():.2f}") # Added Skewness
                        st.write(f"Standard Deviation: {df[selected_num_col_desc].std():.2f}")
                        st.write(f"Variance: {df[selected_num_col_desc].var():.2f}")
                        mean_abs_dev = (df[selected_num_col_desc] - df[selected_num_col_desc].mean()).abs().mean() # Mean Deviation for Ungrouped
                        st.write(f"Mean Absolute Deviation: {mean_abs_dev:.2f}")
                else:
                    st.info("No numerical columns found for detailed descriptive statistics.")

                # Note: Mean Deviation for Discrete Grouped Data is more complex for a universal tool
                # and would require specific group definitions beyond simple column selection.
                # For now, we've included Mean Deviation for Ungrouped Data.

            if st.session_state.get(analysis_options["Exploratory Data Analysis (EDA)"], True):
                st.subheader("🧭 Exploratory Data Analysis (EDA)")
                st.markdown("Investigating data to discover patterns, relationships, and anomalies.")
                
                st.write("Dataset Info:")
                buffer = io.StringIO()
                df.info(buf=buffer)
                s = buffer.getvalue()
                st.text(s)

                st.write("Missing Values per Column:")
                st.write(df.isnull().sum())

                if numerical_cols:
                    st.markdown("Visualizations for Numerical Columns:")
                    selected_num_col_eda = st.selectbox("Select Numerical Column for EDA plots", numerical_cols, key="eda_num_col")
                    if selected_num_col_eda:
                        st.plotly_chart(px.histogram(df, x=selected_num_col_eda, title=f"Histogram of {selected_num_col_eda}"))
                        st.plotly_chart(px.box(df, y=selected_num_col_eda, title=f"Box Plot of {selected_num_col_eda}"))
                    
                    if len(numerical_cols) > 1:
                        st.write("Correlation Heatmap (Numerical Columns):")
                        corr = df[numerical_cols].corr()
                        fig_corr, ax_corr = plt.subplots()
                        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax_corr)
                        st.pyplot(fig_corr)
                    else:
                        st.info("Need at least two numerical columns for a correlation heatmap.")
                else:
                    st.info("No numerical columns found for EDA visualizations.")

                if categorical_cols:
                    st.markdown("Visualizations for Categorical Columns:")
                    selected_cat_col_eda = st.selectbox("Select Categorical Column for EDA plots", categorical_cols, key="eda_cat_col")
                    if selected_cat_col_eda:
                        fig_count, ax_count = plt.subplots()
                        sns.countplot(data=df, y=selected_cat_col_eda, ax=ax_count, order = df[selected_cat_col_eda].value_counts().index)
                        plt.title(f"Count Plot of {selected_cat_col_eda}")
                        plt.xticks(rotation=45)
                        st.pyplot(fig_count)
                else:
                    st.info("No categorical columns found for EDA visualizations.")

            if st.session_state.get(analysis_options["Predictive Analysis"], True):
                st.subheader("🔮 Predictive Analysis (Simple Linear Regression Example)")
                st.markdown("Using statistical models to forecast future outcomes. Here's a simple linear regression example.")
                if len(numerical_cols) >= 2:
                    st.write("Select variables for Simple Linear Regression:")
                    x_var = st.selectbox("Select Independent Variable (X)", numerical_cols, key="pred_x")
                    y_var = st.selectbox("Select Dependent Variable (Y)", numerical_cols, key="pred_y")

                    if x_var and y_var and x_var != y_var:
                        X = df[[x_var]].copy() # Make a copy to avoid SettingWithCopyWarning
                        y = df[y_var].copy()
                        
                        # Handle NaN values by dropping rows with NaNs in selected columns
                        temp_df = pd.concat([X, y], axis=1).dropna()
                        X_clean = temp_df[[x_var]]
                        y_clean = temp_df[y_var]

                        if not X_clean.empty and not y_clean.empty:
                            X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
                            model = LinearRegression()
                            model.fit(X_train, y_train)
                            predictions = model.predict(X_test)
                            r2 = r2_score(y_test, predictions)
                            st.write(f"Linear Regression Model: {y_var} ~ {x_var}")
                            st.write(f"Coefficient: {model.coef_[0]:.2f}")
                            st.write(f"Intercept: {model.intercept_:.2f}")
                            st.write(f"R-squared on Test Set: {r2:.2f}")
                            fig_reg = px.scatter(x=X_test[x_var], y=y_test, title=f"Regression: {y_var} vs {x_var}", labels={x_var: x_var, 'y': y_var})
                            fig_reg.add_scatter(x=X_test[x_var], y=predictions, mode='lines', name='Regression Line')
                            st.plotly_chart(fig_reg)
                        else:
                            st.warning(f"Not enough data after removing NaNs from '{x_var}' and '{y_var}' for regression.")
                    elif x_var == y_var and x_var is not None:
                        st.warning("Independent and Dependent variables cannot be the same.")
                else:
                    st.info("Need at least two numerical columns for a simple linear regression example.")

            if st.session_state.get(analysis_options["Inferential Analysis"], True):
                st.subheader("🧩 Inferential Analysis")
                st.markdown("""
    Drawing conclusions and making predictions about a population based on sample data.
    Common examples include hypothesis testing and confidence intervals.
                   """)
                st.info("""
    Inferential analysis often requires specific hypotheses and assumptions about the data.
    The results should be interpreted in the context of these assumptions and the research question.
                   """)
                if numerical_cols:
                    st.markdown("Confidence Interval for the Mean:")
                    selected_num_col_inf = st.selectbox("Select Numerical Column for Confidence Interval", numerical_cols, key="inf_num_col")
                    confidence_level = st.slider("Select Confidence Level", 0.80, 0.99, 0.95, 0.01, key="inf_confidence")

                    if selected_num_col_inf:
                        data = df[selected_num_col_inf].dropna()
                        if len(data) > 1:
                            dof = len(data)-1 # Degree of Freedom
                            ci = stats.t.interval(confidence_level, dof, loc=data.mean(), scale=stats.sem(data))
                            st.write(f"The {confidence_level*100:.0f}% confidence interval for the mean of **{selected_num_col_inf}** is: ({ci[0]:.2f}, {ci[1]:.2f}) with {dof} degrees of freedom.")
                        else:
                            st.warning(f"Not enough data points in '{selected_num_col_inf}' (after dropping NaNs) to calculate a confidence interval.")
                else:
                    st.info("No numerical columns available to calculate confidence intervals.")

            if st.session_state.get(analysis_options["Prescriptive Analysis"], True):
                st.subheader("💡 Prescriptive Analysis")
                st.markdown("Recommending actions and decisions based on data analysis, often involving optimization and simulation.")
                st.info("Prescriptive analysis builds on predictive models to suggest optimal actions. This is highly domain-specific and often involves complex modeling techniques.")

            if st.session_state.get(analysis_options["Causal Analysis"], True):
                st.subheader("🔗 Causal Analysis")
                st.markdown("Identifying cause-and-effect relationships between variables.")
                st.info("Causal analysis aims to determine if changes in one variable directly cause changes in another. This often requires experimental design or advanced quasi-experimental statistical methods beyond standard descriptive or predictive analytics.")

            if st.session_state.get(analysis_options["ANOVA"], True):
                st.subheader("🔬 ANOVA (One-Way Analysis of Variance)")
                st.markdown("Comparing the means of a numerical variable across two or more groups defined by a categorical variable.")

                if numerical_cols and categorical_cols:
                    st.write("Select variables for One-Way ANOVA:")
                    anova_num_col = st.selectbox("Select Numerical Variable (Dependent)", numerical_cols, key="anova_num")
                    anova_cat_col = st.selectbox("Select Categorical Variable (Independent Factor/Group)", categorical_cols, key="anova_cat")

                    if anova_num_col and anova_cat_col:
                        # Prepare data for ANOVA: list of arrays, one for each group
                        grouped_data = [df[anova_num_col][df[anova_cat_col] == category].dropna()
                                        for category in df[anova_cat_col].unique()]
                        # Filter out empty groups or groups with insufficient data for variance calculation
                        grouped_data_filtered = [g for g in grouped_data if len(g) > 1]

                        if len(grouped_data_filtered) >= 2:
                            f_statistic, p_value = stats.f_oneway(*grouped_data_filtered)
                            st.write(f"**ANOVA Results for {anova_num_col} by {anova_cat_col}:**")
                            st.write(f"F-statistic: {f_statistic:.2f}")
                            st.write(f"P-value: {p_value:.3f}")
                            # Degrees of Freedom
                            df_between = len(grouped_data_filtered) - 1
                            df_within = sum(len(g) for g in grouped_data_filtered) - len(grouped_data_filtered) # type: ignore
                            st.write(f"Degrees of Freedom (Between Groups): {df_between}")
                            st.write(f"Degrees of Freedom (Within Groups): {df_within}")
                        else:
                            st.warning("Not enough groups with sufficient data to perform ANOVA. Each group needs at least 2 data points.")
                else:
                    st.info("ANOVA requires at least one numerical and one categorical column.")

            # Check if any analysis was selected to be shown
            any_analysis_shown = any(st.session_state.get(key, True) for key in analysis_options.values())
            if not any_analysis_shown:
                st.info("No analysis types selected. Please check the boxes above to display specific analyses.")

        # Build the dashboard based on user choices
        st.subheader(f"🚀 {dashboard_title}")
        num_plots = 0

        if include_descriptive:
            st.markdown("### Descriptive Statistics")
            st.write(df.describe(include='all'))  # Show overall stats

        if include_eda:
            st.markdown("### Exploratory Data Analysis")

            if numerical_cols:
                cols = st.columns(num_cols_per_row)
                for col in numerical_cols:
                    with cols[num_plots % num_cols_per_row]:
                        st.plotly_chart(px.histogram(df, x=col, title=f"Distribution of {col}"), use_container_width=True)
                        num_plots += 1
                        if num_plots > 5: # Example Limit (adjust as needed)
                            break
                if len(numerical_cols) > 1:
                   with st.container():  # Ensure heatmap spans full width if needed
                        st.write("Correlation Heatmap")
                        corr = df[numerical_cols].corr()
                        fig_corr, ax_corr = plt.subplots()
                        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax_corr)
                        st.pyplot(fig_corr)


            if categorical_cols:
                cols = st.columns(num_cols_per_row)
                for col in categorical_cols:
                    with cols[num_plots % num_cols_per_row]:
                        fig_count, ax_count = plt.subplots()
                        sns.countplot(data=df, y=col, ax=ax_count, order=df[col].value_counts().index)
                        plt.title(f"Count of {col}")
                        plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
                        plt.tight_layout()
                        st.pyplot(fig_count)
                        num_plots += 1
                        if num_plots > 10:  # Example Limit
                            break

        if num_plots == 0 and not include_descriptive:
            st.info("Enable EDA or Descriptive Statistics to populate the dashboard.")
        else:
             st.success("✅ Dashboard generated successfully!")

        # Example interactive filter (add more!)
        if numerical_cols:
            filter_col = st.selectbox("Add a filter for:", numerical_cols, index=None, placeholder="Choose a column")
            if filter_col:
               min_val, max_val = df[filter_col].min(), df[filter_col].max()
               selected_range = st.slider(f"Filter {filter_col} range:", min_val, max_val, (min_val, max_val))
               df = df[(df[filter_col] >= selected_range[0]) & (df[filter_col] <= selected_range[1])]
               st.write("Filtered Dataset (Preview):")
               st.dataframe(df.head(), use_container_width=True)

else:
    st.info("📂 Upload a dataset or enter data manually to get started.")