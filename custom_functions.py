from pandas import DataFrame, Series, DatetimeIndex, concat
from plotly.express import histogram, box, violin, bar, line, scatter, scatter_3d, pie
from plotly.graph_objects import Heatmap, Layout, Figure
from plotly.figure_factory import create_annotated_heatmap
from string import punctuation, ascii_letters
from numpy import nan, array, where, append, around
from dash import html
from collections import Counter
import warnings




# Global settings ======================================================================================================
group_color = ["#3CB371", "#CD6600", "#0000FF", "#CD1076", "#6B4226", "#BA55D3", "#CD3700", "#007FFF", "#CDB38B", "#00C5CD", "#4F2F4F"]

dash_pal = {
    "eerie black":  "#212529",
    "onyx":         "#343A40",
    "davys grey":   "#495057",
    "sonic silver": "#6C757D",
    "cadet crayola": "#ADB5BD",
    "light gray":   "#CED4DA",
    "gainsboro":    "#DEE2E6",
    "cultured":     "#E9ECEF",
    "cultured2":    "#F8F9FA"
}
plt_color = {
    "bg": "#E9ECEF",
    "bar": "#495057",
    "point": "#343A40",
    "grid_line": "#DEE2E6"
}

heatmap_color_scale = [
    'rgb(204, 204, 204)',
    'rgb(184, 184, 184)',
    'rgb(171, 171, 171)',
    'rgb(153, 153, 153)',
    'rgb(136, 136, 136)',
    'rgb(112, 112, 112)',
    'rgb(85, 85, 85)',
    'rgb(66, 66, 66)',
    'rgb(41, 41, 41)',
    'rgb(8, 8, 8)'
]
card_color = "#E9ECEF"

plot_height = 600





# Functions ============================================================================================================
def match_arg(x, valid_arg):
    """
    x         [string] An argument.
    valid_arg [list] A list of valid values to match.
    """
    if not isinstance(valid_arg, list):
        raise TypeError(f"Expected a list from argument `valid_arg` but got {type(valid_arg)}")
        
    if isinstance(x, list):        
        if not all([arg in valid_arg for arg in x]): 
            raise ValueError(f"'{x}' is not a valid value. use any of - {', '.join(valid_arg)} -")
    else:
        if x not in valid_arg:
            raise ValueError(f"'{x}' is not a valid value. use any of - {', '.join(valid_arg)} -")
        
        
        
# Data cleaning --------------------------------------------------------------------------------------------------------
def to_bool(df, variable):
    """
    parameter
    ---------
    df       [pd.DataFrame]
    variable [string] A variable with binary value.
    
    return
    ------
    A variable with boolean data type.
    """
    valid_bool = ["t", "true", "f", "false"]
    replace_bool = {"t": True,  "true": True, "f": False, "false": False}
    
    if df[variable].dtype in ["int64", "float64"] and df[variable].nunique() != 2:
        warnings.warn(f"can not convert {list(sorted(df[variable].unique()))[0:5]} to boolean")
        return df[variable]

    elif df[variable].dtype not in ["int64", "float64"]:
        if all(x not in valid_bool for x in list(df[variable].str.lower().unique())):
            warnings.warn(f"can not convert {list(sorted(df[variable].unique()))[0:5]} to boolean")
            return df[variable]
    
    else:
        if df[variable].dtype in ["int64", "float64"]:
            return df[variable].astype("bool")
        else:
            return df[variable].str.lower().map(replace_bool)


def to_number(df, variable, num_type):
    """
    parameter
    ---------
    df [pd.DataFrame]
    variable [string] A variable which can be converted to a numeric data type.
    num_type [string] The type of numeric data type to convert the variable to.

    return
    ------
    A variable with numeric data type.
    """
    try:
        if num_type == "int64":
            if any(df[variable].apply(lambda x: "." in x)):
                # warnings.warn("can not convert floats data type to Integer")
                return df[variable].astype("float64").astype("int64")

        return df[variable].astype(num_type)

    except:
        pun_chr = list(punctuation)+list(ascii_letters)
        pun_chr.remove(".")

        for pc in pun_chr:
            df[variable] = df[variable].str.replace(pc, "", regex = False)

        return df[variable].astype(num_type) if num_type == "float" else df[variable].astype("float64").astype("int64")


def get_empty_object(df, variables):
    """
    :param df: dataframe
    :param variables: variable from the dataframe
    :return: a dictionary with a boolean type if variable(s) have missing values and the variable(s) name(s)
    """
    if isinstance(variables, list):
        f_df = df[variables]

        mis_list = []
        for var in f_df.columns:
            bool_vals = f_df[var] == ' '
            mis_list.append(bool_vals.sum())

        if any([var > 0 for var in mis_list]):
            mis_vars = [ind for ind, val in enumerate(mis_list) if val]
            mis_vars = f_df.iloc[:, mis_vars].columns.to_list()
            return {"bool": True, "variables": mis_vars}
        else:
            return {"bool": False}
    else:
        bool_vals = df[variables] == ' '
        if bool_vals.sum() > 0:
            return {"bool": True, "variables": variables}
        else:
            return {"bool": False}

def remove_missing_values_gb(df, variables):
    f_tbl = df.copy()

    if isinstance(variables, list):
        # Get columns with missing values less than the number of rows in the data.
        valid_variables = []
        for var in variables:
            if f_tbl[var].isnull().sum() < f_tbl.shape[0]:
                valid_variables.append(var)

        if valid_variables != []:
            if any(f_tbl[valid_variables].isnull().sum().values > 0):
                f_tbl = f_tbl.dropna(axis="index", how="any", subset=valid_variables)

            if f_tbl.shape[0] != 0:
                empty_vals = get_empty_object(f_tbl, valid_variables)

                if empty_vals["bool"]:
                    for var in empty_vals["variables"]:
                        f_tbl = f_tbl[f_tbl[var] != ' ']

            if f_tbl.shape[0] == 0:
                raise IndexError("The output returned an empty table after removing `Nan` values.")
            else:
                return f_tbl
        else:
            return None

    else:
        # Get columns with missing values less than the number of rows in the data.
        if f_tbl[variables].isnull().sum() < f_tbl.shape[0]:
            if f_tbl[variables].isnull().sum() > 0:
                f_tbl = f_tbl.loc[f_tbl[variables].notna()]

            if f_tbl.shape[0] != 0:
                empty_val = get_empty_object(f_tbl, variables)

                if empty_val["bool"]:
                    f_tbl = f_tbl.loc[f_tbl[variables] != ' ']

            if f_tbl.shape[0] == 0:
                raise IndexError("The output returned an empty table after removing `Nan` values.")
            else:
                return f_tbl
        else:
            return None


def change_dtype(df, variables, to_type):
    """
    parameter
    ---------
    df        [pd.DataFrame]
    variables [string] A variable or list of variables to change the data type.
    to_type   [string] The type of data type to change to. can be any of "character", "integer", 
                     "float", "date", "boolean"
    return
    ------
    A pandas dataframe.
    """
    match_arg(to_type, ["character", "integer", "float", "date", "boolean"])

    Dtype = {"character": "object", "integer": "int64", "float": "float64", "boolean": "bool", "date": "datetime64[ns]"}

    f_tbl = df.copy()

    f_tbl = remove_missing_values_gb(df=f_tbl, variables=variables)

    if f_tbl is not None:
        if isinstance(variables, list):
            for var in variables:
                if to_type == "boolean":
                    f_tbl[var] = to_bool(f_tbl, var)

                elif to_type in ["integer", "float"]:
                    f_tbl[var] = to_number(f_tbl, var, Dtype[to_type])

                else:
                    f_tbl[var] = f_tbl[var].astype(Dtype[to_type])
        else:
            if to_type == "boolean":
                f_tbl[variables] = to_bool(f_tbl, variables)

            elif to_type in ["integer", "float"]:
                f_tbl[variables] = to_number(f_tbl, variables, Dtype[to_type])

            else:
                f_tbl[variables] = f_tbl[variables].astype(Dtype[to_type])

        return f_tbl
    else:
        warnings.warn("All variables supplied have only missing values in them.")
        return df


