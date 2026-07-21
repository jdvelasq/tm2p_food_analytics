from pathlib import Path  # type: ignore

from tm2p.enum import AnalysisUnit  # type: ignore
from tm2p.enum import AssociationIndex  # type: ignore
from tm2p.enum import GraphClusteringAlgorithm  # type: ignore
from tm2p.enum import UnitOrderBy  # type: ignore
from tm2p.portfolio.emerg.emerg import Metrics  # type: ignore
from tm2p.portfolio.thematic_struct.co_occur.direct import (
    ClusterDefinition,
)  # type: ignore

ASSOCIATION_INDEX = AssociationIndex.ASSOCIATION_STRENGTH
CLUSTERING = GraphClusteringAlgorithm.LOUVAIN
ROOT_DIRECTORY = "./scopus/"

MAX_RECURSIVE_CLUSTERING_DEPTH = 3
MIN_RECURSIVE_CLUSTER_SIZE = 8
MINIMUM_PAIR_CO_OCCURRENCE = 1

PARAMETERS = {"YEAR_RANGE": (2016, 2026), "RATIO_THRESHOLD": 1.12}


def main():

    year_start, year_end = PARAMETERS["YEAR_RANGE"]
    ratio_threshold = PARAMETERS["RATIO_THRESHOLD"]

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

    (
        ClusterDefinition()
        #
        # ANALYSIS UNIT:
        .with_analysis_unit(AnalysisUnit.CONCEPT)
        #
        .having_top_n_units(None)
        .having_units_ordered_by(UnitOrderBy.OCC)
        .having_unit_occurrence_between(None, None)
        .having_unit_global_citation_between(None, None)
        .using_minimum_pair_co_occurrence(MINIMUM_PAIR_CO_OCCURRENCE)
        .having_units_in(df.index.tolist())
        #
        # COUNTERS:
        .using_counters(False)
        #
        # NORMALIZATION:
        .using_association_index(ASSOCIATION_INDEX)
        #
        # CLUSTERING:
        .using_clustering(CLUSTERING)
        .using_max_recursive_clustering_depth(MAX_RECURSIVE_CLUSTERING_DEPTH)
        .using_min_recursive_cluster_size(MIN_RECURSIVE_CLUSTER_SIZE)
        #
        # TEXT:
        .with_core_area("food analytics")
        .using_gpt_model("gpt-4.1")
        .using_word_length(300)
        .using_cluster_names([f"C_{i}" for i in range(20)])
        #
        # DATABASE:
        .where_root_directory(ROOT_DIRECTORY)
        .where_record_years_range(year_start, year_end)
        .where_record_global_citations_range(None, None)
        .where_records_match(None)
        #
        .run()
    )


if __name__ == "__main__":
    main()
