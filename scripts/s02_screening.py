"""Creates a json file with the answers"""

import json
import os
import re
import sys
import time

import pandas as pd  # type: ignore
from openai import APIError, OpenAI

SYSTEM_PROMPT = """
CONTEXT:
Your are contributing to the phase of screening (PRISMA) with the aim of
selecting relevant Scopus documents which be used in biblimetric,
scientomeetric, literature review, meta-analysis and tech-mining studies.
The documents are related to the field of PeaceTech, which is an emerging
interdisciplinary field that explores the application of technology and
innovation to promote peace, conflict resolution, and social cohesion.


TASK:
Determine if the provided document should be selected (Included) or discarded
(Excluded) based on the following criteria:

INCLUSION CRITERIA (IC):

* IC1 (Food Domain): The document must address food, food products, food systems, food supply chains, diets, recipes, meals, nutrition, food consumption, food safety, food quality, food production, food services, or agri-food contexts.

* IC2 (Analytics Core): The document must explicitly apply, develop, evaluate, or discuss data analytics, data science, machine learning, deep learning, artificial intelligence, statistical modelling, predictive analytics, data mining, computer vision, natural language processing, recommender systems, optimisation, simulation, or decision-support methods.

* IC3 (Functional Link): There must be a direct link between the analytical method and a food-related objective, such as prediction, classification, detection, monitoring, optimisation, recommendation, traceability, risk assessment, quality control, demand forecasting, food safety assessment, consumer behaviour analysis, nutrition assessment, or decision support.

* IC4 (Empirical, Methodological, or Applied Contribution): The document must present an empirical application, dataset-based analysis, methodological framework, computational model, review, or decision-support approach relevant to Food Analytics.

* IC5 (Sufficient Thematic Centrality): Food Analytics must be a central focus of the document, not only a minor example, incidental application, or brief contextual reference.

EXCLUSION CRITERIA (EC):

* EC1 (Non-Food Domain): Discard if the document does not address food, diet, nutrition, recipes, food products, food safety, food quality, food consumption, food services, food production, or agri-food systems.

* EC2 (No Analytics Component): Discard if the document focuses on food-related issues but does not use or discuss data analytics, computational modelling, artificial intelligence, machine learning, statistical modelling, predictive methods, data mining, optimisation, or decision-support methods.

* EC3 (Purely Laboratory or Instrumental Studies without Analytics): Discard if the document is limited to laboratory experiments, chemical analysis, microbiological testing, sensory evaluation, or instrumental measurement without a clear analytical, computational, predictive, or data-driven modelling component.

* EC4 (General Food Science without Data-Driven Focus): Discard if the document is mainly about food formulation, processing, preservation, packaging, agriculture, nutrition, or food policy without a substantive analytics or data-science contribution.

* EC5 (Generic AI/Data Science without Food Link): Discard if the document discusses analytics, artificial intelligence, machine learning, computer vision, or data science but applies them to a non-food domain, with no direct food-related objective.

* EC6 (Agriculture-Only Noise): Discard if the document focuses exclusively on crop production, livestock management, soil, irrigation, plant disease, precision agriculture, or farm management without a direct connection to food products, food quality, food safety, food supply, food consumption, nutrition, or agri-food decision-making.

* EC7 (Medical/Nutrition Noise without Food Analytics): Discard if the document focuses only on clinical nutrition, disease treatment, biomedical outcomes, metabolism, or public health associations without an analytics-based contribution centred on food, diet, meals, recipes, or consumption data.

* EC8 (Business or Management Noise): Discard if the document focuses only on general business management, marketing, logistics, consumer preferences, sustainability, or supply-chain strategy without a clear data analytics, modelling, or decision-support component.

* EC9 (Methodological Noise): Discard if analytical terms such as “classification,” “prediction,” “clustering,” “modelling,” or “optimisation” refer only to abstract mathematical, engineering, or computational problems without a substantive food-related application.

* EC10 (Incidental Mention): Discard if food-related terms appear only as examples, background context, keywords, or minor references, and the document’s main contribution belongs to another field.

PROCEDURE:

1. Analyze the Title, Abstract, and Keywords.

2. Apply the IC and EC filters.

3. Determine the final answer.


OUTPUT FORMAT (STRICT — JSON ONLY):
The output MUST be a JSON object with the following structure:

{{
    "answer": "yes" or "no",
}}


Any output different of this must be considered invalid.

"""

