from pathlib import Path  # type: ignore

from tm2p.enum import AnalysisUnit  # type: ignore
from tm2p.enum import AssociationIndex  # type: ignore
from tm2p.enum import GraphClusteringAlgorithm  # type: ignore
from tm2p.enum import NodeSizeMetric  # type: ignore
from tm2p.enum import Scaling  # type: ignore
from tm2p.enum import UnitOrderBy  # type: ignore
from tm2p.portfolio.temporal_evol.thematic_evol import Plot  # type: ignore
from tm2p.portfolio.thematic_struct.co_occur.direct import NetworkPlot  # type: ignore
from tm2p.portfolio.thematic_struct.co_occur.direct import (  # type: ignore
    ClusterInterpretation,
    ClusterToUnits,
    StrategicDiagram,
    UnitsByCluster,
)

ASSOCIATION_INDEX = AssociationIndex.ASSOCIATION_STRENGTH
CLUSTERING = GraphClusteringAlgorithm.LOUVAIN
ROOT_DIRECTORY = "./scopus/"

MAX_RECURSIVE_CLUSTERING_DEPTH = 3
MIN_RECURSIVE_CLUSTER_SIZE = 8
MINIMUM_PAIR_CO_OCCURRENCE = 1


PARAMETERS = [
    {
        "YEAR_RANGE": (1983, 2008),
        "SPRING_LAYOUT_K": 1.00,
        "SPRING_LAYOUT_SEED": 3,
        "MIN_OCC": 3,
    },
    {
        "YEAR_RANGE": (2009, 2016),
        "SPRING_LAYOUT_K": 1.00,
        "SPRING_LAYOUT_SEED": 3,
        "MIN_OCC": 3,
    },
    {
        "YEAR_RANGE": (2017, 2019),
        "SPRING_LAYOUT_K": 0.70,
        "SPRING_LAYOUT_SEED": 1,
        "MIN_OCC": 3,
    },
    {
        "YEAR_RANGE": (2020, 2023),
        "SPRING_LAYOUT_K": 0.90,
        "SPRING_LAYOUT_SEED": 0,
        "MIN_OCC": 8,
    },
    {
        "YEAR_RANGE": (2024, 2026),
        "SPRING_LAYOUT_K": 0.90,
        "SPRING_LAYOUT_SEED": 0,
        "MIN_OCC": 19,
    },
]


def main():
    # report_units_by_cluster()
    # report_interpretation_metrics()
    report_strategic_diagrams()
    # make_network_plots()
    # make_thematic_evolution_map()


def make_network_plots():
    for period_parameters in PARAMETERS:
        make_network_plot_per_period(period_parameters)


def make_network_plot_per_period(period_parameters):

    year_start, year_end = period_parameters["YEAR_RANGE"]
    min_occ = period_parameters["MIN_OCC"]
    spring_layout_k = period_parameters["SPRING_LAYOUT_K"]
    spring_layout_seed = period_parameters["SPRING_LAYOUT_SEED"]

    fig = (
        NetworkPlot()
        #
        # ANALYSIS UNIT:
        .with_analysis_unit(AnalysisUnit.CONCEPT)
        #
        .having_top_n_units(None)
        .having_units_ordered_by(UnitOrderBy.OCC)
        .having_unit_occurrence_between(min_occ, None)
        .having_unit_global_citation_between(None, None)
        .having_units_in(None)
        #
        .using_minimum_pair_co_occurrence(1)
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
        # NETWORK:
        .using_spring_layout_k(spring_layout_k)
        .using_spring_layout_iterations(200)
        .using_spring_layout_seed(spring_layout_seed)
        #
        .using_discrete_node_colors(
            (
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",
                "#bcbd22",
                "#17becf",
            )
        )
        .using_min_node_degree(3)
        .using_node_scaling(Scaling.SQRT)
        .using_node_size_metric(NodeSizeMetric.TLS)
        .using_node_size_range(8, 60)
        .using_top_n_nodes(100)
        .using_uniform_node_opacity(0.75)
        #
        .using_max_node_labels(30)
        .using_node_label_max_length(20)
        #
        .using_textfont_opacity_range(0.35, 1.00)
        .using_textfont_size_range(9, 20)
        #
        # https://www.w3schools.com/colors/colors_shades.asp
        .using_edge_opacity_range(0.20, 0.85)
        .using_edge_scaling(Scaling.SQRT)
        .using_edge_width_range(1.0, 5.0)
        .using_global_top_edges(200)
        .using_top_edges_per_node(5)
        .using_uniform_edge_color("#d8d8d8")
        #
        .using_xaxes_range(None, None)
        .using_yaxes_range(None, None)
        .using_axes_visible(False)
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
        Path("outputs") / "paper-1" / f"network_plot_{year_start}_{year_end}.html"
    )

    fig.write_html(filename)