def is_missing_values(df, variables, missing_what):
    """
    :param df: dataframe
    :param variables: variable(s) from the dataframe
    :param missing_what: either 'all' or 'some'
    :return: a dictionary with a boolean type if variable(s) have missing values and the variable(s) name(s).
    """
    n_rows = df.shape[0]

    if missing_what == "all":
        if isinstance(variables, list):
            is_missing_all = []
            for var in variables:
                if df[var].isnull().sum() == n_rows:
                    is_missing_all.append(var)
            if is_missing_all != []:
                return {"bool": True, "variables": is_missing_all}
            else:
                return {"bool": False}
        else:
            bol = df[variables].isnull().sum() == n_rows
            if bol:
                return {"bool": True, "variables": variables}
            else:
                return {"bool": False}
    elif missing_what == "some":
        if isinstance(variables, list):
            is_missing_some = []
            for var in variables:
                n_missing = df[var].isnull().sum()
                if n_missing > 0 and n_missing < n_rows:
                    is_missing_some.append(var)
            if is_missing_some != []:
                return {"bool": True, "variables": is_missing_some}
            else:
                return {"bool": False}
        else:
            n_missing = df[variables].isnull().sum()
            if n_missing > 0 and n_missing < n_rows:
                return {"bool": True, "variables": variables}
            else:
                return {"bool": False}


def check_for(what, df, variables):
    """
    :param what: the condition to check. any of empty_values, missing_all_values, missing_some_values
    :param df: dataframe.
    :param variables: variable(s) from the dataframe.
    :return: a dictionary with a boolean type if variable(s) have missing values and the variable(s) name(s).
    """
    if what == "empty_values":
        return get_empty_object(df, variables)
    elif what == "missing_all_values":
        return is_missing_values(df, variables, "all")
    elif  what == "missing_some_values":
        return is_missing_values(df, variables, "some")


def drop_missing_values(df, how, percentage = None):
    """
    parameter
    ---------
    df  [pd.DataFrame]
    how [string] How to drop missing values. any of "all_cols", "all_rows", "cols_all_na", 
                 "rows_all_na", "percent_missing".
    percentage [integer] drop variables that do not meet the percentage of non missing values. 
    
    return
    ------
    A pandas dataframe.
    """
    match_arg(how, ["all_cols", "all_rows", "cols_all_na", "rows_all_na", "percent_missing"])
    
    if how == "all_cols":                                # Drop all columns with missing values.
        f_tbl = df.dropna(axis = "columns")  
        
    elif how == "all_rows":                              # Drop all rows with missing values. 
        f_tbl = df.dropna(axis = "index")
        
    elif how == "cols_all_na":                           # Drop all columns with only missing values.
        f_tbl = df.dropna(axis = "columns", how = "all")
        
    elif how == "rows_all_na":                           # Drop all rows where all recordes are missing.
        f_tbl = df.dropna(axis = "index", how = "all")
        
    elif how == "percent_missing":
        # drop columns that do not meet a threshold of non missing values.
        if percentage is not None:
            user_percent = percentage/100
            f_tbl = df.dropna(axis = "columns", how = "all", thresh = round(user_percent * df.shape[0]))
        else:
            raise ValueError("argument `percentage` is missing with no default")
        
    return f_tbl



def get_missing_values(df):
    """
    parameter
    ---------
    df [pd.DataFrame]
    
    return
    ------
    if missing values are present, the count and percentage of missing values else 
    a column indicating no missing values
    """
    f_tbl = DataFrame(df.isnull().sum()).reset_index().rename(columns = {"index": "variables", 0: "count"})
    f_tbl["percentage"] = round((f_tbl["count"] / df.shape[0])*100, 2)
    f_tbl = f_tbl.sort_values(by = "count", ascending = False)
    f_tbl = f_tbl.loc[f_tbl["count"] > 0]
    
    if f_tbl.shape[0] > 0:
        return f_tbl
    else:
        return DataFrame({"variable": "No Missing Value"}, index = [0])
    
    
def sort_month_names(to_sort):
    """
    Order month labels from January to December.
    
    return
    ------
    list.
    """
    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                   "October", "November", "December"]
    
    index_list = array(-1)
    
    for month in to_sort:
        get_index = where(array(month) == month_names)
        index_list = append(index_list, get_index)
        
    index_list = list(index_list[1:])
    
    sorted_months = []
    
    for ind in sorted(index_list):
        sorted_months.append(month_names[ind])
        
    return sorted_months    


def change_cat(df, date_type):
    """
    parameter
    ---------
    df   [pd.DataFrame]
    date_type [string] The kind of date to convert to category. any of "second", "minute", "hour", "day",
             "month", "month_name", "quarter", "year", "day_of_year", "week_of_year".
    return
    ------
    A pandas dataframe with selected variables coverted to and ordered category.
    """
    f_tbl = df.copy()

    if isinstance(date_type, list):
        if "month_name" in date_type:
            month_name_cat = sort_month_names(list(f_tbl["month_name"].unique()))
            f_tbl["month_name"] = f_tbl["month_name"].astype("category").cat.reorder_categories(month_name_cat, ordered = True)

            date_type.remove("month_name")
            
        for ddt in date_type:
            f_tbl[ddt] = f_tbl[ddt].astype("category").cat.reorder_categories(sorted(f_tbl[ddt].unique()), ordered = True)
    
    else:
        if date_type != "month_name":
            f_tbl[date_type] = f_tbl[date_type].astype("category").cat.reorder_categories(sorted(f_tbl[date_type].unique()), ordered = True)

        elif date_type == "month_name":
            month_name_cat = sort_month_names(list(f_tbl[date_type].unique()))

            f_tbl[date_type] = f_tbl[date_type].astype("category").cat.reorder_categories(month_name_cat, ordered = True) 
        
    return f_tbl


def extract_datetime(df, date_col, which):
    """
    parameter
    ---------
    df       [DataFrame]
    date_col [string] A variable with datetime64[ns] data type to extract further date values from.
    which    [string] The kind of date to inclued in the table. any of "second", "minute", "hour", "day",
             "month", "month_name", "quarter", "year", "day_of_year", "week_of_year"
    
    return
    ------
    pd.DataFrame containing all included date variables.
    """
    match_arg(which, ["second", "minute", "hour", "day", "month", "month_name", "quarter", "year", "day_of_year", "week_of_year"])
    f_tbl = df.copy()
    
    if f_tbl[date_col].dtypes != "<M8[ns]":
        f_tbl[date_col] = f_tbl[date_col].astype("datetime64[ns]")

    date_dict = {"second"  : "DatetimeIndex(f_tbl[date_col]).second",
                 "minute"  : "DatetimeIndex(f_tbl[date_col]).minute",
                 "hour"    : "DatetimeIndex(f_tbl[date_col]).hour",
                 "day"     : "DatetimeIndex(f_tbl[date_col]).day",
                 "month"   : "DatetimeIndex(f_tbl[date_col]).month",
                 "month_name": "DatetimeIndex(f_tbl[date_col]).month_name()",
                 "quarter" : "DatetimeIndex(f_tbl[date_col]).quarter",
                 "year"    : "DatetimeIndex(f_tbl[date_col]).year",
                 "day_of_year"  : "DatetimeIndex(f_tbl[date_col]).dayofyear",
                 "week_of_year" : "DatetimeIndex(f_tbl[date_col]).isocalendar().week"}
    
    if isinstance(which, list):
        for dates in which:
              f_tbl[dates] = eval(date_dict[dates])
    else:
        f_tbl[which] = eval(date_dict[which])
            
    f_tbl = change_cat(f_tbl, which)
    
    return f_tbl


def clean_data(df, variables = None, to_type = None, how = None, percentage = None, date_var = None, which = None):
    """
    parameter
    ---------
    df [pd.DataFrame]
    variables [string] A variable or list of variables. Passed to `change_dtype()`
    to_type   [string] The type of data type to change to. Passed to `change_dtype()`. it can be any of 
                      "character", "integer", "float", "date", "boolean".
    how       [string] How to drop missing values. passed to `drop_missing_values()`. it can be any of "all_cols", 
                      "all_rows", "cols_all_na",  "rows_all_na", "percent_missing".
    percentage [integer] Drop variables that do not meet the percentage of non missing values. 
                         passed to `drop_missing_values()`.
    date_var [string] A variable with datetime64[ns] data type to extract further date values from.
    which    [string] The kind of date to inclued in the table.
    
    return
    ------
    A pandas Dataframe.
    """
    f_tbl = df.dropna(axis = "columns", how = "all")

    if variables is not None and to_type is not None and how is None and date_var is None:
        f_tbl = f_tbl.dropna(axis = "index")
        f_tbl = change_dtype(df = f_tbl, variables = variables, to_type = to_type)
        
    elif variables is None and to_type is None and how is not None and date_var is None:
        f_tbl = drop_missing_values(df = f_tbl, how = how, percentage = percentage)
        
    elif variables is not None and to_type is not None and how is not None and date_var is not None:
        f_tbl = drop_missing_values(df = f_tbl, how = how, percentage = percentage)
        f_tbl = change_dtype(df = f_tbl, variables = variables, to_type = to_type)
        
        if which is not None:
            f_tbl = extract_datetime(df = f_tbl, date_col = date_var, which = which)
        else:
            f_tbl
            
    elif variables is None and to_type is None and how is None and date_var is not None:
        if which is not None:
            f_tbl = extract_datetime(df = f_tbl, date_col = date_var, which = which)
        else:
            f_tbl
            
    elif variables is not None and to_type is not None and how is None and date_var is not None:
        f_tbl = f_tbl.dropna(axis = "index")
        f_tbl = change_dtype(df = f_tbl, variables = variables, to_type = to_type)
        
        if which is not None:
            f_tbl = extract_datetime(df = f_tbl, date_col = date_var, which = which)
        else:
            f_tbl
            
    elif variables is None and to_type is None and how is not None and date_var is not None:  
        f_tbl = drop_missing_values(df = f_tbl, how = how, percentage = percentage)
        
        if which is not None:
            f_tbl = extract_datetime(df = f_tbl, date_col = date_var, which = which)
        else:
            f_tbl
        
    return f_tbl
        
        