USER_PROMPT = """

TITLE:
{}

ABSTRACT:
"{}"

"""

CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Screening:

    def __init__(
        self,
        input_file: str,
        sep: str,
        output_file: str,
        abstract_col: str,
        title_col: str,
        year_col: str,
        citations_col: str,
        first_pass_model: str = "gpt-4.1-mini",
        second_pass_model: str = "gpt-4.1",
    ) -> None:

        self.input_file: str = input_file
        self.sep: str = sep
        self.output_file: str = output_file

        self.abstract_col: str = abstract_col
        self.title_col: str = title_col
        self.citations_col: str = citations_col
        self.year_col: str = year_col

        self.first_pass_model: str = first_pass_model
        self.second_pass_model: str = second_pass_model

        self._total: int = 0
        self._accepted = 0
        self._counter = 0

        self._current_model: str = self.first_pass_model
        self._last_request_time: float = 0.0

        self._df = None
        self._is_first_pass: bool = True

    def _reset_counters(self):
        self._accepted = 0
        self._counter = 0

    def _mark_all_records(self):
        self._df["_MARKED_"] = True

    def _mark_recent_recods(self):

        df = self._df.copy()
        max_year = df[self.year_col].max()
        df = df.loc[~df["_SELECTED_"], :]
        df = df.loc[df[self.year_col] >= max_year - 2, :]
        self._df["_MARKED_"] = False
        self._df.loc[df.index, "_MARKED_"] = True

    def _mark_old_cited_records(self):

        df = self._df.copy()

        records_by_year = df[self.year_col].value_counts()
        records_by_year = records_by_year[records_by_year <= 20]
        selected_years = records_by_year.index.to_list()

        self._df["_MARKED_"] = False
        self._df.loc[
            df[self.year_col].apply(lambda x: x in selected_years), "_MARKED_"
        ] = True

    def _mark_highly_cited_records(self):

        df = self._df.copy()
        df = df.sort_values(by=self.citations_col, ascending=False)
        df = df.loc[df[self.citations_col] > 0, :]
        n = int(len(df) * 0.1)
        df = df.loc[~df["_SELECTED_"], :]
        df = df.head(n)
        self._df["_MARKED_"] = False
        self._df.loc[df.index, "_MARKED_"] = True

    def _load_raw_csv_file(self):
        self._df = pd.read_csv(self.input_file, sep=self.sep)
        self._total = len(self._df)
        self._df["_SELECTED_"] = False

    def _make_first_pass(self):

        sys.stderr.write(f"\nMaking first pass with model: {self.first_pass_model}\n\n")
        sys.stderr.flush()

        self._current_model = self.first_pass_model
        self._is_first_pass = True
        self._reset_counters()
        self._mark_all_records()
        self._df["_SELECTED_"] = self._df.apply(self._process_row, axis=1)
        self._report()

    def _make_second_pass(self):

        sys.stderr.write(
            f"\nMaking second pass with model: {self.second_pass_model}\n\n"
        )
        sys.stderr.flush()

        self._current_model = self.second_pass_model
        self._is_first_pass = False
        self._reset_counters()
        self._mark_recent_recods()
        self._df["_SELECTED_"] = self._df.apply(self._process_row, axis=1)
        self._report()

    def _make_third_pass(self):

        sys.stderr.write(
            f"\nMaking third pass with model: {self.second_pass_model}\n\n"
        )
        sys.stderr.flush()

        self._current_model = self.second_pass_model
        self._is_first_pass = False
        self._reset_counters()
        self._mark_highly_cited_records()
        self._df["_SELECTED_"] = self._df.apply(self._process_row, axis=1)
        self._report()

    def _make_fourth_pass(self):

        sys.stderr.write(
            f"\nMaking fourth pass with model: {self.second_pass_model}\n\n"
        )
        sys.stderr.flush()

        self._current_model = self.second_pass_model
        self._is_first_pass = False
        self._reset_counters()
        self._mark_old_cited_records()
        self._df["_SELECTED_"] = self._df.apply(self._process_row, axis=1)
        self._report()

    def _report(self):

        sys.stderr.write(
            f"\nTotal: {self._total} = {self._accepted} accepted + {self._total - self._accepted} rejected\n\n"
        )
        sys.stderr.flush()

    def _make_api_call(self, row):

        title = row[self.title_col]
        abstract = row[self.abstract_col]

        query = USER_PROMPT.format(title, abstract)
        max_retries = 6

        for attempt in range(max_retries):
            self._wait_for_rate_limit_slot()

            try:
                response = CLIENT.chat.completions.create(
                    model=self._current_model,
                    messages=[
                        {
                            "role": "system",  # type: ignore
                            "content": SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "role": "user",
                            "content": query,
                        },
                    ],
                    temperature=0,
                    max_completion_tokens=16,
                    response_format={"type": "json_object"},
                )

                raw_answer = response.choices[0].message.content or '{"answer":"no"}'
                return self._parse_answer(raw_answer)

            except APIError as e:
                message = str(e)
                wait_seconds = self._get_wait_seconds(message, attempt)
                sys.stderr.write(
                    f"API error on attempt {attempt + 1}/{max_retries}: {message}. Retrying in {wait_seconds:.2f}s\n"
                )
                sys.stderr.flush()
                time.sleep(wait_seconds)

            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                sys.stderr.write(f"Invalid model response: {e}\n")
                sys.stderr.flush()
                return False

        return False

    def _parse_answer(self, raw_answer):
        parsed = json.loads(raw_answer)
        answer = str(parsed.get("answer", "no")).strip().lower()
        return answer == "yes"

    def _wait_for_rate_limit_slot(self):
        min_interval = 2.0 if self._current_model == self.second_pass_model else 0.8
        elapsed = time.time() - self._last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request_time = time.time()

    def _get_wait_seconds(self, message, attempt):
        # Handles messages such as: "Please try again in 235ms."
        match = re.search(r"try again in\s+([\d.]+)\s*(ms|s)", message, re.IGNORECASE)
        if match is not None:
            value = float(match.group(1))
            unit = match.group(2).lower()
            return value / 1000 if unit == "ms" else value

        return min(2**attempt, 30)

    def _process_row(self, row):

        marked = row["_MARKED_"]
        if marked:
            accepted = self._make_api_call(row)
        else:
            accepted = row["_SELECTED_"]

        if accepted:
            self._accepted += 1

        self._counter += 1
        sys.stderr.write(
            f"  Processing {self._counter:04d} of {self._total:04d} --  Accepted: {self._accepted}\n"
        )
        sys.stderr.flush()

        return accepted

    def _save_results(self):

        self._df = self._df.loc[self._df["_SELECTED_"], :]
        self._df.to_csv(self.output_file, index=False, sep=self.sep)

    def run(self):

        self._load_raw_csv_file()
        self._make_first_pass()
        self._make_second_pass()
        self._make_third_pass()
        self._make_fourth_pass()
        self._save_results()


def main():

    scopus = Screening(
        input_file="scopus/ingest/downloaded/_merged.csv",
        sep=",",
        output_file="scopus/ingest/downloaded/selected.csv",
        abstract_col="Abstract",
        title_col="Title",
        year_col="Year",
        citations_col="Cited by",
        first_pass_model="gpt-4.1-mini",
        second_pass_model="gpt-4.1",
    )

    wos = Screening(
        input_file="wos/ingest/downloaded/_merged.tsv",
        sep="\t",
        output_file="wos/ingest/downloaded/selected.tsv",
        abstract_col="AB",
        title_col="TI",
        year_col="PY",
        citations_col="TC",
        first_pass_model="gpt-4.1-mini",
        second_pass_model="gpt-4.1",
    )

    scopus.run()
    # wos.run()


if __name__ == "__main__":
    main()
