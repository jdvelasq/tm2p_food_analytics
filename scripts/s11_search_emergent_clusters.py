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

PARAMETERS = [
    {
        "YEAR_RANGE": (2016, 2026),
        "RATIO_THRESHOLD": [
            1.10,
            1.11,
            1.12,  # optimal value
            1.13,
            1.14,
            1.15,
            1.16,
            1.17,
        ],
    },
]


def main():
    for period_parameters in PARAMETERS:
        analyze_period(period_parameters)


def analyze_period(period_parameters):

    year_start, year_end = period_parameters["YEAR_RANGE"]

    for ratio_threshold in period_parameters["RATIO_THRESHOLD"]:

        print(f"Processing ratio_threshold: {ratio_threshold}")

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
            .using_emergence_ratio_threshold(ratio_threshold)
            #
            # COUNTERS:
            .using_counters(False)
            #
            # DATABASE:
            .where_root_directory(ROOT_DIRECTORY)
            .where_record_years_range(year_start, year_end)
            .where_record_global_citations_range(None, None)
            .where_records_match(None)
            #
            .run()
        )
        filename = (
            Path("outputs")
            / "search"
            / f"concepts_{year_start}_{year_end}_with_ratio_{ratio_threshold:<3.2f}.txt"
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
            .where_record_years_range(year_start, year_end)
            .where_record_global_citations_range(None, None)
            .where_records_match(None)
            #
            .run()
        )

        units_by_cluster.to_csv(
            Path("outputs")
            / "search"
            / f"units_by_cluster_{year_start}_{year_end}_with_ratio_{ratio_threshold:<3.2f}.tsv",
            index=False,
            sep="\t",
            encoding="utf-8",
        )

    print("\n")


if __name__ == "__main__":
    main()