def get_dtype(df, dtype, return_names = False):
    """
    parameter
    ---------
    df    [pd.DataFrame]
    dtype [string] The names of variables with such data type. either 'numeric', 'character' or 'datetime'.
    return_names [bool] Whether to return the column names or not.
    return
    ------
    Either a list of variable names or selected variable data type.
    """
    match_arg(dtype, ["numeric", "character", "datetime"])

    if return_names:
        if dtype == "numeric":
            var_names = df.select_dtypes(include = ["int64", "float64", "number"]).columns.to_list()
        elif dtype == "character":
            var_names = df.select_dtypes(include = ["object", "category"]).columns.to_list()
        elif dtype == "datetime":
            var_names = df.select_dtypes(include = "datetime64[ns]").columns.to_list()
        return var_names

    else:
        if dtype == "numeric":
            f_tbl = df.select_dtypes(include = ["int64", "float64", "number"])
        elif dtype == "character":
            f_tbl = df.select_dtypes(include = ["object", "category"])
        elif dtype == "datetime":
            f_tbl = df.select_dtypes(include = "datetime64[ns]")

        if f_tbl.shape[1] == 0:
            return DataFrame({"Variable": f"No {str.title(dtype)} Variable Detected."}, index=[0])

        return f_tbl


def sort_chr_vars(df, variables):
    """
    parameter
    ---------
    df [pd.DataFrame]
    variables [string] A list of two character variables.
    
    return
    ------
    A sorted list of variables based on the largest number of unique values.
    """
    if isinstance(variables, list):
        var_dict = {}

        for chr_var in variables:
            var_dict[chr_var] = df[chr_var].nunique()
        
        sort_seris = Series(data = var_dict, index = variables)
        sort_seris = sort_seris.sort_values(ascending = False)
        
        return sort_seris.index.to_list()
    else:
        raise TypeError(f"Expected a list of two values from `variables` argument but got a {type(variables)}")


def char_lump(df, variable, keep_n = 10, others = "others"):
    """
    df [pd.DataFrame]
    variable [string] A character variable data type from the data `df`.
    keep_n   [integer] Number of unique values to keep.
    others   [string] The values to assign the remaining less frequent unique values.
    
    return
    ------
    A pandas dataframe with the least frequent values lumped together. 
    """
    
    if df[variable].nunique() > keep_n:
        top_unique_values = df[variable].value_counts().head(keep_n).index.to_list()

        var_name = variable+"_lump"

        f_tbl = df.copy()
        f_tbl[var_name] = nan
        f_tbl.loc[f_tbl[variable].isin(top_unique_values), var_name] = f_tbl.loc[f_tbl[variable].isin(top_unique_values)][variable]
        f_tbl.loc[~f_tbl[variable].isin(top_unique_values), var_name] = others
        
        return f_tbl
    else:
        return df
        

def remove_lump_name(label):
    """
    parameter
    ---------
    label [string] A string to remove `_lump` if present.
    
    return
    ------
    A string with out `_lump` in it.
    """
    if isinstance(label, list):
        labs = []
        for l in label:
            label = str.replace(l, "_lump", "")
            labs.append(label)

        return labs
    else:
        raise TypeError(f"Expected a list but got {type(label)}")
        
        

def numeric_description(df):
    """
    parameter
    ---------
    df [pd.DataFrame]

    return
    ------
    A pandas dataframe with numeric descriptions.
    """

    def get_description(df, variable):
        f_tbl = DataFrame({
            "minimum": df[variable].min(),
            "Q_25": df[variable].quantile(q = 0.25),
            "median": df[variable].median(),
            "mean": df[variable].mean(),
            "std": df[variable].std(),
            "Q_75": df[variable].quantile(q = 0.75),
            "maximum": df[variable].max()
        }, index = [1]).rename(index = {1: variable})

        return f_tbl

    num_variables = get_dtype(df = df, dtype = "numeric", return_names = True)
    if num_variables != []:
        out_tbl = DataFrame()

        for num in num_variables:
            des = get_description(df, num)
            out_tbl = concat([out_tbl, des])

        return out_tbl.reset_index().rename(columns = {"index": "Variable"})
    else:
        return DataFrame({"Variable": "No Numeric Variable Is Avaliable"}, index = [0])


def chr_unique_value(df, max_n = 9):
    """
    parameter
    ---------
    df    [pd.DataFrame]
    max_n [number]  The maximum number of unique values for each character variable to display.

    return
    ------
    A pandas dataframe with Unique Character values.
    """

    def chr_uq(f_df, var):
        unique_values = list(f_df[var].unique())
        unique_values = [chr_var for chr_var in unique_values if chr_var is not None]

        if unique_values != []:
            if len(unique_values) > 10:
                u_v = f"{', '.join(unique_values[0:max_n])}"
            else:
                u_v = ', '.join(unique_values)
        else:
            u_v = "No Value"

        return DataFrame({"Unique Values": u_v, "Number Of Unique Values": f_df[var].nunique()}, index = [var])

    char_variables = get_dtype(df = df, dtype = "character", return_names = True)

    if char_variables != []:
        out_tbl = DataFrame()

        for char in char_variables:
            char_df = chr_uq(df, char)
            out_tbl = concat([out_tbl, char_df])

        return out_tbl.reset_index().rename(columns = {"index": "Variable"})
    else:
        return DataFrame({"Variable": "No Character Variable Is Avaliable"}, index = [0])



# Outliers -------------------------------------------------------------------------------------------------------------
def get_outlier (df, variable, limit, typ = "both"):
    """
    parameter
    ---------
    df    [DataFrame]
    variable   [int, float64] A numerical variable from the data `df`.
    limit [1.5, 3] The type of limit to use when calculating the outlier. (3) to get extreme outliers.
    typ   [string] The type of output to return. any of 'lower', 'upper' or 'both'
    
    return
    ------
    a List of outlier in the data or a number.
    """
    if limit not in [1.5, 3]:
        raise ValueError(f"argument `limit` must be 1.5 or 3 and not {limit}")
    Q1 = df[variable].quantile(0.25)
    Q3 = df[variable].quantile(0.75)
    
    IQR = Q3 - Q1
    
    lower_outlier = Q1 - limit * IQR
    upper_outlier = Q3 + limit * IQR
    
    if typ == "lower":
        return lower_outlier
    elif typ == "upper":
        return upper_outlier
    elif typ == "both":
        return [lower_outlier , upper_outlier]
    else:
        raise ValueError(f"argument `typ` must be any of 'lower', 'upper' or 'both' and not {typ}")

            
def filterNoneOutlier(df, variable, outlier_type, which = "both"):
    """
    parameter
    ---------
    df       [pd.DataFrame]
    variable [string] A numeric variable from the data `df`.
    outlier_type [string] ...... either "weak" or "strong".
    which    [string] ........ any of "both", "lower" or "upper".
    
    return
    ------
    A pandas dataframe with the selected kind of outlier dropped.
    """
    
    match_arg(outlier_type, ["weak", "strong"])
    match_arg(which, ["both", "lower", "upper"])
    
    ol_type = {"weak": 1.5, "strong": 3}
    var_outlier = get_outlier(df = df, variable = variable, limit = ol_type[outlier_type], typ = "both")
    
    if which == "both":
        f_tbl = df.loc[(df[variable] > var_outlier[0]) & (df[variable] < var_outlier[1])]
        
    elif which == "lower":
        f_tbl = df.loc[df[variable] > var_outlier[0]]
    
    elif which == "upper":
        f_tbl = df.loc[df[variable] < var_outlier[1]]
        
    return f_tbl


