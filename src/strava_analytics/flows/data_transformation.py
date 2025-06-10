"""Data transformation flows for Strava activities data."""

from typing import List
import polars as pl

from prefect import flow, task, get_run_logger


@task
def select_core_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Select and rename core columns from raw activities data."""
    logger = get_run_logger()
    
    if df.is_empty():
        logger.warning("Empty DataFrame provided for column selection")
        return df
    
    logger.info(f"Selecting core columns from DataFrame with shape: {df.shape}")
    
    # Define the columns we want to keep
    core_columns = [
        "id", "name", "distance", "moving_time", "total_elevation_gain",
        "sport_type", "start_date_local", "gear_id", "start_latlng",
        "end_latlng", "average_speed", "max_speed", "pr_count"
    ]
    
    # Check which columns exist in the DataFrame
    available_columns = df.columns
    missing_columns = [col for col in core_columns if col not in available_columns]
    
    if missing_columns:
        logger.warning(f"Missing columns in DataFrame: {missing_columns}")
    
    # Select only the columns that exist
    existing_core_columns = [col for col in core_columns if col in available_columns]
    
    try:
        df_selected = df.select(existing_core_columns)
        logger.info(f"Selected {len(existing_core_columns)} core columns")
        return df_selected
        
    except Exception as e:
        logger.error(f"Error selecting core columns: {e}")
        raise


@task
def create_derived_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Create derived columns with unit conversions and renaming."""
    logger = get_run_logger()
    
    if df.is_empty():
        logger.warning("Empty DataFrame provided for derived column creation")
        return df
    
    logger.info("Creating derived columns with unit conversions")
    
    try:
        df_derived = df.with_columns([
            # Rename and keep original ID and name
            pl.col('id').alias('activity_id'),
            pl.col('name').alias('activity_name'),
            
            # Convert distance from meters to kilometers
            (pl.col('distance') / 1000).round(2).alias('distance_km'),
            
            # Convert moving time from seconds to hours
            (pl.col('moving_time') / 3600).round(2).alias('moving_time_hr'),
            
            # Convert speeds from m/s to km/h
            (pl.col('average_speed') * 3.6).round(2).alias('average_speed_km_per_hr'),
            (pl.col('max_speed') * 3.6).round(2).alias('max_speed_km_per_hr'),
        ])
        
        logger.info("Successfully created derived columns")
        return df_derived
        
    except Exception as e:
        logger.error(f"Error creating derived columns: {e}")
        raise


