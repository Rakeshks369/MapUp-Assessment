import pandas as pd


def generate_car_matrix(df):
    """
    Creates a DataFrame for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values, 
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    # Pivoting the DataFrame to create the desired matrix
    matrix = df.pivot(index='id_1', columns='id_2', values='car').fillna(0)
    
    # Set diagonal values to 0
    for i in matrix.index:
        matrix.loc[i, i] = 0

    return matrix



def get_type_count(df):
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    # Categorize 'car' values into 'car_type'
    df['car_type'] = pd.cut(df['car'], bins=[float('-inf'), 15, 25, float('inf')],
                            labels=['low', 'medium', 'high'], right=False)
    
    # Calculate count of occurrences for each car_type category
    car_type_counts = df['car_type'].value_counts().to_dict()
    
    # Sort the dictionary alphabetically based on keys
    sorted_car_type_counts = dict(sorted(car_type_counts.items()))
    
    return sorted_car_type_counts



def get_bus_indexes(df):
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    # Calculate the mean of the 'bus' column
    bus_mean = df['bus'].mean()
    
    # Find indices where 'bus' values exceed twice the mean
    bus_indexes = df[df['bus'] > 2 * bus_mean].index.tolist()
    
    # Sort the indices in ascending order
    bus_indexes.sort()
    
    return bus_indexes


def filter_routes(df):
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Group by 'route' and calculate the average of 'truck' values
    avg_truck = df.groupby('route')['truck'].mean()
    
    # Filter routes where the average 'truck' values are greater than 7
    filtered_routes = avg_truck[avg_truck > 7].index.tolist()
    
    # Sort the list of routes
    filtered_routes.sort()
    
    return filtered_routes


def multiply_matrix(matrix):
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    # Apply custom conditions to modify matrix values
    modified_matrix = matrix.applymap(lambda x: x * 0.75 if x > 20 else x * 1.25)
    
    # Round values to 1 decimal place
    modified_matrix = modified_matrix.round(1)
    
    return modified_matrix


def time_check(df):
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period.

    Args:
        df (pandas.DataFrame)

    Returns:
        pd.Series: Return a boolean series indicating correctness of timestamps for each (`id`, `id_2`) pair.
    """
    # Combine 'startDay' and 'startTime' columns to create a new 'start' timestamp
    df['start'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'])

    # Combine 'endDay' and 'endTime' columns to create a new 'end' timestamp
    df['end'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'])

    # Calculate time duration for each row
    df['duration'] = df['end'] - df['start']

    # Check if the duration is a full 24-hour period and spans all 7 days
    check = df.groupby(['id', 'id_2'])['duration'].agg(
        lambda x: (x.min() >= pd.Timedelta(days=7)) and (x.max() <= pd.Timedelta(days=7) - pd.Timedelta(seconds=1))
    )

    return check

import pandas as pd

# Load datasets
df1 = pd.read_csv('data/dataset-1.csv')
df2 = pd.read_csv('dataset-2.csv')

# Call the functions
result_car_matrix = generate_car_matrix(df1)
type_count = get_type_count(df1)
bus_indexes = get_bus_indexes(df1)
filtered_routes = filter_routes(df1)
modified_matrix = multiply_matrix(result_car_matrix)
time_check_result = time_check(df2)