def make_thematic_evolution_map():

    mappings = []
    periods = []

    for period_parameters in PARAMETERS:

        year_start = period_parameters["YEAR_RANGE"][0]
        year_end = period_parameters["YEAR_RANGE"][1]
        min_occ = period_parameters["MIN_OCC"]
        periods.append(f"{year_start}-{year_end}")

        mapping = (
            ClusterToUnits()
            #
            # ANALYSIS UNIT:
            .with_analysis_unit(AnalysisUnit.CONCEPT)
            #
            .having_top_n_units(None)
            .having_units_ordered_by(UnitOrderBy.OCC)
            .having_unit_occurrence_between(min_occ, None)
            .having_unit_global_citation_between(None, None)
            .having_units_in(None)
            #
            .using_minimum_pair_co_occurrence(1)
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
        mappings.append(mapping)

    fig = (
        Plot()
        #
        .using_title_text("")
        .using_tmap_minimum_shared_units(2)
        .using_tmap_mininum_jaccard_similarity(0.15)
        .using_tmap_minimum_inclusion_index(0.40)
        .using_clusters_per_period(tuple(mappings))
        .using_tmap_period_headers(periods)
        .using_tmap_n_labels_per_cluster(3)
        #
        .run()
    )

    filename = Path("outputs") / "paper-1" / "evolution_map.html"
    fig.write_html(filename)


def report_units_by_cluster():
    for period_parameters in PARAMETERS:
        report_units_by_cluster_per_period(period_parameters)


def report_units_by_cluster_per_period(period_parameters):

    year_start = period_parameters["YEAR_RANGE"][0]
    year_end = period_parameters["YEAR_RANGE"][1]
    min_occ = period_parameters["MIN_OCC"]

    units_by_cluster = (
        UnitsByCluster()
        #
        # ANALYSIS UNIT:
        .with_analysis_unit(AnalysisUnit.CONCEPT)
        #
        .having_top_n_units(None)
        .having_units_ordered_by(UnitOrderBy.OCC)
        .having_unit_occurrence_between(min_occ, None)
        .having_unit_global_citation_between(None, None)
        .having_units_in(None)
        #
        .using_minimum_pair_co_occurrence(1)
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

    filename = (
        Path("outputs") / "paper-1" / f"units_by_cluster_{year_start}_{year_end}.txt"
    )

    units_by_cluster.to_string(filename, index=False, encoding="utf-8")
    filename = filename.with_suffix(".tsv")
    units_by_cluster.to_csv(filename, index=False, encoding="utf-8", sep="\t")


def report_interpretation_metrics():
    for period_parameters in PARAMETERS:
        report_interpretation_metrics_per_period(period_parameters)


def report_interpretation_metrics_per_period(period_parameters):

    year_start, year_end = period_parameters["YEAR_RANGE"]
    min_occ = period_parameters["MIN_OCC"]

    cluster_interpretation = (
        ClusterInterpretation()
        #
        # ANALYSIS UNIT:
        .with_analysis_unit(AnalysisUnit.CONCEPT)
        #
        .having_top_n_units(None)
        .having_units_ordered_by(UnitOrderBy.OCC)
        .having_unit_occurrence_between(min_occ, None)
        .having_unit_global_citation_between(None, None)
        .having_units_in(None)
        #
        .using_minimum_pair_co_occurrence(1)
        #
        # COUNTERS:
        .using_counters(True)
        #
        # NORMALIZATION:
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

    filename = (
        Path("outputs") / "paper-1" / f"interpretation_{year_start}_{year_end}.txt"
    )

    cluster_interpretation.to_string(filename, index=False, encoding="utf-8")
    filename = filename.with_suffix(".tsv")
    cluster_interpretation.to_csv(filename, index=False, encoding="utf-8", sep="\t")


def report_strategic_diagrams():
    for period_parameters in PARAMETERS:
        make_strategic_diagram_per_period(period_parameters)


def make_strategic_diagram_per_period(period_parameters):

    year_start, year_end = period_parameters["YEAR_RANGE"]
    min_occ = period_parameters["MIN_OCC"]

    fig = (
        StrategicDiagram()
        #
        # ANALYSIS UNIT:
        .with_analysis_unit(AnalysisUnit.CONCEPT)
        #
        .having_top_n_units(None)
        .having_units_ordered_by(UnitOrderBy.OCC)
        .having_unit_occurrence_between(min_occ, None)
        .having_unit_global_citation_between(None, None)
        .having_units_in(None)
        #
        .using_minimum_pair_co_occurrence(1)
        #
        # COUNTERS:
        .using_counters(True)
        #
        # NORMALIZATION:
        .using_association_index(ASSOCIATION_INDEX)
        #
        # CLUSTERING:
        .using_clustering(CLUSTERING)
        .using_max_recursive_clustering_depth(MAX_RECURSIVE_CLUSTERING_DEPTH)
        .using_min_recursive_cluster_size(MIN_RECURSIVE_CLUSTER_SIZE)
        #
        # MAP:
        .using_colorscale(
            [
                [0.00, "#2C7BB6"],
                [0.35, "#00A6CA"],
                [0.65, "#4EBA6F"],
                [1.00, "#F28E2B"],
            ]
        )
        .using_node_size_range(20, 80)
        .using_node_scaling(Scaling.LOG)
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
        Path("outputs") / "paper-1" / f"strategic_diagram_{year_start}_{year_end}.html"
    )

    fig.write_html(filename)


if __name__ == "__main__":
    main()