@task
def drop_original_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Drop original columns that have been converted."""
    logger = get_run_logger()
    
    if df.is_empty():
        logger.warning("Empty DataFrame provided for column dropping")
        return df
    
    columns_to_drop = ['distance', 'moving_time', 'id', 'name', 'max_speed', 'average_speed']
    
    # Only drop columns that exist in the DataFrame
    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    
    if not existing_columns_to_drop:
        logger.info("No columns to drop")
        return df
    
    try:
        df_cleaned = df.drop(existing_columns_to_drop)
        logger.info(f"Dropped {len(existing_columns_to_drop)} original columns: {existing_columns_to_drop}")
        return df_cleaned
        
    except Exception as e:
        logger.error(f"Error dropping columns: {e}")
        raise


@task
def apply_data_types(df: pl.DataFrame) -> pl.DataFrame:
    """Apply appropriate data types to columns."""
    logger = get_run_logger()
    
    if df.is_empty():
        logger.warning("Empty DataFrame provided for data type conversion")
        return df
    
    logger.info("Applying data type conversions")
    
    try:
        # Define type conversions for columns that exist
        type_conversions = []
        
        if 'activity_id' in df.columns:
            type_conversions.append(pl.col('activity_id').cast(pl.Int64))
        
        if 'gear_id' in df.columns:
            type_conversions.append(pl.col('gear_id').cast(pl.Categorical))
        
        if 'activity_name' in df.columns:
            type_conversions.append(pl.col('activity_name').cast(pl.Categorical))
        
        if 'sport_type' in df.columns:
            type_conversions.append(pl.col('sport_type').cast(pl.Categorical))
        
        if 'start_date_local' in df.columns:
            type_conversions.append(pl.col('start_date_local').cast(pl.Datetime))
        
        if type_conversions:
            df_typed = df.with_columns(type_conversions)
            logger.info(f"Applied {len(type_conversions)} data type conversions")
        else:
            df_typed = df
            logger.info("No data type conversions applied")
        
        return df_typed
        
    except Exception as e:
        logger.error(f"Error applying data types: {e}")
        raise


@task
def extract_coordinates(df: pl.DataFrame) -> pl.DataFrame:
    """Extract latitude and longitude from coordinate arrays."""
    logger = get_run_logger()
    logger.info("Extracting coordinates from latlng arrays")

    try:
        df_with_coords = df.with_columns([
            # Extract start coordinates
            pl.when(pl.col("start_latlng").is_not_null())
            .then(pl.col("start_latlng").list.get(0))
            .otherwise(None)
            .alias("start_latitude"),

            pl.when(pl.col("start_latlng").is_not_null())
            .then(pl.col("start_latlng").list.get(1))
            .otherwise(None)
            .alias("start_longitude"),

            # Extract end coordinates
            pl.when(pl.col("end_latlng").is_not_null())
            .then(pl.col("end_latlng").list.get(0))
            .otherwise(None)
            .alias("end_latitude"),

            pl.when(pl.col("end_latlng").is_not_null())
            .then(pl.col("end_latlng").list.get(1))
            .otherwise(None)
            .alias("end_longitude")
        ])

        # Drop the original latlng columns since we have separate lat/lng now
        df_final = df_with_coords.drop(["start_latlng", "end_latlng"])

        logger.info("Successfully extracted coordinates to separate columns")
        return df_final

    except Exception as e:
        logger.error(f"Error extracting coordinates: {e}")
        # If extraction fails, just drop the latlng columns to avoid schema issues
        return df.drop(["start_latlng", "end_latlng"])


@task
def add_feature_engineering(df: pl.DataFrame) -> pl.DataFrame:
    """Add feature engineering columns."""
    logger = get_run_logger()
    
    if df.is_empty():
        logger.warning("Empty DataFrame provided for feature engineering")
        return df
    
    logger.info("Adding feature engineering columns")
    
    try:
        feature_columns = []
        
        # Add activity hour if start_date_local exists
        if 'start_date_local' in df.columns:
            feature_columns.append(
                pl.col('start_date_local').dt.hour().alias('activity_hour')
            )
        
        # Add activity day of week if start_date_local exists
        if 'start_date_local' in df.columns:
            feature_columns.append(
                pl.col('start_date_local').dt.weekday().alias('activity_weekday')
            )
        
        # Add activity year if start_date_local exists
        if 'start_date_local' in df.columns:
            feature_columns.append(
                pl.col('start_date_local').dt.year().alias('activity_year')
            )
        
        # Add activity month if start_date_local exists
        if 'start_date_local' in df.columns:
            feature_columns.append(
                pl.col('start_date_local').dt.month().alias('activity_month')
            )
        
        if feature_columns:
            df_featured = df.with_columns(feature_columns)
            logger.info(f"Added {len(feature_columns)} feature engineering columns")
        else:
            df_featured = df
            logger.info("No feature engineering columns added")
        
        return df_featured
        
    except Exception as e:
        logger.error(f"Error in feature engineering: {e}")
        raise


@flow(name="strava-data-transformation", log_prints=True)
def strava_data_transformation_flow(raw_activities_df: pl.DataFrame) -> pl.DataFrame:
    """
    Main data transformation flow for Strava activities.
    
    Args:
        raw_activities_df: Raw activities DataFrame from API
    
    Returns:
        Transformed and cleaned DataFrame ready for database loading
    """
    logger = get_run_logger()
    logger.info(f"Starting data transformation flow with {len(raw_activities_df)} activities")
    
    if raw_activities_df.is_empty():
        logger.warning("Empty DataFrame provided - returning empty DataFrame")
        return raw_activities_df
    
    # Step 1: Select core columns
    df_selected = select_core_columns(raw_activities_df)
    
    # Step 2: Create derived columns with unit conversions
    df_derived = create_derived_columns(df_selected)
    
    # Step 3: Drop original columns
    df_cleaned = drop_original_columns(df_derived)
    
    # Step 4: Extract coordinates to separate columns
    df_coords = extract_coordinates(df_cleaned)

    # Step 5: Apply data types
    df_typed = apply_data_types(df_coords)

    # Step 6: Add feature engineering
    df_final = add_feature_engineering(df_typed)
    
    logger.info(f"Data transformation completed. Final shape: {df_final.shape}")
    logger.info(f"Final columns: {df_final.columns}")
    
    return df_final


if __name__ == "__main__":
    # For testing with sample data
    import polars as pl
    
    # Create sample data for testing
    sample_data = {
        'id': [1, 2, 3],
        'name': ['Morning Run', 'Evening Bike', 'Weekend Hike'],
        'distance': [5000, 15000, 8000],  # meters
        'moving_time': [1800, 3600, 7200],  # seconds
        'sport_type': ['Run', 'Ride', 'Hike'],
        'start_date_local': ['2024-01-01T08:00:00Z', '2024-01-02T18:00:00Z', '2024-01-03T10:00:00Z'],
        'average_speed': [2.78, 4.17, 1.11],  # m/s
        'max_speed': [5.56, 8.33, 2.22]  # m/s
    }
    
    sample_df = pl.DataFrame(sample_data)
    result = strava_data_transformation_flow(sample_df)
    print(f"Transformed DataFrame shape: {result.shape}")
    print(result)