def filter_none_outlier(df, variable, filter_type):
    """
    parameter
    ---------
    df       [pd.DataFrame]
    variable [string] A numeric variable from the data `df`.
    filter_type [string] The kind of filter to apply when dropping outlier. it can be any of 
                "strong_both", "strong_lower", "strong_upper", "weak_both", "weak_lower", "weak_upper".
     
    return
    ------
     A pandas dataframe with outlier filtered out.
    """
    
    match_arg(filter_type, ["strong_both", "strong_lower", "strong_upper", "weak_both", "weak_lower", "weak_upper"])

    filter_type = str.replace(filter_type, "_", " ").split()

    return filterNoneOutlier(df = df, variable = variable, outlier_type = filter_type[0], which = filter_type[1])
        
    

def clean_plot_label(label):
    """
    parameter
    ---------
    label [string] A string to clean.
    
    return
    ------
    A string.
    """
    
    for lab in list(punctuation):
        label = str.replace(label, lab, " ")
        
    return str.title(label)



def num_stat_summary(df, variable):
    """
    parameter
    ---------
    df       [pd.DataFrame]
    variable [string] A list or single variable to summarise
    
    return
    ------
    A pandas dataframe with descriptive summary.
    """
    
    def get_stat_summary(x, var):
        f_tbl = x[[var]].describe().T
        f_tbl = f_tbl.iloc[:, 1:]
        f_tbl.columns = ["Mean", "Std", "Minimum", "Quantile 25", "Median", "Quantile 75", "maximum"]
        f_tbl = f_tbl[["Minimum",  "Quantile 25", "Mean", "Std", "Median", "Quantile 75", "maximum"]]
        f_tbl = round(f_tbl, 3)
        return f_tbl
    
    if isinstance(variable, list):
        variable = list(set(variable))
        
        m_tbl = DataFrame()
        
        for num_vars in variable:
            desc = get_stat_summary(x = df, var = num_vars)
            m_tbl = m_tbl.append(desc)
        return m_tbl
    else:
        return get_stat_summary(x = df, var = variable)

             
# plot [issue: weak upper does not seem to be filtered]
def single_num_distribution_out(df, variable, dis_type = "hist", drop_outlier = None, p_color = None, n_bin = None, output_type = "plot"):
    """
    parameter
    ---------
    df       [pd.DataFrame]
    variable [string] A numerical variable from the data `df`.
    dis_type [string] The type of distribution plot to create. either "'hist'OGRAM", "'box'PLOT", "'vio'LIN".
    drop_outlier [string] Remove outliers for the data, can be any of: "strong_both", "strong_lower", "strong_upper",
                          "weak_both", "weak_lower", "weak_upper"
    p_color  [string] Plot Color.
    n_bin    [number] Only useful when dis_type = 'hist', The number of bins to use.

    return
    -------
    A plotly.graph_objects.Figure.
    """

    if drop_outlier is not None:
        f_tbl = filter_none_outlier(df = df, variable = variable, filter_type = drop_outlier)
    else:
        f_tbl = df

    if output_type == "plot":
        match_arg(dis_type, ["hist", "box", "vio"])

        var_name = str.replace(variable, "_", " ").title()
        p_template = "plotly_white"
        fp_color = [plt_color["bar"]] if p_color is None else p_color
        p_title = f"Distribution Of {var_name}"
        p_labels = {variable: var_name}

        if dis_type == "hist":
            f_fig = histogram(
                data_frame = f_tbl,
                x = variable,
                marginal = "box",
                nbins = n_bin,
                color_discrete_sequence = fp_color,
                labels = p_labels,
                title = p_title,
                template = p_template,
                height = plot_height
            )
        elif dis_type == "box":
            f_fig = box(
                data_frame = f_tbl,
                x = variable,
                color_discrete_sequence = fp_color,
                labels = p_labels,
                title = p_title,
                notched = True,
                template = p_template,
                height = plot_height
            )
        elif dis_type == "vio":
            f_fig = violin(
                data_frame = f_tbl,
                x = variable,
                color_discrete_sequence = fp_color,
                box = True,
                labels = p_labels,
                title = p_title,
                template = p_template,
                height = plot_height
            )
        f_fig = f_fig.update_xaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_layout(paper_bgcolor = plt_color["bg"], plot_bgcolor = plt_color["bg"])
        return f_fig.update_traces(hoverlabel = {"font_color": "white"})

    elif output_type == "table":
        return num_stat_summary(f_tbl, variable).T.reset_index().rename(columns={"index": "Stat Discription", variable: "Values"})
    


def num_relationship_out(df, variables, drop_outlier = None, p_color = None, plot_type = "2d", output_type = "plot"):
    """
    parameter
    ---------
    df           [pd.DataFrame]
    variables    [string] 2 or 3 numeric variables from the data 'df'.
    drop_outlier [string] Remove outliers for the data, can be any of: "strong_both", "strong_lower", "strong_upper",
                          "weak_both", "weak_lower", "weak_upper".
    p_color      [string] Plot colors.
    output_type  [string] The type of output either a 'table' or a 'plot'.

    return
    ------
    A plotly.graph_objects.Figure if output_type is plot else a table.
    """

    if drop_outlier is not None:
        for num_var in variables:
            f_tbl = filter_none_outlier(df = df, variable = num_var, filter_type = drop_outlier)
    else:
        f_tbl = df

    if output_type == "plot":
        p_color = [plt_color["point"]] if p_color is None else p_color
        p_template = "plotly_white"
        clean_lab = [clean_plot_label(var) for var in variables]

        if len(variables) == 2:
            x_lab = clean_lab[0]
            y_lab = clean_lab[1]

            f_fig = scatter(
                data_frame= f_tbl,
                x = variables[0],
                y = variables[1],
                color_discrete_sequence = p_color,
                labels ={variables[0]: x_lab, variables[1]: y_lab},
                title = f"Relationship Between {x_lab} & {y_lab}",
                template = p_template,
                height = plot_height
            )

        elif len(variables) == 3:
            x_lab = clean_lab[0]
            y_lab = clean_lab[1]
            z_lab = clean_lab[2]

            if plot_type == "3d":
                f_fig = scatter_3d(
                    data_frame = f_tbl,
                    x = variables[0],
                    y = variables[1],
                    z = variables[2],
                    color_discrete_sequence = p_color,
                    labels = {variables[0]: x_lab, variables[1]: y_lab, variables[2]: z_lab},
                    title = f"Relationship Between {x_lab}, {y_lab} & {z_lab}",
                    template = p_template,
                    height = plot_height
                )

            elif plot_type == "2d":
                f_fig = scatter(
                    data_frame = f_tbl,
                    x = variables[0],
                    y = variables[1],
                    color = variables[2],
                    labels = {variables[0]: x_lab, variables[1]: y_lab, variables[2]: z_lab},
                    title = f"Relationship Between {x_lab}, {y_lab} & {z_lab}",
                    template = p_template,
                    height = plot_height
                )
        f_fig = f_fig.update_xaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_layout(paper_bgcolor = plt_color["bg"], plot_bgcolor = plt_color["bg"])

        return f_fig.update_traces(hoverlabel = {"font_color": "white"})

    elif output_type == "table":
        tbl = num_stat_summary(df = f_tbl, variable=variables)
        return tbl.reset_index().rename(columns = {"index": "Variable"})



def char_count(df, variables, sort = None):  
    """
    parameter
    ---------
    df        [pd.DataFrame]
    variables [string] A character or list of character variables from the data `df`.
    sort      [string] one of the values in the argument `variables`.
    
    return
    ------
    A pandas dataframe with the number of each unique values of the variable(s).
    """
    
    if isinstance(variables, list) and len(variables) > 1:
        s_variables = sort_chr_vars(df = df, variables = variables)
        f_tbl = DataFrame(df[s_variables].value_counts()).reset_index().rename(columns = {0: "count"})
        f_tbl["proportion"] = round((f_tbl["count"] / f_tbl["count"].sum())*100, 2)
        
        if sort is not None:
            f_tbl =  f_tbl.sort_values(by = sort, ascending = False, ignore_index = True)
            
    else:
        f_tbl = DataFrame(df[[variables]].value_counts()).reset_index().rename(columns = {0: "count"})
        f_tbl["proportion"] = round((f_tbl["count"] / f_tbl["count"].sum())*100, 2)
    
    return f_tbl


