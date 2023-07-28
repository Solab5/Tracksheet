import streamlit as st
import pandas as pd
from io import BytesIO
import os
# Function to preprocess data
def preprocess_data(data):
    data['pre_village'] = data['pre_village'].apply(lambda x: 'Biizi' if x == 'Bizi' else x)

# Function to sample data
def sample_data(data, num_samples, num_contractors):
    sampled_data = pd.DataFrame()
    for pre_village, data_group in data.groupby('pre_village'):
        for contractor in range(1, num_contractors + 1):
            num_samples_to_take = min(num_samples, len(data_group))
            if num_samples_to_take > 0:
                sampled_rows = data_group.sample(n=num_samples_to_take)
                sampled_rows['contractor'] = contractor
                sampled_data = pd.concat([sampled_data, sampled_rows])
    return sampled_data.reset_index(drop=True)

# Main function to run the Streamlit app
def main():
    st.title("RTV TrackSheet Generator")
    
    # File upload section
    st.header("Upload The Target File And Reserve File Separetely")
    target_file = st.file_uploader("Upload Target File (Excel)", type=["xlsx"])
    reserve_file = st.file_uploader("Upload Reserve File (Excel)", type=["xlsx"])
    sheet_name = st.text_input("Sheet Name")

    enter_button = st.button("Enter")

    if target_file and reserve_file and sheet_name:
        # Load data from the uploaded files
        targets = pd.read_excel(target_file, sheet_name=sheet_name)
        reserves = pd.read_excel(reserve_file, sheet_name=sheet_name)

        # Preprocess data
        preprocess_data(targets)
        preprocess_data(reserves)

        # Get user inputs for sampling
        num_target_samples = st.number_input("Number of Target Samples", value=8, min_value=1)
        num_reserve_samples = st.number_input("Number of Reserve Samples", value=4, min_value=1)
        num_contractors = st.number_input("Number of Contractors", value=4, min_value=1)

        # Sample data
        sampled_targets = sample_data(targets, num_target_samples, num_contractors)
        sampled_reserves = sample_data(reserves, num_reserve_samples, num_contractors)

        # Combine sampled data from both targets and reserves
        sampled_data = pd.concat([sampled_targets, sampled_reserves], ignore_index=True)

        # Display the final sampled data
        st.header("Final Data")
        st.dataframe(sampled_data)

        # Option to save the final file
        if st.button("Download File"):
        # Convert the sampled data to an Excel file
            excel_file = BytesIO()
            with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
                sampled_data.to_excel(writer, index=False)

            # Create a button to download the Excel file
            st.download_button(
                label="Download File as Excel",
                data=excel_file.getvalue(),
                file_name=f"{sheet_name}_tracksheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# Run the app
if __name__ == "__main__":
    main()
