from pathlib import Path  # type: ignore

from tm2p.enum import AnalysisUnit  # type: ignore
from tm2p.enum import AssociationIndex  # type: ignore
from tm2p.enum import GraphClusteringAlgorithm  # type: ignore
from tm2p.enum import UnitOrderBy  # type: ignore
from tm2p.ingest.rec import Coverage  # type: ignore
from tm2p.portfolio.emerg.emerg import Metrics  # type: ignore
from tm2p.portfolio.thematic_struct.co_occur.direct import (
    UnitsByCluster,
)  # type: ignore

ASSOCIATION_INDEX = AssociationIndex.ASSOCIATION_STRENGTH
CLUSTERING = GraphClusteringAlgorithm.LOUVAIN
ROOT_DIRECTORY = "./scopus/"


MAX_RECURSIVE_CLUSTERING_DEPTH = 3
MIN_RECURSIVE_CLUSTER_SIZE = 8
MINIMUM_PAIR_CO_OCCURRENCE = 1
RATIO_THRESHOLD = 1.00
YEAR = 2018
YEAR_RANGE = (YEAR - 9, YEAR)


def main():

    filename = Path("outputs") / f"concepts_{YEAR_RANGE[0]}_{YEAR_RANGE[1]}.txt"

    if filename.exists():
        filename.unlink()

    df = (
        Metrics()
        #
        # ANALYSIS UNIT:
        .with_analysis_unit(AnalysisUnit.CONCEPT)
        #
        # EMERGENCE:
        .using_emergence_baseline_periods(3)
        .using_emergence_recent_periods(4)
        .using_emergence_novelty_threshold(0.3)
        .using_emergence_min_total_records(7)
        .using_emergence_min_active_periods(3)
        .using_emergence_ratio_threshold(RATIO_THRESHOLD)
        #
        # COUNTERS:
        .using_counters(False)
        #
        # DATABASE:
        .where_root_directory(ROOT_DIRECTORY)
        .where_record_years_range(YEAR_RANGE[0], YEAR_RANGE[1])
        .where_record_global_citations_range(None, None)
        .where_records_match(None)
        #
        .run()
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(df.to_string())
        f.write("\n\n")

    units_by_cluster = (
        UnitsByCluster()
        #
        # ANALYSIS UNIT:
        .with_analysis_unit(AnalysisUnit.CONCEPT)
        #
        .having_top_n_units(None)
        .having_units_ordered_by(UnitOrderBy.OCC)
        .having_unit_occurrence_between(None, None)
        .having_unit_global_citation_between(None, None)
        .having_units_in(df.index.tolist())
        #
        .using_minimum_pair_co_occurrence(MINIMUM_PAIR_CO_OCCURRENCE)
        #
        # COUNTERS:
        .using_counters(False)
        #
        # NETWORK:
        .using_association_index(ASSOCIATION_INDEX)
        #
        # CLUSTERING:
        .using_clustering(CLUSTERING)
        .using_max_recursive_clustering_depth(MAX_RECURSIVE_CLUSTERING_DEPTH)
        .using_min_recursive_cluster_size(MIN_RECURSIVE_CLUSTER_SIZE)
        #
        # DATABASE:
        .where_root_directory(ROOT_DIRECTORY)
        .where_record_years_range(YEAR_RANGE[0], YEAR_RANGE[1])
        .where_record_global_citations_range(None, None)
        .where_records_match(None)
        #
        .run()
    )

    units_by_cluster.to_csv(
        Path("outputs") / f"units_by_cluster_{YEAR_RANGE[0]}_{YEAR_RANGE[1]}.tsv",
        index=False,
        sep="\t",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
