import dash
import pandas as pd
from dash import Input, Output, State, dcc, html, dash_table, ctx
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Scheme, Group

import datetime
import base64
import io

import custom_functions as cf
from pandas.api.types import is_numeric_dtype


# Read Demo data.
demo_df = pd.read_csv("m_sales.csv")

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.LUX])
server = app.server

# Tabs =================================================================================================================
# Upload Tab ---------------------------------------------------------------------------------------------------------|-
tab_data_choice = dbc.Tab(
    id = "tab_data_choice",
    label = "Data Choice",
    tab_class_name = "tab-style-23",
    active_tab_class_name = "tab-selected",
    label_class_name = "tab-label-style",
    children = [
        dbc.Row(
            class_name = "g-6 tab-top-row",
            children = [
                dbc.Col(
                    html.Div(
                        [
                            dcc.Upload(
                            id = "upload_data",
                            children = [
                                dbc.Button(
                                    children = html.Div(["Drag and Drop or Select file"]),
                                    color = "primary",
                                    outline = True,
                                    class_name = "me-1"
                                )
                            ],
                            className = "d-grid gap-2",
                            multiple = True
                            )
                        ],
                    ),
                    width = 4,
                    align = "center"
                ),

                dbc.Col(
                    html.Div(
                        [
                            dbc.Button(
                                children = html.Div(["Use Demo Data"]),
                                id = "use_demo_data",
                                color = "primary",
                                outline = True,
                                class_name = "me-1"
                            )
                        ],
                        className = "d-grid gap-2",
                    ),
                    width = 4,
                    align = "center",
                )
            ],
            justify = "center",
        ),

        html.Br(),

        dbc.Row(
            class_name = "g-6 tab-row",
            children = html.Div(
                [
                    dcc.Store(id = "store_data"),
                    dbc.Card(
                        [
                            dbc.CardHeader("Data Preview", class_name = "card-title"),
                            dcc.Loading(
                                id = "display_data_spinner",
                                color = "black",
                                children = [
                                    dbc.CardBody(id = "display_data")
                                ]
                            )
                        ]
                    )
                ]
            )
        ),
    ]
)


# Data Checks Tab ----------------------------------------------------------------------------------------------------|-
tab_data_inpection = dbc.Tab(
    tab_id = "tab_data_check",
    label = "Data Inspection",
    tab_class_name = "tab-style-22",
    active_tab_class_name = "tab-selected",
    label_class_name = "tab-label-style",
    children = [
        dbc.Row(
            class_name = "tab-top-row",
            children = [
                dbc.Col(
                    width = 3,
                    children = [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.H5("Select A Variable Type"),
                                                        dcc.Dropdown(
                                                            id = "data_variable_type",
                                                            options = [
                                                                {"label": "Numeric",  "value": "numeric"},
                                                                {"label": "Character", "value": "character"},
                                                                {"label": "Datetime", "value": "datetime"}
                                                            ],
                                                            searchable = True,
                                                        )
                                                    ]
                                                ),

                                                html.Br(),
                                                html.Br(),

                                                html.Div(
                                                    [
                                                        dbc.ButtonGroup(
                                                            [
                                                                dbc.Button(
                                                                    id = "unique_chr_value",
                                                                    children = "Check Unique Character Values",
                                                                ),

                                                                html.Br(),

                                                                dbc.Button(
                                                                    id = "numeric_summary",
                                                                    children = "Check Numeric summary",
                                                                ),

                                                                html.Br(),

                                                                dbc.Button(
                                                                    id = "missing_values",
                                                                    children = "Check Missing Values",
                                                                )
                                                            ],
                                                            vertical = True
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),

                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Data Preview", class_name="card-title"),
                                dcc.Loading(
                                    id="data_check_spinner",
                                    color="black",
                                    children=[
                                        dbc.CardBody(id="data_check_output")
                                    ]
                                ),
                            ]
                        ),

                        html.Br(),

                        dbc.Card(
                            [
                                dbc.CardHeader("Data Structure", class_name = "card-title"),
                                dbc.CardBody(dcc.Markdown(id = "data_inspection_summary"), )
                            ]
                        ),
                    ],

                    width = 9,
                )
            ]
        )
    ]
)