def one_char_out(df, variable, p_type = "bar", p_color = None, num_unique_obs = 15, output_type = "plot"):
    """
    parameter
    ---------
    df [pd.DataFrame]
    variable [string] A character variable from the data `df`.
    p_type [str] The type of Plot geom.
    p_color [string] Plot colors.
    output_type [string] The type of output either a 'plot' or a 'table'.

    return
    ------
    A plotly.graph_objects.Figure if output type is plot else pandas dataframe.
    """

    f_tbl = char_count(df = df, variables = variable)

    if output_type == "plot":
        match_arg(p_type, ["bar", "pie"])

        var_lab = clean_plot_label(label = variable)

        if p_type == "bar":
            if f_tbl[variable].nunique() <= 6:
                f_fig = bar(data_frame = f_tbl,
                            x = variable,
                            y = "count",
                            hover_name = variable,
                            hover_data = {variable: False, "proportion": True},
                            color_discrete_sequence = [plt_color["bar"]] if p_color is None else p_color,
                            labels = {variable: var_lab, "count": "Count"},
                            title = f"Number Of Unique {var_lab} Values.",
                            template = "plotly_white",
                            height = plot_height
                            )
            else:
                f_tbl = f_tbl.head(num_unique_obs)
                f_tbl = f_tbl.sort_values(by="count")

                f_fig = bar(data_frame = f_tbl,
                            y = variable,
                            x = "count",
                            hover_name = variable,
                            hover_data = {variable: False, "proportion": True},
                            color_discrete_sequence = [plt_color["bar"]] if p_color is None else p_color,
                            labels = {"count": "Count", variable: var_lab},
                            title = f"Top {num_unique_obs} Unique {var_lab} Values.",
                            template = "plotly_white",
                            height = plot_height
                            )
        elif p_type == "pie":
            if f_tbl[variable].nunique() <= 5:
                f_fig = pie(data_frame = f_tbl,
                            names = variable,
                            values = "count",
                            hover_data = {variable: False},
                            color_discrete_sequence = group_color if p_color is None else p_color,
                            hole = 0.35,
                            title = f"Percentage Of Unique {var_lab} Values.",
                            height = plot_height
                            )
                f_fig.update_layout(legend = dict(xanchor="center", yanchor = "top", y = 1.1, x = 0.50, orientation = "h"))
            else:
                raise Exception("pie chart will only work for variables with less than 6 unique values")

        f_fig = f_fig.update_xaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_layout(paper_bgcolor=plt_color["bg"], plot_bgcolor=plt_color["bg"])

        return f_fig.update_traces(hoverlabel = {"font_color": "white"})

    elif output_type == "table":
        return f_tbl


def multi_char_out(df, variables, p_color = None, num_unique_obs = 15, output_type = "plot"):
    """
    parameters
    ----------
    df [pd.DataFrame]
    variables [string] A list of character variables from the data `df`.
    p_color   [string] plot color.
    output_type [string] The type of output either a 'plot' or a 'table'.

    return
    ------
    A plotly.graph_objects.Figure if output type is plot else pandas dataframe.
    """

    f_tbl = char_count(df, variables)

    if output_type == "plot":
        s_variables = sort_chr_vars(df = f_tbl, variables = variables)

        plot_label = [clean_plot_label(char_var) for char_var in s_variables]
        add_to_title = plot_label[1] if len(plot_label) == 2 else " & ".join(plot_label[1:])

        p_title = f"Number Of Unique {plot_label[0]} Values By {add_to_title}"

        if df[s_variables[0]].nunique() > 8:
            f_tbl = f_tbl.head(num_unique_obs)
            p_title = f"Top {num_unique_obs} Unique {plot_label[0]} Values By {add_to_title}"

        def plotly_bar(p_x, p_y, p_facet_col, p_facet_col_spacing = None, pf_color = None):
            f_plt = bar(
                data_frame = f_tbl,
                x = p_x,
                y = p_y,
                facet_col = p_facet_col,
                facet_col_spacing = p_facet_col_spacing,
                color_discrete_sequence = p_color,
                color = pf_color,
                title = p_title,
                labels= {s_variables[2]: plot_label[2]} if pf_color is not None else None,
                template = "plotly_white",
                height = plot_height
            )
            return f_plt

        if df[s_variables[0]].nunique() <= 5:
            if len(variables) == 2:
                f_fig = plotly_bar(p_x = s_variables[0],
                                   p_y = "count",
                                   p_facet_col = s_variables[1],
                                   p_facet_col_spacing = 0.07)
            elif len(variables) == 3:
                f_fig = plotly_bar(p_x = s_variables[0],
                                   p_y = "count",
                                   p_facet_col = s_variables[1],
                                   pf_color = s_variables[2])
            f_fig.update_yaxes(matches = None, showticklabels = True)
        else:
            if len(variables) == 2:
                f_fig = plotly_bar(p_x = "count",
                                   p_y = s_variables[0],
                                   p_facet_col = s_variables[1],
                                   p_facet_col_spacing = 0.07)
            elif len(variables) == 3:
                f_fig = plotly_bar(p_x = "count",
                                   p_y = s_variables[0],
                                   p_facet_col = s_variables[2],
                                   pf_color = s_variables[1])
            f_fig.update_xaxes(matches = None, showticklabels = True)

        f_fig = f_fig.update_xaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_layout(paper_bgcolor=plt_color["bg"], plot_bgcolor=plt_color["bg"])

        return f_fig.update_traces(hoverlabel = {"font_color": "white"})

    elif output_type == "table":
        return f_tbl



def char_num_summary(df, chr_var1, num_var1, chr_var2 = None, num_var2 = None):
    """
    parameter
    ---------
    df [pd.DataFrame]
    chr_var1 [string] A character variable from the data `df`.
    chr_var2 [string (optional)] A character variable from the data `df`.
    num_var1 [string] A numeric variable from the data `df`.
    num_var2 [string (optional)] A numeric variable from the data `df`.
    
    return
    ------
    A pandas dataframe of numeric summary grouped by character variable.
    """
    aggregate_summary = ["min", "mean", "median", "max", "sum"]
    
    if chr_var2 is None and num_var2 is None:
        f_tbl = df.groupby(chr_var1)[num_var1].agg(aggregate_summary).reset_index()
        
    elif chr_var2 is None and num_var2 is not None:
        f_tbl = df.groupby(chr_var1)[[num_var1, num_var2]].agg(aggregate_summary).reset_index()
        f_tbl.columns = f_tbl.columns.map("_".join).str.strip("_") 
        
    elif chr_var2 is not None and num_var2 is None:
        f_tbl = df.groupby([chr_var1, chr_var2])[num_var1].agg(aggregate_summary).reset_index()
        
    return f_tbl


def single_char_num_out(df, chr_var, num_var, agg_fun = "mean", drop_outlier = None, p_color=None, keep_num_unique_chr = 10,
                        output_type="plot"):
    """
    parameter
    ---------
    df      [pd.DataFrame]
    chr_var [string] A character variable data type from the data `df`.
    num_var [string] A numeric variable data type from the data `df`.
    agg_fun [string] The aggregate summary to display.
    p_color [string] plot color.
    output_type [string] The type of output either a 'plot' or a 'table'.

    return
    ------
    A plotly.graph_objects.Figure if output type is plot else pandas dataframe.
    """

    if drop_outlier is not None:
        f_tbl = filter_none_outlier(df = df, variable = num_var, filter_type = drop_outlier)
    else:
        f_tbl = df

    f_tbl = char_num_summary(df = f_tbl, chr_var1 = chr_var, num_var1 = num_var)

    if output_type == "plot":
        match_arg(agg_fun, ["min", "mean", "median", "max", "sum"])

        plot_labels = [clean_plot_label(var) for var in [chr_var, num_var]]
        agg_labels = {"min": "Minimum", "mean": "Average", "median": "Median", "max": "Maximum", "sum": "Total"}

        p_title = f"{agg_labels[agg_fun]} {plot_labels[1]} By {plot_labels[0]}"

        # f_tbl = char_lump(df = f_tbl, variable = chr_var, keep_n = keep_num_unique_chr, others = "Others")
        f_tbl = f_tbl.sort_values(by = agg_fun, ascending = False)

        if f_tbl[chr_var].nunique() > 8:
            f_tbl = f_tbl.head(keep_num_unique_chr)
            f_tbl = f_tbl.sort_values(by=agg_fun, ascending=True)

            p_title = f"Top {keep_num_unique_chr} {agg_labels[agg_fun]} {plot_labels[1]} By {plot_labels[0]}"

        p_color = ["#9400D3"] if p_color is None else p_color

        def plotly_bar(p_x, p_y):
            f_plt = bar(
                data_frame = f_tbl,
                x = p_x,
                y = p_y,
                color_discrete_sequence = p_color,
                labels = {chr_var: plot_labels[0], agg_fun: agg_labels[agg_fun]},
                title = p_title,
                template = "plotly_white",
                height = plot_height
            )
            return f_plt

        if f_tbl[chr_var].nunique() <= 5:
            f_fig = plotly_bar(p_x = chr_var,
                               p_y = agg_fun)
        else:
            f_fig = plotly_bar(p_x = agg_fun,
                               p_y = chr_var)

        f_fig = f_fig.update_xaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_layout(paper_bgcolor=plt_color["bg"], plot_bgcolor=plt_color["bg"])

        return f_fig.update_traces(hoverlabel = {"font_color": "white"})

    elif output_type == "table":
        return f_tbl



