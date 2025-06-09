"""Main orchestration flow for the Strava analytics pipeline."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from prefect import flow, get_run_logger
# Note: Deployment creation is now handled via prefect.yaml and CLI

from src.flows.token_management import proactive_token_management_flow
from src.flows.data_extraction import strava_data_extraction_flow
from src.flows.data_transformation import strava_data_transformation_flow
from src.flows.database_operations import strava_database_operations_flow


@flow(name="strava-analytics-pipeline", log_prints=True)
def strava_analytics_pipeline_flow(
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    max_pages: int = 100,
    table_name: str = 'activities',
    if_exists: str = 'append',
    remove_duplicates: bool = True
) -> Dict[str, Any]:
    """
    Main orchestration flow for the complete Strava analytics pipeline.
    
    This flow:
    1. Ensures tokens are valid and refreshed if needed
    2. Extracts data from Strava API
    3. Transforms the data
    4. Loads the data to the database
    
    Args:
        after_date: ISO date string (YYYY-MM-DD) to fetch activities after
        before_date: ISO date string (YYYY-MM-DD) to fetch activities before
        max_pages: Maximum number of pages to fetch from API
        table_name: Target database table name
        if_exists: How to behave if table exists ('append', 'replace', 'fail')
        remove_duplicates: Whether to remove duplicates before loading
    
    Returns:
        Dictionary with pipeline execution results
    """
    logger = get_run_logger()
    logger.info("🚀 Starting Strava Analytics Pipeline")
    
    pipeline_start_time = datetime.now()
    results = {
        'pipeline_start_time': pipeline_start_time,
        'success': False,
        'steps_completed': [],
        'errors': []
    }
    
    try:
        # Step 1: Token Management
        logger.info("📋 Step 1: Proactive Token Management")
        token_result = proactive_token_management_flow()
        
        if not token_result['success']:
            error_msg = f"Token management failed: {token_result.get('error')}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        results['steps_completed'].append('token_management')
        results['token_management'] = token_result
        logger.info("✅ Token management completed successfully")
        
        # Step 2: Data Extraction
        logger.info("📊 Step 2: Data Extraction from Strava API")
        activities_df = strava_data_extraction_flow(
            after_date=after_date,
            before_date=before_date,
            max_pages=max_pages
        )
        
        if activities_df.is_empty():
            logger.warning("⚠️ No activities extracted from API")
            results['steps_completed'].append('data_extraction')
            results['data_extraction'] = {
                'activities_count': 0,
                'message': 'No activities found'
            }
        else:
            results['steps_completed'].append('data_extraction')
            results['data_extraction'] = {
                'activities_count': len(activities_df),
                'columns': activities_df.columns
            }
            logger.info(f"✅ Data extraction completed: {len(activities_df)} activities")
        
        # Step 3: Data Transformation
        logger.info("🔄 Step 3: Data Transformation")
        transformed_df = strava_data_transformation_flow(activities_df)
        
        results['steps_completed'].append('data_transformation')
        results['data_transformation'] = {
            'input_rows': len(activities_df),
            'output_rows': len(transformed_df),
            'final_columns': transformed_df.columns if not transformed_df.is_empty() else []
        }
        logger.info(f"✅ Data transformation completed: {len(transformed_df)} rows")
        
        # Step 4: Database Operations
        if not transformed_df.is_empty():
            logger.info("💾 Step 4: Database Operations")
            db_result = strava_database_operations_flow(
                activities_df=transformed_df,
                table_name=table_name,
                if_exists=if_exists,
                remove_duplicates_flag=remove_duplicates
            )
            
            results['steps_completed'].append('database_operations')
            results['database_operations'] = db_result
            
            if db_result['success']:
                logger.info(f"✅ Database operations completed: {db_result['rows_loaded']} rows loaded")
            else:
                error_msg = f"Database operations failed: {db_result.get('error')}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                return results
        else:
            logger.info("⏭️ Skipping database operations - no data to load")
            results['database_operations'] = {
                'success': True,
                'rows_loaded': 0,
                'message': 'No data to load'
            }
        
        # Pipeline completed successfully
        pipeline_end_time = datetime.now()
        pipeline_duration = pipeline_end_time - pipeline_start_time
        
        results.update({
            'success': True,
            'pipeline_end_time': pipeline_end_time,
            'pipeline_duration': str(pipeline_duration),
            'total_activities_processed': len(transformed_df) if not transformed_df.is_empty() else 0
        })
        
        logger.info(f"🎉 Pipeline completed successfully in {pipeline_duration}")
        logger.info(f"📈 Total activities processed: {results['total_activities_processed']}")
        
        return results
        
    except Exception as e:
        error_msg = f"Pipeline failed with unexpected error: {str(e)}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
        results['pipeline_end_time'] = datetime.now()
        results['pipeline_duration'] = str(results['pipeline_end_time'] - pipeline_start_time)
        return results


@flow(name="daily-strava-sync", log_prints=True)
def daily_strava_sync_flow() -> Dict[str, Any]:
    """
    Daily sync flow that fetches recent activities.
    Designed to run daily to keep the database up to date.
    """
    logger = get_run_logger()
    logger.info("🌅 Starting daily Strava sync")
    
    # Get activities from the last 7 days to ensure we don't miss anything
    after_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    result = strava_analytics_pipeline_flow(
        after_date=after_date,
        max_pages=10,  # Limit pages for daily sync
        table_name='activities',
        if_exists='append',
        remove_duplicates=True
    )
    
    logger.info(f"🌅 Daily sync completed. Success: {result['success']}")
    return result


@flow(name="weekly-full-sync", log_prints=True)
def weekly_full_sync_flow() -> Dict[str, Any]:
    """
    Weekly full sync flow that fetches all activities.
    Designed to run weekly to ensure data completeness.
    """
    logger = get_run_logger()
    logger.info("📅 Starting weekly full sync")
    
    result = strava_analytics_pipeline_flow(
        max_pages=200,  # Higher limit for full sync
        table_name='activities',
        if_exists='append',
        remove_duplicates=True
    )
    
    logger.info(f"📅 Weekly sync completed. Success: {result['success']}")
    return result


# Note: Deployments are now configured in prefect.yaml
# Use `prefect deploy --all` to deploy all flows with their schedules


if __name__ == "__main__":
    # For testing - run the main pipeline
    result = strava_analytics_pipeline_flow()
    print(f"Pipeline result: {result}")
