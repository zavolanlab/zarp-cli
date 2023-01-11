"""ZARP sample table processing."""

from copy import deepcopy
from pathlib import Path
import logging
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

from bidict import frozenbidict
import pandas as pd  # type: ignore

from zarp.config.enums import FieldNameMappingDirection
from zarp.utils import list_get

LOGGER = logging.getLogger(__name__)


class SampleTableProcessor:
    """Process ZARP sample tables.

    Read, write and process ZARP sample tables.

    Args:
        records: List of sample table records.

    Attributes:
        records: List of sample table records.
    """

    # bijective map: ZARP sample table column names <> Sample model properties
    # Cf.
    # https://github.com/zavolanlab/zarp/blob/ce1ce2ee2f37517967e6b8aaa0dc4cda3014e08e/pipeline_documentation.md#read-sample-table
    # some values are manually transformed
    key_mapping = frozenbidict(
        {
            "sample": "name",
            "organism": "source",
            "gtf": "annotations",
            "genome": "reference_sequences",
            "sd": "fragment_length_distribution_sd",
            "mean": "fragment_length_distribution_mean",
            "libtype": "read_orientation",
            "index_size": "star_sjdb_overhang",
            "kmer": "salmon_kmer_size",
        }
    )
    col_order = [
        "sample",
        "fq1",
        "fq2",
        "organism",
        "gtf",
        "genome",
        "gtf",
        "libtype",
        "fq1_3p",
        "fq2_3p",
        "fq1_5p",
        "fq2_5p",
        "fq1_polya_3p",
        "fq2_polya_3p",
        "fq1_polya_5p",
        "fq2_polya_5p",
        "mean",
        "sd",
        "index_size",
        "kmer",
    ]

    def __init__(
        self,
        records: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Class constructor."""
        self.records: List[Dict[str, Any]] = [] if records is None else records

    def read(self, path: Path) -> None:
        """Read sample table.

        Args:
            path: Path to sample table.
        """
        LOGGER.debug(f"Reading sample table: {path}")
        data = pd.read_csv(
            path,
            comment="#",
            sep="\t",
            keep_default_na=False,
        )
        self.records = data.to_dict("records")  # type: ignore
        self._to_model_records(table_dir=path.parent)
        LOGGER.debug(f"Sample table records found: {len(self.records)}")

    def write(self, path: Path) -> None:
        """Write ZARP sample table.

        Args:
            path: Path where sample table is to be written.
        """
        LOGGER.debug(f"Writing sample table: {path}")
        self._to_sample_table_records()
        data = pd.DataFrame(self.records)
        data_reordered = data[self.col_order]
        data_reordered.to_csv(path, sep="\t", index=False)
        LOGGER.debug(f"Records written: {len(self.records)}")

    def _to_model_records(self, table_dir: Path) -> None:
        """Transform sample table to model records.

        Args:
            table_dir: Directory where sample table is located.
        """
        self._translate_field_names(
            direction=FieldNameMappingDirection.TO_MODEL_PROPERTIES
        )
        records: List[Dict[str, Any]] = []
        for record in self.records:
            rec_cp = {key: val for key, val in record.items() if val != ""}
            rec_cp["paths"] = (
                None
                if rec_cp.get("fq1", None) is None
                else self.resolve_path(anchor=table_dir, path=rec_cp["fq1"]),
                None
                if rec_cp.get("fq2", None) is None
                else self.resolve_path(anchor=table_dir, path=rec_cp["fq2"]),
            )
            rec_cp["annotations"] = (
                None
                if rec_cp.get("annotations", None) is None
                else self.resolve_path(
                    anchor=table_dir, path=rec_cp["annotations"]
                )
            )
            rec_cp["reference_sequences"] = (
                None
                if rec_cp.get("reference_sequences", None) is None
                else self.resolve_path(
                    anchor=table_dir,
                    path=rec_cp["reference_sequences"],
                )
            )
            rec_cp["adapter_3p"] = (
                rec_cp.get("fq1_3p", None),
                rec_cp.get("fq2_3p", None),
            )
            rec_cp["adapter_5p"] = (
                rec_cp.get("fq1_5p", None),
                rec_cp.get("fq2_5p", None),
            )
            rec_cp["adapter_poly_3p"] = (
                rec_cp.get("fq1_polya_3p", None),
                rec_cp.get("fq2_polya_3p", None),
            )
            rec_cp["adapter_poly_5p"] = (
                rec_cp.get("fq1_polya_5p", None),
                rec_cp.get("fq2_polya_5p", None),
            )
            entries_to_remove = [
                "fq1",
                "fq2",
                "fq1_3p",
                "fq2_3p",
                "fq1_5p",
                "fq2_5p",
                "fq1_polya_3p",
                "fq2_polya_3p",
                "fq1_polya_5p",
                "fq2_polya_5p",
                "seqmode",
            ]
            for key in entries_to_remove:
                _ = rec_cp.pop(key, None)
            records.append(rec_cp)
        self.records = records

    def _to_sample_table_records(self) -> None:
        """Transform model to sample table records."""
        self._translate_field_names(
            direction=FieldNameMappingDirection.TO_TABLE_COL_NAMES
        )
        records: List[Dict[str, Any]] = []
        for record in self.records:
            rec_cp = deepcopy(record)
            rec_cp["fq1"] = str(list_get(rec_cp.get("paths", []), 0, ""))
            rec_cp["fq2"] = str(list_get(rec_cp.get("paths", []), 1, ""))
            rec_cp["fq1_3p"] = list_get(rec_cp.get("adapter_3p", []), 0, "")
            rec_cp["fq2_3p"] = list_get(rec_cp.get("adapter_3p", []), 1, "")
            rec_cp["fq1_5p"] = list_get(rec_cp.get("adapter_5p", []), 0, "")
            rec_cp["fq2_5p"] = list_get(rec_cp.get("adapter_5p", []), 1, "")
            rec_cp["fq1_polya_3p"] = list_get(
                rec_cp.get("adapter_poly_3p", []), 0, ""
            )
            rec_cp["fq2_polya_3p"] = list_get(
                rec_cp.get("adapter_poly_3p", []), 1, ""
            )
            rec_cp["fq1_polya_5p"] = list_get(
                rec_cp.get("adapter_poly_5p", []), 0, ""
            )
            rec_cp["fq2_polya_5p"] = list_get(
                rec_cp.get("adapter_poly_5p", []), 1, ""
            )
            rec_cp_clean = {
                key: ("" if val is None else val)
                for key, val in rec_cp.items()
            }
            entries_to_remove = [
                "adapter_3p",
                "adapter_5p",
                "adapter_poly_3p",
                "adapter_poly_5p",
                "id",
                "paths",
                "type",
            ]
            for key in entries_to_remove:
                _ = rec_cp_clean.pop(key, None)
            records.append(rec_cp_clean)
        self.records = records

    def _translate_field_names(
        self,
        direction: FieldNameMappingDirection = (
            FieldNameMappingDirection.TO_MODEL_PROPERTIES
        ),
    ) -> None:
        """Translate record field names.

        Args:
            direction: Direction of mapping. Either to model property or to
                sample table column names.
        """
        data = pd.DataFrame(self.records)
        mapping = (
            self.key_mapping
            if direction == FieldNameMappingDirection.TO_MODEL_PROPERTIES
            else self.key_mapping.inv
        )
        data_renamed = data.rename(columns=mapping)
        self.records = data_renamed.to_dict("records")  # type: ignore

    @staticmethod
    def resolve_path(anchor: Union[Path, str], path: Union[Path, str]) -> Path:
        """Resolve absolute path relative to an anchor.

        Args:
            anchor: Anchor path.
            path: Path to resolve. If absolute, will be returned as is, but as
                Path object.
        """
        if Path(path).is_absolute():
            return Path(path)
        return (Path(anchor) / path).resolve()