def one_chr_two_num_out(df, chr_var, num_var1, num_var2, p_color = group_color, drop_outlier = None, output_type = "plot"):
    """
    parameter
    ---------
    df [pd.DataFrame]
    chr_var  [string] A character variable data type from the data `df`.
    num_var1 [string] A numeric variable data type from the data `df`.
    num_var2 [string] A numeric variable data type from the data `df`.
    drop_outlier [string] Remove outlier from the numeric variable.
    output_type [string] The type of output either a 'plot' or a 'table'.

    return
    ------
    A plotly.graph_objects.Figure if output type is plot else pandas dataframe.
    """

    if drop_outlier is not None:
        for num_var in [num_var1, num_var2]:
            f_tbl = filter_none_outlier(df, num_var, drop_outlier)
    else:
        f_tbl = df


    if output_type == "plot":
        f_tbl = char_lump(df = f_tbl, variable = chr_var, keep_n = 10, others = "Others")
        p_chr_var = chr_var + "_lump" if chr_var + "_lump" in f_tbl.columns else chr_var

        plot_label = [clean_plot_label(var) for var in [chr_var, num_var1, num_var2]]

        f_fig = scatter(
            data_frame = f_tbl,
            x = num_var1,
            y = num_var2,
            color_discrete_sequence = p_color,
            color = p_chr_var,
            labels = {p_chr_var: plot_label[0], num_var1: plot_label[1], num_var2: plot_label[2]},
            title = f"Relationship Between {plot_label[1]} & {plot_label[2]} By {plot_label[0]}",
            template = "plotly_white",
            height = plot_height
        )

        f_fig = f_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=plt_color["grid_line"])

        return f_fig.update_layout(paper_bgcolor=plt_color["bg"], plot_bgcolor=plt_color["bg"])

    elif output_type == "table":
        return char_num_summary(df = f_tbl, chr_var1 = chr_var, num_var1 = num_var1, num_var2 = num_var2)



def one_num_two_chr_out(df, num_var, chr_var1, chr_var2, agg_fun = "mean", drop_outlier = None, p_color = None, output_type = "plot"):
    """
    parameter
    ---------
    df       [pd.DataFrame]
    num_var  [string] A numeric variable data type from the data `df`.
    chr_var1 [string] A character variable data type from the data `df`.
    chr_var2 [string] A character variable data type from the data `df`.
    agg_fun  [string] The aggregate summary to display.
    drop_outlier [string] Remove outlier from the numeric variable.
    p_color  [string] plot color.
    output_type [string] The type of output either a 'plot' or a 'table'.

    return
    ------
    A plotly.graph_objects.Figure if output type is plot else pandas dataframe.
    """
    if drop_outlier is not None:
        f_tbl = filter_none_outlier(df = df, variable = num_var, filter_type = drop_outlier)
    else:
        f_tbl = df

    if output_type == "plot":
        match_arg(agg_fun, ["min", "mean", "median", "max", "sum"])
        for chr_var in [chr_var1, chr_var2]:
            f_tbl = char_lump(df=f_tbl, variable=chr_var, keep_n=10, others="Others")

        p_chr_var1 = chr_var1 + "_lump" if chr_var1 + "_lump" in f_tbl.columns else chr_var1
        p_chr_var2 = chr_var2 + "_lump" if chr_var2 + "_lump" in f_tbl.columns else chr_var2

        f_tbl = char_num_summary(df = f_tbl,
                                 chr_var1 = p_chr_var1,
                                 num_var1 = num_var,
                                 chr_var2 = p_chr_var2)

        s_chars = sort_chr_vars(df = f_tbl, variables = [p_chr_var1, p_chr_var2])
        sc_chars = remove_lump_name(s_chars)

        p_color = ["#9400D3"] if p_color is None else p_color
        plot_label = [clean_plot_label(var) for var in [num_var] + sc_chars]
        agg_labels = {"min": "Minimum", "mean": "Average", "median": "Median", "max": "Maximum", "sum": "Total"}

        def plotly_bar(p_x, p_y, p_facet_col_spacing = None):
            f_plt = bar(
                data_frame = f_tbl,
                x = p_x,
                y = p_y,
                facet_col = s_chars[1],
                facet_col_spacing = p_facet_col_spacing,
                color_discrete_sequence = p_color,
                labels = {agg_fun: "", s_chars[0]: plot_label[1]},
                title = f"{agg_labels[agg_fun]} {plot_label[0]} By {plot_label[1]} & {plot_label[2]}",
                template = "plotly_white",
                height = plot_height
            )

            return f_plt

        if f_tbl[s_chars[0]].nunique() <= 6:
            f_fig = plotly_bar(p_x = s_chars[0],
                               p_y = agg_fun,
                               p_facet_col_spacing = 0.07)
            f_fig.update_yaxes(matches = None, showticklabels = True)

        else:
            f_fig = plotly_bar(p_x = agg_fun,
                               p_y = s_chars[0])
            f_fig.update_xaxes(matches = None, showticklabels = True)

        f_fig = f_fig.update_xaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_layout(paper_bgcolor=plt_color["bg"], plot_bgcolor=plt_color["bg"])

        return f_fig.update_traces(hoverlabel = {"font_color": "white"})

    elif output_type == "table":
        return char_num_summary(df = f_tbl, chr_var1 = chr_var1, num_var1 = num_var, chr_var2 = chr_var2)



def one_date_summary_out(df, date_var, n_bin = None, p_color = None, output_type = "plot"):
    """
    parameters
    ----------
    df       [pd.DataFrame]
    date_var [string] A variables with a datetime data type from the data `df`.
    output_type [string] The type of output either a 'plot' or a 'table'.

    return
    ------
    A plotly.graph_objects.Figure if output type is plot else pandas dataframe.
    """

    if output_type == "plot":
        p_tl = clean_plot_label(date_var)
        f_fig = histogram(data_frame = df,
                          x = date_var,
                          labels = {date_var: p_tl},
                          nbins = n_bin,
                          color_discrete_sequence = p_color,
                          title = f"Number Of Recordes In Each {p_tl}",
                          template = "plotly_white",
                          height = plot_height
                          )

        f_fig = f_fig.update_xaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_layout(paper_bgcolor=plt_color["bg"], plot_bgcolor=plt_color["bg"])

        return f_fig.update_traces(hoverlabel = {"font_color": "white"})

    elif output_type == "table":
        return df[date_var].value_counts().reset_index().rename(columns = {"index": date_var, date_var: "count"})


def date_summary(df, date_var, num_var, chr_var = None):
    """
    parameter
    ---------
    df [pd.DataFrame]
    date_var [string] A variables with a datetime data type from the data `df`.
    num_var [string] A numeric variable data type frome tha data `df`.
    chr_var [string (Optional)] A character variable data type frome tha data `df`.
    
    return
    ------
    A pandas dataframe with a date summary.
    """
    if df[date_var].nunique() < df.shape[0]:
        aggregate_fun = ["min", "mean", "median", "max", "sum"]
        if chr_var is None:
            f_tbl = df.groupby(date_var)[num_var].agg(aggregate_fun).reset_index()
        else:
            f_tbl = df.groupby([date_var, chr_var])[num_var].agg(aggregate_fun).reset_index()
        
        return f_tbl
    else:
        return df


