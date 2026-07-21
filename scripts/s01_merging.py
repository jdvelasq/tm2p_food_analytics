import glob

import pandas as pd  # type: ignore


def main():
    _merged_scopus_files()
    # _merged_wos_files()


def _merged_scopus_files():
    files = _get_files("scopus/ingest/downloaded/*.csv")
    df = _concatenate_files(files, sep=",")
    _save_merged(df, "scopus/ingest/downloaded/_merged.csv", sep=",")


# def _merged_wos_files():
#     files = _get_files("wos/ingest/downloaded/*.tsv")
#     df = _concatenate_files(files, sep="\t")
#     _save_merged(df, "wos/ingest/downloaded/_merged.tsv", sep="\t")


def _get_files(path):
    files = glob.glob(path)
    files = [file for file in files if "_merged" not in file]
    return files


def _concatenate_files(files, sep):
    dfs = [pd.read_csv(file, sep=sep) for file in files]
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(keep="first")
    return df


def _save_merged(df, file, sep):
    df.to_csv(file, index=False, sep=sep)


if __name__ == "__main__":
    main()
