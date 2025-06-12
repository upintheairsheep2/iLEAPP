import plistlib
import scripts.artifacts.artGlobals #use to get iOS version from seeker

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_column_exist_in_db

__artifacts_v2__ = {
    "SiriHashtagImages": {
        "name": "Siri Hashtag Images",
        "description": "Parses recent search queries and recently used items from the Hashtag Images plugin in iMessage",
        "author": "upintheairsheep",
        "version": "0.1",
        "date": "2025-06-12",
        "category": "Siri Activity",
        "paths": ('*/Library/Preferences/com.apple.siri.parsec.HashtagImagesApp.HashtagImagesExtension.plist',),
        "function": "get_siri_hashtag_images",
        "output_types": ("lava", "html", "tsv", "timeline")
    }
}

def get_siri_hashtag_images(files_found, report_folder, seeker, wrap_text, timezone_offset):
    queries_data = []
    results_data = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        with open(file_found, 'rb') as f:
            try:
                plist = plistlib.load(f)
                
                # Process recent queries
                if 'STSRecentQueries' in plist:
                    for i, query in enumerate(plist['STSRecentQueries']):
                        queries_data.append((i+1, query))
                
                # Process recent results
                if 'STSRecentResults1' in plist:
                    for i, result in enumerate(plist['STSRecentResults1']):
                        app_provider = result.get('app-provider-name', '')
                        url = result.get('url', '')
                        thumbnail_url = result.get('thumbnail-url', '')
                        store_id = result.get('store-identifier', '')
                        result_type = result.get('result-type', '')
                        host_page = result.get('meta-hostpage-url', '')
                        
                        results_data.append((
                            i+1,
                            app_provider,
                            url,
                            thumbnail_url,
                            store_id,
                            result_type,
                            host_page
                        ))
                
                # Get legal notice count if present
                legal_notice_count = plist.get('LegalNoticeCount', 0)
                
            except Exception as ex:
                logfunc(f'Error parsing Siri Hashtag Images plist: {str(ex)}')
    
    # Define headers for queries
    queries_headers = ('Position', 'Search Query')
    
    # Define headers for results
    results_headers = ('Position', 'Provider App', 'URL', 'Thumbnail URL', 'App Store ID', 'Result Type', 'Host Page URL')
    
    # Write queries data
    if queries_data:
        description = 'Hashtag Images GIF Search Queries'
        report = ArtifactHtmlReport('Siri Hashtag Images - Recent Search Queries')
        report.start_artifact_report(report_folder, 'Siri Hashtag Images - Recent Search Queries', description)
        report.add_script()
        data_headers = queries_headers
        report.write_artifact_data_table(data_headers, queries_data, file_found)
        report.end_artifact_report()
        
        tsvname = f'Siri Hashtag Images - Recent Search Queries'
        tsv(report_folder, data_headers, queries_data, tsvname)
        
        tlactivity = 'Siri Hashtag Images - Recent Search Queries'
        timeline(report_folder, tlactivity, queries_data, queries_headers)
    else:
        logfunc('No Siri Hashtag Images queries data available')
    
    # Write results data
    if results_data:
        description = 'Hashtag Images GIF Recently Used'
        report = ArtifactHtmlReport('Siri Hashtag Images - Recently Used Images')
        report.start_artifact_report(report_folder, 'Siri Hashtag Images - Recently Used Images', description)
        report.add_script()
        data_headers = results_headers
        report.write_artifact_data_table(data_headers, results_data, file_found)
        report.end_artifact_report()
        
        tsvname = f'Siri Hashtag Images - Recently Used Images'
        tsv(report_folder, data_headers, results_data, tsvname)
        
        tlactivity = 'Siri Hashtag Images - Recently Used Images'
        timeline(report_folder, tlactivity, results_data, results_headers)
    else:
        logfunc('No Siri Hashtag Images results data available')
    
    return queries_headers + results_headers, queries_data + results_data, ''