def date_summary_out(df, date_var, num_var, chr_var = None, agg_fun = "mean", drop_outlier = None, p_color = None,
                     output_type = "plot"):
    """
    parameter
    ---------
    df [pd.DataFrame]
    date_var [string] A variables with a datetime data type from the data `df`.
    num_var [string] A numeric variable data type frome tha data `df`.
    chr_var [string (Optional)] A character variable data type frome tha data `df`.
    agg_fun [string] The aggregate summary to display.
    p_color [string] Plot colors.
    output_type [string] The type of output either a 'plot' or a 'table'.

    return
    ------
    A plotly.graph_objects.Figure if output type is plot else pandas dataframe.
    """

    if drop_outlier is not None:
        f_tbl = filter_none_outlier(df, num_var, drop_outlier)
    else:
        f_tbl = df

    f_tbl = date_summary(df = f_tbl, date_var = date_var, num_var = num_var, chr_var = chr_var)

    if output_type == "plot":
        clean_names = [date_var, num_var] if chr_var is None else [date_var, num_var, chr_var]
        plot_label = [clean_plot_label(var) for var in clean_names]
        agg_labels = {"min": "Minimum", "mean": "Average", "median": "Median", "max": "Maximum", "sum": "Total"}

        if chr_var is None:
            f_fig = line(
                data_frame = f_tbl,
                x = date_var,
                y = agg_fun,
                color_discrete_sequence = p_color,
                labels = {date_var: plot_label[0], agg_fun: agg_labels[agg_fun]},
                title = f"{agg_labels[agg_fun]} {plot_label[1]} By {plot_label[0]}",
                template = "plotly_white",
                height = plot_height
            )
        #         f_fig.update_xaxes(type = "category")
        else:
            f_fig = line(
                data_frame = f_tbl,
                x = date_var,
                y = agg_fun,
                color = chr_var,
                color_discrete_sequence = p_color,
                labels = {date_var: plot_label[0], agg_fun: agg_labels[agg_fun], chr_var: plot_label[2]},
                title = f"{agg_labels[agg_fun]} {plot_label[1]} By {plot_label[0]} For Each {plot_label[2]}",
                template = "plotly_white",
                height = plot_height
            )
        #         f_fig.update_xaxes(type = "category")
        f_fig = f_fig.update_xaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_yaxes(showgrid = True, gridwidth = 1, gridcolor = plt_color["grid_line"])
        f_fig = f_fig.update_layout(paper_bgcolor=plt_color["bg"], plot_bgcolor=plt_color["bg"])

        return f_fig.update_traces(hoverlabel = {"font_color": "white"})

    elif output_type == "table":
        return f_tbl



def empty_out(output_type):
    if output_type == "plot":
        f_plt = bar(template = "plotly_white")
        return f_plt
    elif output_type == "table":
        return DataFrame()


def is_all_dtype(dtype, dt_dict):
    var_dtypes = [vals for vals in dt_dict.values()]

    if not isinstance(dtype, list):
        return all([dt == dtype for dt in var_dtypes])

    else:
        return not (Counter(dtype) - Counter(var_dtypes))


def dtype_variable(dt_dict, data_type):
    dv_out = []

    for dt in dt_dict.keys():
        if dt_dict[dt] == data_type:
            dv_out.append(dt)

    if len(dv_out) == 1:
        dv_out = " ".join(dv_out)

    return dv_out


def get_vars_dtypes(df, variables):
    """
    parameters
    -----------
    df [pd.DataFrame]
    variables [string] A variable or variables from the data.

    return
    ------
    A dictionary with the variable name and the data type.
    """

    def is_dtype(f_df, f_variable):
        useable_dtypes = {"object": "character", "category": "character", "bool": "character", "int64": "numeric",
                          "float64": "numeric", "datetime64[ns]": "datetime", "datetime64[ns, UTC]": "datetime"}

        for dt in useable_dtypes.keys():
            if f_df[f_variable].dtype.name == dt:
                out_dtype = useable_dtypes[dt]
        return out_dtype

    var_dict = {}

    if isinstance(variables, list):
        for var in variables:
            var_dict[var] = is_dtype(df, var)
    else:
        var_dict[variables] = is_dtype(df, variables)

    return var_dict


def wrapper_summary(w_df,
                    first_variable = None, second_variable = None, third_variable = None,
                    plt_type = None, num_agg_type = "mean", outlier_type = None, n_char_unique_value = 10, output_type = None):
    """
    parameters
    ----------
    df [pd.DataFrame]
    first_variable, second_variable(Optional), third_variable(optional), list[string] Variables from the data.
    plt_type [string] The type of Plot geom.
    num_agg_type [string] The aggregate summary to display.
    outlier_type [string] Remove outlier from the numeric variable.
    output_type [string] The type of output to return either a 'plot' or a 'table'.

    return
    ------
    A plotly.graph_objects.Figure if output type is plot else pandas dataframe.
    """

    supplied_var = [first_variable, second_variable, third_variable]
    avaliable_var = [var for var in supplied_var if var is not None]

    if avaliable_var == []:
        return empty_out(output_type = output_type)

    if len(avaliable_var) != len(set(avaliable_var)):
        return empty_out(output_type = output_type)

    if len(avaliable_var) == 1:
        avaliable_var = " ".join(avaliable_var)

    vars_dt = get_vars_dtypes(df = w_df, variables = avaliable_var)

    single_bar_color = [plt_color["bar"]]
    group_color = ["#3CB371", "#CD6600", "#0000FF", "#CD1076", "#6B4226", "#BA55D3", "#CD3700", "#007FFF", "#CDB38B", "#00C5CD", "#4F2F4F"]

    if not isinstance(avaliable_var, list):
        if vars_dt[avaliable_var] == "numeric":
            plt_type = "hist" if plt_type is None else plt_type
            output = single_num_distribution_out(df = w_df, variable = avaliable_var, dis_type = plt_type, drop_outlier = outlier_type,
                                                 p_color = single_bar_color, n_bin = None, output_type = output_type)

        elif vars_dt[avaliable_var] == "character":
            plt_type = "bar" if plt_type is None else plt_type
            char_pie_colors = single_bar_color if plt_type == "bar" else group_color
            output = one_char_out(df = w_df, variable = avaliable_var, p_type = plt_type, p_color = char_pie_colors,
                                  num_unique_obs = n_char_unique_value, output_type = output_type)

        elif vars_dt[avaliable_var] == "datetime":
            output = one_date_summary_out(df = w_df, date_var = avaliable_var, n_bin = None, p_color = single_bar_color,
                                          output_type = output_type)

        else:
            output = empty_out(output_type = output_type)

    else:
        if len(avaliable_var) == 2:
            if is_all_dtype(dtype = "numeric", dt_dict = vars_dt):  # -----------| All Numeric variables
                output = num_relationship_out(df = w_df, variables = avaliable_var, drop_outlier = outlier_type, p_color = [plt_color["point"]],
                                              output_type = output_type)

            elif is_all_dtype(dtype = "character", dt_dict = vars_dt):  # -----------| ALl Character variables
                output = multi_char_out(df = w_df, variables = avaliable_var, p_color = single_bar_color,
                                        num_unique_obs = n_char_unique_value, output_type = output_type)

            elif is_all_dtype(dtype = "datetime", dt_dict = vars_dt):  # ----------| All datetime
                output = empty_out(output_type = output_type)

            elif is_all_dtype(dtype = ["numeric", "character"], dt_dict = vars_dt):  # ----------| A character and numeric variable
                output = single_char_num_out(df = w_df,
                                             chr_var = dtype_variable(dt_dict = vars_dt, data_type = "character"),
                                             num_var = dtype_variable(dt_dict = vars_dt, data_type = "numeric"),
                                             agg_fun = num_agg_type, drop_outlier = outlier_type, p_color = single_bar_color,
                                             keep_num_unique_chr = n_char_unique_value, output_type = output_type)

            elif is_all_dtype(dtype = ["numeric", "datetime"], dt_dict = vars_dt):  # ---------| A numeric and Datetime variable
                output = date_summary_out(df = w_df,
                                          date_var = dtype_variable(dt_dict = vars_dt, data_type = "datetime"),
                                          num_var = dtype_variable(dt_dict = vars_dt, data_type = "numeric"),
                                          chr_var = None, agg_fun = num_agg_type, p_color = single_bar_color, output_type = output_type)

            elif is_all_dtype(dtype = ["character", "datetime"], dt_dict = vars_dt):  # ---------| A character and Datetime variable
                output = empty_out(output_type = output_type)  # No Solution Yet.

            else:
                output = empty_out(output_type = output_type)

        elif len(avaliable_var) == 3:
            if is_all_dtype(dtype = "numeric", dt_dict = vars_dt):     # ---------| All numeric
                plt_type = "2d" if plt_type is None else plt_type
                output = num_relationship_out(df = w_df, variables = avaliable_var, drop_outlier = outlier_type, p_color = single_bar_color,
                                              plot_type = plt_type, output_type = output_type)

            elif is_all_dtype(dtype = "character", dt_dict = vars_dt):  # --------| All character
                output = multi_char_out(df = w_df, variables = avaliable_var, p_color = group_color,
                                        num_unique_obs = n_char_unique_value, output_type = output_type)

            elif is_all_dtype(dtype = ["numeric", "character", "character"], dt_dict = vars_dt):  # --------| A numeric and two character variable
                chr_vars = dtype_variable(dt_dict = vars_dt, data_type = "character")
                output = one_num_two_chr_out(df = w_df,
                                             num_var  = dtype_variable(dt_dict = vars_dt, data_type = "numeric"),
                                             chr_var1 = chr_vars[0],
                                             chr_var2 = chr_vars[1],
                                             agg_fun  = num_agg_type, drop_outlier = outlier_type, p_color = single_bar_color,
                                             output_type = output_type)

            elif is_all_dtype(dtype = ["character", "numeric", "numeric"], dt_dict = vars_dt):  # -------| A character and two numeric variable.
                num_vars = dtype_variable(dt_dict = vars_dt, data_type = "numeric")
                output = one_chr_two_num_out(df = w_df,
                                             chr_var  = dtype_variable(dt_dict = vars_dt, data_type = "character"),
                                             num_var1 = num_vars[0],
                                             num_var2 = num_vars[1],
                                             p_color = group_color,
                                             drop_outlier = outlier_type, output_type = output_type)

            elif is_all_dtype(dtype = ["datetime", "numeric", "character"], dt_dict = vars_dt):  # -------| A datetime, numeric and character variable.
                output = date_summary_out(df = w_df,
                                          date_var = dtype_variable(dt_dict = vars_dt, data_type = "datetime"),
                                          num_var  = dtype_variable(dt_dict = vars_dt, data_type = "numeric"),
                                          chr_var  = dtype_variable(dt_dict = vars_dt, data_type = "character"),
                                          agg_fun  = num_agg_type, p_color = group_color, drop_outlier = outlier_type, output_type = output_type)

            else:
                output = empty_out(output_type = output_type)

    return output


