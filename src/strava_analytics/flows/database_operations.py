"""Database operations flows for Strava activities data."""

from typing import Dict, Any, Optional
import polars as pl
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from prefect.cache_policies import INPUTS

from ..config import settings


@task(retries=3, retry_delay_seconds=30)
def create_database_connection():
    """Create and test database connection."""
    logger = get_run_logger()
    
    try:
        engine = create_engine(settings.database_url, echo=False)
        
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("✅ Database connection successful")
        return engine
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to database: {e}")
        raise


@task
def check_table_exists(engine, table_name: str) -> bool:
    """Check if a table exists in the database."""
    logger = get_run_logger()
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = '{settings.db_name}' 
                AND table_name = '{table_name}'
            """))
            
            exists = result.fetchone()[0] > 0
            logger.info(f"Table '{table_name}' exists: {exists}")
            return exists
            
    except Exception as e:
        logger.error(f"Error checking if table '{table_name}' exists: {e}")
        raise


@task
def get_table_row_count(engine, table_name: str) -> int:
    """Get the current row count of a table."""
    logger = get_run_logger()
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.fetchone()[0]
            logger.info(f"Table '{table_name}' has {count} rows")
            return count
            
    except Exception as e:
        logger.warning(f"Could not get row count for table '{table_name}': {e}")
        return 0


@task
def convert_polars_to_pandas(df: pl.DataFrame) -> pd.DataFrame:
    """Convert Polars DataFrame to Pandas for database operations."""
    logger = get_run_logger()
    
    if df.is_empty():
        logger.warning("Empty Polars DataFrame provided")
        return pd.DataFrame()
    
    try:
        pandas_df = df.to_pandas()
        logger.info(f"Converted Polars DataFrame to Pandas. Shape: {pandas_df.shape}")
        return pandas_df
        
    except Exception as e:
        logger.error(f"Error converting Polars to Pandas DataFrame: {e}")
        raise


@task
def check_for_duplicates(df: pd.DataFrame, id_column: str = 'activity_id') -> Dict[str, Any]:
    """Check for duplicate activities in the DataFrame."""
    logger = get_run_logger()
    
    if df.empty:
        return {'has_duplicates': False, 'duplicate_count': 0}
    
    if id_column not in df.columns:
        logger.warning(f"ID column '{id_column}' not found in DataFrame")
        return {'has_duplicates': False, 'duplicate_count': 0}
    
    try:
        duplicate_mask = df.duplicated(subset=[id_column], keep=False)
        duplicate_count = duplicate_mask.sum()
        has_duplicates = duplicate_count > 0
        
        if has_duplicates:
            duplicate_ids = df[duplicate_mask][id_column].unique()
            logger.warning(f"Found {duplicate_count} duplicate activities with IDs: {duplicate_ids}")
        else:
            logger.info("No duplicate activities found")
        
        return {
            'has_duplicates': has_duplicates,
            'duplicate_count': duplicate_count,
            'duplicate_ids': duplicate_ids.tolist() if has_duplicates else []
        }
        
    except Exception as e:
        logger.error(f"Error checking for duplicates: {e}")
        return {'has_duplicates': False, 'duplicate_count': 0, 'error': str(e)}


@task
def remove_duplicates(df: pd.DataFrame, id_column: str = 'activity_id') -> pd.DataFrame:
    """Remove duplicate activities, keeping the first occurrence."""
    logger = get_run_logger()
    
    if df.empty:
        return df
    
    if id_column not in df.columns:
        logger.warning(f"ID column '{id_column}' not found in DataFrame")
        return df
    
    try:
        original_count = len(df)
        df_deduplicated = df.drop_duplicates(subset=[id_column], keep='first')
        final_count = len(df_deduplicated)
        removed_count = original_count - final_count
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate activities. "
                       f"Original: {original_count}, Final: {final_count}")
        else:
            logger.info("No duplicates to remove")
        
        return df_deduplicated
        
    except Exception as e:
        logger.error(f"Error removing duplicates: {e}")
        raise


@task(retries=2, retry_delay_seconds=60)
def load_data_to_database(
    engine, 
    df: pd.DataFrame, 
    table_name: str, 
    if_exists: str = 'append'
) -> Dict[str, Any]:
    """Load DataFrame to database table."""
    logger = get_run_logger()
    
    if df.empty:
        logger.warning("Empty DataFrame provided - no data to load")
        return {
            'success': True,
            'rows_loaded': 0,
            'message': 'No data to load'
        }
    
    try:
        logger.info(f"Loading {len(df)} rows to table '{table_name}' with if_exists='{if_exists}'")
        
        # Get row count before loading
        initial_count = get_table_row_count(engine, table_name) if check_table_exists(engine, table_name) else 0
        
        # Load data to database
        rows_affected = df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            method='multi',
            chunksize=1000
        )
        
        # Get row count after loading
        final_count = get_table_row_count(engine, table_name)
        actual_rows_added = final_count - initial_count
        
        logger.info(f"✅ Successfully loaded data to '{table_name}'. "
                   f"Rows added: {actual_rows_added}, Total rows: {final_count}")
        
        return {
            'success': True,
            'rows_loaded': actual_rows_added,
            'total_rows_in_table': final_count,
            'initial_count': initial_count
        }
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error loading data to '{table_name}': {e}")
        return {
            'success': False,
            'error': f"Database error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error loading data to '{table_name}': {e}")
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }


@flow(name="strava-database-operations", log_prints=True)
def strava_database_operations_flow(
    activities_df: pl.DataFrame,
    table_name: str = 'activities',
    if_exists: str = 'append',
    remove_duplicates_flag: bool = True
) -> Dict[str, Any]:
    """
    Main database operations flow for Strava activities.
    
    Args:
        activities_df: Transformed activities DataFrame
        table_name: Target database table name
        if_exists: How to behave if table exists ('append', 'replace', 'fail')
        remove_duplicates_flag: Whether to remove duplicates before loading
    
    Returns:
        Dictionary with operation results
    """
    logger = get_run_logger()
    logger.info(f"Starting database operations flow for {len(activities_df)} activities")
    
    if activities_df.is_empty():
        logger.warning("Empty DataFrame provided - no database operations needed")
        return {
            'success': True,
            'rows_loaded': 0,
            'message': 'No data to process'
        }
    
    try:
        # Create database connection
        engine = create_database_connection()
        
        # Convert to Pandas DataFrame
        pandas_df = convert_polars_to_pandas(activities_df)
        
        # Check for duplicates
        duplicate_info = check_for_duplicates(pandas_df)
        
        # Remove duplicates if requested
        if remove_duplicates_flag and duplicate_info['has_duplicates']:
            pandas_df = remove_duplicates(pandas_df)
        
        # Load data to database
        load_result = load_data_to_database(
            engine=engine,
            df=pandas_df,
            table_name=table_name,
            if_exists=if_exists
        )
        
        # Prepare final result
        result = {
            'success': load_result['success'],
            'rows_processed': len(activities_df),
            'rows_loaded': load_result.get('rows_loaded', 0),
            'total_rows_in_table': load_result.get('total_rows_in_table', 0),
            'duplicate_info': duplicate_info,
            'table_name': table_name
        }
        
        if not load_result['success']:
            result['error'] = load_result.get('error')
        
        logger.info(f"Database operations completed. Success: {result['success']}")
        return result
        
    except Exception as e:
        logger.error(f"Database operations flow failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'rows_processed': len(activities_df)
        }


if __name__ == "__main__":
    # For testing
    import polars as pl
    
    # Create sample data
    sample_data = {
        'activity_id': [1, 2, 3],
        'activity_name': ['Morning Run', 'Evening Bike', 'Weekend Hike'],
        'distance_km': [5.0, 15.0, 8.0],
        'moving_time_hr': [0.5, 1.0, 2.0],
        'sport_type': ['Run', 'Ride', 'Hike']
    }
    
    sample_df = pl.DataFrame(sample_data)
    result = strava_database_operations_flow(sample_df)
    print(f"Database operations result: {result}")