# Data Cleaning Tab --------------------------------------------------------------------------------------------------|-
tab_data_cleaning = dbc.Tab(
    tab_id = "tab_data_cleaning",
    label = "Data Cleaning",
    tab_class_name = "tab-style-22",
    active_tab_class_name = "tab-selected",
    label_class_name = "tab-label-style",
    children = [
            dbc.Row(
                class_name = "tab-top-row",
                children = [
                    dbc.Col(
                        width = 3,
                        children = [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.H5("Drop Missing Values"),
                                                        dcc.Dropdown(
                                                            id = "drop_missing_values",
                                                            options = [
                                                                {"label": "Rows with missing values.", "value": "all_rows"},
                                                                {"label": "Columns with missing values.", "value": "all_cols"},
                                                                {"label": "Rows when all records are missing.", "value": "rows_all_na"},
                                                                {"label": "Columns with only missing values.", "value": "cols_all_na"},
                                                                {"label": "Columns based on percentage of missing values.", "value": "percent_missing"}
                                                            ],
                                                            searchable = True,
                                                            placeholder = "How to drop missing values",
                                                        ),

                                                        html.Br(),

                                                        html.P("This is necessary when Columns based on percentage of missing values is selected"),
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.Input(placeholder = "Non Missing",
                                                                          id = "percent_non_missing",
                                                                          type = "number",
                                                                          min = 0, max = 100),
                                                                dbc.InputGroupText("%"),
                                                            ],
                                                            className = "styled-numeric-input"
                                                        ),
                                                        dbc.Tooltip(
                                                            children = "Number must be between 1 and 100",
                                                            target = "percent_non_missing",
                                                            placement = "right",
                                                        )
                                                    ],
                                                ),

                                                html.Br(),
                                                html.Br(),

                                                html.Div(
                                                    [
                                                        html.H5("Change Data Type"),
                                                        dbc.Accordion(
                                                            children = [
                                                                dbc.AccordionItem(
                                                                    [
                                                                        dcc.Dropdown(
                                                                            id = "change_character_var",
                                                                            multi = True,
                                                                        ),
                                                                    ],
                                                                    title = "To Character",
                                                                ),

                                                                dbc.AccordionItem(
                                                                    [
                                                                        html.H6("Integer"),
                                                                        dcc.Dropdown(
                                                                            id = "change_integer_var",
                                                                            multi = True,
                                                                        ),

                                                                        html.Br(),

                                                                        html.H6("Float"),
                                                                        dcc.Dropdown(
                                                                            id = "change_float_var",
                                                                            multi = True,
                                                                        ),
                                                                    ],
                                                                    title = "To Numeric",
                                                                ),

                                                                dbc.AccordionItem(
                                                                    [
                                                                        dcc.Dropdown(
                                                                            id = "change_boolean_var",
                                                                            multi = True,
                                                                        ),
                                                                    ],
                                                                    title = "To Boolean",
                                                                ),

                                                                dbc.AccordionItem(
                                                                    [
                                                                        dcc.Dropdown(
                                                                            id = "change_datetime_var",
                                                                            multi = True,
                                                                        ),
                                                                    ],
                                                                    title = "To Datetime",
                                                                ),
                                                            ],
                                                            start_collapsed = True,
                                                        ),
                                                    ],
                                                ),

                                                html.Br(),
                                                html.Br(),

                                                html.Div(
                                                    [
                                                        html.H5("Extract More Datetime variables"),
                                                        dcc.Dropdown(
                                                            id = "datetime_variable",
                                                            placeholder = "Select A Datetime variable",
                                                        ),

                                                        html.Br(),

                                                        html.H6("Type Of Datetime To Extract"),
                                                        dcc.Dropdown(
                                                            id = "type_datetime",
                                                            options = [
                                                                {"label": "Second", "value": "second"},
                                                                {"label": "Minute", "value": "minute"},
                                                                {"label": "Hour", "value": "hour"},
                                                                {"label": "Day", "value": "day"},
                                                                {"label": "Month", "value": "month"},
                                                                {"label": "Month Name", "value": "month_name"},
                                                                {"label": "Quarter", "value": "quarter"},
                                                                {"label": "Year", "value": "year"},
                                                                {"label": "Day of year", "value": "day_of_year"},
                                                                {"label": "Week of year", "value": "week_of_year"}
                                                            ],
                                                            multi = True,
                                                            placeholder = "Which"
                                                        )
                                                    ]
                                                ),

                                                html.Br(),
                                                html.Br(),

                                                html.Div(
                                                    [
                                                        dbc.Button(
                                                        children = "Clean",
                                                        id = "clean",
                                                        color = "success",
                                                        class_name = "me-1"
                                                        ),
                                                    ],
                                                    className = "d-grid gap-2",
                                                )
                                            ]
                                        )
                                    ]
                                )
                            )
                        ]
                    ),

                    dbc.Col(
                        width = 9,
                        children = [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Data Preview"),
                                    dcc.Loading(
                                        id = "data_cleaning_spinner",
                                        color = "black",
                                        children = [
                                            dbc.CardBody(id = "data_cleaning_output"),
                                        ]
                                    ),

                                    html.Br(),

                                    dcc.Markdown(id = "table_summary"),

                                    dcc.Store(id = "store_cleaned_data"),
                                ]
                            ),

                            html.Br(),

                            dbc.Card(
                                [
                                    dbc.CardHeader("Data types"),
                                    dbc.CardBody(id = "data_type_output"),
                                ],
                            ),
                        ]
                    )
                ]
            )
        ]
)


