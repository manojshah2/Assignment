# You can create more variables according to your project. The following are the basic variables that have been provided to you
DB_PATH = '../unit_test/'
DB_FILE_NAME = 'utils_output.db'
UNIT_TEST_DB_FILE_NAME = 'unit_test_cases.db'
DATA_DIRECTORY = '../scripts/data/'
INTERACTION_MAPPING = 'interaction_mapping.csv'
LEAD_SCORING_DATA = "leadscoring.csv"
LEAD_SCORING_TEST_DATA = "leadscoring_test.csv"
INDEX_COLUMNS_TRAINING = ['created_date', 'first_platform_c',
       'first_utm_medium_c', 'first_utm_source_c', 'total_leads_droppped', 'city_tier',
       'referred_lead', 'app_complete_flag']
INDEX_COLUMNS_INFERENCE = ['created_date', 'city_tier', 'first_platform_c',
       'first_utm_medium_c', 'first_utm_source_c', 'total_leads_droppped',
       'referred_lead', 'app_complete_flag']
NOT_FEATURES = ['created_date', 'assistance_interaction', 'career_interaction',
                'payment_interaction', 'social_interaction', 'syllabus_interaction']