def check_dtype(df, variables, ckeck_for):
    """
    parameter
    ---------
    df  [pd.DataFrame]
    variables list/str variables from the data.
    ckeck_for [string] What to check for either 'plot_type' or 'agg_fun'

    value
    -----
    A string if ckeck_for = "plot_type" else boolean if ckeck_for = "agg_fun"
    """
    supplied_var = [var for var in variables if var is not None]

    if ckeck_for == "plot_type":

        if len(supplied_var) == 1:
            avaliable_var = " ".join(supplied_var)

            vars_dt = get_vars_dtypes(df = df, variables = avaliable_var)

            return vars_dt[avaliable_var]

        elif len(supplied_var) == 3:
            vars_dt = get_vars_dtypes(df = df, variables = supplied_var)
            if is_all_dtype("numeric", vars_dt):
                return "scatter_num"
            else:
                return None
        else:
            return None

    elif ckeck_for == "agg_fun":
        if len(supplied_var) > 1:
            vars_dt = get_vars_dtypes(df=df, variables = supplied_var)

            if len(supplied_var) == 2:
                if is_all_dtype(dtype = ["character", "numeric"], dt_dict = vars_dt):
                    return True
                elif is_all_dtype(dtype = ["datetime", "numeric"], dt_dict = vars_dt):
                    return True
                else:
                    return None

            elif len(supplied_var) == 3:
                if is_all_dtype(dtype = ["numeric", "character", "character"], dt_dict = vars_dt):
                    return True
                elif is_all_dtype(dtype = ["datetime", "numeric", "character"], dt_dict = vars_dt):
                    return True
                else:
                    return None


def clean_column_names(df):
    clean_names = []

    for col in df.columns.to_list():
        for letter in col:
            if letter in punctuation:
                col = col.replace(letter, " ")
        clean_names.append(col.title())

    df.columns = clean_names
    return df


def create_data_type_table(df):
    """
    parameter
    ---------
    df [pd.DataFrame]

    return
    -------
    A pandas dataframe.
    """

    dtype_values = []
    null_values = []

    for col in df.columns.to_list():
        dtype_values.append(df[col].dtype.name)
        null_values.append(df[col].isnull().sum())

    f_tbl = DataFrame({"Variable": df.columns.to_list(),
                       "Data Type": dtype_values,
                       "Missing Values": null_values})

    f_tbl.loc[f_tbl["Data Type"] == "object", "Data Type"] = "Character"
    f_tbl.loc[f_tbl["Data Type"] == "float64", "Data Type"] = "Float"
    f_tbl.loc[f_tbl["Data Type"] == "int64", "Data Type"] = "Integer"
    f_tbl.loc[f_tbl["Data Type"] == "datetime64[ns]", "Data Type"] = "Datetime"
    f_tbl.loc[f_tbl["Data Type"] == "datetime64[ns, UTC]", "Data Type"] = "Datetime[UTC]"
    f_tbl.loc[f_tbl["Data Type"] == "category", "Data Type"] = "Category"
    f_tbl.loc[f_tbl["Data Type"] == "bool", "Data Type"] = "Boolean"

    return f_tbl


def table_structure(df):
    """
    parameter
    ---------
    df [pd.DataFrame]

    return
    ------
    String
    """

    f_tbl_shape = df.shape
    number_Float_vars = len(df.select_dtypes(["float64"]).columns.to_list())
    number_integer_vars = len(df.select_dtypes(["int64"]).columns.to_list())
    number_character_vars = len(df.select_dtypes(["object"]).columns.to_list())
    number_boolean_vars = len(df.select_dtypes(["bool"]).columns.to_list())
    number_datetime_vars = len(df.select_dtypes(["datetime64[ns]", "datetime64[ns, UTC]"]).columns.to_list())

    c_row = "rows" if f_tbl_shape[0] > 1 else "row"
    c_col = "columns" if f_tbl_shape[1] > 1 else "column"
    return f"""
            Data has {f_tbl_shape[0]:,} {c_row} and {f_tbl_shape[1]} {c_col}.  
              
                
            | -Data Type- |  -Number Of Variables- |
            | --- | --: |
            | Character | {number_character_vars} |
            | Integer | {number_integer_vars} |
            | Float | {number_Float_vars} |
            | Boolean | {number_boolean_vars} |
            | datetime | {number_datetime_vars} |
            """



def get_matrix_var(df):
    return df.select_dtypes(["int64", "float64"]).columns.to_list()


def corr_matrix(df, variables = None, plt_bg_color="#E9ECEF"):
    """
    :param df: a dataframe with numerical data types
    :param variables: a list of numerical variables from the data.
    :param plt_bg_color: plot background color.
    :return: plotly object
    """
    f_df = df.select_dtypes(["int64", "float64"])

    if variables is not None:
        if len(variables) >= 2:
            f_df = f_df[variables]
        else:
            f_df

    corr_mtx = f_df.corr()

    if corr_mtx.shape != (0, 0):
        if corr_mtx.shape[1] <= 8:
            z = array(corr_mtx)

            f_fig = create_annotated_heatmap(
                z=z,
                x=list(corr_mtx.columns),
                y=list(corr_mtx.index),
                annotation_text= around(z, decimals=2),
                hoverinfo=["x", "y"],
                hovertemplate="%{x}<br>%{y}<extra></extra>",
                colorscale=heatmap_color_scale,
                showscale=True,
                font_colors=["white"],
                ygap=1, xgap=1,
                zmin=-1, zmid=0, zmax=1,
            )
            f_fig.update_xaxes(side="bottom")
            f_fig.update_layout(paper_bgcolor=plt_bg_color, plot_bgcolor=plt_bg_color,
                                title_text="Correlation Matrix",
                                title_x=0.1,
                                xaxis_showgrid=False, yaxis_showgrid=False,
                                template="plotly_white")

            for i in range(len(f_fig.layout.annotations)):
                if f_fig.layout.annotations[i].text == "nan":
                    f_fig.layout.annotations[i].text = ""

            return f_fig

        elif corr_mtx.shape[1] > 8:
            heatmap = Heatmap(
                x=corr_mtx.columns,
                y=corr_mtx.index,
                z= array(corr_mtx),
                zmin=-1, zmid=0, zmax=1,
                xgap=1, ygap=1,
                hovertemplate="%{x}<br>%{y}<br>%{z:.3f}<extra></extra>",
                colorscale=heatmap_color_scale
            )

            layout = Layout(
                title_text="Correlation Matrix",
                title_x=0.1,
                xaxis_showgrid=False, yaxis_showgrid=False,
                paper_bgcolor=plt_bg_color, plot_bgcolor=plt_bg_color,
                template="plotly_white"
            )

            f_fig = Figure(data=[heatmap], layout=layout)
            return f_fig