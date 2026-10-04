"""Generates powerbi/power_query_all_tables.m (copy/paste M code for each table) from data/processed/*.csv"""
import glob, os
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROC = os.path.join(BASE, "data", "processed")
out = []
out.append("""// ============================================================================
// POWER QUERY (M) CODE - one block per table. In Power BI Desktop:
//   Home -> Transform data -> New Source -> Blank Query -> Advanced Editor -> paste ONE block -> Done -> rename query
// STEP 0: create the parameter first:  Home -> Manage Parameters -> New Parameter
//         Name: DataFolder | Type: Text | Current Value: the full path ending with a backslash, e.g.
//         C:\\Users\\you\\bi-projects\\03-powerbi-olist-dashboard\\data\\processed\\
// ============================================================================

""")
for path in sorted(glob.glob(os.path.join(PROC, "*.csv"))):
    name = os.path.basename(path)[:-4]
    df = pd.read_csv(path, nrows=2000)
    cols = []
    for c in df.columns:
        s = df[c]
        if c in ("date", "purchase_date", "creation_date"):
            t = "type date"
        elif c.endswith("_ts") or c in ("approved_at", "shipping_limit_date"):
            t = "type datetime"
        elif pd.api.types.is_integer_dtype(s) and not c.endswith("_id") and c not in ("zip_prefix",):
            t = "Int64.Type"
        elif pd.api.types.is_float_dtype(s) and not c.endswith("_id"):
            t = "type number"
        elif c == "zip_prefix":
            t = "type text"
        else:
            t = "type text"
        cols.append(f'{{"{c}", {t}}}')
    out.append(f"// ---------------------------------------------------------------- {name}\n")
    out.append(f"""let
    Source  = Csv.Document(File.Contents(DataFolder & "{name}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{{", ".join(cols)}}}, "en-US")
in
    Typed

""")
open(os.path.join(BASE, "powerbi", "power_query_all_tables.m"), "w", encoding="utf-8").write("".join(out))
print("written powerbi/power_query_all_tables.m")
