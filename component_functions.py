import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Scheme, Group
from pandas.api.types import is_numeric_dtype
from string import punctuation


datetime_type = ["second", "minute", "hour", "day", "month", "month_name", "quarter", "year", "day_of_year", "week_of_year"]
outlier_values = ["weak_lower", "weak_upper", "weak_both", "strong_lower", "strong_upper", "strong_both"]


def have_empty_values_markdown(value):  # change conversion to conce
    """
    :param value:
    :return:
    """
    if isinstance(value["variables"], list):
        variables = ", ".join(value["variables"])

        return f"""
                All empty values such as ' ' in   
                **{variables}**   
                have been dropped before conversion was done.
               """
    else:
        return f"""
                All empty values such as ' ' in **{value["variables"]}** have been    
                dropped before conversion was done.
               """


def clean_column_names(df):
    clean_names = []

    for col in df.columns.to_list():
        for letter in col:
            if letter in punctuation:
                col = col.replace(letter, " ")
        clean_names.append(col.title())

    df.columns = clean_names
    return df


def create_dataframe(df, page_size = 10, align_text = "left", increase_col_width = None, tbl_height = None):
    d_tbl = clean_column_names(df)

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
                style_header = {"backgroundColor": "#CED4DA", "color": "#212529", "fontWeight": "blue", 'borderBottom': '1px solid #212529'},
                style_data_conditional = [
                    {"if": {"row_index": "even"}, "backgroundColor": "#E9ECEF", "color": "#000000"},
                    {"if": {"row_index": "odd"}, "backgroundColor": "#F8F9FA", "color": "#000000"},
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


def create_modal_ui(m_id, m_body_id, m_close_btn_id, modal_title = ""):
    """
    :param m_id: Modal id
    :param m_body_id: Markdown id inside the modal body.
    :param m_close_btn_id: Close button id.
    :return:
    """
    return dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(modal_title)
                    ),
                    dbc.ModalBody(
                        dcc.Markdown(id = m_body_id)
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Okay",
                            id = m_close_btn_id,
                            n_clicks = 0,
                            class_name = "ms-auto"
                        )
                    )
                ],
                id = m_id,
                is_open=False,
            )