
# from enum import Enum
# from dotenv import load_dotenv, find_dotenv
# import sys
# import os

# def get_env_path():
#     # Determine if the script is running in a bundle (PyInstaller)
#     if getattr(sys, 'frozen', False):
#         # Running as executable, get the directory of the .exe
#         basedir = os.path.dirname(sys.executable)
#     else:
#         # Running as normal Python script
#         basedir = os.path.dirname(os.path.abspath(__file__))
    
#     return os.path.join(basedir, '.env')

# dotenv_path=get_env_path()
# load_dotenv(dotenv_path)

# DEFAULT_JOB_CARD_FOLDER = os.getenv('DEFAULT_JOB_CARD_FOLDER')
# DEFAULT_WITEM_FOLDER = os.getenv('DEFAULT_WITEM_FOLDER')
# DEFAULT_JOB_CARD_FOLDER = "Test"
# DEFAULT_JOB_CARD_FOLDER = "\\\\keibhdfile01\\JOB CARDS BHD PTH CHP\\JOBORDER BHD\\"
# DEFAULT_WITEM_FOLDER = "\\\\keibhdfile01\\commonall\\biplob\Excel\\JOB_CARD_DATA\\db\\"
DEFAULT_JOB_CARD_FOLDER = "C:\\Users\\biplob\\Downloads\\PY_Projects\\JobCardFinder_Prj\\test\\"
DEFAULT_WITEM_FOLDER = "C:\\Users\\biplob\\Downloads\\PY_Projects\\JobCardFinder_Prj\\test\\"

# DEFAULT_JOB_CARD_FOLDER = "C:\\Users\\biplob\\Downloads\\"
# DEFAULT_JOB_CARD_FOLDER = "\\\\keibhdfile01\\JOB CARDS BHD PTH CHP\\JOBORDER BHD\\"

# DEFAULT_WITEM_FOLDER = "\\\\keibhdfile01\\commonall\\biplob\Excel\\JOB_CARD_DATA\\db\\"
# DEFAULT_WITEM_FOLDER = "C:\\Users\\biplob\\Downloads\\Jupyter Notebook Prjs\\"
# DEFAULT_WITEM_FOLDER = "\\\\keibhdfile01\\JOB CARDS BHD PTH CHP\\JOBORDER BHD\\"

# class Sheets(Enum):
#     BOOKS = "Books"
#     TDS = "TDS"
#     ONE_TAN = 'One TAN'
#     TAN_FULL_M_LT_100 = 'Tan Fully Match Diff <=100'
#     OWN_TAN_M = 'Own Sheet TAN Matched'
#     S_TAN_M_LT_1 = 'Single Entry Amount Match Diff <=1'
#     S_TAN_DIFFSEC_M_LT_1 = 'Single Entry Amount (Diff Section) Match Diff <=1'
#     G_TAN_M_LT_1 = 'Group Amount Match Diff <=1'
#     M_TAN_M_LT_1 = 'Multiple Entry Amount Match Diff <=1'
#     G_TAN_M_LT_50 ='Group Amount Match Diff <=50'

# class ColumnsName(Enum):
#     BP_Code = 'B.P CODE'
#     BP_Name = 'BP NAME'
#     Doc_no = 'DOCUMENT NO.'
#     pan = 'PAN'
#     tan = 'TAN'
#     section = 'Section'
#     type = 'Type'
#     tds_amnt_books = 'TDS Amount (Books)'
#     tds_amnt_26as = 'TDS Amount (26AS)'
#     amnt = 'Amount'
#     remark = 'Remark'
#     remark2 = 'Remark2'
#     matched = 'Matched'
#     balance = 'Balance'
#     books = "Books"
#     tds = "26AS"

# class LevelEnum(Enum):
#     SINGLE_LINE_TOTAL = 'SINGLE_LINE_TOTAL'
#     GROUP_TOTAL = 'GROUP_TOTAL'
#     TYPE_WISE_GROUP_TOTAL = 'TYPE_WISE_GROUP_TOTAL'
#     COMBINATION_PERMUTATION = 'COMBINATION_PERMUTATION'


# SAMPLE_FILE = 'sample_file'
# SHEETS = ['Books', 'TDS']
# COMMON_COLUMNS = ['B.P CODE', 'BP NAME', 'DOCUMENT NO.', 'PAN', 'TAN', 'Section', 'Date']
# BOOKS_COLUMN = ['TDS Amount (Books)']
# TDS_COLUMN = ['TDS Amount (26AS)']
# REMARKS_COLUMN = ['Remark','Remark2','Matched','Balance']
# # REMK_COLUMN = ['Remark']
# # REMK2_COLUMN = ['Remark2']
# # MATCHED_COLUMN = ['Matched']
# # BALANCE_COLUMN = ['Balance']

# TAN = ['TAN']
# TAN_SEC_L1_AMNT = ['TAN', "Section", 'Type', 'L1_Rank', "Abs(Amount)"]
# TAN_SEC_L2_AMNT = ['TAN', "Section", 'L2_Rank', "Abs(Amount)"]
# TAN_L2_AMNT = ['TAN', 'L2_Rank', "Abs(Amount)"]
# TAN_SEC = ['TAN','Section']


# ALL_COLUMNS = COMMON_COLUMNS + BOOKS_COLUMN + TDS_COLUMN + ["Type", "Amount"] + REMARKS_COLUMN