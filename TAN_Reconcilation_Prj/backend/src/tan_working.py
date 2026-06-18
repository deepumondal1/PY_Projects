# Import Libraries
import pandas as pd
import numpy as np
from itertools import combinations, permutations
from .default_code import ColumnsName
# from tqdm import tqdm, trange, tqdm_notebook
# from tqdm.notebook import tqdm
# import time
# import math

class TAN_Working:
    tan_df = pd.DataFrame()
   
    def __init__(self, books:pd.DataFrame, tds:pd.DataFrame):
        self.books=books
        self.tds=tds
        self.__create_tan_df__(books, tds)

    def remark_summary(self)->pd.Series:
        # return self.tan_df.groupby(['Remark'])['Amount'].sum()
        return self.tan_df.pivot_table(index=['Remark'], values='Amount', aggfunc=['count','sum'], margins=True, margins_name='Total').round(2)
    
    def tan_summary(self)->pd.Series:
        # return self.tan_df.groupby(['Remark'])['Amount'].sum()
        tan_df = self.tan_df
        tan_df['TOTAL TDS Amount'] = tan_df[ColumnsName.tds_amnt_books.value].fillna(0) + tan_df[ColumnsName.tds_amnt_26as.value].fillna(0)
        tan_df['Matched Amount'] = tan_df[tan_df['Remark']!='']['TOTAL TDS Amount']
        tan_df['UnMatched Amount'] = tan_df[tan_df['Remark']=='']['TOTAL TDS Amount']
        vals = ['TOTAL TDS Amount', 'Matched Amount', 'UnMatched Amount']
        return self.tan_df.pivot_table(index=['TAN'], columns=['Type'], values=vals, aggfunc=['sum'], sort=False).round(2)
    
    def __create_tan_df__(self,books:pd.DataFrame, tds:pd.DataFrame):
        try:
            # Normalize column names
            books.columns = books.columns.str.strip()
            tds.columns = tds.columns.str.strip()

            # Add SheetName
            books["Type"] = ColumnsName.books.value
            tds["Type"] = ColumnsName.tds.value

            # Normalize Amount
            books["Round(Amount)"] = books["TDS Amount (Books)"].astype(int)
            tds["Round(Amount)"] = tds["TDS Amount (26AS)"].astype(int)
            books["Abs(Amount)"] = abs(books["Round(Amount)"])
            tds["Abs(Amount)"] = abs(tds["Round(Amount)"])
            
            # In Amount, Books in +ve and TDS in -ve
            books["Amount"] = books["TDS Amount (Books)"]
            tds["Amount"] = -(tds["TDS Amount (26AS)"])

            books["R(Amount)"] = books["Amount"].astype(int)
            tds["R(Amount)"] = tds["Amount"].astype(int)

            # Adding Remark Columns
            books['Remark'] = ''
            books['Remark2'] = ''
            books['Matched'] = False
            books['Balance'] = np.nan
            tds['Remark'] = ''
            tds['Remark2'] = ''
            tds['Matched'] = False
            tds['Balance'] = np.nan

            # Join Books and TDS
            tan_df = pd.concat([books, tds])
            tan_df.sort_values(by=["TAN","Section",'Amount'], inplace=True)
            tan_df.reset_index(drop=True, inplace=True)

            # L1Rank and L2Rank
            GROUP_1 = ['TAN','Section','Type','R(Amount)']
            GROUP_2 = ['TAN','Section','R(Amount)']
            i_number = tan_df.groupby(by=GROUP_1)['Round(Amount)'].rank(method='first',ascending=True)
            o_number = tan_df.groupby(by=GROUP_2)['Round(Amount)'].rank(method='first',ascending=True)
            tan_df['L1_Rank'] = i_number
            tan_df['L2_Rank'] = o_number

            self.books = books
            self.tds = tds
            self.tan_df = tan_df

        except Exception as e:
            raise e


    # ---------- Matching Entries ----------
    def match_entries_new(self, group_tan:pd.DataFrame, tol, remark, level, allow_section_mismatch=False):
        try:

            group_tan = group_tan[group_tan['Matched'] == False]
            group_books = group_tan[group_tan['Type']==ColumnsName.books.value]
            group_tds = group_tan[group_tan['Type']==ColumnsName.tds.value]

            if ((len(group_books) == 0 or len(group_tds) == 0) and (level != 0 and level != 10)) or (len(group_tan) == 1) :
                return

            match level:
                case 10:
                    if len(group_tan)==1:
                        self.tan_df.loc[list(group_tan.index), 'Remark'] = remark
                        self.tan_df.loc[list(group_tan.index), 'Matched'] = True
                        self.tan_df.loc[list(group_tan.index), 'Remark2'] = str(list(group_tan['Amount']))

                case 0:
                    total = group_tan['Amount'].sum()
                    if abs(total) <= tol:
                        self.tan_df.loc[list(group_tan.index), 'Remark'] = remark
                        self.tan_df.loc[list(group_tan.index), 'Matched'] = True
                        self.tan_df.loc[list(group_tan.index), 'Remark2'] = str(list(group_tan['Amount']))
                        self.tan_df.loc[list(group_tan.index), 'Balance'] = total

                case 2:
                    group_books = group_books.sort_values(by="Amount",ascending=False)
                    group_tds = group_tds.sort_values(by="Amount")
                    while True:
                        b_sum = group_books['Amount'].sum()
                        t_sum = group_tds['Amount'].sum()
                        total = b_sum + t_sum
                        if abs(total) <= tol:
                            tot_list = list(group_books.index) + list(group_tds.index)
                            self.tan_df.loc[tot_list, 'Remark'] = remark
                            self.tan_df.loc[tot_list, 'Matched'] = True
                            self.tan_df.loc[tot_list, 'Remark2'] = str(list(tot_list))
                            self.tan_df.loc[tot_list, 'Balance'] = total
                            break
                              
                        if total > 0:
                            a = group_books.loc[group_books["Amount"]<=total][:1]
                            if a.empty:
                                break
                            group_books.drop(index=a.index , inplace=True)
                        if total < 0:
                            a=group_tds.loc[group_tds["Amount"]>=total][:1]
                            if a.empty:
                                break
                            group_tds.drop(index=a.index, inplace=True)

                case 21:
                    group_tan = group_tan.sort_values(by="Amount")
                    while True:
                        tan_sum = group_tan['Amount'].sum()
                        total = tan_sum
                        if abs(total) <= tol:
                            tot_list = list(group_tan.index)
                            self.tan_df.loc[tot_list, 'Remark'] = remark
                            self.tan_df.loc[tot_list, 'Matched'] = True
                            self.tan_df.loc[tot_list, 'Remark2'] = str(list(tot_list))
                            self.tan_df.loc[tot_list, 'Balance'] = total
                            break
                              
                        if total > 0:
                            a = group_tan.loc[group_tan["Amount"]<=total][:-1]
                            if a.empty:
                                break
                            group_tan.drop(index=a.index , inplace=True)
                        if total < 0:
                            a=group_tan.loc[group_tan["Amount"]>=total][:1]
                            if a.empty:
                                break
                            group_tan.drop(index=a.index, inplace=True)

                case 5:
                    combo_del_list = []
                    for r in range(2, 6):
                        tol_dic = {}
                        tol_dic_no = {}
                        filter_tol = {}
                        filter_tol2 = {}
                        ctr=0
                        while True:
                            group_tan = group_tan[group_tan['Matched'] == False]
                            if ((len(group_tan[group_tan['Type']==ColumnsName.books.value]) == 0 or len(group_tan[group_tan['Type']==ColumnsName.tds.value]) == 0)):
                                break 
                            # Setup limit for 2,3,4,and above combinations [for 3, count gt 200], [for 4, count gt 25], [for 5, count gt 10]
                            if (r>=3 and len(group_tan) > 200) or (r>=4 and len(group_tan) > 25) or (r>=5 and len(group_tan) > 10):
                                break             
            
                            combinas = list(combinations(group_tan.index, r))
                            combinas_len=len(combinas)
                            group_tan_dic={x:[i for i in combinas if x in i] for x in list(group_tan.index)}
                
                            while combinas_len>0:
                                for combo in combinas:
                                    total = group_tan.loc[list(combo), 'Amount'].sum()
                                    # Grouping of 1, 5 & 50
                                    for x in [1,5,50]: 
                                        if len(set(combo).intersection(tol_dic_no.get(x,set())))==0:
                                            tol_dic_no.setdefault(x, set()).update(set(combo)) if abs(total) <= x else None
                                            tol_dic.setdefault(x, []).append(combo) if abs(total) <= x else None
                                    if abs(total) <= tol:
                                        self.tan_df.loc[list(combo), 'Remark'] = remark
                                        self.tan_df.loc[list(combo), 'Matched'] = True
                                        self.tan_df.loc[list(combo), 'Remark2'] = str(list(combo))
                                        self.tan_df.loc[list(combo), 'Balance'] = total
                                        group_tan.loc[list(combo), 'Matched'] = True
                                        for i in combo:
                                            combinas=list(set(combinas)-set(group_tan_dic[i]))
                                        combinas=list(set(combinas)-set(combo_del_list))
                                        combo_del_list.clear()
                                        combinas_len=len(combinas)
                                        break
                                    combo_del_list.append(combo)
                                    combinas_len=combinas_len-1


                            for x in [(1,5),(1,50),(5,50)]:
                                filter_tol[x[1]] = list(set(filter_tol.get(x[1],tol_dic.get(x[1],[])))-set(tol_dic.get(x[0],[])))
                                filter_tol2[x[1]] = list(set(filter_tol2.get(x[1],tol_dic_no.get(x[1],[])))-set(tol_dic_no.get(x[0],[])))
                            # filter_tol = {x[1]:list(set(tol_dic.get(x[1],[]))-set(tol_dic.get(x[0],[]))) for x in [(1,5),(5,50)]}
                            # filter_tol2 = {x[1]:list(set(tol_dic_no.get(x[1],[]))-set(tol_dic_no.get(x[0],[]))) for x in [(1,5),(5,50)]}
                            for k, vals in filter_tol2.items():
                                vals = set(filter_tol[k]).intersection(set(permutations(vals,r)))
                                vals = {x for x in vals if len(self.tan_df.loc[list(x)].groupby('Type')) > 1}
                                if vals:
                                    for v in vals:
                                        self.tan_df.loc[list(v), 'Remark'] = remark + "[<" + str(k) + "]"
                                        self.tan_df.loc[list(v), 'Matched'] = True
                                        self.tan_df.loc[list(v), 'Remark2'] = str(list(v))
                                        self.tan_df.loc[list(v), 'Balance'] = group_tan.loc[list(v), 'Amount'].sum()
                                        group_tan.loc[list(v), 'Matched'] = True
                                        for i in v:
                                            combinas=list(set(combinas)-set(group_tan_dic[i]))
                            break

        except Exception as e:
            raise e




