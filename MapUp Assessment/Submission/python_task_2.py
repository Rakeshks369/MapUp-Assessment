import pandas as pd

def calculate_distance_matrix(df):
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Set 'ID' column as index for easier manipulation
    df.set_index('ID', inplace=True)
    
    # Initialize an empty distance matrix
    distance_matrix = pd.DataFrame(index=df.index, columns=df.index)
    distance_matrix = distance_matrix.fillna(0)  # Filling NaN values with 0
    
    # Iterate through rows and columns of the distance matrix
    for i in distance_matrix.index:
        for j in distance_matrix.columns:
            # Check if the distance is known (not NaN) and set both sides of the matrix symmetrically
            if not pd.isnull(df.loc[i, j]) and not pd.isnull(df.loc[j, i]):
                distance_matrix.loc[i, j] = df.loc[i, j] + df.loc[j, i]
                distance_matrix.loc[j, i] = df.loc[i, j] + df.loc[j, i]
            elif not pd.isnull(df.loc[i, j]):
                distance_matrix.loc[i, j] = df.loc[i, j]
            elif not pd.isnull(df.loc[j, i]):
                distance_matrix.loc[j, i] = df.loc[j, i]
    
    # Set diagonal values to 0
    distance_matrix.values[[range(len(distance_matrix))]*2] = 0
    
    return distance_matrix

# Load the dataset
df = pd.read_csv('dataset-3.csv')

# Call the function to calculate distance matrix
result_distance_matrix = calculate_distance_matrix(df)


def unroll_distance_matrix(distance_matrix):
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        distance_matrix (pandas.DataFrame): Distance matrix DataFrame

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Initialize an empty list to store the unrolled data
    unrolled_data = []
    
    # Iterate through the distance matrix to create combinations and their distances
    for i in distance_matrix.index:
        for j in distance_matrix.columns:
            # Exclude same id_start to id_end combinations and consider only non-zero distances
            if i != j and distance_matrix.loc[i, j] != 0:
                unrolled_data.append({'id_start': i, 'id_end': j, 'distance': distance_matrix.loc[i, j]})
    
    # Create a DataFrame from the unrolled data
    unrolled_df = pd.DataFrame(unrolled_data)
    
    return unrolled_df

# Assuming 'result_distance_matrix' is the DataFrame obtained from Question 1
# Call the function to unroll the distance matrix
result_unrolled_distance = unroll_distance_matrix(result_distance_matrix)


def find_ids_within_ten_percentage_threshold(df, reference_id):
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame): DataFrame containing columns 'id_start', 'id_end', and 'distance'.
        reference_id (int): Reference ID for calculating the average distance.

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Filter the DataFrame for rows with the reference_id as id_start
    reference_df = df[df['id_start'] == reference_id]
    
    # Calculate the average distance for the reference_id
    reference_avg_distance = reference_df['distance'].mean()
    
    # Calculate the threshold values (10% of the reference average distance)
    lower_threshold = reference_avg_distance - (0.1 * reference_avg_distance)
    upper_threshold = reference_avg_distance + (0.1 * reference_avg_distance)
    
    # Filter the DataFrame for IDs within the 10% threshold
    within_threshold_ids = df[(df['id_start'] != reference_id) & 
                              (df['distance'] >= lower_threshold) & 
                              (df['distance'] <= upper_threshold)]['id_start'].unique()
    
    # Sort the IDs within the threshold
    within_threshold_ids.sort()
    
    return pd.DataFrame({'id_start': within_threshold_ids})

# Assuming 'result_unrolled_distance' is the DataFrame obtained from Question 2
# Call the function to find IDs within 10% threshold of the reference ID's average distance
reference_value = 5  # Replace with your desired reference ID
result_ids_within_threshold = find_ids_within_ten_percentage_threshold(result_unrolled_distance, reference_value)


def calculate_toll_rate(df):
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame): Unrolled DataFrame containing columns 'id_start', 'id_end', 'distance'.

    Returns:
        pandas.DataFrame: DataFrame with added columns for toll rates of different vehicle types.
    """
    # Define rate coefficients for different vehicle types
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}
    
    # Calculate toll rates for each vehicle type by multiplying distance with rate coefficients
    for vehicle_type, rate in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate
    
    return df

# Assuming 'result_unrolled_distance' is the DataFrame obtained from Question 2
# Call the function to calculate toll rates
result_with_toll_rates = calculate_toll_rate(result_unrolled_distance)


def calculate_time_based_toll_rates(df):
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame): DataFrame with columns 'id_start', 'id_end', 'distance'.

    Returns:
        pandas.DataFrame: DataFrame with added columns for time-based toll rates.
    """
    # Define time ranges and discount factors
    time_ranges = [
        ('00:00:00', '10:00:00', 0.8),
        ('10:00:00', '18:00:00', 1.2),
        ('18:00:00', '23:59:59', 0.8)
    ]
    weekend_discount_factor = 0.7

    # Convert columns to datetime for further manipulation
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    
    # Create a map for weekdays and weekends
    weekday_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday'}
    weekend_map = {5: 'Saturday', 6: 'Sunday'}

    # Apply discount factors based on time ranges and days
    for index, row in df.iterrows():
        start_day = row['start_time'].weekday()
        end_day = row['end_time'].weekday()

        if start_day in weekday_map:
            start_day = weekday_map[start_day]
            end_day = weekday_map[end_day]
            
            # Calculate toll rate based on time range for weekdays
            for start, end, discount_factor in time_ranges:
                if start <= str(row['start_time'].time()) <= end:
                    df.at[index, 'car'] *= discount_factor
                    break
        else:
            start_day = weekend_map[start_day]
            end_day = weekend_map[end_day]
            
            # Apply constant discount factor for weekends
            df.at[index, 'car'] *= weekend_discount_factor

        # Assign start_day and end_day values
        df.at[index, 'start_day'] = start_day
        df.at[index, 'end_day'] = end_day

    return df

# Assuming 'result_ids_within_threshold' is the DataFrame obtained from Question 3
# Call the function to calculate time-based toll rates
result_time_based_toll_rates = calculate_time_based_toll_rates(result_ids_within_threshold)