# Data Summary Tab ---------------------------------------------------------------------------------------------------|-
tab_data_summary = dbc.Tab(
    id = "tab_data_summary",
    tab_id = "data_summary_tab",
    label = "Data Summary",
    tab_class_name = "tab-style-23",
    active_tab_class_name = "tab-selected",
    label_class_name = "tab-label-style",
    children = [
        dbc.Row(
            class_name = "tab-top-row",
            children = [
                dbc.Col(
                    width = 3,
                    children = [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.H6("Select A Variable"),
                                                        dcc.Dropdown(
                                                            id = "first_variable",
                                                            searchable = True,
                                                            placeholder = "Nothing Selected",
                                                        )
                                                    ]
                                                ),

                                                html.Br(),

                                                html.Div(
                                                    [
                                                        html.H6("Select A Variable (Optional)"),
                                                        dcc.Dropdown(
                                                            id = "second_variable",
                                                            searchable = True,
                                                            placeholder = "Nothing Selected",
                                                        )
                                                    ]
                                                ),

                                                html.Br(),

                                                html.Div(
                                                    [
                                                        html.H6("Select A variable (Optional)"),
                                                        dcc.Dropdown(
                                                            id = "third_variable",
                                                            searchable = True,
                                                            placeholder = "Nothing Selected",
                                                        )
                                                    ]
                                                ),

                                                dbc.Modal(
                                                    [
                                                        dbc.ModalBody(
                                                            dcc.Markdown(id = "duplicate_input")
                                                        ),
                                                        dbc.ModalFooter(
                                                            dbc.Button(
                                                                "Okay",
                                                                id = "close_modal",
                                                                n_clicks = 0,
                                                                class_name = "ms-auto"
                                                            )
                                                        )
                                                    ],
                                                    id = "modal_id",
                                                    is_open = False,
                                                ),

                                                html.Br(),

                                                html.Div(
                                                    [
                                                        dbc.Accordion(
                                                            [
                                                                dbc.AccordionItem(
                                                                    [
                                                                        html.P(
                                                                         "This is useful when a single numerical or character variable is selected."
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id = "plot_type",
                                                                            searchable = True,
                                                                            placeholder = "Nothing Selected",
                                                                        ),
                                                                    ],
                                                                    title = "Plot Type"
                                                                ),

                                                                dbc.AccordionItem(
                                                                    [
                                                                        html.P("This is useful when a numeric and any other data type variable is selected"),
                                                                        dcc.Dropdown(
                                                                            id = "agg_function",
                                                                            searchable = True,
                                                                            # value = "mean",
                                                                            placeholder = "Nothing Selected",
                                                                        )
                                                                    ],
                                                                    title = "Aggregate Function"
                                                                ),

                                                                dbc.AccordionItem(
                                                                    [
                                                                        html.P("This is useful when a numeric variable is selected."),
                                                                        dcc.Dropdown(
                                                                            id = "drop_outlier",
                                                                            searchable = True,
                                                                            options = [
                                                                                {"label": "Weak Lower", "value": "weak_lower"},
                                                                                {"label": "Weak Upper", "value": "weak_upper"},
                                                                                {"label": "Weak Both", "value": "weak_both"},
                                                                                {"label": "Strong Lower", "value": "strong_lower"},
                                                                                {"label": "Strong Upper", "value": "strong_upper"},
                                                                                {"label": "Strong Both", "value": "strong_both"}
                                                                            ],
                                                                            placeholder = "Nothing Selected",
                                                                        )
                                                                    ],
                                                                    title = "Drop Outlier"
                                                                )
                                                            ],
                                                            start_collapsed = True,
                                                        )
                                                    ]
                                                ),

                                                html.Br(),

                                                html.Div(
                                                    [
                                                        html.H6("Type Of Output"),
                                                        dbc.RadioItems(
                                                            id = "output_type",
                                                            options = [
                                                                {"label": "Graph", "value": "plot"},
                                                                {"label": "Table", "value": "table"}
                                                            ],
                                                            value = "plot",
                                                        ),

                                                        html.Br(),

                                                        html.H6("Number Of Rows"),
                                                        dbc.Input(
                                                            id = "num_rows",
                                                            type = "number",
                                                            min = 3, value = 10,
                                                        )
                                                    ]
                                                ),

                                                html.Br(),
                                                html.Br(),

                                                html.Div(
                                                    [
                                                        dbc.Button(
                                                            children = "Display",
                                                            id = "run_summary",
                                                            color = "success",
                                                            class_name = "me-1"
                                                        )
                                                    ],
                                                    className = "d-grid gap-2",
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),

                dbc.Col(
                    width = 9,
                    children = [
                        dbc.Card(
                            [
                                dcc.Loading(
                                    id = "summary_spinner",
                                    color = "black",
                                    children = [
                                        dbc.CardBody(id = "summary_output"),
                                    ]
                                ),
                                dcc.Store(id = "summary_data"),
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)



# Layout ===============================================================================================================
app.layout = html.Div(
    children = [
        dbc.Row(
            html.Div(
                html.Div(
                    html.H3("Data Variable Summary", className = "header-H2"),
                    className = "header-inner"
                ),
            )
        ),

        html.Br(),

        dbc.Row(
            children = [
                html.Div(
                    dbc.Tabs(
                        id = "top_tab",

                        children = [
                            tab_data_choice,
                            tab_data_inpection,
                            tab_data_cleaning,
                            tab_data_summary
                        ]
                    )
                ),
            ]
        )
    ]
)


# Output Functions =====================================================================================================
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)

    try:
        if "csv" in filename:
            u_data = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            u_data = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return u_data


def create_dataframe(df, page_size = 10, align_text = "left", increase_col_width = None, tbl_height = None):
    d_tbl = cf.clean_column_names(df)

    if increase_col_width is not None:
        cell_conditional = [{"if": {"column_id": increase_col_width[0]}, "width": increase_col_width[1]}]
    else:
        cell_conditional = []

    table_style = {"overflowX": "auto", "overflowY": "auto"}
    if tbl_height is not None:
        table_style["height"] = tbl_height


    return html.Div(
        [
            dash_table.DataTable(
                data = d_tbl.to_dict("records"),
                columns = [
                    {"name": col, "id": col,
                     "format": Format(nully = "N/A",
                                      precision = 2,
                                      scheme = Scheme.fixed,
                                      group  = Group.yes,
                                      groups = 3,
                                      ), "type": "numeric" if is_numeric_dtype(d_tbl[col]) else None} for col in d_tbl.columns
                ],
                #{"specifier": ".2f"},
                page_size = page_size,
                style_table = table_style,
                fixed_rows = {"headers": True},
                style_cell = {"minWidth": 100, "maxWidth": 700, "width": 100, "textAlign": align_text, 'textOverflow': 'ellipsis'},
                style_header = {"backgroundColor": "#E8E8E8", "color": "0F0F0F", "fontWeight": "blue", 'borderBottom': '1px solid #595959'},
                style_data_conditional = [
                    {"if": {"row_index": "even"}, "backgroundColor": "#FAFAFA", "color": "#000000"},
                    {"if": {"row_index": "odd"}, "backgroundColor": "#F5F5F5", "color": "#000000"},
                        ],
                style_cell_conditional = cell_conditional,
            )
        ]
    )


def create_graph(graph_object):
    return html.Div(
        [
            dcc.Graph(figure = graph_object,
                      config={
                          "displaylogo": False,
                          "modeBarButtonsToRemove": ["pan2d", "lasso2d", "zoomIn2d", "zoomOut2d", "zoom2d", "toImage",
                                                     "select2d", "autoScale2d"]
                      }
                      )
        ]
    )


# Callbacks ============================================================================================================
@app.callback(
    Output("store_data", "data"),
    Input("use_demo_data", "n_clicks"),
    Input("upload_data", "contents"),
    State("upload_data", "filename"),
    State("upload_data", "last_modified")
)
def data_choice(click_demo, list_of_contents, list_of_names, list_of_dates):
    if click_demo and not list_of_contents:
        return demo_df.to_json(date_format = "iso", orient = "split")

    elif click_demo and list_of_contents:
        if ctx.triggered_id is not None:
            button_id = ctx.triggered_id #[0]["prop_id"].split(".")[0]

            if button_id == "upload_data":
                f_tbl = [parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
                return f_tbl[0].to_json(date_format = "iso", orient = "split")

            elif button_id == "use_demo_data":
                return demo_df.to_json(date_format = "iso", orient = "split")

    elif not click_demo  and list_of_contents:
        f_tbl = [parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return f_tbl[0].to_json(date_format = "iso", orient = "split")


@app.callback(
    Output("display_data", "children"),
    Input("store_data", "data"),
)
def display_data(jsonified_data):
    if jsonified_data is not None:
        c_tbl = pd.read_json(jsonified_data, orient = "split")

        return create_dataframe(df = c_tbl)



@app.callback(
    Output("data_check_output", "children"),
    Input("store_data", "data"),
    Input("data_variable_type", "value"),
    Input("unique_chr_value", "n_clicks"),
    Input("numeric_summary", "n_clicks"),
    Input("missing_values", "n_clicks"),
)
def check_for(jsonified_data, variable_type, unique_chr, num_summary, missing_vals):
    if jsonified_data is not None:
        c_tbl = pd.read_json(jsonified_data, orient = "split")

        if variable_type is not None or unique_chr is not None or num_summary is not None or missing_vals is not None:
            recent_id = ctx.triggered_id if not None else None

            if recent_id == "data_variable_type" and variable_type is not None:
                selected_dtype = cf.get_dtype(df = c_tbl, dtype = variable_type, return_names = False)
                return create_dataframe(selected_dtype)

            elif recent_id == "unique_chr_value":
                unique_chr_tbl = cf.chr_unique_value(df = c_tbl, max_n=10)
                return create_dataframe(unique_chr_tbl, increase_col_width = ["Number Of Unique Values", 220])

            elif recent_id == "numeric_summary":
                num_summary_tbl = cf.numeric_description(df = c_tbl)
                return create_dataframe(num_summary_tbl)

            elif recent_id == "missing_values":
                missing_vals_tbl = cf.get_missing_values(df = c_tbl)
                return create_dataframe(missing_vals_tbl)



@app.callback(
    Output("data_inspection_summary", "children"),
    Input("store_data", "data")
)
def update_data_inspection_summary(jsonified_data):
    if jsonified_data is not None:
        c_tbl = pd.read_json(jsonified_data, orient = "split")

        return cf.table_structure(c_tbl)


@app.callback(
    [Output("change_character_var", "options"),
     Output("change_integer_var", "options"),
     Output("change_float_var", "options"),
     Output("change_boolean_var", "options"),
     Output("change_datetime_var", "options"),
     Output("datetime_variable", "options")],
    Input("store_data", "data"),
)
def update_variable_names(jsonified_data):
    if jsonified_data is not None:
        c_tbl = pd.read_json(jsonified_data, orient="split")
        variable_names = c_tbl.columns.to_list()

        return variable_names, variable_names, variable_names, variable_names, variable_names, variable_names
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update



@app.callback(
    Output("data_cleaning_output", "children"),
    Output("store_cleaned_data", "data"),
    Input("store_data", "data"),
    Input("clean", "n_clicks"),
    [State("drop_missing_values", "value"),
    State("percent_non_missing", "value"),
    State("change_character_var", "value"),
    State("change_integer_var", "value"),
    State("change_float_var", "value"),
    State("change_boolean_var", "value"),
    State("change_datetime_var", "value"),
    State("datetime_variable", "value"),
    State("type_datetime", "value")],
)
def clean_data(jsonified_data, click, drop_missing, percent_missing,
               change_chr, change_int, change_float, change_bool, change_date, date_var, typ_date):
    if jsonified_data is not None:
        c_tbl = pd.read_json(jsonified_data, orient = "split")
        d_tbl = c_tbl.copy()

        if drop_missing is not None:
            if drop_missing != "percent_missing":
                d_tbl = cf.drop_missing_values(df = d_tbl, how = drop_missing, percentage = None)
            else:
                if percent_missing is not None:
                    d_tbl = cf.drop_missing_values(df = d_tbl, how = drop_missing, percentage = percent_missing)
                else:
                    dash.no_update

        if change_chr is not None:
            d_tbl = cf.change_dtype(df = d_tbl, variables = change_chr, to_type = "character")
        if change_int is not None:
            d_tbl = cf.change_dtype(df = d_tbl, variables = change_int, to_type = "integer")
        if change_float is not None:
            d_tbl = cf.change_dtype(df = d_tbl, variables = change_float, to_type = "float")
        if change_bool is not None:
            d_tbl = cf.change_dtype(df = d_tbl, variables = change_bool, to_type = "boolean")
        if change_date is not None:
            d_tbl = cf.change_dtype(df = d_tbl, variables = change_date, to_type = "date")


        if date_var is not None:
            if typ_date is not None:
                d_tbl = cf.extract_datetime(df = d_tbl, date_col = date_var, which = typ_date)
            else:
                d_tbl

        if click:
            return  create_dataframe(d_tbl, page_size = 20, tbl_height = "600px"), d_tbl.to_json(date_format = "iso", orient = "split")
        else:
            raise dash.exceptions.PreventUpdate

    else:
        return dash.no_update, dash.no_update


@app.callback(
    Output("table_summary", "children"),
    Input("store_cleaned_data", "data"),
)
def update_cleaned_data_summary(cleaned_jsonified_data):
    if cleaned_jsonified_data is not None:
        clean_df = pd.read_json(cleaned_jsonified_data, orient = "split")

        return cf.table_structure(clean_df)



@app.callback(
    Output("data_type_output", "children"),
    Input("store_cleaned_data", "data"),
)
def create_data_type_table(cleaned_jsonified_data):
    if cleaned_jsonified_data is not None:
        clean_df = pd.read_json(cleaned_jsonified_data, orient = "split")

        desc_output = cf.create_data_type_table(clean_df)
        return create_dataframe(desc_output, page_size = 20, tbl_height = "400px")

    else:
        dash.no_update



@app.callback(
    Output("summary_data", "data"),
    Input("store_cleaned_data", "data"),
    Input("store_data", "data"),
)
def update_summary_data(cleaned_jsonified_data, jsonified_data):
    if cleaned_jsonified_data is None and jsonified_data is not None:
        return jsonified_data
    elif cleaned_jsonified_data is not None and jsonified_data is not None:
        return cleaned_jsonified_data
    else:
        raise dash.exceptions.PreventUpdate



@app.callback(
    Output("first_variable", "options"),
    Output("second_variable", "options"),
    Output("second_variable", "value"),
    Output("third_variable", "options"),
    Output("third_variable", "value"),
    Input("summary_data", "data"),
)
def update_cleaned_variable_names(jsonified_summary_data):
    if jsonified_summary_data is not None:
        s_tbl = pd.read_json(jsonified_summary_data, orient = "split")

        variable_names = s_tbl.columns.to_list()
        variable_names_no_sel = variable_names + ["No Selection"]

        return variable_names, variable_names_no_sel, "No Selection", variable_names_no_sel, "No Selection"

    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output("modal_id", "is_open"),
    Input("first_variable", "value"),
    Input("second_variable", "value"),
    Input("third_variable", "value"),
    Input("close_modal", "n_clicks"),
    State("modal_id", "is_open")
)
def toggle_duplicate_modal(first_var, second_var, third_var, close_click, is_open):
    if first_var is not None and second_var is not None and third_var is not None:
        if second_var != "No Selection" and third_var == "No Selection":
            if first_var == second_var:
                return not is_open
            elif close_click:
                return is_open

        elif second_var != "No Selection" and third_var != "No Selection":
            if first_var == second_var or  first_var == third_var or second_var == third_var:
                return not is_open

            elif close_click:
                return is_open
    else:
        dash.no_update

@app.callback(
    Output("duplicate_input", "children"),
    Input("first_variable", "value"),
    Input("second_variable", "value"),
    Input("third_variable", "value"),
)
def update_duplicate_message(first_var, second_var, third_var):
    def markdown_output(variable_type):
        return f"""
                **Duplicate variables detected**  
                
                All variables supplied must be unique.  
                  
                | variable | | value |
                | --- | --- | ---: |
                | first | = | {first_var} |
                | second | = | {second_var} |
                | Third | = | {third_var} |  
                
                {var_type} are similar.
               """

    if first_var is not None and second_var is not None and third_var is not None:
        if second_var != "No Selection" and third_var == "No Selection":
            duplicate_value = ["first", "second"]

            var_type = f"The {duplicate_value[0]} and {duplicate_value[1]} variable"
            return markdown_output(var_type)

        elif second_var != "No Selection" and third_var != "No Selection":
            if first_var == second_var and first_var == third_var:
                duplicate_value = "All"
            elif first_var == third_var:
                duplicate_value = ["first", "third"]
            elif second_var == third_var:
                duplicate_value = ["second", "third"]
            elif first_var == second_var:
                duplicate_value = ["first", "second"]
            else:
                duplicate_value = ""

            if isinstance(duplicate_value, list):
                var_type = f"The {duplicate_value[0]} and {duplicate_value[1]} variable"
            else:
                var_type = "All variables"

            return markdown_output(var_type)
    else:
        return dash.no_update


@app.callback(
    Output("plot_type", "options"),
    Output("agg_function", "options"),
    Output("agg_function", "value"),
    Input("summary_data", "data"),
    Input("first_variable", "value"),
    Input("second_variable", "value"),
    Input("third_variable", "value"),
)
def update_plot_agg_type(jsonified_summary_data, first_var, second_var, third_var):
    if jsonified_summary_data is not None:
        s_tbl = pd.read_json(jsonified_summary_data, orient = "split")

        second_var = None if second_var == "No Selection" else second_var
        third_var = None if third_var == "No Selection" else third_var

        if first_var is not None:
            supplied_variables = [first_var, second_var, third_var]

            for_plot_type = cf.check_dtype(df = s_tbl, variables = supplied_variables, ckeck_for = "plot_type")
            for_agg_value = cf.check_dtype(df = s_tbl, variables = supplied_variables, ckeck_for = "agg_fun")

            if for_plot_type == "character":
                pt_options = [
                    {"label": "Bar Chart", "value": "bar"},
                    {"label": "Pie Chart", "value": "pie"}
                ]
            elif for_plot_type == "numeric":
                pt_options = [
                    {"label": "Histogram", "value": "hist"},
                    {"label": "Box Plot", "value": "box"},
                    {"label": "Violin Plot", "value": "vio"},
                ]
            elif for_plot_type == "scatter_num":
                pt_options = [
                    {"label": "2-dimension", "value": "2d"},
                    {"label": "3-dimension", "value": "3d"}
                ]
            else:
                pt_options = []

            if for_agg_value:
                af_options = [
                   {"label": "Average", "value": "mean"},
                   {"label": "Median", "value": "median"},
                   {"label": "Sum", "value": "sum"},
                   {"label": "Minimum", "value": "min"},
                   {"label": "Maximum", "value": "max"}
                ]
                af_value = "mean"
            else:
                af_options = []
                af_value = ""

            return pt_options, af_options, af_value
        else:
            return [], [], []
    else:
        return dash.no_update, dash.no_update, dash.no_update



@app.callback(
    Output("summary_output", "children"),
    Input("summary_data", "data"),
    Input("run_summary", "n_clicks"),
    State("first_variable", "value"),
    State("second_variable", "value"),
    State("third_variable", "value"),
    State("plot_type", "value"),
    State("agg_function", "value"),
    State("drop_outlier", "value"),
    State("output_type", "value"),
    State("num_rows", "value")
)
def create_summary(jsonified_data, clicks, first_var, second_var, third_var, plot_type, agg_fun, drop_outlier, output_type, n_rows):
    if jsonified_data is not None:
        cc_tbl = pd.read_json(jsonified_data, orient = "split")

        if clicks:
            second_var = None if second_var == "No Selection" else second_var
            third_var = None if third_var == "No Selection" else third_var

            u_output = cf.wrapper_summary(w_df = cc_tbl,
                                          first_variable  = first_var,
                                          second_variable = second_var,
                                          third_variable  = third_var,
                                          plt_type = plot_type,
                                          num_agg_type = agg_fun,
                                          outlier_type = drop_outlier,
                                          output_type  = output_type)

            if output_type == "plot":
                return create_graph(u_output)
            elif output_type == "table":
                return create_dataframe(df = u_output, page_size = n_rows)
    else:
        return dash.no_update






if __name__ == "__main__":
    app.run_server(debug = True)